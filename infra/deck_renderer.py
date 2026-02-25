#!/usr/bin/env python3
"""
HTML deck to PDF renderer.

Takes a self-contained HTML presentation file and renders it to PDF
via headless Chrome with landscape 16:9 orientation.

Usage:
    python infra/deck_renderer.py --input reports/AAPL_deck.html --output reports/AAPL_deck.pdf
"""

import argparse
import json
import os
import shutil
import subprocess
import sys


def _find_chrome():
    """Find Chrome/Chromium binary."""
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
    ]
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
        found = shutil.which(candidate)
        if found:
            return found
    return None


def render_deck(input_path, output_path):
    """Render HTML deck to PDF via headless Chrome."""
    if not os.path.exists(input_path):
        print(json.dumps({"error": f"Input file not found: {input_path}"}), file=sys.stderr)
        sys.exit(1)

    # Validate it contains embedded CSS (self-contained check)
    with open(input_path, "r") as f:
        content = f.read()
    if "<style" not in content:
        print(json.dumps({"warning": "HTML file does not appear to have embedded CSS. "
                          "Output may lack styling."}))

    chrome = _find_chrome()
    if not chrome:
        print(json.dumps({
            "status": "error",
            "message": "Chrome/Chromium not found. Open the HTML file in a browser and print to PDF manually.",
            "html_path": input_path
        }), file=sys.stderr)
        sys.exit(1)

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    abs_input = os.path.abspath(input_path)
    abs_output = os.path.abspath(output_path)

    cmd = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={abs_output}",
        "--no-pdf-header-footer",
        f"file://{abs_input}",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    if result.returncode != 0:
        print(json.dumps({"error": f"Chrome PDF rendering failed: {result.stderr.strip()}"}),
              file=sys.stderr)
        sys.exit(1)

    print(json.dumps({"status": "ok", "path": output_path}))


def main():
    parser = argparse.ArgumentParser(description="Render HTML deck to PDF.")
    parser.add_argument("--input", "-i", required=True, help="Input HTML file path")
    parser.add_argument("--output", "-o", required=True, help="Output PDF file path")
    args = parser.parse_args()

    render_deck(args.input, args.output)


if __name__ == "__main__":
    main()
