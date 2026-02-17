# Data Access Reference

All skills that need financial data should follow this reference to determine HOW to access Daloopa data. There are two supported methods — detect which is available and use it.

## Detection Logic

1. **Check for MCP**: Look at your available tools. If you see Daloopa MCP tools (`discover_companies`, `discover_company_series`, `get_company_fundamentals`, `search_documents`), MCP is available.
2. **Check for API credentials**: Check if `recipes/daloopa_client.py` exists and `.env` contains `DALOOPA_EMAIL` and `DALOOPA_API_KEY`. If so, the API is available via recipe scripts.
3. **Both available?** Either works. Use whichever fits the task better — MCP returns structured data directly, API scripts are more flexible and composable.
4. **Neither available?** Tell the user to run `/setup` to configure their data access.

## Method 1: MCP Tools

Call the Daloopa MCP tools directly:

| Operation | MCP Tool |
|---|---|
| Find company by ticker/name | `discover_companies(keywords=["TICKER"])` |
| Find available series/metrics | `discover_company_series(company_id, keywords, periods)` |
| Pull financial data | `get_company_fundamentals(company_id, periods, series_ids)` |
| Search SEC filings | `search_documents(keywords, company_ids, periods)` |

Results come back as structured data you can use directly.

## Method 2: API via Recipe Scripts

Run the Python recipe scripts via Bash. Parse their stdout for the data you need.

| Operation | Recipe Command |
|---|---|
| Find company by ticker/name | `python recipes/company_fundamentals.py TICKER` (shows company search results) |
| Find series + pull data | `python recipes/company_fundamentals.py TICKER PERIOD1 PERIOD2 ...` (discovers series and fetches fundamentals) |
| Search SEC filings | `python recipes/document_search.py "KEYWORDS" --companies TICKER1 TICKER2` |
| Industry comparison | `python recipes/industry_analysis.py --search "KEYWORD"` or `python recipes/industry_analysis.py SUB_ID PERIOD1 PERIOD2` |

### API Notes
- Recipe scripts print results to stdout. Parse the output to extract values.
- The company_fundamentals recipe handles company lookup, series discovery, AND data retrieval in one run. To search for specific series, you may need to call the API functions from a Python snippet directly:
  ```
  python -c "
  import sys; sys.path.insert(0, 'recipes')
  from company_fundamentals import search_company, discover_series, get_fundamentals
  companies = search_company('AAPL')
  company_id = companies[0]['id']
  series = discover_series(company_id, ['revenue', 'net income'])
  series_ids = [s['id'] for s in series]
  results = get_fundamentals(company_id, ['2024Q1','2024Q2'], series_ids)
  for r in results:
      print(f\"{r['label']}|{r['calendar_period']}|{r['value_raw']}|{r['unit']}|{r['id']}\")
  "
  ```
- For document search, results include document_id, filing_type, and context snippets.
- All recipe scripts read credentials from `.env` automatically.
- Citation format is the same regardless of method: `[$X.XX million](https://daloopa.com/src/{fundamental_id})`

## Market Data (yfinance + FRED)

For market-side data (price, multiples, historical prices, peer comparisons, risk-free rate), use the infrastructure scripts:

| Operation | Command |
|---|---|
| Current quote (price, mkt cap, beta) | `python infra/market_data.py quote TICKER` |
| Trading multiples (P/E, EV/EBITDA, etc.) | `python infra/market_data.py multiples TICKER` |
| Historical OHLCV | `python infra/market_data.py history TICKER --period 2y` |
| Peer multiples comparison | `python infra/market_data.py peers TICKER1 TICKER2 ...` |
| Risk-free rate (10Y Treasury) | `python infra/market_data.py risk-free-rate` |

All commands output JSON to stdout. If the scripts aren't available (e.g., yfinance not installed), note this limitation and proceed with Daloopa data only.

## Charts

For chart generation, use: `python infra/chart_generator.py {chart_type} --data '{json}' --output path.png`

Available chart types: `revenue-trend`, `margin-trend`, `segment-pie`, `segment-stack`, `eps-trend`, `scenario-bar`, `dcf-sensitivity`, `price-history`

## Projections

For forward financial projections: `python infra/projection_engine.py --context input.json --output projections.json`
