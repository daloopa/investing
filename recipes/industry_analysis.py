"""
Recipe 6: Industry Analysis
=============================
Compare companies within a sub-industry using standardized taxonomy metrics.
Lists available sub-industries, finds common metrics, and pulls comparable data.

Usage:
    # List all sub-industries
    python recipes/06_industry_analysis.py --list

    # Analyze a sub-industry by ID
    python recipes/06_industry_analysis.py 281 2024Q1 2024Q2 2024Q3 2024Q4

    # Search sub-industries by name
    python recipes/06_industry_analysis.py --search "cruise"
"""

import sys

from daloopa_client import get, paginate


def list_sub_industries() -> list[dict]:
    """List all available sub-industries."""
    return paginate("/taxonomy/sub-industries")


def search_sub_industries(keyword: str) -> list[dict]:
    """Search sub-industries by name."""
    all_subs = list_sub_industries()
    keyword_lower = keyword.lower()
    return [s for s in all_subs if keyword_lower in s.get("sub_industry_name", "").lower()
            or keyword_lower in s.get("industry_name", "").lower()]


def get_sub_industry_metrics(sub_industry_id: int) -> list[dict]:
    """Get standardized metrics available for a sub-industry."""
    return paginate("/taxonomy/metrics", params={"sub_industry_id": sub_industry_id})


def get_metric_detail(metric_id: int, sub_industry_id: int) -> dict:
    """Get company-series mappings for a metric within a sub-industry."""
    return get(f"/taxonomy/metrics/{metric_id}", params={"sub_industry_id": sub_industry_id})


def get_fundamentals(company_id: int, periods: list[str], series_ids: list[int]) -> list[dict]:
    """Fetch fundamental data."""
    param_tuples = [("company_id", company_id)]
    for p in periods:
        param_tuples.append(("periods", p))
    for sid in series_ids:
        param_tuples.append(("series_ids", sid))
    data = get("/companies/fundamentals", params=param_tuples)
    return data.get("results", []) if isinstance(data, dict) else data


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python recipes/06_industry_analysis.py --list")
        print("  python recipes/06_industry_analysis.py --search KEYWORD")
        print("  python recipes/06_industry_analysis.py SUB_INDUSTRY_ID PERIOD1 [PERIOD2 ...]")
        sys.exit(1)

    if sys.argv[1] == "--list":
        subs = list_sub_industries()
        print(f"{'ID':<6} {'Sub-Industry':<40} {'Sector':<30} {'Companies'}")
        print("-" * 100)
        for s in subs:
            tickers = ", ".join(c["ticker"] for c in s.get("companies", [])[:5])
            extra = f" +{len(s['companies']) - 5}" if len(s.get("companies", [])) > 5 else ""
            print(f"{s['sub_industry_id']:<6} {s.get('sub_industry_name', ''):<40} {s.get('sector_name', ''):<30} {tickers}{extra}")
        return

    if sys.argv[1] == "--search":
        keyword = sys.argv[2] if len(sys.argv) > 2 else ""
        subs = search_sub_industries(keyword)
        if not subs:
            print(f"No sub-industries matching '{keyword}'")
            return
        print(f"{'ID':<6} {'Sub-Industry':<40} {'Industry':<30} {'Companies'}")
        print("-" * 100)
        for s in subs:
            tickers = ", ".join(c["ticker"] for c in s.get("companies", [])[:5])
            print(f"{s['sub_industry_id']:<6} {s.get('sub_industry_name', ''):<40} {s.get('industry_name', ''):<30} {tickers}")
        return

    # Analyze a specific sub-industry
    sub_id = int(sys.argv[1])
    periods = sys.argv[2:] if len(sys.argv) > 2 else ["2024Q3", "2024Q4"]

    # Get available metrics for this sub-industry
    print(f"Loading metrics for sub-industry {sub_id}...")
    metrics = get_sub_industry_metrics(sub_id)
    if not metrics:
        print("No metrics found.")
        sys.exit(1)

    print(f"  Found {len(metrics)} standardized metric(s). Top 10:")
    for m in metrics[:10]:
        print(f"    [{m['metric_id']}] {m['metric_name']}")

    # Pick the first 3 metrics for comparison
    selected = metrics[:3]
    print(f"\nComparing top {len(selected)} metrics across companies for {', '.join(periods)}:\n")

    for metric in selected:
        detail = get_metric_detail(metric["metric_id"], sub_id)
        company_series = detail.get("metric_series", [])
        if not company_series:
            continue

        print(f"--- {metric['metric_name']} ---")
        header = f"  {'Company':<10}" + "".join(f"{p:>15}" for p in periods)
        print(header)

        for cs in company_series:
            results = get_fundamentals(cs["company_id"], periods, [cs["series_id"]])
            period_values = {r["calendar_period"]: r for r in results}
            row = f"  {cs['ticker']:<10}"
            for p in periods:
                if p in period_values:
                    val = period_values[p]["value_raw"]
                    row += f"{val:>15,.1f}"
                else:
                    row += f"{'N/A':>15}"
            print(row)
        print()


if __name__ == "__main__":
    main()
