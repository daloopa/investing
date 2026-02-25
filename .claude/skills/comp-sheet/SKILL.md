---
name: comp-sheet
description: Build an industry comp sheet Excel model with deep operational KPIs
argument-hint: TICKER
---

Build a multi-company industry comp sheet Excel model for the company specified by the user: $ARGUMENTS

This produces an interactive `.xlsx` workbook — the kind of comp sheet every analyst on a coverage team maintains. Multi-company, multi-tab, with deep operational KPIs alongside standard financials.

**Before starting, read the `data-access.md` reference (co-located with this skill) for data access methods and `design-system.md` for formatting conventions.** Follow the data access detection logic and design system throughout this skill.

Follow these steps:

## 1. Company & Peer Setup

Look up the target company by ticker. Then identify 6-10 comparable companies using the same logic as `/comps`:
- **Direct competitors** in the same market
- **Business model peers** (similar revenue model)
- **Size peers** (similar market cap range)
- **Growth profile peers** (similar growth rate)

Look up all peer company_ids via Daloopa. If a peer isn't available in Daloopa, include it with market data only and note the limitation.

List the full peer group with brief justification for each.

## 2. Deep Data Gathering

For each company (target + all peers), pull from Daloopa:

**Last 8 quarters of financials:**
- Revenue, Gross Profit, Operating Income, Net Income, Diluted EPS
- Operating Cash Flow, Capital Expenditures, D&A
- Free Cash Flow (compute as OCF - CapEx)
- R&D Expense, SG&A (where available)

**Segment revenue breakdown** (all available segments, 8 quarters)

**Company-specific operational KPIs** — use the 9-sector taxonomy to know what to search for:
- **SaaS/Cloud**: ARR, net revenue retention, RPO/cRPO, customers >$100K, cloud gross margin
- **Consumer Tech**: DAU/MAU, ARPU, engagement metrics, installed base, paid subscribers
- **E-commerce/Marketplace**: GMV, take rate, active buyers/sellers, order frequency
- **Retail**: same-store sales, store count, average ticket, transactions
- **Telecom/Media**: subscribers, churn, ARPU, content spend
- **Hardware**: units shipped, ASP, attach rate, installed base
- **Financial Services**: AUM, NIM, loan growth, credit quality metrics, fee income ratio
- **Pharma/Biotech**: pipeline stage, patient starts, scripts, market share
- **Industrials/Energy**: backlog, book-to-bill, utilization, production volumes, reserves

**Market data** for each company (see data-access.md Section 2):
- Price, market cap, enterprise value, shares outstanding, beta
- All trading multiples: P/E (trailing + forward), EV/EBITDA, P/S, P/B, EV/FCF, dividend yield

## 3. KPI Discovery & Mapping

After pulling data, build the KPI mapping:
- Which KPIs are available for which companies? Build a coverage matrix.
- Group KPIs into categories:
  - **Segment Revenue**: product/service line breakdowns
  - **Growth KPIs**: subscriber growth, unit growth, same-store sales growth
  - **Unit Economics**: ARPU, ASP, take rate, retention
  - **Efficiency**: R&D % of revenue, SBC % of revenue, CapEx % of revenue
  - **Engagement**: DAU/MAU, retention, churn
- Flag KPIs that are comparable across peers vs company-specific

## 4. Compute Derived Metrics

For each company, calculate:

**Margins:**
- Gross Margin, Operating Margin, Net Margin, FCF Margin (each quarter)

**Growth rates:**
- Revenue YoY, EPS YoY, segment revenue YoY (each quarter where year-ago data exists)

**Capital metrics:**
- Net Debt (Total Debt - Cash)
- Net Debt/EBITDA
- FCF Yield (trailing 4Q FCF / Market Cap)
- Shareholder Yield (Buybacks + Dividends) / Market Cap

**Implied valuation:**
- For each valuation methodology (P/E, EV/EBITDA, P/S, EV/FCF):
  - Peer median multiple × target metric = implied value
  - Convert to implied share price
- Compute median implied price across methodologies

## 5. Build Context JSON

Structure the data as a multi-company context JSON for the comp_builder:

```json
{
  "target_ticker": "AAPL",
  "as_of_date": "YYYY-MM-DD",
  "companies": [
    {
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "is_target": true,
      "market_data": {
        "price": ..., "market_cap": ..., "enterprise_value": ...,
        "shares_outstanding": ..., "beta": ...,
        "trailing_pe": ..., "forward_pe": ...,
        "ev_ebitda": ..., "price_to_sales": ...,
        "ev_fcf": ..., "dividend_yield": ...
      },
      "periods": ["2024Q1", "2024Q2", ...],
      "financials": {
        "Revenue": {"2024Q1": ..., ...},
        "Gross Profit": {...}, ...
      },
      "margins": {
        "Gross Margin": {"2024Q1": ..., ...}, ...
      },
      "growth": {
        "Revenue Growth YoY": {"2024Q1": ..., ...}, ...
      },
      "kpis": {
        "iPhone Revenue": {"2024Q1": ..., ...}, ...
      },
      "kpi_categories": {
        "Segment Revenue": ["iPhone Revenue", "Services Revenue", ...],
        "Growth KPIs": ["Services Growth YoY"],
        "Efficiency": ["R&D % Revenue", "SBC % Revenue"]
      }
    },
    ...more companies...
  ],
  "implied_valuation": {
    "pe_implied": ...,
    "ev_ebitda_implied": ...,
    "ps_implied": ...,
    "ev_fcf_implied": ...,
    "median_implied": ...
  }
}
```

Save to `reports/.tmp/{TICKERS}_comp_context.json`.

## 6. Render Excel

Build the comp sheet workbook (see data-access.md Section 5 for infrastructure):
`python3 infra/comp_builder.py --context reports/.tmp/{TICKERS}_comp_context.json --output reports/{TICKERS}_comp_sheet.xlsx`

The builder creates 8 tabs:
1. **Comp Summary** — one-pager with all companies, multiples, implied valuation
2. **Revenue Drivers** — unit economics decomposition per company (trailing 4Q)
3. **Operating KPIs** — cross-company KPI comparison matrix
4. **Financial Summary** — side-by-side income statements (trailing 4Q)
5. **Growth & Margins** — trend analysis (up to 8Q)
6. **Valuation Detail** — implied prices by methodology, premium/discount
7. **Balance Sheet & Capital** — leverage and capital returns
8. **Raw Data** — full quarterly appendix for each company

## 7. Output

Tell the user where the `.xlsx` was saved.

Highlight in your summary:
- **Target positioning vs peers**: Where does it rank on growth, margins, and valuation?
- **Most differentiated KPIs**: Which operational metrics set the target apart (positive or negative)?
- **Implied valuation range**: What does the peer group suggest the stock is worth?
- **Key risk**: What's the biggest vulnerability the comp sheet reveals (e.g., premium valuation with decelerating KPIs, margins below peers, etc.)?

All financial figures in the summary must use Daloopa citation format: [$X.XX million](https://daloopa.com/src/{fundamental_id})
