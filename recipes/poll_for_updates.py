"""
Recipe 3: Poll for Updates
===========================
Monitor companies for new earnings data and fetch updates when detected.
Useful for building automated pipelines that react to new filings.

Usage:
    # One-shot check
    python recipes/03_poll_for_updates.py AAPL MSFT GOOG

    # Continuous polling (every 15 min)
    python recipes/03_poll_for_updates.py --poll AAPL MSFT GOOG
"""

import json
import sys
import time
from pathlib import Path

from daloopa_client import get, post

CACHE_FILE = Path(__file__).parent / ".poll_cache.json"
POLL_INTERVAL = 900  # 15 minutes


def check_status(company_ids: list[int]) -> list[dict]:
    """Check the latest update timestamps for a list of companies."""
    return post("/companies/status", json_body={"companies": company_ids})


def search_company(keyword: str) -> dict | None:
    """Look up a single company by ticker."""
    results = get("/companies", params={"keyword": keyword})
    return results[0] if results else None


def load_cache() -> dict:
    """Load last-seen timestamps from disk."""
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}


def save_cache(cache: dict):
    """Persist last-seen timestamps to disk."""
    CACHE_FILE.write_text(json.dumps(cache, indent=2))


def get_fundamentals_since(company_id: int, latest_period: str) -> list[dict]:
    """Fetch the latest period's data for a company."""
    param_tuples = [("company_id", company_id), ("periods", latest_period)]
    data = get("/companies/fundamentals", params=param_tuples)
    return data.get("results", []) if isinstance(data, dict) else data


def check_once(tickers: list[str]):
    """Run a single poll cycle."""
    cache = load_cache()

    # Resolve tickers to company IDs
    companies = {}
    for t in tickers:
        c = search_company(t)
        if c:
            companies[t] = c
        else:
            print(f"  Warning: '{t}' not found, skipping.")

    if not companies:
        return

    company_ids = [c["id"] for c in companies.values()]
    statuses = check_status(company_ids)

    updates_found = False
    for status in statuses:
        cid = status["company_id"]
        ticker = next((t for t, c in companies.items() if c["id"] == cid), f"ID:{cid}")
        last_ts = status.get("latest_datapoint_created_at", "")
        cached_ts = cache.get(str(cid), "")

        if last_ts != cached_ts:
            updates_found = True
            print(f"  NEW DATA for {ticker}: period={status['latest_period']}, updated={last_ts}")

            # Fetch the new data
            results = get_fundamentals_since(cid, status["latest_period"])
            print(f"    Retrieved {len(results)} datapoints for {status['latest_period']}")
            for r in results[:5]:
                print(f"      {r['label']}: {r['value_raw']:,.2f} {r['unit']}")
            if len(results) > 5:
                print(f"      ... and {len(results) - 5} more")

            cache[str(cid)] = last_ts
        else:
            print(f"  {ticker}: no changes since last check")

    if not updates_found:
        print("  No new data detected.")

    save_cache(cache)


def main():
    continuous = "--poll" in sys.argv
    tickers = [a for a in sys.argv[1:] if a != "--poll"]

    if not tickers:
        print("Usage: python recipes/03_poll_for_updates.py [--poll] TICKER1 [TICKER2 ...]")
        print("  --poll: continuously check every 15 minutes")
        sys.exit(1)

    if continuous:
        print(f"Polling {', '.join(tickers)} every {POLL_INTERVAL // 60} minutes (Ctrl+C to stop)...")
        while True:
            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking...")
            check_once(tickers)
            time.sleep(POLL_INTERVAL)
    else:
        print(f"Checking {', '.join(tickers)} for updates...")
        check_once(tickers)


if __name__ == "__main__":
    main()
