"""
Recipe 4: Export to CSV
========================
Bulk export all datapoints for a company as a CSV file.
Supports historical data, real-time (incremental) data, or both.

Usage:
    # Historical data only (default)
    python recipes/04_export_csv.py AAPL

    # Real-time incremental data only (latest earnings, not yet published)
    python recipes/04_export_csv.py AAPL --real-time

    # Both historical + real-time
    python recipes/04_export_csv.py AAPL --real-time --include-historical
"""

import sys
from pathlib import Path

from daloopa_client import download

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "reports"


def export_csv(ticker: str, real_time: bool = False, include_historical: bool = False) -> str:
    """Export company fundamentals to CSV."""
    params = {}
    if real_time:
        params["real_time"] = "true"
        params["show_historical_data"] = "true" if include_historical else "false"

    OUTPUT_DIR.mkdir(exist_ok=True)
    suffix = "_realtime" if real_time and not include_historical else "_full" if real_time else ""
    dest = str(OUTPUT_DIR / f"{ticker.upper()}{suffix}_export.csv")

    print(f"Exporting {ticker.upper()} to {dest}...")
    download(f"/export/{ticker.upper()}", dest, params=params)
    return dest


def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith("--"):
        print("Usage: python recipes/04_export_csv.py TICKER [--real-time] [--include-historical]")
        sys.exit(1)

    ticker = sys.argv[1]
    real_time = "--real-time" in sys.argv
    include_historical = "--include-historical" in sys.argv

    dest = export_csv(ticker, real_time=real_time, include_historical=include_historical)

    # Show a preview
    lines = Path(dest).read_text().splitlines()
    print(f"\nExported {len(lines) - 1} rows to {dest}")
    print("\nPreview (first 5 rows):")
    for line in lines[:6]:
        print(f"  {line[:120]}")


if __name__ == "__main__":
    main()
