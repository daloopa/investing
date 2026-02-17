"""
Recipe 1: Company-First Workflow
=================================
Look up a company by ticker, find available financial series, and pull
fundamental data for specific periods.

Usage:
    python recipes/01_company_fundamentals.py AAPL 2024Q1 2024Q2 2024Q3 2024Q4
"""

import sys

from daloopa_client import get


def search_company(keyword: str) -> list[dict]:
    """Search for a company by ticker or name."""
    return get("/companies", params={"keyword": keyword})


def discover_series(company_id: int, keywords: list[str]) -> list[dict]:
    """Find available financial series for a company, filtered by keywords."""
    params = {"company_id": company_id}
    for kw in keywords:
        params.setdefault("keywords", [])
    # requests handles list params via list of tuples
    param_tuples = [("company_id", company_id)]
    for kw in keywords:
        param_tuples.append(("keywords", kw))
    resp = get("/companies/series", params=param_tuples)
    return resp


def get_fundamentals(company_id: int, periods: list[str], series_ids: list[int]) -> list[dict]:
    """Fetch fundamental data for specific series and periods."""
    param_tuples = [("company_id", company_id)]
    for p in periods:
        param_tuples.append(("periods", p))
    for sid in series_ids:
        param_tuples.append(("series_ids", sid))
    data = get("/companies/fundamentals", params=param_tuples)
    return data.get("results", []) if isinstance(data, dict) else data


def main():
    if len(sys.argv) < 3:
        print("Usage: python recipes/01_company_fundamentals.py TICKER PERIOD1 [PERIOD2 ...]")
        print("Example: python recipes/01_company_fundamentals.py AAPL 2024Q1 2024Q2")
        sys.exit(1)

    ticker = sys.argv[1]
    periods = sys.argv[2:]

    # Step 1: Find the company
    print(f"Searching for '{ticker}'...")
    companies = search_company(ticker)
    if not companies:
        print(f"No company found for '{ticker}'")
        sys.exit(1)
    company = companies[0]
    company_id = company["id"]
    print(f"  Found: {company['name']} (ID: {company_id}, latest: {company.get('latest_quarter')})")

    # Step 2: Discover key financial series
    print("\nDiscovering financial series...")
    search_terms = ["revenue", "net income", "EPS", "gross profit", "operating income"]
    series = discover_series(company_id, search_terms)
    if not series:
        print("  No series found. Try broader keywords.")
        sys.exit(1)
    print(f"  Found {len(series)} series:")
    for s in series[:15]:
        print(f"    [{s['id']}] {s['full_series_name']}")
    if len(series) > 15:
        print(f"    ... and {len(series) - 15} more")

    # Step 3: Pull fundamentals for all discovered series
    series_ids = [s["id"] for s in series[:15]]  # limit to top 15 to keep output readable
    print(f"\nFetching fundamentals for {len(periods)} period(s)...")
    results = get_fundamentals(company_id, periods, series_ids)
    if not results:
        print("  No data returned.")
        sys.exit(0)

    # Print results as a table
    print(f"\n{'Series':<50} {'Period':<10} {'Value':>15} {'Unit':<10} {'Source'}")
    print("-" * 110)
    for r in results:
        source = f"https://daloopa.com/src/{r['id']}"
        print(f"{r['label']:<50} {r['calendar_period']:<10} {r['value_raw']:>15,.2f} {r['unit']:<10} {source}")


if __name__ == "__main__":
    main()
