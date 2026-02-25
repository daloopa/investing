---
name: capital-allocation
description: Deep dive into capital deployment, buybacks, dividends, and shareholder yield
argument-hint: TICKER
---

Perform a deep dive into capital allocation for the company specified by the user: $ARGUMENTS

**Before starting, read the `data-access.md` reference (co-located with this skill) for data access methods and `design-system.md` for formatting conventions.** Follow the data access detection logic and design system throughout this skill.

Follow these steps:

## 1. Company Lookup
Look up the company by ticker. Note the company_id, full name, and latest available quarter.

## 2. Market Data
Get the current stock price, market cap, and shares outstanding for {TICKER} (see data-access.md Section 2 for how to source market data in your environment).
- This is needed to compute yields and per-share metrics

If market data is unavailable, note that market-derived metrics (yields, etc.) cannot be computed and proceed with Daloopa data only.

## 3. Capital Allocation Data
Pull 8 quarters of:

**Share Count & Buybacks:**
- Diluted shares outstanding
- Share repurchase amounts (dollars)
- Shares retired/repurchased (units, if available)

**Dividends:**
- Dividends per share
- Total dividend payments
- Special dividends (if any)

**Cash Flow:**
- Operating Cash Flow
- Capital Expenditures
- Free Cash Flow (compute as OCF - CapEx, label "(calc.)")
- D&A (for reference)

**Balance Sheet:**
- Cash and equivalents
- Short-term investments / marketable securities
- Total debt (short + long term)
- Net debt (compute as Total Debt - Cash - Investments, label "(calc.)")

**M&A / Investments:**
- Search for "acquisition", "purchase of business", "investment" in series
- Pull any available M&A-related series

## 4. Compute Capital Allocation Metrics
Calculate for each quarter where data is available:

**Shareholder Returns:**
- Total Buyback Amount
- Total Dividend Amount
- Total Shareholder Return = Buybacks + Dividends
- Shareholder Yield = (Buybacks + Dividends) / Market Cap (annualized)
- Buyback Yield = Buybacks / Market Cap (annualized)
- Dividend Yield = Dividends / Market Cap (annualized)

**FCF Deployment:**
- FCF Payout Ratio = Total Shareholder Return / FCF
- CapEx as % of Revenue
- CapEx as % of OCF
- FCF Margin = FCF / Revenue

**Leverage:**
- Net Debt / EBITDA (if EBITDA available; compute from Operating Income + D&A if needed)
- Net Debt / Equity
- Interest Coverage = Operating Income / Interest Expense (if available)
- Cash as % of Market Cap

**Share Count Dynamics:**
- QoQ share count change
- YoY share count change
- Implied buyback rate (QoQ % reduction)
- At current buyback rate, years to retire X% of shares

## 5. Qualitative Research
Search SEC filings for capital allocation strategy and context. Try multiple searches:
- **Buyback program**: Try "repurchase program", "share repurchase"; fallback to "buyback", "authorization"
- **Dividend policy**: Try "dividend", "capital return"; fallback to "distribution", "payout"
- **M&A strategy**: Try "acquisition", "strategic"; fallback to "purchase", "investment"
- **Capital priorities**: Try "capital allocation", "priorities"; fallback to "deploy", "balance sheet"
- **Debt management**: Try "debt", "refinance"; fallback to "leverage", "maturity"

Extract:
- Board-authorized buyback programs (remaining authorization amount)
- Dividend policy (commitment to growth, payout ratio targets)
- M&A philosophy (bolt-on vs transformational, deal pipeline commentary)
- Management's stated capital allocation framework and priorities
- Any changes in capital allocation strategy
- Direct quotes with document citations

## 6. Historical Analysis & Value Judgment
Analyze the 8-quarter trend:
- Is buyback activity accelerating or decelerating?
- Is the company buying back more shares when price is lower (disciplined) or higher (less disciplined)?
- Dividend growth rate (if applicable)
- Shift between CapEx, buybacks, dividends, and debt repayment over time
- FCF conversion trend (is more/less of OCF converting to FCF?)

**Honestly assess whether capital allocation is creating or destroying value:**
- If the company is buying back stock at all-time-high prices with deteriorating fundamentals, call it value destruction — even if EPS looks better from the lower share count.
- If the company is under-investing in CapEx or R&D to fund buybacks, flag the risk to long-term competitiveness.
- If FCF payout ratio exceeds 100%, the company is funding returns with debt or cash drawdowns — flag this as unsustainable.
- Compare the implied return from buybacks (inverse of P/E at purchase prices) to what the company could earn from organic reinvestment or M&A.

## 7. Save Report
Save to `reports/{TICKER}_capital_allocation.md`. Format:

```
# {Company Name} ({TICKER}) — Capital Allocation Analysis
Generated: {date}

## Summary
{2-3 sentences: How does this company deploy its capital? Key takeaways.}

## Current Snapshot
| Metric | Value |
|---|---|
| Market Cap | $XXX |
| Trailing 4Q FCF | $XXX |
| FCF Yield | X.X% |
| Shareholder Yield | X.X% |
| Net Debt / EBITDA | X.Xx |
| Remaining Buyback Authorization | $XXX |

## Cash Flow & FCF (8 Quarters)
| Metric | Q1 | Q2 | ... | Q8 |
{OCF, CapEx, FCF, FCF Margin % — with Daloopa citations}

## Share Repurchases & Dividends (8 Quarters)
| Metric | Q1 | Q2 | ... | Q8 |
{Buyback $, Dividends $, Total Return, Share Count — with Daloopa citations}

## Shareholder Yield Analysis
| Metric | Q1 | Q2 | ... | Q8 |
{Buyback Yield, Div Yield, Total Yield, FCF Payout Ratio}

## Leverage & Balance Sheet (8 Quarters)
| Metric | Q1 | Q2 | ... | Q8 |
{Cash, Debt, Net Debt, Net Debt/EBITDA — with Daloopa citations}

## Capital Allocation Framework
{Management's stated priorities from filings, with document citations}

## Buyback Discipline Analysis
{Analysis of buyback timing vs price, share count reduction trend, authorization remaining}

## M&A Activity
{Any acquisitions from filings, deal sizes, strategic rationale}

## Key Observations
- {3-5 bullet points on capital allocation quality, trends, and implications}

Data sourced from Daloopa
```

All financial figures must use Daloopa citation format: [$X.XX million](https://daloopa.com/src/{fundamental_id})

Tell the user where the report was saved and highlight the key capital allocation story (e.g., "AAPL returned $XX billion to shareholders over the last year, a X.X% shareholder yield, with buybacks accelerating").
