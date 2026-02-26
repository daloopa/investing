# Data Access Reference

All skills that need financial data should follow this reference. Read `design-system.md` (in this same directory) for formatting, analytical density, and styling conventions.

---

## Section 1: Daloopa MCP Tools

Check your available tools. If you see Daloopa MCP tools (`discover_companies`, `discover_company_series`, `get_company_fundamentals`, `search_documents`), MCP is available.

| Operation | MCP Tool |
|---|---|
| Find company by ticker/name | `discover_companies(keywords=["TICKER"])` |
| Find available series/metrics | `discover_company_series(company_id, keywords, periods)` |
| Pull financial data | `get_company_fundamentals(company_id, periods, series_ids)` |
| Search SEC filings | `search_documents(keywords, company_ids, periods)` |

Results come back as structured data you can use directly.

If MCP is not available, check for API credentials (`recipes/daloopa_client.py` + `.env` with `DALOOPA_EMAIL` and `DALOOPA_API_KEY`). If so, use recipe scripts:

| Operation | Recipe Command |
|---|---|
| Find company by ticker/name | `python recipes/company_fundamentals.py TICKER` |
| Find series + pull data | `python recipes/company_fundamentals.py TICKER PERIOD1 PERIOD2 ...` |
| Search SEC filings | `python recipes/document_search.py "KEYWORDS" --companies TICKER1 TICKER2` |

If neither MCP nor API is available, tell the user to run `/setup`.

## Section 2: External Market Data

Skills that need market-side data should gather the following. Use whatever tools or data sources are available in your environment.

| Data Need | What to Get |
|---|---|
| **Stock quote** | Current price, market cap, shares outstanding, beta |
| **Trading multiples** | Trailing P/E, Forward P/E, EV/EBITDA, P/S, P/B, dividend yield |
| **Historical prices** | OHLCV data for trend analysis (1-5 years) |
| **Peer multiples** | Side-by-side trading multiples for 5-10 comparable companies |
| **Risk-free rate** | 10Y Treasury yield (for WACC/DCF calculations) |

If market data is unavailable, note the limitation and proceed with Daloopa fundamentals only. Use reasonable defaults where needed (beta=1.0, risk-free rate=4.5%).

## Section 3: Consensus Estimates (Optional)

When available, consensus analyst estimates add valuable context. Look for:

| Data Need | Use Case |
|---|---|
| **Consensus revenue / EPS** | Beat/miss analysis vs. Street expectations |
| **Forward estimates (NTM)** | Forward P/E, forward EV/EBITDA for comps |
| **Estimate revisions** | Trend in analyst expectations (up/down/stable) |
| **Price targets** | Consensus target and range for context |

If consensus data is not available, skip these sections and note "consensus data not available" rather than guessing.

## Section 4: Citation Requirements (MANDATORY)

**Every financial figure sourced from Daloopa MUST include a citation link.** This is non-negotiable.

Format: `[$X.XX million](https://daloopa.com/src/{fundamental_id})`

The `fundamental_id` (or `id`) is returned in every `get_company_fundamentals` response and in every API recipe result. You must:

1. **Capture the `fundamental_id` at data-pull time** — when you call `get_company_fundamentals` or parse recipe output, record the `id` for every value
2. **Carry the ID through to output** — when building tables, prose, or context JSON, attach the citation link to every Daloopa-sourced number
3. **Never drop citation IDs** — if a value came from Daloopa, it gets a link. No exceptions. Computed values (e.g., margins, growth rates) derived from Daloopa figures should cite the underlying inputs
4. **Document citations** — when quoting SEC filings from `search_documents`, link to: `[Document Name](https://marketplace.daloopa.com/document/{document_id})`

If you output a financial figure without a citation, it cannot be verified. Uncitable numbers are useless to an analyst.

---

## Section 5: Infrastructure Tools (Project Repo Only)

The following tools are available in the project repo environment. If these scripts are not available (e.g., in a plugin context), skip these steps — the skill's core analysis works without them.

### Market Data Scripts

| Operation | Command |
|---|---|
| Current quote (price, mkt cap, beta) | `python infra/market_data.py quote TICKER` |
| Trading multiples (P/E, EV/EBITDA, etc.) | `python infra/market_data.py multiples TICKER` |
| Historical OHLCV | `python infra/market_data.py history TICKER --period 2y` |
| Peer multiples comparison | `python infra/market_data.py peers TICKER1 TICKER2 ...` |
| Risk-free rate (10Y Treasury) | `python infra/market_data.py risk-free-rate` |

All commands output JSON to stdout.

### Charts

For chart generation: `python infra/chart_generator.py {chart_type} --data '{json}' --output path.png`

Available chart types: `time-series`, `waterfall`, `football-field`, `pie`, `scenario-bar`, `dcf-sensitivity`

### Projections

For forward financial projections: `python infra/projection_engine.py --context input.json --output projections.json`

### HTML Report Output (Building Block Skills)

Building block skills generate styled HTML directly using the template in `design-system.md`. No external scripts needed — the HTML file IS the deliverable. Save to: `reports/{TICKER}_{skill}.html`

### Word / Excel / Comp Sheet Rendering

- Word documents: `python infra/docx_renderer.py --template templates/research_note.docx --context context.json --output output.docx`
- Excel models: `python infra/excel_builder.py --context context.json --output output.xlsx`
- Comp sheet models: `python3 infra/comp_builder.py --context context.json --output output.xlsx`
- Context diffs: `python infra/report_differ.py --old old.json --new new.json --output diff.json`
