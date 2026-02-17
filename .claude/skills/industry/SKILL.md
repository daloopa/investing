---
name: industry
description: Cross-company industry comparison across multiple tickers
argument-hint: TICKER1 TICKER2 ...
---

Perform an industry comparison across the companies specified by the user: $ARGUMENTS

The user will provide multiple tickers separated by spaces (e.g., "AAPL MSFT GOOG AMZN").

**Before starting, read `.claude/skills/data-access.md` to determine whether to use MCP tools or API recipe scripts for data access.** Follow its detection logic and use the appropriate method throughout this skill.

Follow these steps:

## 1. Company Lookups
Look up all provided tickers. Collect company_ids for each. Note each company's fiscal year end — this is critical for calendar quarter alignment.

## 2. Comparable Financial Metrics
For each company, find and pull these metrics for the last 4 quarters PLUS the year-ago quarter for each (i.e., 8 quarters total to compute YoY for every recent quarter):

**Income Statement:**
- Revenue
- Gross Profit / Gross Margin
- Operating Income / Operating Margin
- EBITDA (if not reported, compute as Operating Income + D&A — label "(calc.)")
- Net Income / Net Margin
- Diluted EPS
- R&D Expense
- Stock-Based Compensation (SBC)

**Cash Flow:**
- Operating Cash Flow
- CapEx (Purchases of property, plant and equipment)
- Free Cash Flow (compute as OCF - CapEx — label "(calc.)")
- D&A (needed for EBITDA calc if not directly reported)

For any derived/computed metric, mark it with "(calc.)" so the reader knows it's not directly sourced.

## 3. Company-Specific KPIs
First, think about what KPIs matter for the specific industry being compared. For example:
- **Cloud/AI companies**: ARR, RPO/cRPO, Azure/Cloud growth rates, cloud gross margin
- **Consumer tech**: installed base, subscribers, ARPU, engagement
- **E-commerce**: GMV, take rate, active buyers
- **SaaS**: net revenue retention, seat count, ARPU

For each company, discover and pull the most relevant KPIs. Note which KPIs are common across the group (apples-to-apples comparison) and which are unique to specific companies.

## 4. Normalize & Compare
- **Calendar quarter alignment is critical.** Ensure all companies are compared on the same calendar quarters. Note each company's fiscal year end and map fiscal quarters to calendar quarters.
- Build side-by-side comparison tables
- Calculate margins for ALL 4 recent quarters (not just the latest) to show trends
- Calculate YoY growth rates for each of the last 4 quarters

## 5. Ranking & Analysis
- Rank companies on each key metric (revenue growth, margins, FCF yield, etc.)
- Identify the leader and laggard for each metric
- Flag notable outliers (unusually high/low margins, accelerating/decelerating growth)
- Note any divergence in KPIs or business model differences
- Compute R&D as % of revenue and SBC as % of revenue for each company — these reveal structural differences in how each company invests and compensates
- Show YoY segment growth rates for the most recent quarter, not just absolute segment revenue
- Flag one-time items that distort any quarter's comparison

## 6. Document Search
For each company, search the most recent 2 quarters of filings across multiple queries. If any search returns empty, try alternative keywords before giving up.

- **Competitive positioning**: Try "competition", "market share"; fallback to "competitive", "leader", "position"
- **Industry trends**: Try "industry", "market", "demand"; fallback to "secular", "trend", "adoption"
- **Strategic differentiation**: Try "differentiate", "advantage", "moat"; fallback to "unique", "proprietary", "platform"
- **Growth strategy**: Try "growth", "opportunity", "expansion"; fallback to "invest", "launch", "new market"
- **Macro / headwinds**: Try "macro", "headwind"; fallback to "tariff", "regulatory", "geopolitical", "inflation"

If a company returns sparse results across all searches, try broader single-keyword searches (e.g., just "competitive" or just "growth") and search additional periods.

For each company, extract:
- How management describes their competitive position
- Key strategic priorities and investments
- Industry or macro commentary that affects the whole group
- Any direct references to competitors in the comparison set

Use these findings to enrich the rankings analysis — numbers tell you who's winning, filings tell you why.

## 7. Save Report
Save to `reports/{INDUSTRY_LABEL}_industry_comp.md` where INDUSTRY_LABEL is derived from the tickers (e.g., "tech_megacap" or just the tickers joined: "AAPL_MSFT_GOOG_AMZN"). The report should include:
- Summary header listing all companies compared, with fiscal year end dates
- Side-by-side financial metrics table (last 4 calendar quarters, companies as columns, metrics as rows, Daloopa citations)
- Trailing 4-quarter totals for revenue, operating income, net income, EPS, OCF, CapEx, FCF
- **Margin trend table**: Gross margin, operating margin, net margin for ALL 4 quarters per company (not just latest quarter snapshot)
- **Growth comparison table**: Revenue YoY and EPS YoY for each of the last 4 quarters per company
- **R&D and SBC comparison**: R&D % of revenue and SBC % of revenue for each company (latest quarter + trend)
- Segment revenue tables per company with YoY growth rates for each segment in the most recent quarter
- KPI comparison (where applicable), noting common vs company-specific KPIs
- **Cash flow comparison**: OCF, CapEx, FCF side-by-side with CapEx as % of revenue to highlight investment intensity differences
- Rankings summary table
- Key competitive insights from filings (with document citations)
- Note on calendar quarter alignment and any fiscal year differences
- All financial figures must use Daloopa citation format: [$X.XX million](https://daloopa.com/src/{fundamental_id})

Tell the user where the report was saved and highlight the key takeaways (who's winning, key differentiators).
