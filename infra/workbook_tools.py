#!/usr/bin/env python3
"""
CLI tool for reading and editing an existing Excel workbook (openpyxl).

Used by the workbook-edit skills (/port-replicate-model, /fix-debug-audit).
Every command prints JSON to stdout. Edits are always written to a copy — the
user's original file is never overwritten.

Usage:
    python infra/workbook_tools.py tabs model.xlsx
    python infra/workbook_tools.py read model.xlsx "Model!A1:M80"
    python infra/workbook_tools.py read model.xlsx "Model" --all
    python infra/workbook_tools.py refs model.xlsx "Model!B10:M80"
    python infra/workbook_tools.py apply model.xlsx changes.json --label audit
    python infra/workbook_tools.py apply reports/model_audit_20261106.xlsx more.json --in-place
    python infra/workbook_tools.py recalc reports/model_audit_20261106.xlsx --cells "Model!F95:M95"

Change list format (apply) — a JSON array, applied in order:
    {"cell": "Model!C14", "value": 1234.5}
    {"cell": "Model!F30", "formula": "=F28-F29"}
    {"cell": "Model!F30", "clear": true}
    {"range": "Model!C14:C20", "format": {"number_format": "#,##0.0", "bold": false,
                                          "italic": false, "font_name": "Arial", "font_size": 10,
                                          "font_color": "FF0000FF", "fill": "FFFFFF00" | "none"}}
    {"range": "HGV!A1:Z90", "copy_format_from": "TNL Model!A1:Z90"}
    {"add_sheet": "HGV", "after": "TNL Model"}
    {"sheet": "HGV", "layout_from": "TNL Model"}      (column widths, row heights, freeze panes)
    {"cell": "DATA!C5", "value": 812.0, "link": "https://daloopa.com/src/123"}
A value/formula write keeps the cell's existing format and hyperlink; it never adds a link
unless "link" is given.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from copy import copy
from datetime import date, datetime

from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter, range_boundaries
from openpyxl.workbook.properties import CalcProperties

DALOOPA_LINK = re.compile(r"daloopa\.com/src/(\d+)")

# Cell references inside a formula: optional sheet (quoted or bare, optional [n] external
# book prefix), then A1 or A1:B2. Not preceded by a name character, not followed by "(" so
# function names like LOG10( are skipped.
FORMULA_REF = re.compile(
    r"(?<![A-Za-z0-9_.$])"
    r"(?:(?P<sheet>'(?:[^']|'')+'|\[\d+\][A-Za-z0-9_.]+|[A-Za-z_][A-Za-z0-9_.]*)!)?"
    r"\$?(?P<c1>[A-Z]{1,3})\$?(?P<r1>\d+)"
    r"(?::\$?(?P<c2>[A-Z]{1,3})\$?(?P<r2>\d+))?"
    r"(?![A-Za-z0-9_(])"
)
STRING_LITERAL = re.compile(r'"(?:[^"]|"")*"')

# Workbook parts openpyxl does not round-trip reliably.
FRAGILE_PARTS = {
    "xl/drawings/": "drawings/shapes",
    "xl/charts/": "charts",
    "xl/pivotTables/": "pivot tables",
    "xl/externalLinks/": "links to other workbooks",
    "xl/slicers/": "slicers",
}


def fail(message):
    print(json.dumps({"error": message}, indent=2))
    sys.exit(1)


def parse_target(target, wb):
    """Split "Sheet!A1:B2" / "'My Sheet'!A1" / "Sheet" into (sheet_name, range_or_None)."""
    if "!" in target:
        sheet, _, rng = target.rpartition("!")
    else:
        sheet, rng = target, None
    sheet = sheet.strip()
    if sheet.startswith("'") and sheet.endswith("'"):
        sheet = sheet[1:-1].replace("''", "'")
    if sheet not in wb.sheetnames:
        fail(f"Sheet not found: {sheet!r}. Sheets: {wb.sheetnames}")
    return sheet, (rng.replace("$", "") if rng else None)


def iter_range(ws, rng):
    """Yield cells of rng (or the sheet's used range when rng is None)."""
    if rng is None:
        rng = ws.dimensions
    min_col, min_row, max_col, max_row = range_boundaries(rng)
    for row in ws.iter_rows(min_row=min_row, max_row=max_row, min_col=min_col, max_col=max_col):
        yield from row


def color_str(color):
    if color is None:
        return None
    if color.type == "rgb" and color.rgb not in (None, "00000000"):
        return color.rgb
    if color.type == "theme":
        return f"theme:{color.theme}" + (f"{color.tint:+.2f}" if color.tint else "")
    if color.type == "indexed" and color.indexed not in (None, 64):
        return f"indexed:{color.indexed}"
    return None


def json_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if value is None or isinstance(value, (int, float, str, bool)):
        return value
    return str(value)


def cell_kind(value):
    if value is None:
        return "empty"
    if isinstance(value, str) and value.startswith("="):
        return "formula"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "input"
    return "text"


def describe_cell(cell, cached):
    kind = cell_kind(cell.value)
    info = {"cell": cell.coordinate, "kind": kind}
    if kind == "formula":
        info["formula"] = cell.value
        info["cached"] = json_value(cached)
    else:
        info["value"] = json_value(cell.value)
    if cell.number_format and cell.number_format != "General":
        info["number_format"] = cell.number_format
    font = cell.font
    font_info = {}
    if font.name:
        font_info["name"] = font.name
    if font.sz:
        font_info["size"] = float(font.sz)
    if font.b:
        font_info["bold"] = True
    if font.i:
        font_info["italic"] = True
    font_color = color_str(font.color)
    if font_color:
        font_info["color"] = font_color
    if font_info:
        info["font"] = font_info
    if cell.fill is not None and cell.fill.fill_type == "solid":
        fill = color_str(cell.fill.fgColor)
        if fill:
            info["fill"] = fill
    if cell.hyperlink is not None and cell.hyperlink.target:
        info["link"] = cell.hyperlink.target
        match = DALOOPA_LINK.search(cell.hyperlink.target)
        if match:
            info["daloopa_id"] = int(match.group(1))
    return info


def fragile_parts(path):
    found = []
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
    except zipfile.BadZipFile:
        fail(f"Not a valid .xlsx/.xlsm file: {path}")
    for prefix, label in FRAGILE_PARTS.items():
        if any(n.startswith(prefix) for n in names):
            found.append(label)
    return found


def open_workbook(path, data_only=False):
    if not os.path.isfile(path):
        fail(f"Workbook not found: {path}")
    keep_vba = path.lower().endswith(".xlsm")
    return load_workbook(path, data_only=data_only, keep_vba=keep_vba)


def referenced_sheets(formula):
    sheets = set()
    for match in FORMULA_REF.finditer(STRING_LITERAL.sub('""', formula)):
        sheet = match.group("sheet")
        if sheet:
            sheets.add(sheet.strip("'").replace("''", "'"))
    return sheets


# ─────────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────────


def cmd_tabs(args):
    """List sheets with size, content mix and the sheets each one's formulas read from."""
    wb = open_workbook(args.workbook)
    sheets = []
    for ws in wb.worksheets:
        counts = {"input": 0, "formula": 0, "text": 0}
        reads_from = set()
        for row in ws.iter_rows():
            for cell in row:
                kind = cell_kind(cell.value)
                if kind == "empty":
                    continue
                counts[kind] += 1
                if kind == "formula":
                    reads_from |= referenced_sheets(cell.value)
        sheets.append(
            {
                "sheet": ws.title,
                "used_range": ws.dimensions,
                "state": ws.sheet_state,
                "cells": counts,
                "blank": sum(counts.values()) == 0,
                "reads_from": sorted(reads_from - {ws.title}),
            }
        )
    result = {"workbook": args.workbook, "sheets": sheets}
    warnings = fragile_parts(args.workbook)
    if warnings:
        result["warning"] = (
            "Workbook contains " + ", ".join(warnings) + "; these may not survive an edit via apply."
        )
    print(json.dumps(result, indent=2))


def cmd_read(args):
    """Dump a range: formulas, cached values, formatting and Daloopa ids per cell."""
    wb = open_workbook(args.workbook)
    wb_values = open_workbook(args.workbook, data_only=True)
    sheet, rng = parse_target(args.target, wb)
    ws, ws_values = wb[sheet], wb_values[sheet]

    cells = []
    for cell in iter_range(ws, rng):
        if cell.value is None and not args.all:
            continue
        cached = ws_values[cell.coordinate].value
        cells.append(describe_cell(cell, cached))
        if len(cells) >= args.max_cells:
            break

    min_col, _, max_col, _ = range_boundaries(rng or ws.dimensions)
    widths = {}
    for col in range(min_col, max_col + 1):
        letter = get_column_letter(col)
        dim = ws.column_dimensions.get(letter)
        if dim is not None and dim.width:
            widths[letter] = round(dim.width, 2)

    result = {
        "sheet": sheet,
        "range": rng or ws.dimensions,
        "freeze_panes": ws.freeze_panes,
        "column_widths": widths,
        "merged": [str(m) for m in ws.merged_cells.ranges],
        "cells": cells,
    }
    if len(cells) >= args.max_cells:
        result["truncated"] = f"Stopped at {args.max_cells} cells; read a smaller range."
    print(json.dumps(result, indent=2))


def cmd_refs(args):
    """List every cell/range the formulas in a range reference, grouped by sheet."""
    wb = open_workbook(args.workbook)
    sheet, rng = parse_target(args.target, wb)
    refs = {}
    external = set()
    for cell in iter_range(wb[sheet], rng):
        if cell_kind(cell.value) != "formula":
            continue
        for match in FORMULA_REF.finditer(STRING_LITERAL.sub('""', cell.value)):
            ref_sheet = match.group("sheet")
            if ref_sheet and ref_sheet.startswith("["):
                external.add(ref_sheet)
                continue
            ref_sheet = ref_sheet.strip("'").replace("''", "'") if ref_sheet else sheet
            ref = f"{match.group('c1')}{match.group('r1')}"
            if match.group("c2"):
                ref += f":{match.group('c2')}{match.group('r2')}"
            refs.setdefault(ref_sheet, set()).add(ref)
    result = {"sheet": sheet, "range": rng, "references": {s: sorted(r) for s, r in refs.items()}}
    if external:
        result["external_workbook_refs"] = sorted(external)
    print(json.dumps(result, indent=2))


def apply_format(cell, fmt):
    if "number_format" in fmt:
        cell.number_format = fmt["number_format"]
    font_keys = {"bold": "b", "italic": "i", "font_name": "name", "font_size": "sz", "font_color": "color"}
    if any(k in fmt for k in font_keys):
        # Copy so every attribute not named in fmt (scheme, family, underline...) is kept.
        font = copy(cell.font)
        for key, attr in font_keys.items():
            if key in fmt:
                setattr(font, attr, fmt[key])
        cell.font = font
    if "fill" in fmt:
        if fmt["fill"] in (None, "none"):
            cell.fill = PatternFill(fill_type=None)
        else:
            cell.fill = PatternFill(fill_type="solid", fgColor=fmt["fill"])


def default_output(path, label):
    stem, ext = os.path.splitext(os.path.basename(path))
    stamp = datetime.now().strftime("%Y%m%d")
    return os.path.join("reports", f"{stem}_{label}_{stamp}{ext}")


def cmd_apply(args):
    """Apply a JSON change list and save to a copy (never over the original)."""
    with open(args.changes) as f:
        changes = json.load(f)
    if not isinstance(changes, list):
        fail("Change list must be a JSON array.")

    source = os.path.abspath(args.workbook)
    if args.in_place:
        reports_dir = os.path.abspath("reports")
        if not source.startswith(reports_dir + os.sep):
            fail("--in-place is only allowed on a copy under reports/, never the user's original.")
        output = source
    else:
        output = os.path.abspath(args.output or default_output(args.workbook, args.label))
        if output == source:
            fail("Output path equals the input workbook; refusing to overwrite the original.")

    wb = open_workbook(args.workbook)
    log = []

    def sheet_of(target):
        name, rng = parse_target(target, wb)
        return wb[name], rng

    for i, change in enumerate(changes):
        try:
            if "add_sheet" in change:
                name = change["add_sheet"]
                if name in wb.sheetnames:
                    fail(f"Change {i}: sheet {name!r} already exists.")
                index = wb.sheetnames.index(change["after"]) + 1 if change.get("after") else None
                wb.create_sheet(name, index)
                log.append({"change": i, "added_sheet": name})
            elif "layout_from" in change:
                src, dst = wb[change["layout_from"]], wb[change["sheet"]]
                for letter, dim in src.column_dimensions.items():
                    dst.column_dimensions[letter].width = dim.width
                    dst.column_dimensions[letter].hidden = dim.hidden
                for idx, dim in src.row_dimensions.items():
                    dst.row_dimensions[idx].height = dim.height
                dst.freeze_panes = src.freeze_panes
                log.append({"change": i, "layout": f"{change['layout_from']} -> {change['sheet']}"})
            elif "copy_format_from" in change:
                src_ws, src_rng = sheet_of(change["copy_format_from"])
                dst_ws, dst_rng = sheet_of(change["range"])
                if not src_rng or not dst_rng:
                    fail(f"Change {i}: copy_format_from and range need explicit cell ranges.")
                src_cells = [list(r) for r in src_ws[src_rng]] if ":" in src_rng else [[src_ws[src_rng]]]
                dst_cells = [list(r) for r in dst_ws[dst_rng]] if ":" in dst_rng else [[dst_ws[dst_rng]]]
                if len(src_cells) != len(dst_cells) or len(src_cells[0]) != len(dst_cells[0]):
                    fail(f"Change {i}: copy_format_from and range differ in shape.")
                for src_row, dst_row in zip(src_cells, dst_cells):
                    for s, d in zip(src_row, dst_row):
                        d._style = copy(s._style)
                log.append({"change": i, "copied_format": f"{change['copy_format_from']} -> {change['range']}"})
            elif "format" in change:
                ws, rng = sheet_of(change.get("range") or change["cell"])
                for cell in iter_range(ws, rng):
                    apply_format(cell, change["format"])
                log.append({"change": i, "formatted": change.get("range") or change["cell"], "format": change["format"]})
            else:
                ws, ref = sheet_of(change["cell"])
                cell = ws[ref]
                old = json_value(cell.value)
                if change.get("clear"):
                    cell.value = None
                elif "formula" in change:
                    formula = change["formula"]
                    cell.value = formula if formula.startswith("=") else "=" + formula
                elif "value" in change:
                    cell.value = change["value"]
                else:
                    fail(f"Change {i}: nothing to apply ({change}).")
                if change.get("link"):
                    cell.hyperlink = change["link"]
                log.append({"change": i, "cell": change["cell"], "old": old, "new": json_value(cell.value)})
        except KeyError as e:
            fail(f"Change {i}: missing or unknown key {e} in {change}")

    # openpyxl drops every cached formula result; make Excel recalculate on open.
    if wb.calculation is None:
        wb.calculation = CalcProperties()
    wb.calculation.fullCalcOnLoad = True

    os.makedirs(os.path.dirname(output), exist_ok=True)
    wb.save(output)

    result = {"input": args.workbook, "output": output, "applied": len(log), "changes": log}
    warnings = fragile_parts(args.workbook)
    if warnings:
        result["warning"] = (
            "Source workbook contains " + ", ".join(warnings) + "; check they survived in the output."
        )
    print(json.dumps(result, indent=2))


def find_soffice():
    for name in ("soffice", "libreoffice"):
        path = shutil.which(name)
        if path:
            return path
    for path in (
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ):
        if os.path.isfile(path):
            return path
    return None


def cmd_recalc(args):
    """Recalculate a workbook with headless LibreOffice and report the values of --cells."""
    soffice = find_soffice()
    if not soffice:
        print(
            json.dumps(
                {
                    "recalculated": False,
                    "reason": "LibreOffice not found. Values recalculate when the file is opened in Excel.",
                },
                indent=2,
            )
        )
        return

    with tempfile.TemporaryDirectory() as tmp:
        profile = "file:///" + os.path.join(tmp, "profile").replace("\\", "/").lstrip("/")
        cmd = [
            soffice,
            f"-env:UserInstallation={profile}",
            "--headless",
            "--norestore",
            "--convert-to",
            "xlsx",
            "--outdir",
            tmp,
            os.path.abspath(args.workbook),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=args.timeout)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(json.dumps({"recalculated": False, "reason": f"LibreOffice failed: {e}"}, indent=2))
            return
        converted = os.path.join(tmp, os.path.splitext(os.path.basename(args.workbook))[0] + ".xlsx")
        wb = load_workbook(converted, data_only=True)
        values = {}
        for target in args.cells:
            sheet, rng = parse_target(target, wb)
            for cell in iter_range(wb[sheet], rng):
                values[f"{sheet}!{cell.coordinate}"] = json_value(cell.value)

    print(json.dumps({"recalculated": True, "values": values}, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Read and edit an existing Excel workbook (outputs JSON)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    tabs_parser = subparsers.add_parser("tabs", help="List sheets, their content mix and cross-sheet reads")
    tabs_parser.add_argument("workbook", help="Path to .xlsx/.xlsm")
    tabs_parser.set_defaults(func=cmd_tabs)

    read_parser = subparsers.add_parser("read", help="Formulas, cached values, formatting, Daloopa ids")
    read_parser.add_argument("workbook", help="Path to .xlsx/.xlsm")
    read_parser.add_argument("target", help='"Sheet!A1:M80", or "Sheet" for its used range')
    read_parser.add_argument("--all", action="store_true", help="Include empty cells")
    read_parser.add_argument("--max-cells", type=int, default=5000, help="Stop after N cells. Default: 5000")
    read_parser.set_defaults(func=cmd_read)

    refs_parser = subparsers.add_parser("refs", help="Cells the formulas in a range reference")
    refs_parser.add_argument("workbook", help="Path to .xlsx/.xlsm")
    refs_parser.add_argument("target", help='"Sheet!A1:M80", or "Sheet" for its used range')
    refs_parser.set_defaults(func=cmd_refs)

    apply_parser = subparsers.add_parser("apply", help="Apply a JSON change list to a copy")
    apply_parser.add_argument("workbook", help="Path to .xlsx/.xlsm")
    apply_parser.add_argument("changes", help="Path to change-list JSON")
    apply_parser.add_argument("--label", default="edited", help="Suffix for the copy's name. Default: edited")
    apply_parser.add_argument("--output", help="Output path. Default: reports/{name}_{label}_{YYYYMMDD}.xlsx")
    apply_parser.add_argument("--in-place", action="store_true", help="Edit a copy already under reports/")
    apply_parser.set_defaults(func=cmd_apply)

    recalc_parser = subparsers.add_parser("recalc", help="Recalculate via LibreOffice and read values")
    recalc_parser.add_argument("workbook", help="Path to .xlsx/.xlsm")
    recalc_parser.add_argument("--cells", nargs="+", required=True, help='Targets to read, e.g. "Model!F95:M95"')
    recalc_parser.add_argument("--timeout", type=int, default=180, help="Seconds. Default: 180")
    recalc_parser.set_defaults(func=cmd_recalc)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
