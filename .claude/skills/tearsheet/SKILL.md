---
name: tearsheet
description: Quick one-page company overview and snapshot
argument-hint: TICKER
---

Generate a concise company tearsheet for the company specified by the user: $ARGUMENTS

This should be a quick, one-page overview — the kind of snapshot an analyst pulls up before a meeting.

**Before starting, read `.claude/skills/data-access.md` to determine whether to use MCP tools or API recipe scripts for data access.** Follow its detection logic and use the appropriate method throughout this skill.

Follow these steps:

## 1. Company Lookup
Look up the company by ticker. Note the ticker, full name, and latest available quarter.

## 2. Key Financials
Pull the last 4 quarters PLUS the year-ago quarter for each of those 4 (i.e., 8 quarters total to enable YoY for every recent quarter):
- Revenue
- Gross Profit
- Operating Income
- EBITDA (if not reported, compute as Operating Income + D&A — label it "EBITDA (calc.)" in the report)
- Net Income
- Diluted EPS
- Operating Cash Flow
- CapEx (Purchases of property, plant and equipment)
- Free Cash Flow (compute as Operating Cash Flow - CapEx — label it "FCF (calc.)" in the report)

For any derived/computed metric, mark it with "(calc.)" so the reader knows it's not directly sourced.

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

Then search for those specific KPIs by name, plus cast a wider net for anything else Daloopa has. Also search for:
- Segment/product revenue breakdown
- Geographic revenue breakdown
- Share count and share repurchase activity

Pull for the same period as financials.

## 4. Compute Key Ratios
Show trend over the last 4 quarters with YoY change for EACH quarter (not just the earliest):
- Gross Margin %
- Operating Margin %
- EBITDA Margin %
- Net Margin %
- Revenue Growth (YoY)
- EPS Growth (YoY)

If the company has strong seasonality (e.g., retail Q4, back-to-school, etc.), add a brief note flagging it so YoY comparisons are read in context rather than sequential QoQ.

## 5. Recent Developments
Search the most recent 2 quarters of filings. Try multiple keyword searches to get coverage:
- First search: company name + "results" or "record" for earnings highlights
- Second search: "outlook" or "guidance" or "expect" for forward-looking commentary
- Third search: strategy-specific terms relevant to the company (e.g., "AI", "cloud", "subscribers", "margin")
- If a search returns empty, try broader single-keyword searches before giving up

Extract:
- Business description / what the company does (2-3 sentences)
- Key recent developments or announcements
- Management's top priorities or strategic focus areas
- Any notable management quotes (with document citations)
Keep this brief — 3-5 bullet points max.

## 6. Save Report
Save to `reports/{TICKER}_tearsheet.md`. Format as a clean, scannable tearsheet:

```
# {Company Name} ({TICKER}) — Tearsheet
Generated: {date}

## Company Overview
{2-3 sentence description from filings}

## Key Financials (Last 4 Quarters)
| Metric | Q(oldest) | Q | Q | Q(latest) |
{table with Daloopa citations; derived metrics marked (calc.)}

## Segment / Geographic Breakdown
{segment revenue table or geographic revenue table, whichever is more relevant}

## Key Operating KPIs
| KPI | Q(oldest) | Q | Q | Q(latest) |
{table with Daloopa citations; include share count/buyback data if available}

## Margins & Growth
| Metric | Q(oldest) | Q | Q | Q(latest) |
| --- | --- | --- | --- | --- |
| Gross Margin % | X% | X% | X% | X% |
| ... | ... | ... | ... | ... |
| Rev Growth YoY | X% | X% | X% | X% |
| EPS Growth YoY | X% | X% | X% | X% |
{each cell shows the YoY change for THAT quarter}
{note on seasonality if applicable}

## Recent Developments
- {bullet points from filings with document citations}

Data sourced from Daloopa
```

All financial figures must use Daloopa citation format: [$X.XX million](https://daloopa.com/src/{fundamental_id})

Tell the user where the report was saved and give a 2-3 sentence summary of the company's current state.
