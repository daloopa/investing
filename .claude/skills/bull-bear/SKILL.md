---
name: bull-bear
description: Bull/bear/base case scenario framework for a given company
argument-hint: TICKER
---

Build a bull/bear/base case scenario framework for the company specified by the user: $ARGUMENTS

**Before starting, read `.claude/skills/data-access.md` to determine whether to use MCP tools or API recipe scripts for data access.** Follow its detection logic and use the appropriate method throughout this skill.

Follow these steps:

## 1. Company Lookup
Look up the company by ticker. Extract company_id and latest available quarter.

## 2. Historical Financial Baseline
Pull at least 8 quarters of:
- Revenue
- Gross Profit / Gross Margin %
- Operating Income / Operating Margin %
- EBITDA (if not reported, compute as Operating Income + D&A — label "(calc.)")
- Net Income
- Diluted EPS
- Operating Cash Flow
- CapEx
- Free Cash Flow (compute as OCF - CapEx — label "(calc.)")
- Segment-level revenue breakdowns
- Geographic revenue breakdowns

Compute trailing 4-quarter totals for revenue, EBITDA, net income, EPS, and FCF — these are the baseline the scenarios build from.

Flag any one-time items that distort quarters.

## 3. Key Operating KPIs
First, think about what the most important KPIs are for THIS specific company based on its business model and what drives its valuation. For example:
- **SaaS/cloud**: ARR, net revenue retention, RPO/cRPO, customers >$100K
- **Consumer tech**: DAU/MAU, ARPU, engagement metrics, installed base, paid subscribers
- **E-commerce/marketplace**: GMV, take rate, active buyers/sellers, order frequency
- **Retail**: same-store sales, store count, average ticket, transactions
- **Telecom/media**: subscribers, churn, ARPU, content spend
- **Hardware**: units shipped, ASP, attach rate
- **Financial services**: AUM, NIM, loan growth, credit quality metrics
- **Pharma/biotech**: pipeline stage, patient starts, scripts, market share

Search for those specific KPIs by name and pull them. These are the building blocks for bottoms-up scenario math.

Also pull capital allocation data: share count, buyback amounts, dividends.

## 4. Qualitative Research
Search SEC filings/documents across multiple queries. If any search returns empty, try alternative keywords before giving up.
- **Risk factors**: Try "risk", "uncertainty", "challenge"; fallback to "adverse", "headwind"
- **Growth drivers**: Try "growth", "opportunity", "expansion"; fallback to "momentum", "strong demand"
- **Competitive dynamics**: Try "competition", "market share"; fallback to "competitive"
- **Management outlook**: Try "outlook", "guidance", "expect"; fallback to "anticipate", "forward"
- **Capital allocation**: Try "repurchase", "dividend"; fallback to "buyback", "capital return"
- **Macro/regulatory**: Try "tariff", "regulatory"; fallback to "geopolitical", "compliance"

## 5. Construct Three Scenarios

For each scenario, build a **bottoms-up revenue model** showing key segment or product-level assumptions (e.g., units x ASP, subscribers x ARPU, segment growth rates). Don't just state a revenue range — show the math that gets there.

### Bull Case
- Identify the most favorable realistic trajectory
- Key assumptions: revenue acceleration, margin expansion, KPI improvement, favorable macro/competitive shifts
- Quantify using historical highs and growth rates as anchors
- Show segment-level build: what needs to go right in each business line
- List specific catalysts that could drive this outcome
- Consider how capital allocation (buybacks) amplifies EPS upside

### Base Case
- Extrapolate current trends forward
- Key assumptions: continuation of recent growth rates, stable margins, steady KPI progression
- This should be the "most likely" scenario grounded in the last 4-8 quarters of data
- Show segment-level build using current trend rates
- Reference historical analogs if applicable (e.g., prior product cycles, similar macro environments)

### Bear Case
- Identify realistic downside risks
- Key assumptions: revenue deceleration, margin compression, KPI deterioration, competitive/macro headwinds
- Quantify using historical lows, risk factor analysis, and specific cost headwinds from filings (e.g., tariff drag, regulatory impact)
- Show segment-level build: what breaks in each business line
- List specific risks that could drive this outcome
- Consider how capital allocation behavior changes in a downturn (buybacks may accelerate at lower prices)

### Probability Weighting
Don't default to 25/50/25. Assign probabilities informed by the most recent data points:
- If recent results are accelerating, weight bull higher
- If macro headwinds are intensifying, weight bear higher
- Explain your reasoning for the weighting

## 6. Save Report
Save to `reports/{TICKER}_bull_bear.md`. The report should include:
- Company overview and current state summary
- Historical financial data table (8 quarters, Daloopa citations, including computed EBITDA/FCF)
- Trailing 4-quarter totals as the scenario baseline
- Segment and geographic revenue tables
- KPI trends table
- Capital allocation summary (buybacks, dividends, share count)
- Three scenario sections each with:
  - Key assumptions (bulleted)
  - Bottoms-up segment revenue build
  - Implied revenue/margin/EPS trajectory
  - Implied KPI trajectory
  - Catalysts / risks specific to that scenario
- Probability-weighted summary with reasoning
- Key risk factors and growth drivers from filings (with document citations)
- Summary comparison table across scenarios
- Key swing factors section — the 3-5 variables that most determine which scenario plays out
- All financial figures must use Daloopa citation format: [$X.XX million](https://daloopa.com/src/{fundamental_id})

Tell the user where the report was saved and highlight the key swing factors between bull and bear cases.
