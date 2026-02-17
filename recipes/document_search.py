"""
Recipe 7: Document Search (Beta)
==================================
Search SEC filings (10-K, 10-Q, 8-K, transcripts) for specific keywords.
Find management commentary, risk factors, guidance language, etc.

Usage:
    # Search across all companies
    python recipes/07_document_search.py "revenue guidance"

    # Search within specific companies
    python recipes/07_document_search.py "cybersecurity" --companies AAPL MSFT

    # Filter by filing type
    python recipes/07_document_search.py "guidance" --companies AAPL --filing-types 10-K 10-Q
"""

import sys

from daloopa_client import get, post


def search_company(keyword: str) -> dict | None:
    """Look up a single company by ticker."""
    results = get("/companies", params={"keyword": keyword})
    return results[0] if results else None


def keyword_search(
    keywords: list[str],
    company_ids: list[int] | None = None,
    filing_types: list[str] | None = None,
    operator: str = "AND",
    size: int = 10,
) -> dict:
    """Search documents by keywords with optional filters."""
    body: dict = {
        "keywords": keywords,
        "options": {
            "size": size,
            "operator": operator,
        },
    }
    filters = {}
    if company_ids:
        filters["company_ids"] = company_ids
    if filing_types:
        filters["filing_types"] = filing_types
    if filters:
        body["filters"] = filters

    return post("/documents/keyword-search", json_body=body)


def main():
    if len(sys.argv) < 2:
        print("Usage: python recipes/07_document_search.py KEYWORDS [--companies T1 T2] [--filing-types 10-K 10-Q]")
        sys.exit(1)

    # Parse args
    keywords_str = sys.argv[1]
    keywords = keywords_str.split()

    company_tickers = []
    filing_types = []
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--companies":
            i += 1
            while i < len(sys.argv) and not sys.argv[i].startswith("--"):
                company_tickers.append(sys.argv[i])
                i += 1
        elif sys.argv[i] == "--filing-types":
            i += 1
            while i < len(sys.argv) and not sys.argv[i].startswith("--"):
                filing_types.append(sys.argv[i])
                i += 1
        else:
            i += 1

    # Resolve tickers to company IDs
    company_ids = []
    if company_tickers:
        print("Resolving companies...")
        for t in company_tickers:
            c = search_company(t)
            if c:
                company_ids.append(c["id"])
                print(f"  {t} -> {c['name']} (ID: {c['id']})")
            else:
                print(f"  Warning: '{t}' not found, skipping.")

    # Run the search
    print(f"\nSearching for: {keywords}")
    if company_ids:
        print(f"  Filtered to companies: {company_tickers}")
    if filing_types:
        print(f"  Filing types: {filing_types}")

    results = keyword_search(
        keywords=keywords,
        company_ids=company_ids or None,
        filing_types=filing_types or None,
    )

    total = results.get("total_hits", 0)
    docs = results.get("documents", [])
    print(f"\n  {total} total hit(s), showing {len(docs)}:\n")

    for doc in docs:
        doc_id = doc.get("document_id")
        filing = doc.get("filing_type", "N/A")
        date = doc.get("affinitized_date", "N/A")
        score = doc.get("score", 0)
        doc_url = f"https://marketplace.daloopa.com/document/{doc_id}"

        print(f"  [{filing}] {date} (score: {score:.3f})")
        print(f"    Link: {doc_url}")

        for match in doc.get("matches", [])[:3]:
            context = match.get("context", "").strip()
            # Truncate long contexts
            if len(context) > 200:
                context = context[:200] + "..."
            print(f"    > ...{context}")
        print()


if __name__ == "__main__":
    main()
