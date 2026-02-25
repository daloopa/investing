---
name: earnings
description: Full earnings analysis with guidance tracking for a given company
argument-hint: TICKER
---

Perform a comprehensive earnings analysis for the company specified by the user: $ARGUMENTS

**Before starting, read the `data-access.md` reference (co-located with this skill) for data access methods and `design-system.md` for formatting conventions.** Follow the data access detection logic and design system throughout this skill.

Follow these steps:

## 1. Company Lookup
Look up the company by ticker to get the company_id and latest available quarter.

## 2. Core Financial Metrics
Search for these metrics, then pull the last 8 quarters of data:

**Income Statement:**
- Revenue / Net Sales
- Gross Profit
- Operating Income / EBIT
- EBITDA (if not reported, compute as Operating Income + D&A — label it "EBITDA (calc.)")
- Net Income
- Diluted EPS
- Operating Expenses (SG&A, R&D where available)

**Cash Flow & Balance Sheet:**
- Operating Cash Flow
- CapEx (Purchases of property, plant and equipment)
- Free Cash Flow (compute as Operating Cash Flow - CapEx — label it "FCF (calc.)")
- D&A (needed for EBITDA calc if not directly reported)

For any derived/computed metric, mark it with "(calc.)" so the reader knows it's not directly sourced.

Flag any one-time items that distort a quarter (e.g., tax charges, impairments, litigation settlements) with a footnote so YoY comparisons aren't misleading.

## 3. Company-Specific KPIs
First, think about what the most important KPIs are for THIS specific company based on its business model and what drives its valuation. For example:
- **SaaS/cloud**: ARR, net revenue retention, RPO/cRPO, customers >$100K
- **Consumer tech**: DAU/MAU, ARPU, engagement metrics, installed base, paid subscribers
- **E-commerce/marketplace**: GMV, take rate, active buyers/sellers, order frequency
- **Retail**: same-store sales, store count, average ticket, transactions
- **Telecom/media**: subscribers, churn, ARPU, content spend
- **Hardware**: units shipped, ASP, attach rate
- **Financial services**: AUM, NIM, loan growth, credit quality metrics
- **Pharma/biotech**: pipeline stage, patient starts, scripts, market share

Then search for those specific KPIs by name, plus cast a wider net for anything else available. Also search for:
- Segment/product revenue breakdown
- Geographic revenue breakdown

Pull for the same 8-quarter period. If some KPIs only have data for recent quarters, include what's available and note the gap.

## 4. Growth & Margins
Calculate and present:
- YoY revenue growth for each of the last 4 quarters (not just one)
- Gross margin, operating margin, EBITDA margin, net margin trends over 8 quarters
- EPS growth YoY for each of the last 4 quarters
- Segment revenue YoY growth for the most recent quarter
- Geographic revenue YoY growth for the most recent quarter
- KPI growth rates where applicable

If the company has strong seasonality (e.g., retail Q4 holiday, back-to-school, cyclical patterns), add a note so the reader interprets QoQ swings correctly.

## 5. Guidance vs Actuals
Search for guidance series (revenue guidance, EPS guidance, margin guidance, OpEx guidance, any KPI guidance). If available:
- Pull guidance and actual results
- CRITICAL: Apply +1 quarter offset — guidance from Q(N) applies to Q(N+1) results
- Calculate beat/miss amounts and percentages
- Note patterns (consistent beats, narrows, etc.)
- If the company provides directional guidance (e.g., "low-to-mid-teens growth") rather than hard numbers, note this and compare against the actual growth rate

If no formal guidance series exist, note that the company does not provide quantitative guidance.

## 6. Consensus Context (if available)
If consensus estimates are available (see data-access.md Section 3), add:
- Consensus revenue and EPS vs actual results — beat/miss vs Street
- Estimate revision trends (are estimates moving up or down?)
- Note the source of consensus data used

If consensus data is not available, skip this section and note "consensus data not available."

## 7. Management Commentary
Search SEC filings/documents for management commentary. Try multiple searches to get broad coverage:
- First search: "results" or "record" for earnings highlights
- Second search: "outlook" or "guidance" for forward-looking commentary
- Third search: strategy-specific terms relevant to the company (e.g., "AI", "cloud", "subscribers")
- If a search returns empty, try broader single-keyword searches before giving up

Extract:
- Earnings results and key drivers
- Forward outlook and guidance language
- Segment performance highlights
- Any notable call-outs (one-time items, macro commentary, strategic updates)
- Direct management quotes where available (with document citations)

## 8. Save Report
Save the complete analysis to `reports/{TICKER}_earnings_{PERIOD}.md` where PERIOD is the most recent quarter analyzed. The report should include:
- Executive summary (2-3 sentence overview of the quarter + 2-3 most notable findings)
- Core financial metrics table (8 quarters, periods as columns, metrics as rows, including FCF)
- Segment and geographic revenue breakdown tables
- KPI table (with notes on any data gaps)
- Margin trends table (8 quarters)
- YoY growth rates table (last 4 quarters, showing each quarter's YoY)
- Guidance vs actuals table (if applicable) with pattern analysis
- Management commentary with direct quotes and document citations
- Seasonality note if applicable
- All financial figures must use Daloopa citation format: [$X.XX million](https://daloopa.com/src/{fundamental_id})

Tell the user where the report was saved and highlight the 2-3 most notable findings with a critical lens:
- **Quality of earnings**: Are the beats sustainable or driven by one-time items, favorable timing, or accounting changes? Is revenue growth real or pulled forward?
- **Red flags**: Any deterioration in cash conversion, growing GAAP vs non-GAAP gaps, rising SBC dilution, margin expansion from under-investment?
- **What the market is missing**: What does the data say that consensus might not be pricing in — positive or negative?
