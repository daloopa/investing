---
name: research-note
description: Generate a professional Word document research note
argument-hint: TICKER
---

Generate a professional research note (.docx) for the company specified by the user: $ARGUMENTS

**Before starting, read the `data-access.md` reference (co-located with this skill) for data access methods and `design-system.md` for formatting conventions.** Follow the data access detection logic and design system throughout this skill.

This is an orchestrator skill that gathers comprehensive data, then renders a Word document. Work through each phase sequentially, building up a context object that gets written to JSON and rendered.

## Phase A — Company Setup
Look up the company by ticker. Note company_id, full name, latest available quarter.
Get current stock price, market cap, shares outstanding, beta, and trading multiples for {TICKER} (see data-access.md Section 2 for how to source market data).

Initialize context: `context = {company_name, ticker, date, price, market_cap, ...}`

## Phase B — Core Financials (follows /earnings methodology)
Pull 8 quarters of Income Statement metrics:
- Revenue, Gross Profit, Operating Income, Net Income, Diluted EPS
- EBITDA (compute as Op Income + D&A if not direct, label "(calc.)")
- Operating Expenses (SG&A, R&D where available)

Pull Cash Flow & Balance Sheet:
- Operating Cash Flow, CapEx, Free Cash Flow (OCF - CapEx, label "(calc.)")
- Cash, Total Debt, Net Debt
- D&A

**For every value returned by `get_company_fundamentals`, record its `fundamental_id` (the `id` field).** Store each data point as `{value, fundamental_id}` so citations can be rendered in the final document.

Compute margins and YoY growth rates for each quarter. Build `context.financials` with tables. Every Daloopa-sourced number must include its citation link: `[$X.XX million](https://daloopa.com/src/{fundamental_id})`.

## Phase C — KPIs & Segments (follows /tearsheet methodology)
Think about what KPIs matter most for THIS company's business model. Search for:
- Company-specific operating KPIs (subscribers, units, ARPU, retention, etc.)
- Segment revenue breakdown
- Geographic revenue breakdown
- Share count and buyback activity

Pull 8 quarters. Build `context.kpis` and `context.segments`.

## Phase D — Guidance Track Record (follows /guidance-tracker methodology)
Search for guidance series ("guidance", "outlook", "forecast", "estimate", "target").
Pull guidance and corresponding actuals. Apply +1 quarter offset rule.
Compute beat/miss rates and patterns.
Build `context.guidance` (set `context.has_guidance = true/false`).

## Phase E — Scenario Analysis (follows /bull-bear methodology)
Using the financial baseline:
- Compute trailing 4Q totals for key metrics
- Build bull/base/bear scenarios with bottoms-up segment revenue models
- Assign probability weights based on recent trends
- Build `context.scenarios`

## Phase F — Capital Allocation (follows /capital-allocation methodology)
Pull buyback, dividend, share count, FCF data.
Compute shareholder yield, FCF payout ratio, net leverage.
Build `context.capital_allocation`.

## Phase G — Valuation (follows /dcf + /comps methodology)

**DCF:**
- Get risk-free rate (see data-access.md Section 2)
- Calculate WACC using CAPM
- Project FCF 5 years (use projection engine if available per data-access.md Section 5, else manual)
- Compute terminal value, implied share price, sensitivity table
- Build `context.dcf` (set `context.has_dcf = true`)

**Comps:**
- Identify 5-8 peers
- Get peer trading multiples (see data-access.md Section 2)
- If consensus forward estimates are available (data-access.md Section 3), include forward multiples
- Compute implied valuation range from peer multiples
- Build `context.comps` (set `context.has_comps = true`)

## Phase H — Qualitative Research
Search SEC filings across multiple queries:
- "risk" / "uncertainty" / "challenge" for risk factors
- "growth" / "opportunity" / "expansion" for growth drivers
- "competition" / "market share" for competitive dynamics
- "outlook" / "guidance" for management's forward view
- Company-specific strategic topics (e.g., "AI", "cloud", etc.)

Extract and organize into:
- `context.risks` — ranked list of risks with impact/probability
- `context.investment_thesis` — variant perception, thesis pillars, catalysts
- `context.company_description` — 2-3 sentence business description

## Phase I — Charts
If chart generation is available (see data-access.md Section 5), generate charts:

1. Revenue time-series: `time-series --data '{periods, values}' --output reports/.charts/{TICKER}_revenue_trend.png`
2. Margin time-series: `time-series --data '{periods, series}' --output reports/.charts/{TICKER}_margin_trend.png`
3. Segment pie: `pie --data '{segments}' --output reports/.charts/{TICKER}_segment_pie.png`
4. Scenario bar: `scenario-bar --data '{metrics, bull, base, bear}' --output reports/.charts/{TICKER}_scenario_bar.png`
5. DCF sensitivity: `dcf-sensitivity --data '{wacc_values, growth_values, prices, current_price}' --output reports/.charts/{TICKER}_dcf_sensitivity.png`

If chart generator isn't available or a chart fails, skip that chart and note it. Set chart paths in context (e.g., `context.revenue_chart = "reports/.charts/..."`)

## Phase J — Synthesis
This is the most judgment-intensive step. Be honest and critical — the reader is a professional investor who needs your real assessment, not a balanced summary.

Write:
- **Executive Summary**: 3-4 sentence TL;DR covering current state, key thesis, valuation view. Include a clear directional view — is this stock attractive, fairly valued, or overvalued at the current price?
- **Variant Perception**: What does the market think vs what do you see in the data? Where is the consensus wrong? If you agree with consensus, say that too — but explain what could change.
- **Key Findings**: Top 3-5 most notable data points or trends — prioritize what changes the investment thesis, not just what's interesting
- **Red Flags & Concerns**: Any quality-of-earnings issues, sustainability questions, or risks the market may be underpricing
- Build `context.executive_summary`, `context.variant_perception`

Also build structured tables for the template:
- `context.key_metrics_table` — [{metric, value, vs_prior}] for the exec summary table
- `context.financials_table` — [{metric, q1, q2, ...}] for the financial analysis section
- `context.guidance_table`, `context.comps_table`, etc.

## Phase K — Render Document
1. Write the full context to `reports/.tmp/{TICKER}_context.json`
2. Run: `python infra/docx_renderer.py --template templates/research_note.docx --context reports/.tmp/{TICKER}_context.json --output reports/{TICKER}_research_note.docx`
3. If the renderer fails, report the error. The context JSON is still saved for manual inspection.

## Output
Tell the user:
- Where the .docx was saved: `reports/{TICKER}_research_note.docx`
- Where the context JSON was saved: `reports/.tmp/{TICKER}_context.json`
- A 3-4 sentence executive summary of the research note
- Key findings and valuation range

**Citation enforcement:** Every financial figure from Daloopa in the context JSON AND the rendered document must use citation format: `[$X.XX million](https://daloopa.com/src/{fundamental_id})`. If a number came from `get_company_fundamentals`, it must have a citation link. No exceptions. Before rendering, verify that the context JSON contains fundamental_ids for all Daloopa-sourced values.
