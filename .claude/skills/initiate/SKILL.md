---
name: initiate
description: Initiate coverage — generate both research note (.docx) and Excel model (.xlsx)
argument-hint: TICKER
---

Initiate coverage on the company specified by the user: $ARGUMENTS

**Before starting, read `.claude/skills/data-access.md` to determine whether to use MCP tools or API recipe scripts for data access.** Follow its detection logic and use the appropriate method throughout this skill.

This is the capstone skill that produces both a research note and an Excel model from a single comprehensive data gathering pass.

## Strategy
Rather than running `/research-note` and `/model` independently (which would duplicate data gathering), this skill gathers a superset of data once, then renders both outputs.

## Phase 1 — Company Setup
Look up the company by ticker. Note company_id, full name, latest available quarter.
Run market data commands:
- `python infra/market_data.py quote {TICKER}` — price, market cap, shares, beta
- `python infra/market_data.py multiples {TICKER}` — trading multiples
- `python infra/market_data.py risk-free-rate` — for DCF

## Phase 2 — Comprehensive Data Gathering
Follow the `/model` skill's Phase 2 data pull (the most comprehensive). Pull 8-16 quarters of:
- Full Income Statement (Revenue through EPS, including D&A for EBITDA calc)
- Full Balance Sheet (Cash through Equity)
- Full Cash Flow Statement (OCF, CapEx, FCF, Dividends, Buybacks)
- Segment revenue and operating income breakdowns
- Geographic revenue breakdown
- All company-specific operating KPIs
- All guidance series and corresponding actuals
- Share count, buyback amounts

## Phase 3 — Peer Analysis
Identify 5-8 comparable companies.
Run `python infra/market_data.py peers {PEER1} {PEER2} ...` for multiples.
Pull peer fundamentals from Daloopa where available (revenue growth, margins).

## Phase 4 — Projections
Write historical data to `reports/.tmp/{TICKER}_initiate_input.json`.
Run projection engine if available:
`python infra/projection_engine.py --context reports/.tmp/{TICKER}_initiate_input.json --output reports/.tmp/{TICKER}_initiate_projections.json`
Otherwise project manually.

## Phase 5 — DCF Valuation
- Calculate WACC (CAPM)
- Project 5-year FCFs
- Terminal value
- Implied share price
- Sensitivity table (WACC × terminal growth)

## Phase 6 — Qualitative Research
Search SEC filings comprehensively:
- Risk factors, growth drivers, competitive dynamics
- Management outlook and guidance language
- Capital allocation strategy
- Company-specific strategic topics
Extract business description, risks (ranked), investment thesis, catalysts.

## Phase 7 — Scenario Analysis
Build bull/base/bear cases:
- Bottoms-up segment revenue builds for each scenario
- Margin, EPS, and price target implications
- Probability weighting based on recent data
- Key swing factors

## Phase 8 — Synthesis & Charts
Write the executive summary, variant perception, and key findings.

Generate charts:
1. `python infra/chart_generator.py revenue-trend ...`
2. `python infra/chart_generator.py margin-trend ...`
3. `python infra/chart_generator.py segment-pie ...`
4. `python infra/chart_generator.py scenario-bar ...`
5. `python infra/chart_generator.py dcf-sensitivity ...`

Skip any charts that fail; note which were generated.

## Phase 9 — Render Both Outputs

**Research Note (.docx):**
1. Build the research note context with all gathered data, charts, narrative sections
2. Write to `reports/.tmp/{TICKER}_context.json`
3. Run: `python infra/docx_renderer.py --template templates/research_note.docx --context reports/.tmp/{TICKER}_context.json --output reports/{TICKER}_research_note.docx`

**Excel Model (.xlsx):**
1. Build the model context with all financial data, projections, DCF, comps
2. Write to `reports/.tmp/{TICKER}_model_context.json`
3. Run: `python infra/excel_builder.py --context reports/.tmp/{TICKER}_model_context.json --output reports/{TICKER}_model.xlsx`

## Output
Tell the user:
- Research note saved to: `reports/{TICKER}_research_note.docx`
- Excel model saved to: `reports/{TICKER}_model.xlsx`
- Context files saved to: `reports/.tmp/` (for future updates)
- 3-4 sentence executive summary
- Key valuation range (DCF implied price + comps range)
- Top 3 findings
- Remind user that yellow cells in the Excel model's Projections tab are editable inputs

All financial figures must use Daloopa citation format: [$X.XX million](https://daloopa.com/src/{fundamental_id})
