#!/usr/bin/env python3
"""Compare two context JSON files and produce a structured diff.

Usage:
    python infra/report_differ.py --old old_context.json --new new_context.json --output diff.json
    python infra/report_differ.py --old old_context.json --new new_context.json  # prints to stdout
"""

import argparse
import json
import os
import sys
from datetime import date


# ---------------------------------------------------------------------------
# Diff logic
# ---------------------------------------------------------------------------

def _flatten(obj, prefix=""):
    """Recursively flatten a nested dict into dot-notation key/value pairs."""
    items = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            items.update(_flatten(v, path))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            path = f"{prefix}[{i}]"
            items.update(_flatten(v, path))
    else:
        items[prefix] = obj
    return items


def _top_level_section(path):
    """Extract the top-level section name from a dotted path."""
    return path.split(".")[0].split("[")[0]


def _compare_lists(old_list, new_list, path):
    """Compare two lists and return change entries for added/removed/changed items."""
    changes = []
    old_set = set()
    new_set = set()

    # For lists of primitives, compare by value
    # For lists of dicts/complex objects, compare by index
    all_primitives = all(
        not isinstance(v, (dict, list)) for v in old_list + new_list
    )

    if all_primitives:
        old_set = set(old_list)
        new_set = set(new_list)

        for item in sorted(new_set - old_set, key=str):
            changes.append({
                "path": path,
                "old_value": None,
                "new_value": item,
                "status": "added",
            })
        for item in sorted(old_set - new_set, key=str):
            changes.append({
                "path": path,
                "old_value": item,
                "new_value": None,
                "status": "removed",
            })
    else:
        # Index-based comparison for complex lists
        max_len = max(len(old_list), len(new_list))
        for i in range(max_len):
            item_path = f"{path}[{i}]"
            if i >= len(old_list):
                changes.append({
                    "path": item_path,
                    "old_value": None,
                    "new_value": new_list[i],
                    "status": "added",
                })
            elif i >= len(new_list):
                changes.append({
                    "path": item_path,
                    "old_value": old_list[i],
                    "new_value": None,
                    "status": "removed",
                })
            elif old_list[i] != new_list[i]:
                # Recurse into dicts, otherwise mark changed
                if isinstance(old_list[i], dict) and isinstance(new_list[i], dict):
                    changes.extend(_compare_dicts(old_list[i], new_list[i], item_path))
                else:
                    entry = {
                        "path": item_path,
                        "old_value": old_list[i],
                        "new_value": new_list[i],
                        "status": "changed",
                    }
                    changes.append(entry)

    return changes


def _compare_dicts(old_dict, new_dict, prefix=""):
    """Recursively compare two dicts, returning a list of change entries."""
    changes = []
    all_keys = set(old_dict.keys()) | set(new_dict.keys())

    for key in sorted(all_keys):
        path = f"{prefix}.{key}" if prefix else key
        old_val = old_dict.get(key)
        new_val = new_dict.get(key)

        if key not in old_dict:
            # New field
            flat_new = _flatten(new_val, path)
            for flat_path, flat_val in sorted(flat_new.items()):
                changes.append({
                    "path": flat_path,
                    "old_value": None,
                    "new_value": flat_val,
                    "status": "new",
                })
        elif key not in new_dict:
            # Removed field
            flat_old = _flatten(old_val, path)
            for flat_path, flat_val in sorted(flat_old.items()):
                changes.append({
                    "path": flat_path,
                    "old_value": flat_val,
                    "new_value": None,
                    "status": "removed",
                })
        elif isinstance(old_val, dict) and isinstance(new_val, dict):
            changes.extend(_compare_dicts(old_val, new_val, path))
        elif isinstance(old_val, list) and isinstance(new_val, list):
            changes.extend(_compare_lists(old_val, new_val, path))
        elif old_val != new_val:
            entry = {
                "path": path,
                "old_value": old_val,
                "new_value": new_val,
                "status": "changed",
            }
            # Compute numeric delta and pct_change
            if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
                delta = new_val - old_val
                entry["delta"] = delta
                if old_val != 0:
                    entry["pct_change"] = round(delta / abs(old_val), 6)
                else:
                    entry["pct_change"] = None
            changes.append(entry)

    return changes


def _compute_sections_status(changes, old_dict, new_dict):
    """Determine changed/unchanged status for each top-level section."""
    all_sections = sorted(set(old_dict.keys()) | set(new_dict.keys()))
    changed_sections = set()
    for change in changes:
        changed_sections.add(_top_level_section(change["path"]))

    status = {}
    for section in all_sections:
        status[section] = "changed" if section in changed_sections else "unchanged"
    return status


def diff_json(old_data, new_data):
    """Compare two JSON objects and return a structured diff report."""
    changes = _compare_dicts(old_data, new_data)

    # Count total fields in both files
    old_flat = _flatten(old_data)
    new_flat = _flatten(new_data)
    total_fields = len(set(old_flat.keys()) | set(new_flat.keys()))

    changed_count = sum(1 for c in changes if c["status"] == "changed")
    new_count = sum(1 for c in changes if c["status"] == "new")
    removed_count = sum(1 for c in changes if c["status"] == "removed")

    sections_status = _compute_sections_status(changes, old_data, new_data)

    return {
        "generated_at": date.today().isoformat(),
        "summary": {
            "total_fields": total_fields,
            "changed_fields": changed_count,
            "new_fields": new_count,
            "removed_fields": removed_count,
        },
        "changes": changes,
        "sections_status": sections_status,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Compare two context JSON files and produce a structured diff.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--old",
        required=True,
        help="Path to the old (baseline) JSON file.",
    )
    parser.add_argument(
        "--new",
        required=True,
        help="Path to the new (updated) JSON file.",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Path for the output diff JSON. If omitted, prints to stdout.",
    )
    args = parser.parse_args()

    # Load old JSON
    try:
        with open(args.old, "r", encoding="utf-8") as f:
            old_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {args.old}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: malformed JSON in {args.old}: {exc}", file=sys.stderr)
        sys.exit(1)

    # Load new JSON
    try:
        with open(args.new, "r", encoding="utf-8") as f:
            new_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {args.new}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: malformed JSON in {args.new}: {exc}", file=sys.stderr)
        sys.exit(1)

    # Compute diff
    result = diff_json(old_data, new_data)

    # Output
    output_json = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        parent = os.path.dirname(args.output)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
            f.write("\n")
        print(args.output)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
