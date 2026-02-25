---
name: dcf
description: Discounted cash flow valuation with sensitivity analysis
argument-hint: TICKER
---

Build a discounted cash flow (DCF) valuation for the company specified by the user: $ARGUMENTS

**Before starting, read the `data-access.md` reference (co-located with this skill) for data access methods and `design-system.md` for formatting conventions.** Follow the data access detection logic and design system throughout this skill.

Follow these steps:

## 1. Company Lookup
Look up the company by ticker. Note the company_id, full name, and latest available quarter.

## 2. Market Data
Get market-side inputs for {TICKER} (see data-access.md Section 2 for how to source market data in your environment):
- Current price, market cap, shares outstanding, beta
- 10Y Treasury yield (risk-free rate for WACC)

If market data is unavailable, use reasonable defaults: beta=1.0, risk-free rate=4.5%, and note the assumptions.

## 3. Historical Financials from Daloopa
Pull 8 quarters of:
- Revenue
- Operating Income
- Net Income
- Diluted EPS
- Operating Cash Flow
- Capital Expenditures
- Free Cash Flow (compute as OCF - CapEx, label "(calc.)")
- Depreciation & Amortization
- Tax expense and pre-tax income (for effective tax rate)
- Interest expense (for cost of debt)
- Total debt (short + long term)
- Cash and equivalents
- Shares outstanding

Also pull segment revenue and any available guidance series.

## 4. Calculate WACC

**Cost of Equity (CAPM):**
- Risk-free rate (Rf) = 10Y Treasury from market data
- Equity risk premium (ERP) = 5.5% (standard assumption)
- Beta from market data (or 1.0 default)
- Cost of equity = Rf + Beta × ERP

**Cost of Debt:**
- If interest expense and total debt available: Cost of debt = Interest Expense / Average Total Debt
- After-tax cost of debt = Cost of debt × (1 - effective tax rate)
- If not available, use 5.0% pre-tax as default

**Capital Structure:**
- Market cap for equity weight
- Total debt for debt weight
- WACC = (E/V) × Re + (D/V) × Rd × (1-t)

Show all inputs and the resulting WACC clearly.

## 5a. KPI-Driven Revenue Build (Preferred)

Before projecting top-down, attempt a bottoms-up revenue build using operational KPIs. This produces a significantly more defensible DCF — a top-down trend decay is a guess; a bottoms-up KPI build is analysis.

**Discover segment and KPI data:**
Pull segment revenue breakdown + segment-specific KPIs for the target company. Use the sector taxonomy to know what to search for:

- **SaaS/Cloud**: ARR, net revenue retention, RPO/cRPO, customers >$100K, cloud gross margin
- **Consumer Tech**: DAU/MAU, ARPU, engagement metrics, installed base, paid subscribers
- **E-commerce/Marketplace**: GMV, take rate, active buyers/sellers, order frequency
- **Retail**: same-store sales, store count, average ticket, transactions
- **Telecom/Media**: subscribers, churn, ARPU, content spend
- **Hardware**: units shipped, ASP, attach rate, installed base
- **Financial Services**: AUM, NIM, loan growth, credit quality metrics, fee income ratio
- **Pharma/Biotech**: pipeline stage, patient starts, scripts, market share
- **Industrials/Energy**: backlog, book-to-bill, utilization, production volumes, reserves

**Build bottoms-up projections per segment:**
For each segment with KPI data, project revenue using unit economics:
- Hardware segments: projected units × projected ASP
- Subscription segments: projected subscribers × projected ARPU (net of churn)
- Marketplace segments: projected GMV × projected take rate
- Services/recurring: apply growth rate informed by retention metrics and customer adds

Sum segment projections to get total revenue for each of 5 years. Show the build clearly so the reader can challenge individual segment assumptions.

**Fall back to top-down if KPIs aren't available.** If segment KPIs are sparse or unavailable, use the top-down approach in Section 5b instead, but note explicitly that the model is less reliable without bottoms-up drivers.

## 5b. Top-Down FCF Projections (Fallback)

Build 5-year FCF projections. If a projection engine is available (see data-access.md Section 5), use it. Otherwise, project manually:
- **Revenue:** Use management guidance for near-term, then decay toward 3% long-term growth
- **FCF Margin:** Use trailing average, adjust for any clear trends
- **FCF = Projected Revenue × Projected FCF Margin**

Show all assumptions clearly — this is the most judgment-intensive part. If using this fallback instead of the KPI-driven build (Section 5a), note the limitation.

## 6. Terminal Value
Calculate terminal value using perpetuity growth method:
- Terminal FCF = Year 5 FCF × (1 + terminal growth rate)
- Terminal Value = Terminal FCF / (WACC - terminal growth rate)
- Default terminal growth rate: 2.5-3.0% (should not exceed long-term GDP growth)
- Discount terminal value to present

## 7. Compute Implied Valuation
- Sum of PV of projected FCFs + PV of terminal value = Enterprise Value
- Equity Value = Enterprise Value - Net Debt
- Implied Share Price = Equity Value / Shares Outstanding
- Compare to current market price: upside/downside %

Also compute:
- Implied EV/EBITDA (Enterprise Value / Trailing EBITDA)
- Implied P/E (Equity Value / Trailing Net Income)
- Terminal value as % of total value (flag if > 80% — this means the DCF is very sensitive to terminal assumptions)

## 8. Sensitivity Analysis
Build a sensitivity table varying two key inputs:

**WACC (rows):** Base WACC ± 2% in 0.5% increments (7 rows)
**Terminal Growth Rate (columns):** 1.5% to 4.0% in 0.5% increments (6 columns)

Each cell = implied share price at that WACC/growth combination.
Highlight the base case cell and the current market price for reference.

Also show a secondary sensitivity: Revenue Growth vs FCF Margin if data supports it.

## 9. Consensus Sanity Check (if available)
If consensus estimates are available (see data-access.md Section 3):
- Compare your projected revenue/EPS path to consensus for the next 1-2 years
- Note where your DCF assumptions diverge from Street expectations
- If your implied price is significantly above/below consensus target, explain why

If consensus data is not available, skip this check.

## 10. Sanity Checks & Self-Challenge
Flag any issues:
- If implied price is >2x or <0.5x current price, note that the DCF produces an extreme result and examine assumptions
- If terminal value is >85% of total value, the model is highly sensitive to terminal assumptions
- If WACC < risk-free rate or > 15%, the capital structure inputs may be off
- Compare implied multiples to historical trading range

**Challenge your own assumptions — don't anchor to the current price:**
- Build the DCF from fundamentals first, THEN compare to market price. Don't work backwards from the current price to justify assumptions.
- If your base case revenue growth assumes continuation of recent trends, stress-test: what if growth mean-reverts to the industry average? What if the current cycle peaks?
- Explicitly state what has to go right for the bull case implied price and what has to go wrong for the bear case.
- If the DCF only "works" with aggressive terminal growth or unrealistically low WACC, say so — the stock may simply be expensive on fundamentals.

## 11. Save Report
Save to `reports/{TICKER}_dcf.md`. Format:

```
# {Company Name} ({TICKER}) — DCF Valuation
Generated: {date}

## Summary
| Metric | Value |
|---|---|
| Current Price | $XXX |
| Implied Share Price | $XXX |
| Upside / Downside | +X.X% / -X.X% |
| WACC | X.X% |
| Terminal Growth | X.X% |
| Terminal Value % of Total | XX% |

## WACC Calculation
| Component | Value | Source |
|---|---|---|
| Risk-Free Rate | X.X% | FRED 10Y Treasury |
| Equity Risk Premium | 5.5% | Standard assumption |
| Beta | X.XX | Market data |
| Cost of Equity | X.X% | CAPM |
| Cost of Debt (after-tax) | X.X% | Interest/Debt × (1-t) |
| Equity Weight | XX% | Market cap |
| Debt Weight | XX% | Total debt |
| **WACC** | **X.X%** | |

## Historical Free Cash Flow (8 Quarters)
| Metric | Q1 | Q2 | ... | Q8 |
{OCF, CapEx, FCF, FCF Margin — with Daloopa citations}

## FCF Projections (5 Years)
| Metric | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 |
{Revenue, FCF Margin, FCF — with assumptions noted}

## Valuation Bridge
| Component | Value |
|---|---|
| PV of Projected FCFs | $XXX |
| PV of Terminal Value | $XXX |
| Enterprise Value | $XXX |
| Less: Net Debt | ($XXX) |
| Equity Value | $XXX |
| Shares Outstanding | XXX |
| **Implied Share Price** | **$XXX** |

## Sensitivity Table: WACC vs Terminal Growth
| WACC \ Growth | 1.5% | 2.0% | 2.5% | 3.0% | 3.5% | 4.0% |
{matrix of implied share prices, base case bolded}

Current market price: $XXX for reference.

## Key Assumptions & Risks
- {List all key assumptions and what could invalidate them}

## Sanity Checks
- {Implied multiples vs historical, terminal value concentration, etc.}

Data sourced from Daloopa
```

All financial figures must use Daloopa citation format: [$X.XX million](https://daloopa.com/src/{fundamental_id})

## 12. Render PDF
Render the markdown report to PDF (see data-access.md Section 5 for infrastructure):
`python3 infra/pdf_renderer.py --input reports/{TICKER}_dcf.md --output reports/{TICKER}_dcf.pdf`

Tell the user where the PDF was saved. If PDF rendering fails, note the error and point them to the markdown file.

Summarize: implied price vs current price, key upside/downside drivers, and the biggest sensitivity.
