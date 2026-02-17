"""
Recipe 8: Check Series Continuations
======================================
Series IDs can change over time when Daloopa restructures a company's model.
This recipe checks for deprecated series and their replacements so you can
keep your cached series IDs up to date.

Usage:
    python recipes/08_series_continuation.py AAPL
    python recipes/08_series_continuation.py --by-id 2
"""

import sys

from daloopa_client import get


def search_company(keyword: str) -> dict | None:
    """Look up a single company by ticker."""
    results = get("/companies", params={"keyword": keyword})
    return results[0] if results else None


def get_continuations(company_id: int) -> list[dict]:
    """Get all series continuations (old -> new mappings) for a company."""
    return get("/series-continuation", params={"company_id": company_id})


def main():
    if len(sys.argv) < 2:
        print("Usage: python recipes/08_series_continuation.py TICKER")
        print("       python recipes/08_series_continuation.py --by-id COMPANY_ID")
        sys.exit(1)

    if sys.argv[1] == "--by-id":
        company_id = int(sys.argv[2])
        ticker = f"company_{company_id}"
    else:
        ticker = sys.argv[1].upper()
        company = search_company(ticker)
        if not company:
            print(f"Company '{ticker}' not found.")
            sys.exit(1)
        company_id = company["id"]
        print(f"Checking series continuations for {company['name']} (ID: {company_id})...")

    continuations = get_continuations(company_id)

    if not continuations:
        print("  No series continuations found. All series IDs are current.")
        return

    print(f"\n  Found {len(continuations)} continuation(s):\n")
    for c in continuations:
        cont_type = c.get("type", "UNKNOWN")
        created = c.get("created_at", "")[:10]
        print(f"  [{cont_type}] {created}")

        print("    OLD series (deprecated):")
        for s in c.get("old_series", []):
            print(f"      [{s['id']}] {s['full_series_name']}")

        print("    NEW series (use these instead):")
        for s in c.get("new_series", []):
            print(f"      [{s['id']}] {s['full_series_name']}")
        print()

    # Summary: build a quick old->new lookup
    print("  Quick lookup (old_id -> new_id):")
    for c in continuations:
        old_ids = [s["id"] for s in c.get("old_series", [])]
        new_ids = [s["id"] for s in c.get("new_series", [])]
        for oid in old_ids:
            print(f"    {oid} -> {new_ids}")


if __name__ == "__main__":
    main()
