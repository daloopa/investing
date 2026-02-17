"""
Recipe 2: Taxonomy-First Workflow
==================================
Compare a standardized metric (e.g., "Total Revenue") across multiple
companies using Daloopa's taxonomy system.

Usage:
    python recipes/02_taxonomy_comparison.py "Total Revenue" 2024Q1 2024Q2 2024Q3 2024Q4
"""

import sys

from daloopa_client import get, paginate


def search_taxonomy_metrics(keyword: str) -> list[dict]:
    """Search for standardized taxonomy metrics by keyword."""
    return paginate("/taxonomy/metrics", params={"keywords": keyword})


def get_metric_series(metric_id: int, sub_industry_id: int | None = None) -> dict:
    """Get company-series mappings for a taxonomy metric."""
    params = {}
    if sub_industry_id:
        params["sub_industry_id"] = sub_industry_id
    return get(f"/taxonomy/metrics/{metric_id}", params=params)


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
        print('Usage: python recipes/02_taxonomy_comparison.py "METRIC_NAME" PERIOD1 [PERIOD2 ...]')
        print('Example: python recipes/02_taxonomy_comparison.py "Total Revenue" 2024Q1 2024Q2')
        sys.exit(1)

    metric_keyword = sys.argv[1]
    periods = sys.argv[2:]

    # Step 1: Find the taxonomy metric
    print(f"Searching for metric '{metric_keyword}'...")
    metrics = search_taxonomy_metrics(metric_keyword)
    if not metrics:
        print("No matching metrics found.")
        sys.exit(1)

    print(f"  Found {len(metrics)} metric(s):")
    for m in metrics[:5]:
        print(f"    [{m['metric_id']}] {m['metric_name']}")

    # Use the first match
    metric = metrics[0]
    metric_id = metric["metric_id"]
    print(f"\n  Using: {metric['metric_name']} (ID: {metric_id})")

    # Step 2: Get company-series mappings for this metric
    print("\nFinding companies with this metric...")
    metric_detail = get_metric_series(metric_id)
    company_series = metric_detail.get("metric_series", [])
    if not company_series:
        print("  No companies found for this metric.")
        sys.exit(1)

    print(f"  Found {len(company_series)} company(ies):")
    for cs in company_series[:10]:
        print(f"    {cs['ticker']:<8} series={cs['series_id']}  ({cs['full_series_name']})")
    if len(company_series) > 10:
        print(f"    ... and {len(company_series) - 10} more")

    # Step 3: Fetch fundamentals for each company
    print(f"\nFetching data for {len(periods)} period(s)...\n")

    # Header
    header = f"{'Company':<10}" + "".join(f"{p:>15}" for p in periods)
    print(header)
    print("-" * len(header))

    for cs in company_series[:10]:
        results = get_fundamentals(cs["company_id"], periods, [cs["series_id"]])
        # Build a period -> value map
        period_values = {r["calendar_period"]: r for r in results}
        row = f"{cs['ticker']:<10}"
        for p in periods:
            if p in period_values:
                val = period_values[p]["value_raw"]
                unit = period_values[p]["unit"]
                row += f"{val:>14,.1f}{unit[0] if unit else ''}"
            else:
                row += f"{'N/A':>15}"
        print(row)


if __name__ == "__main__":
    main()
