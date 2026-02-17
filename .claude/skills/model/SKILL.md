---
name: model
description: Build a multi-tab Excel financial model
argument-hint: TICKER
---

Build a comprehensive Excel financial model (.xlsx) for the company specified by the user: $ARGUMENTS

**Before starting, read `.claude/skills/data-access.md` to determine whether to use MCP tools or API recipe scripts for data access.** Follow its detection logic and use the appropriate method throughout this skill.

This skill gathers all available financial data and builds a multi-tab Excel model from scratch using openpyxl.

## Phase 1 — Company Setup
Look up the company by ticker. Note company_id, full name, latest available quarter.
Run `python infra/market_data.py quote {TICKER}` for price, market cap, shares outstanding, beta.
Run `python infra/market_data.py multiples {TICKER}` for current trading multiples.

## Phase 2 — Comprehensive Data Pull
Pull as much data as Daloopa has for this company. Target 8-16 quarters.

**Income Statement — search and pull all available:**
- Revenue / Net Sales
- Cost of Revenue / COGS
- Gross Profit
- Research & Development
- Selling, General & Administrative
- Total Operating Expenses
- Operating Income
- Interest Expense / Income
- Pre-tax Income
- Tax Expense
- Net Income
- Diluted EPS
- Diluted Shares Outstanding
- EBITDA (or compute from Op Income + D&A)
- D&A

**Balance Sheet — search and pull all available:**
- Cash and Equivalents
- Short-term Investments
- Accounts Receivable
- Inventory
- Total Current Assets
- PP&E (net)
- Goodwill
- Total Assets
- Accounts Payable
- Short-term Debt
- Long-term Debt
- Total Liabilities
- Total Equity

**Cash Flow — search and pull all available:**
- Operating Cash Flow
- Capital Expenditures
- Depreciation & Amortization
- Acquisitions
- Dividends Paid
- Share Repurchases
- Free Cash Flow (compute if not direct)

**Segments:**
- Revenue by segment
- Operating income by segment (if available)

**KPIs:**
- All company-specific operating metrics

**Guidance:**
- All guidance series and corresponding actuals

## Phase 3 — Market Data & Peers
- Get peer multiples: identify 5-8 peers, run `python infra/market_data.py peers {PEER1} {PEER2} ...`
- Get risk-free rate: `python infra/market_data.py risk-free-rate`

## Phase 4 — Projections
Build forward estimates. If projection engine is available:
1. Write historical data to `reports/.tmp/{TICKER}_model_input.json`
2. Run: `python infra/projection_engine.py --context reports/.tmp/{TICKER}_model_input.json --output reports/.tmp/{TICKER}_model_projections.json`
3. Read projections

If not available, project manually:
- Revenue: guidance + decay to long-term growth
- Margins: mean-revert to trailing averages
- CapEx, D&A, tax rate, share count: trailing trends

Project 4-8 quarters forward.

## Phase 5 — DCF Inputs
Calculate:
- WACC (CAPM: Rf + Beta × ERP; cost of debt from interest/debt)
- 5-year FCF projections (annualized from quarterly)
- Terminal value (perpetuity growth at 2.5-3%)
- Sensitivity matrix: WACC (7 values) × terminal growth (6 values)

## Phase 6 — Build Excel Model
Write the complete context to `reports/.tmp/{TICKER}_model_context.json`, then run:
`python infra/excel_builder.py --context reports/.tmp/{TICKER}_model_context.json --output reports/{TICKER}_model.xlsx`

The context JSON should include ALL of these sections (each optional — the builder handles missing data):
```json
{
  "company": {name, ticker, exchange, currency},
  "market_data": {price, market_cap, shares_outstanding, beta, trailing_pe, forward_pe, ev_ebitda, ...},
  "periods": ["2023Q1", ...],
  "projected_periods": ["2026Q1", ...],
  "income_statement": {"Revenue": {"2023Q1": value, ...}, ...},
  "balance_sheet": {"Total Assets": {...}, ...},
  "cash_flow": {"Operating Cash Flow": {...}, ...},
  "segments": {"Revenue by Segment": {"iPhone": {...}, ...}},
  "kpis": {"Metric Name": {...}, ...},
  "guidance": {"series": {...}, "actuals": {...}},
  "projections": {"Revenue": {...}, ...},
  "projection_assumptions": {revenue_growth, gross_margin, op_margin, capex_pct_revenue, tax_rate, buyback_rate_qoq},
  "dcf": {wacc, terminal_growth, risk_free_rate, equity_risk_premium, projected_fcf, terminal_value, enterprise_value, implied_share_price, sensitivity},
  "comps": {"peers": [{ticker, name, trailing_pe, ev_ebitda, ...}, ...]}
}
```

If the Excel builder fails, report the error. The context JSON is still saved for debugging.

## Output
Tell the user:
- Where the .xlsx was saved: `reports/{TICKER}_model.xlsx`
- Where the context JSON was saved: `reports/.tmp/{TICKER}_model_context.json`
- Summary of what tabs were built
- Key model outputs: trailing revenue, projected revenue growth, implied DCF value, peer-implied range
- Remind user that yellow cells in the Projections tab are editable inputs

All financial figures gathered must use Daloopa citation format: [$X.XX million](https://daloopa.com/src/{fundamental_id})
