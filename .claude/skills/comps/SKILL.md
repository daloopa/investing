---
name: comps
description: Trading comparables analysis with peer multiples and implied valuation
argument-hint: TICKER
---

Build a trading comparables analysis for the company specified by the user: $ARGUMENTS

**Before starting, read `.claude/skills/data-access.md` to determine whether to use MCP tools or API recipe scripts for data access.** Follow its detection logic and use the appropriate method throughout this skill.

Follow these steps:

## 1. Company Lookup
Look up the company by ticker. Note the company_id, full name, and latest available quarter.

## 2. Identify Peer Group
Based on the company's business model, sector, size, and competitive landscape, identify 5-10 comparable companies. Consider:
- **Direct competitors** in the same market
- **Business model peers** (similar revenue model even if different sector)
- **Size peers** (similar market cap range)
- **Growth profile peers** (similar growth rate)

Prioritize relevance over size matching. A direct competitor at a different scale is more useful than a similar-sized company in a different industry.

List the peer tickers and briefly justify each selection (1 sentence).

## 3. Target Company Fundamentals
Pull from Daloopa for the target company (last 4 quarters):
- Revenue (compute trailing 4Q total)
- EBITDA (compute trailing 4Q; if not available, use Op Income + D&A, label "(calc.)")
- Net Income (trailing 4Q)
- Diluted EPS (trailing 4Q sum)
- Free Cash Flow (trailing 4Q; compute as OCF - CapEx, label "(calc.)")
- Revenue YoY growth (most recent quarter)
- Operating Margin (most recent quarter)
- Net Margin (most recent quarter)

## 4. Peer Market Multiples
For each peer, run:
- `python infra/market_data.py multiples {PEER_TICKER}` — P/E, EV/EBITDA, P/S, P/B, div yield, PEG ratio
- `python infra/market_data.py quote {PEER_TICKER}` — price, market cap

If market data scripts aren't available, note that peer multiples cannot be sourced and provide a framework for manual completion.

If a peer ticker fails (delisted, no data), drop it and note why.

## 5. Peer Fundamentals from Daloopa
For each peer that is available in Daloopa:
- Look up the company
- Pull trailing 4Q revenue, operating income, net income
- Compute revenue growth YoY, operating margin, net margin

For peers not in Daloopa, rely on yfinance multiples only and note the data source limitation.

## 6. Build Comps Table
Create the main comparables table with these columns:
| Company | Ticker | Mkt Cap | EV | P/E | Fwd P/E | EV/EBITDA | P/S | Rev Growth | Op Margin | Net Margin | FCF Yield |

Sort by market cap descending. Include:
- **Peer median** row
- **Peer mean** row
- **Target company** row (highlighted / separated)
- Target's percentile rank within the peer group for each metric

## 7. Implied Valuation
Apply peer group median and mean multiples to the target's fundamentals:

| Methodology | Peer Median Multiple | Target Metric | Implied Value |
|---|---|---|---|
| P/E | XX.Xx | $X.XX EPS | $XXX |
| EV/EBITDA | XX.Xx | $XXX EBITDA | $XXX |
| P/S | XX.Xx | $XXX Revenue | $XXX |
| FCF Yield | X.X% | $XXX FCF | $XXX |

For each:
- Implied Enterprise Value = Multiple × Target's Metric
- Implied Equity Value = EV - Net Debt (for EV-based multiples) or direct (for equity multiples)
- Implied Share Price = Equity Value / Shares Outstanding

Compute range (min to max implied price) and central tendency.

## 8. Premium/Discount Analysis
Assess whether the target trades at a premium or discount to peers:
- For each multiple, show target vs peer median as a % premium/discount
- Consider whether a premium/discount is justified based on:
  - Growth differential (higher growth = deserves premium)
  - Margin differential (higher margins = deserves premium)
  - Market position (leader vs challenger)
  - Risk profile

## 9. Save Report
Save to `reports/{TICKER}_comps.md`. Format:

```
# {Company Name} ({TICKER}) — Comparable Companies Analysis
Generated: {date}

## Summary
{2-3 sentences: Where does the company trade relative to peers? Is it cheap or expensive and why?}

## Peer Group Selection
| Peer | Ticker | Rationale |
{table with justification for each peer}

## Comparables Table
| Company | Ticker | Mkt Cap | P/E | Fwd P/E | EV/EBITDA | P/S | Rev Growth | Op Margin |
{full comps table with target highlighted}
| **Peer Median** | | | XX.Xx | XX.Xx | XX.Xx | XX.Xx | X.X% | X.X% |
| **Peer Mean** | | | XX.Xx | XX.Xx | XX.Xx | XX.Xx | X.X% | X.X% |
| **{TICKER}** | | | **XX.Xx** | **XX.Xx** | **XX.Xx** | **XX.Xx** | **X.X%** | **X.X%** |

## Target vs Peer Premium/Discount
| Multiple | Target | Peer Median | Premium/Discount |
{table showing where target is rich/cheap}

## Implied Valuation
| Methodology | Multiple | Target Metric | Implied Price | vs Current |
{table with implied values}

| **Valuation Range** | **Low** | **Median** | **High** |
| Implied Price | $XXX | $XXX | $XXX |
| vs Current Price | -X% | +X% | +X% |

## Premium/Discount Justification
{Analysis of whether current premium/discount is warranted}

## Key Observations
- {3-5 bullet points on relative valuation, standout metrics, peer group dynamics}

Data sourced from Daloopa
```

All financial figures from Daloopa must use citation format: [$X.XX million](https://daloopa.com/src/{fundamental_id})

Tell the user where the report was saved and highlight: where the stock trades relative to peers (premium/discount), the implied valuation range, and the most relevant multiple for this company.
