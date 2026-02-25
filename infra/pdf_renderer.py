#!/usr/bin/env python3
"""
Markdown-to-PDF renderer with design system styling.

Converts a markdown report to styled HTML, then renders to PDF via headless Chrome.

Usage:
    python infra/pdf_renderer.py --input reports/AAPL_tearsheet.md --output reports/AAPL_tearsheet.pdf

Requirements:
    - Google Chrome or Chromium installed (uses --print-to-pdf)
    - markdown library (pip install markdown)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

try:
    import markdown
except ImportError:
    print(json.dumps({"error": "markdown library required. Install with: pip install markdown"}),
          file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Design system CSS
# ---------------------------------------------------------------------------

CSS = """
:root {
    --navy: #1B2A4A;
    --steel-blue: #4A6FA5;
    --gold: #C5A55A;
    --green: #27AE60;
    --red: #C0392B;
    --light-gray: #F8F9FA;
    --mid-gray: #E9ECEF;
    --dark-gray: #6C757D;
    --near-black: #343A40;
}

@page {
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
    @bottom-center {
        content: counter(page);
        font-size: 9px;
        color: var(--dark-gray);
    }
}

* {
    box-sizing: border-box;
}

body {
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Arial, sans-serif;
    font-size: 12px;
    line-height: 1.6;
    color: var(--near-black);
    max-width: 100%;
    margin: 0;
    padding: 0;
}

h1 {
    font-size: 24px;
    font-weight: bold;
    color: var(--navy);
    border-bottom: 3px solid var(--navy);
    padding-bottom: 8px;
    margin-top: 0;
    margin-bottom: 16px;
}

h2 {
    font-size: 18px;
    font-weight: bold;
    color: var(--navy);
    border-bottom: 1px solid var(--mid-gray);
    padding-bottom: 4px;
    margin-top: 24px;
    margin-bottom: 12px;
}

h3 {
    font-size: 14px;
    font-weight: bold;
    color: var(--steel-blue);
    margin-top: 16px;
    margin-bottom: 8px;
}

p {
    margin-bottom: 8px;
}

a {
    color: var(--steel-blue);
    text-decoration: none;
}

strong {
    font-weight: 600;
}

em {
    font-style: italic;
    color: var(--dark-gray);
}

blockquote {
    border-left: 4px solid var(--steel-blue);
    background: var(--light-gray);
    padding: 12px 16px;
    margin: 12px 0;
    font-size: 11px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 11px;
    font-variant-numeric: tabular-nums;
}

thead {
    background: var(--navy);
    color: white;
}

th {
    padding: 8px 10px;
    text-align: left;
    font-weight: 600;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

td {
    padding: 6px 10px;
    border-bottom: 1px solid var(--mid-gray);
}

/* Right-align numeric columns (2nd column onward) */
td:not(:first-child), th:not(:first-child) {
    text-align: right;
}

tr:nth-child(even) {
    background: var(--light-gray);
}

tr:hover {
    background: #EDF2F7;
}

code {
    background: var(--light-gray);
    padding: 2px 4px;
    border-radius: 3px;
    font-size: 10px;
}

pre {
    background: var(--light-gray);
    padding: 12px;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 10px;
}

ul, ol {
    padding-left: 20px;
    margin-bottom: 8px;
}

li {
    margin-bottom: 4px;
}

hr {
    border: none;
    border-top: 1px solid var(--mid-gray);
    margin: 20px 0;
}

img {
    max-width: 100%;
    height: auto;
    margin: 12px 0;
}

/* Footer */
.footer {
    text-align: center;
    font-size: 9px;
    color: var(--dark-gray);
    font-style: italic;
    margin-top: 24px;
    padding-top: 8px;
    border-top: 1px solid var(--mid-gray);
}
"""


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>{css}</style>
</head>
<body>
{content}
<div class="footer">Data sourced from Daloopa</div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Chrome detection
# ---------------------------------------------------------------------------

def _find_chrome():
    """Find Chrome/Chromium binary."""
    candidates = [
        # macOS
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        # Linux
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def render_pdf(input_path, output_path):
    """Convert markdown file to styled PDF."""
    # Read markdown
    with open(input_path, "r") as f:
        md_content = f.read()

    # Convert to HTML
    html_body = markdown.markdown(
        md_content,
        extensions=["tables", "fenced_code", "toc"],
    )

    # Embed chart images if they exist
    # Replace relative image paths with absolute file:// URLs
    report_dir = os.path.dirname(os.path.abspath(input_path))
    html_body = html_body.replace('src="reports/', f'src="file://{os.path.abspath("reports")}/')

    # Build full HTML
    html_content = HTML_TEMPLATE.format(css=CSS, content=html_body)

    # Write temporary HTML file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as tmp:
        tmp.write(html_content)
        tmp_path = tmp.name

    try:
        # Find Chrome
        chrome = _find_chrome()
        if not chrome:
            # Fallback: save HTML and notify
            html_output = output_path.replace(".pdf", ".html")
            shutil.move(tmp_path, html_output)
            print(json.dumps({
                "status": "partial",
                "html_path": html_output,
                "message": "Chrome not found. HTML saved instead of PDF."
            }))
            return

        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Render PDF via headless Chrome
        cmd = [
            chrome,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            f"--print-to-pdf={os.path.abspath(output_path)}",
            "--no-pdf-header-footer",
            f"file://{tmp_path}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            print(json.dumps({"error": f"Chrome PDF rendering failed: {result.stderr.strip()}"}),
                  file=sys.stderr)
            sys.exit(1)

        print(json.dumps({"status": "ok", "path": output_path}))

    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def main():
    parser = argparse.ArgumentParser(description="Convert markdown reports to styled PDF.")
    parser.add_argument("--input", "-i", required=True, help="Input markdown file path")
    parser.add_argument("--output", "-o", required=True, help="Output PDF file path")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(json.dumps({"error": f"Input file not found: {args.input}"}), file=sys.stderr)
        sys.exit(1)

    render_pdf(args.input, args.output)


if __name__ == "__main__":
    main()
