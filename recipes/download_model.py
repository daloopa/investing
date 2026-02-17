"""
Recipe 5: Download Excel Model
================================
Download the full Excel model for a company for offline analysis.
Models include historical data, KPIs, guidance, and pre-built charts.

Usage:
    python recipes/05_download_model.py AAPL
    python recipes/05_download_model.py --by-id 2
"""

import sys
from pathlib import Path

import requests

from daloopa_client import get

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "reports"


def search_company(keyword: str) -> dict | None:
    """Look up a single company by ticker."""
    results = get("/companies", params={"keyword": keyword})
    return results[0] if results else None


def get_download_url(company_id: int, model_type: str = "company") -> str:
    """Get a pre-signed download URL for the Excel model."""
    data = get("/download-company-model", params={
        "company_id": company_id,
        "model_type": model_type,
    })
    return data["download_url"]


def download_file(url: str, dest: str) -> str:
    """Download a file from a pre-signed URL."""
    resp = requests.get(url, timeout=120, stream=True)
    resp.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return dest


def main():
    if len(sys.argv) < 2:
        print("Usage: python recipes/05_download_model.py TICKER")
        print("       python recipes/05_download_model.py --by-id COMPANY_ID")
        sys.exit(1)

    if sys.argv[1] == "--by-id":
        company_id = int(sys.argv[2])
        ticker = f"company_{company_id}"
    else:
        ticker = sys.argv[1].upper()
        print(f"Looking up {ticker}...")
        company = search_company(ticker)
        if not company:
            print(f"Company '{ticker}' not found.")
            sys.exit(1)
        company_id = company["id"]
        print(f"  Found: {company['name']} (ID: {company_id})")

    # Get pre-signed URL
    print("Requesting download URL...")
    url = get_download_url(company_id)
    print("  URL obtained (expires in ~1 hour)")

    # Download
    OUTPUT_DIR.mkdir(exist_ok=True)
    dest = str(OUTPUT_DIR / f"{ticker}_model.xlsx")
    print(f"Downloading to {dest}...")
    download_file(url, dest)

    size_mb = Path(dest).stat().st_size / (1024 * 1024)
    print(f"  Done! ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
