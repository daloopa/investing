#!/usr/bin/env python3
"""Render a Word document from a docxtpl template and a context JSON file.

Tables are built dynamically as Subdoc objects (not via template row loops).
Chart paths ending in '_chart' are converted to InlineImage objects.

Usage:
    python infra/docx_renderer.py \
        --template templates/research_note.docx \
        --context context.json \
        --output output.docx
"""

import argparse
import json
import os
import sys

from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches, Pt, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml


# ---------------------------------------------------------------------------
# Table configuration: context_key -> list of (header, data_key, width_inches)
# ---------------------------------------------------------------------------

TABLE_CONFIGS = {
    "key_metrics_table": [
        ("Metric", "metric", 3.0),
        ("Value", "value", 1.75),
        ("vs Prior", "vs_prior", 1.75),
    ],
    "financials_table": [
        ("Metric", "metric", 1.9),
        ("Q1", "q1", 0.92),
        ("Q2", "q2", 0.92),
        ("Q3", "q3", 0.92),
        ("Q4", "q4", 0.92),
        ("FY", "fy", 0.92),
    ],
    "guidance_table": [
        ("Period", "period", 0.9),
        ("Metric", "metric", 1.6),
        ("Guidance", "guidance", 1.1),
        ("Actual", "actual", 1.1),
        ("Surprise", "surprise", 1.8),
    ],
    "comps_table": [
        ("Company", "company", 1.5),
        ("EV/Revenue", "ev_revenue", 1.25),
        ("EV/EBITDA", "ev_ebitda", 1.25),
        ("P/E", "pe", 1.25),
        ("PEG", "peg", 1.25),
    ],
    "risks_table": [
        ("Risk", "risk", 4.0),
        ("Impact", "impact", 1.25),
        ("Probability", "probability", 1.25),
    ],
}

# ---------------------------------------------------------------------------
# Table styling helpers
# ---------------------------------------------------------------------------

FONT_NAME = "Calibri"
FONT_SIZE = Pt(10)
HEADER_GRAY = "D9D9D9"
LIGHT_GRAY = "F2F2F2"
WHITE = "FFFFFF"
BORDER_COLOR = "BFBFBF"


def _set_cell_shading(cell, color_hex):
    shading = parse_xml(
        f'<w:shd {nsdecls("w")} w:fill="{color_hex}" w:val="clear"/>'
    )
    cell._tc.get_or_add_tcPr().append(shading)


def _set_cell_borders(cell):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}></w:tcBorders>')
    for edge in ("top", "bottom", "left", "right"):
        elm = parse_xml(
            f'<w:{edge} {nsdecls("w")} '
            f'w:sz="4" w:val="single" w:color="{BORDER_COLOR}"/>'
        )
        borders.append(elm)
    tcPr.append(borders)


def _style_cell(cell, text, is_header=False, row_idx=0):
    """Write text into a cell and apply formatting."""
    cell.text = str(text) if text is not None else ""
    _set_cell_borders(cell)

    if is_header:
        _set_cell_shading(cell, HEADER_GRAY)
    else:
        shade = LIGHT_GRAY if row_idx % 2 == 0 else WHITE
        _set_cell_shading(cell, shade)

    for para in cell.paragraphs:
        para.paragraph_format.space_before = Pt(2)
        para.paragraph_format.space_after = Pt(2)
        for run in para.runs:
            run.font.name = FONT_NAME
            run.font.size = FONT_SIZE
            if is_header:
                run.font.bold = True


def _build_table_subdoc(doc, rows_data, config):
    """Build a Subdoc containing a formatted table.

    Args:
        doc: DocxTemplate instance
        rows_data: list of dicts (the table rows)
        config: list of (header_text, data_key, width_inches) tuples
    Returns:
        Subdoc object ready to be placed in context
    """
    subdoc = doc.new_subdoc()
    n_rows = len(rows_data) + 1  # +1 for header
    n_cols = len(config)

    table = subdoc.add_table(rows=n_rows, cols=n_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header row
    for j, (header, _, width) in enumerate(config):
        cell = table.rows[0].cells[j]
        cell.width = Inches(width)
        _style_cell(cell, header, is_header=True)

    # Data rows
    for i, row_data in enumerate(rows_data):
        for j, (_, key, width) in enumerate(config):
            cell = table.rows[i + 1].cells[j]
            cell.width = Inches(width)
            val = row_data.get(key, "")
            _style_cell(cell, val, row_idx=i)

    # Set column widths on all rows for consistency
    for row in table.rows:
        for j, (_, _, width) in enumerate(config):
            row.cells[j].width = Inches(width)

    return subdoc


# ---------------------------------------------------------------------------
# Context processors
# ---------------------------------------------------------------------------

def process_chart_images(doc, context):
    """Replace keys ending in '_chart' with InlineImage objects."""
    for key in list(context.keys()):
        if not key.endswith("_chart"):
            continue
        image_path = context[key]
        if isinstance(image_path, str) and os.path.isfile(image_path):
            context[key] = InlineImage(doc, image_path, width=Inches(6))
        else:
            context[key] = ""


def process_table_subdocs(doc, context):
    """Convert list-of-dicts table data into Subdoc objects with formatted tables."""
    for key, config in TABLE_CONFIGS.items():
        rows_data = context.get(key)
        if not isinstance(rows_data, list) or not rows_data:
            continue
        context[key] = _build_table_subdoc(doc, rows_data, config)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Render a Word document from a template and context JSON."
    )
    parser.add_argument("--template", required=True, help="Path to the .docx template.")
    parser.add_argument("--context", required=True, help="Path to the context JSON.")
    parser.add_argument("--output", required=True, help="Path for the output .docx.")
    return parser.parse_args()


def load_context(context_path):
    with open(context_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    args = parse_args()

    if not os.path.isfile(args.template):
        print(f"Error: template not found: {args.template}", file=sys.stderr)
        sys.exit(1)

    try:
        context = load_context(args.context)
    except FileNotFoundError:
        print(f"Error: context file not found: {args.context}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: malformed JSON in context file: {exc}", file=sys.stderr)
        sys.exit(1)

    doc = DocxTemplate(args.template)

    # Convert chart paths to InlineImage objects
    process_chart_images(doc, context)

    # Convert table data to Subdoc objects with formatted tables
    process_table_subdocs(doc, context)

    # Render and save
    doc.render(context)
    doc.save(args.output)

    print(args.output)


if __name__ == "__main__":
    main()
