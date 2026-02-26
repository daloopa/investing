# Daloopa Financial Analysis Toolkit

This is a financial analysis toolkit powered by Daloopa's institutional-grade financial data, designed for hedge fund analysts doing fundamental equity research.

## Analyst Context
- Perspective: long/short equity, fundamental analysis
- Data source: Daloopa MCP server (SEC filings, earnings, financial statements)
- Market data: yfinance (price, multiples, historical), FRED (risk-free rate)
- Consensus estimates: optional (when available, adds beat/miss and forward context)
- All analysis should be thorough, data-driven, and cite sources
- Follow `design-system.md` for number formatting, analytical density, and styling

## MCP Tool Workflow
Always follow this pattern when working with Daloopa data:

1. **`discover_companies`** — Look up company by ticker or name to get `company_id`
2. **`discover_company_series`** — Find available financial metrics and KPIs for the company
3. **`get_company_fundamentals`** — Pull actual data for specific series and periods
4. **`search_documents`** — Search SEC filings (10-K, 10-Q, 8-K) for qualitative information

## Market Data
Market data is sourced via `infra/market_data.py` using yfinance:
- `python infra/market_data.py quote TICKER` — price, market cap, shares, beta
- `python infra/market_data.py multiples TICKER` — P/E, EV/EBITDA, P/S, P/B
- `python infra/market_data.py history TICKER --period 2y` — historical OHLCV
- `python infra/market_data.py peers TICKER1 TICKER2 ...` — side-by-side multiples
- `python infra/market_data.py risk-free-rate` — 10Y Treasury from FRED

## Design System
All skills reference `.claude/skills/design-system.md` for consistent formatting:
- Number formatting ($X.Xbn, X.X%, X.Xx multiples, +/-Xbps)
- Three-layer analytical density (data point + context + implication)
- Table conventions (columns = periods, rows = metrics, growth sub-rows)
- Commentary blocks after every major table
- Color palette (navy #1B2A4A, steel blue #4A6FA5, gold #C5A55A)

## Citation Format
Every financial figure must link back to its Daloopa source:
```
[$X.XX million](https://daloopa.com/src/{fundamental_id})
```
Example: Revenue grew to [$75.2 billion](https://daloopa.com/src/113433925)

## Table Format
Always use standard financial analysis layout:
- **Columns** = time periods (Q1 2024, Q2 2024, etc.)
- **Rows** = financial metrics (Revenue, Net Income, etc.)

## Guidance vs Actuals Rules
- Quarterly guidance from Q(N) applies to Q(N+1) results
- Annual guidance from Q1/Q2/Q3 applies to current fiscal year
- Annual guidance from Q4 applies to NEXT fiscal year
- Never compare same-quarter guidance to same-quarter actual

## Key Operating KPIs
When analyzing any company, always discover and include company-specific KPIs beyond standard financials (e.g., subscribers, ARR, GMV, same-store sales, DAU/MAU, ARPU, units, bookings, backlog).

## Reports
All generated analysis is saved to the `reports/` directory. Reports are gitignored so each analyst generates their own. Word documents, Excel models, PDFs, and decks are also saved there.

## Available Commands

### Building Block Skills (HTML reports)
- `/setup` — Walk through initial setup and authentication
- `/earnings TICKER` — Full earnings analysis with guidance tracking
- `/tearsheet TICKER` — Quick one-page company overview
- `/industry TICKER1 TICKER2 ...` — Cross-company industry comparison
- `/bull-bear TICKER` — Bull/bear/base scenario framework
- `/guidance-tracker TICKER` — Track management guidance accuracy
- `/inflection TICKER` — Auto-detect biggest metric accelerations/decelerations
- `/capital-allocation TICKER` — Deep dive into buybacks, dividends, shareholder yield
- `/dcf TICKER` — Discounted cash flow valuation with sensitivity analysis
- `/comps TICKER` — Trading comparables with peer multiples and implied valuation
- `/comp-sheet TICKER` — Multi-company industry comp sheet Excel model with deep KPIs

### Investment Deliverables (.docx, .xlsx, .pdf)
- `/research-note TICKER` — Generate professional Word research note
- `/build-model TICKER` — Build multi-tab Excel financial model
- `/initiate TICKER` — Initiate coverage: generates both research note + Excel model
- `/update TICKER` — Refresh existing coverage with latest quarter's data
- `/ib-deck TICKER` — Generate institutional-grade pitch deck (HTML → PDF)

## Infrastructure
- `infra/market_data.py` — Market data from yfinance (price, multiples, history)
- `infra/chart_generator.py` — Professional chart generation (6 chart types: time-series, waterfall, football-field, pie, scenario-bar, dcf-sensitivity)
- `infra/projection_engine.py` — Forward financial projections
- `infra/excel_builder.py` — Multi-tab Excel model builder (single-company)
- `infra/comp_builder.py` — Multi-company comp sheet Excel builder (8 tabs)
- `infra/docx_renderer.py` — Word document renderer from templates
- `infra/pdf_renderer.py` — Markdown → styled HTML → PDF renderer
- `infra/deck_renderer.py` — HTML deck → PDF renderer
- `infra/report_differ.py` — Context JSON diff for update tracking
- `templates/research_note.docx` — Word template for research notes

## Plugin
The building block skills (10 analysis skills) are also available as a standalone Claude Code plugin at `../daloopa-plugin/`. The plugin uses MCP + generic market data language (no Python infrastructure required). Use `scripts/sync_plugin.sh` to sync shared skill files to the plugin repo.

## API Documentation
The `daloopa-docs` MCP server provides direct access to Daloopa's knowledgebase for API usage questions, data coverage, and platform features. A local copy of the docs is also in `daloopa_docs/`. See also: https://docs.daloopa.com
