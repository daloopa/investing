---
name: tearsheet
description: Quick one-page company overview and snapshot
argument-hint: TICKER
---

Generate a concise company tearsheet for the company specified by the user: $ARGUMENTS

This should be a quick, one-page overview — the kind of snapshot an analyst pulls up before a meeting.

**Before starting, read the `data-access.md` reference (co-located with this skill) for data access methods and `design-system.md` for formatting conventions.** Follow the data access detection logic and design system throughout this skill.

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
This section is strictly for **business-driver metrics** — the operational numbers that actually move revenue and earnings. Do NOT put financial statement items (D&A, share count, buybacks, dividends) here — those belong in the financials or capital return sections.

First, think about what the most important KPIs are for THIS specific company based on its business model and what drives its valuation. For example:
- **SaaS/cloud**: ARR, net revenue retention, RPO/cRPO, customers >$100K, cloud gross margin
- **Consumer tech**: DAU/MAU, ARPU, engagement metrics, installed base, paid subscribers
- **E-commerce/marketplace**: GMV, take rate, active buyers/sellers, order frequency
- **Retail**: same-store sales, store count, average ticket, transactions
- **Telecom/media**: subscribers, churn, ARPU, content spend
- **Hardware**: units shipped, ASP, attach rate, installed base, products vs services gross margin split
- **Financial services**: AUM, NIM, loan growth, credit quality metrics
- **Pharma/biotech**: pipeline stage, patient starts, scripts, market share
- **Industrials/energy**: backlog, book-to-bill, utilization, production volumes

Then search for those specific KPIs by name, plus cast a wider net for anything else Daloopa has. Also search for:
- Segment/product revenue breakdown
- Geographic revenue breakdown

**If the company discloses few operational KPIs** (e.g., Apple stopped reporting iPhone units in 2019), acknowledge the disclosure gap explicitly rather than padding the section with financial metrics. A short note like "Apple does not disclose unit volumes or ASPs; segment revenue is the finest granularity available" is more informative than showing D&A and buybacks as fake KPIs.

**Always search broadly** — companies often disclose more KPIs than you'd expect. For Apple, beyond segment revenue, Daloopa also has: installed base active devices (~2.5bn), products gross margin vs services gross margin (the mix shift story), and paid subscriptions. These are real operational metrics. Search with keywords like "installed", "active", "subscriber", "margin" by segment, not just the obvious financial terms.

Pull for the same period as financials.

## 3b. Capital Return
Pull share count, share repurchases, and dividends paid for the same periods. This is a separate section from operating KPIs — it shows how the company is returning cash to shareholders.

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
{table with Daloopa citations — ONLY business-driver metrics, NOT financial items}
{if few KPIs available, note the disclosure gap}

## Capital Return
| Metric | Q(oldest) | Q | Q | Q(latest) |
{share count, buybacks, dividends — separate from operating KPIs}

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

## 7. Render PDF
Render the markdown report to PDF (see data-access.md Section 5 for infrastructure):
`python3 infra/pdf_renderer.py --input reports/{TICKER}_tearsheet.md --output reports/{TICKER}_tearsheet.pdf`

Tell the user where the PDF was saved. If PDF rendering fails, note the error and point them to the markdown file.

Give a 2-3 sentence summary of the company's current state, including an honest assessment: What is the single biggest risk or concern? Does the current valuation (price, implied multiples) seem warranted given the growth trajectory? What would make you cautious about owning this stock?
