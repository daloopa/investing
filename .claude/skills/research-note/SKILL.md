---
name: research-note
description: Generate a professional Word document research note
argument-hint: TICKER
---

Generate a professional research note (.docx) for the company specified by the user: $ARGUMENTS

**Before starting, read `../data-access.md` for data access methods and `../design-system.md` for formatting conventions.** Follow the data access detection logic and design system throughout this skill.

This is an orchestrator skill that gathers comprehensive data, then renders a Word document. Work through each phase sequentially, building up a context object that gets written to JSON and rendered.

## Phase A — Company Setup
Look up the company by ticker. Note company_id, full name, latest available quarter.
Get current stock price, market cap, shares outstanding, beta, and trading multiples for {TICKER} (see ../data-access.md Section 2 for how to source market data).

Initialize context: `context = {company_name, ticker, date, price, market_cap, ...}`

## Phase B — Core Financials + Cost Structure
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

### Cost Structure & Margin Analysis (NEW)
After the core financial pull, add:

- **COGS driver identification**: Search for cost-related series ("cost of goods", "materials", "manufacturing", "input cost"). Identify 3-5 biggest cost line items and their trends over 8Q.
- **OpEx breakdown**: Pull R&D and SG&A separately. Compute R&D % of revenue and SG&A % of revenue trends over 8Q.
- **Margin driver analysis**: For each major margin (gross, operating, net), identify what's driving expansion or compression — pricing power, cost leverage, mix shift, or one-time items.

New context keys:
- `cost_margin_analysis` (string) — narrative explaining what's driving margins, with Daloopa citations
- `opex_breakdown_table` (dynamic table) — [{metric, Q1, Q2, ...}] rows for R&D, SG&A, Other OpEx, each with absolute values and % of revenue sub-rows

## Phase C — KPIs, Segments & Industry Deep Dive
Think about what KPIs matter most for THIS company's business model. Search for:
- Company-specific operating KPIs (subscribers, units, ARPU, retention, etc.)
- Segment revenue breakdown
- Geographic revenue breakdown
- Share count and buyback activity

Pull 8 quarters. Build `context.kpis` and `context.segments`.

### Industry-Specific Deep Dive (NEW)
After the KPI/segment pull, determine the company's sector and apply the relevant analysis template:

- **Manufacturing/Industrial**: Bookings & backlog, book-to-bill ratio, pipeline by geography, capacity utilization
- **SaaS/Technology**: ARR/MRR trajectory, net retention rate, customer cohort analysis, RPO/deferred revenue trends
- **Retail/Consumer**: Same-store sales, store count trajectory, traffic vs ticket decomposition, inventory health
- **Financials/Banks**: NIM trajectory, provision trends, loan growth by category, capital ratios (CET1, TCE)
- **Healthcare/Pharma**: Pipeline summary (drug, indication, phase, milestone), product revenue breakdown, patent cliff timeline
- **Energy**: Production volumes, realized pricing vs benchmark, proved reserves, breakeven analysis

Search for relevant series using `discover_company_series` with sector-appropriate keywords. Pull available data and build the narrative.

New context key:
- `industry_deep_dive` (string) — sector-specific analysis narrative with Daloopa citations, organized by the relevant template above

## Phase D — Guidance Track Record (follows /guidance-tracker methodology)
Search for guidance series ("guidance", "outlook", "forecast", "estimate", "target").
Pull guidance and corresponding actuals. Apply +1 quarter offset rule.
Compute beat/miss rates and patterns.
Build `context.guidance` (set `context.has_guidance = true/false`).

## Phase E — What You Need to Believe (replaces Scenario Analysis)
Using the financial baseline from Phase B:
- Compute trailing 4Q totals for key metrics (revenue, EBITDA, EPS, FCF)
- Analyze segment-level trends and inflections

Build **falsifiable bull/bear beliefs** instead of probability-weighted scenarios:

### Bull Beliefs (To Go Long)
Write 4-6 numbered beliefs, each with:
- One **bold statement** (the belief itself)
- 2-3 sentences of **evidence** with Daloopa citations supporting why this could be true
- Each belief must be **falsifiable** — testable with observable data within 6 months

Example format: "1. **Revenue growth re-accelerates to 15%+ as AI monetization scales.** Cloud segment grew [$X.Xbn](link) last quarter, up X% YoY, with management noting..."

### Bear Beliefs (To Go Short)
Same format — 4-6 numbered falsifiable beliefs with evidence for the downside case.

### Valuation Math
For each side:
- Bull target: forward multiple × forward earnings estimate = price target. Show the math.
- Bear target: same structure with bear-case multiple and earnings.

### Risk/Reward Assessment
- Compare bull upside % vs bear downside % from current price
- If asymmetry is significant (e.g., 30% upside vs 40% downside), flag it explicitly
- State which side has the better risk/reward and why

New context keys:
- `bull_beliefs` (string) — numbered falsifiable beliefs with evidence
- `bear_beliefs` (string) — numbered falsifiable beliefs with evidence
- `bull_target` (string) — price target + valuation math
- `bear_target` (string) — price target + valuation math
- `risk_reward_assessment` (string) — asymmetry analysis

**Do NOT set these old keys** (they are removed from the template): `bull_probability`, `base_probability`, `bear_probability`, `bull_description`, `base_description`, `bear_description`, `scenario_chart`, `bull_price_target`, `base_price_target`, `bear_price_target`.

## Phase F — Capital Allocation (follows /capital-allocation methodology)
Pull buyback, dividend, share count, FCF data.
Compute shareholder yield, FCF payout ratio, net leverage.
Build `context.capital_allocation`.

## Phase G — Valuation (follows /dcf + /comps methodology)

**DCF:**
- Get risk-free rate (see ../data-access.md Section 2)
- Calculate WACC using CAPM
- Project FCF 5 years (use projection engine if available per ../data-access.md Section 5, else manual)
- Compute terminal value, implied share price, sensitivity table
- Build `context.dcf` (set `context.has_dcf = true`)

**Comps:**
- Identify 5-8 peers
- Get peer trading multiples (see ../data-access.md Section 2)
- If consensus forward estimates are available (../data-access.md Section 3), include forward multiples
- Compute implied valuation range from peer multiples
- Build `context.comps` (set `context.has_comps = true`)

## Phase H — Qualitative Research + News & Catalysts
### SEC Filing Research
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

### News & Catalysts via WebSearch (NEW)
Run 4 WebSearch queries to gather recent external context:
1. `"{TICKER} {company_name} news {year}"` — recent headlines and developments
2. `"{TICKER} analyst upgrade downgrade price target"` — sell-side sentiment shifts
3. `"{TICKER} catalysts risks"` — forward-looking events and risk factors
4. `"{company_name} industry outlook {sector}"` — macro and industry trends

Organize results into three new context keys:

- `news_timeline` (string) — 6-10 key events from the last 6-12 months in reverse chronological order. Each event: date, headline, 1-sentence impact, sentiment tag (Positive / Negative / Mixed / Upcoming). Format as a numbered list.

- `forward_catalysts` (string) — Organized by timeframe:
  - **Near-term (0-3 months, HIGH priority)**: earnings dates, product launches, regulatory decisions
  - **Medium-term (3-12 months, MEDIUM priority)**: strategic milestones, contract renewals, industry events
  - **Long-term (1-3 years, LOW priority)**: secular trends, market expansion, competitive dynamics

- `policy_backdrop` (string) — Macro/regulatory context affecting the company. Tariffs, regulation, interest rates, sector-specific policy. Leave empty string if not material.

## Phase I — Charts
If chart generation is available (see ../data-access.md Section 5), generate charts:

1. Revenue time-series: `time-series --data '{periods, values}' --output reports/.charts/{TICKER}_revenue_trend.png`
2. Margin time-series: `time-series --data '{periods, series}' --output reports/.charts/{TICKER}_margin_trend.png`
3. Segment pie: `pie --data '{segments}' --output reports/.charts/{TICKER}_segment_pie.png`
4. DCF sensitivity: `dcf-sensitivity --data '{wacc_values, growth_values, prices, current_price}' --output reports/.charts/{TICKER}_dcf_sensitivity.png`

If chart generator isn't available or a chart fails, skip that chart and note it. Set chart paths in context (e.g., `context.revenue_chart = "reports/.charts/..."`)

**Note:** scenario_chart is no longer generated by this skill (research notes use bull/bear beliefs, not scenario analysis). The `/ib-deck` skill still uses scenario-bar charts.

## Phase J — Synthesis + Tensions + Monitoring
This is the most judgment-intensive step. Be honest and critical — the reader is a professional investor who needs your real assessment, not a balanced summary.

### Core Synthesis
Write:
- **Executive Summary**: 3-4 sentence TL;DR covering current state, key thesis, valuation view. Include a clear directional view — is this stock attractive, fairly valued, or overvalued at the current price?
- **Variant Perception**: What does the market think vs what do you see in the data? Where is the consensus wrong? If you agree with consensus, say that too — but explain what could change.
- **Key Findings**: Top 3-5 most notable data points or trends — prioritize what changes the investment thesis, not just what's interesting
- **Red Flags & Concerns**: Any quality-of-earnings issues, sustainability questions, or risks the market may be underpricing
- Build `context.executive_summary`, `context.variant_perception`

### Five Key Tensions (NEW)
Identify the 5 most critical bull/bear debates for this stock. Each tension is a single line that frames both sides. Alternate between bullish-leaning and bearish-leaning tensions. Every tension must reference a specific data point from the analysis.

Format as a numbered list:
1. "[Bullish factor] vs [Bearish factor]" — cite the specific metric
2. "[Bearish factor] vs [Bullish factor]" — cite the specific metric
...etc.

Build `context.five_key_tensions` (string).

### Monitoring Framework (NEW)
Build two monitoring lists for ongoing tracking:

**Quantitative Monitors** — 5-7 specific metrics with explicit thresholds:
- Format: "Metric: current value → bull threshold / bear threshold"
- Example: "Gross Margin: 45.2% → above 46% confirms pricing power / below 43% signals cost pressure"

**Qualitative Monitors** — 5-7 factors to watch:
- Management tone shifts on earnings calls
- Competitive dynamics (new entrants, pricing pressure)
- Regulatory developments
- Customer concentration changes
- Capital allocation pivots

Build `context.monitoring_quantitative` and `context.monitoring_qualitative` (strings, numbered lists).

### Structured Tables
Also build structured tables for the template:
- `context.key_metrics_table` — [{metric, value, vs_prior}] for the exec summary table
- `context.financials_table` — [{metric, q1, q2, ...}] for the financial analysis section
- `context.segments_table`, `context.geo_table`, `context.shares_outstanding_table`
- `context.opex_breakdown_table` — [{metric, q1, q2, ...}] for R&D, SG&A, % of revenue rows
- `context.guidance_table`, `context.comps_table`, etc.

## Phase K — Render Document
1. Write the full context to `reports/.tmp/{TICKER}_context.json`
2. Run: `python infra/docx_renderer.py --template templates/research_note.docx --context reports/.tmp/{TICKER}_context.json --output reports/{TICKER}_research_note.docx`
3. If the renderer fails, report the error. The context JSON is still saved for manual inspection.

### Context Key Checklist
Verify these keys exist before rendering (set empty string if data unavailable):

**Cover & Summary:**
`company_name`, `ticker`, `date`, `price`, `market_cap`, `five_key_tensions`, `executive_summary`, `key_metrics_table`

**Thesis & Overview:**
`investment_thesis`, `variant_perception`, `company_description`

**News:**
`news_timeline`

**Financials:**
`revenue_chart`, `financials_table`, `margin_chart`, `cost_margin_analysis`, `opex_breakdown_table`, `segment_chart`, `segments_table`, `geo_table`, `shares_outstanding_table`

**Industry:**
`industry_deep_dive`

**Guidance:**
`has_guidance`, `guidance_track_record`

**What You Need to Believe:**
`bull_beliefs`, `bull_target`, `bear_beliefs`, `bear_target`, `risk_reward_assessment`

**Catalysts:**
`forward_catalysts`, `policy_backdrop`

**Capital Allocation:**
`capital_allocation_commentary`

**Valuation:**
`has_dcf`, `dcf_summary`, `dcf_sensitivity_chart`, `has_comps`, `comps_commentary`

**Risks:**
`risks_summary`

**Monitoring:**
`monitoring_quantitative`, `monitoring_qualitative`

**Appendix:**
`appendix_content`

## Output
Tell the user:
- Where the .docx was saved: `reports/{TICKER}_research_note.docx`
- Where the context JSON was saved: `reports/.tmp/{TICKER}_context.json`
- A 3-4 sentence executive summary of the research note
- Key findings and valuation range

**Citation enforcement:** Every financial figure from Daloopa in the context JSON AND the rendered document must use citation format: `[$X.XX million](https://daloopa.com/src/{fundamental_id})`. If a number came from `get_company_fundamentals`, it must have a citation link. No exceptions. Before rendering, verify that the context JSON contains fundamental_ids for all Daloopa-sourced values.
