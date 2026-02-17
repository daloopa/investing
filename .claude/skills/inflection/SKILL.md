---
name: inflection
description: Auto-detect biggest acceleration/deceleration inflections across all metrics
argument-hint: TICKER
---

Detect the biggest financial and operating inflections for the company specified by the user: $ARGUMENTS

**Before starting, read `.claude/skills/data-access.md` to determine whether to use MCP tools or API recipe scripts for data access.** Follow its detection logic and use the appropriate method throughout this skill.

Follow these steps:

## 1. Company Lookup
Look up the company by ticker. Note the company_id, full name, and latest available quarter.

## 2. Broad Series Discovery
Cast a wide net to discover ALL available series for this company. Search with multiple keyword sets to maximize coverage:
- Financial: "revenue", "income", "profit", "margin", "eps", "cash flow"
- Operating: "subscriber", "user", "customer", "unit", "arpu", "retention"
- Segment: "segment", "product", "service", "geographic"
- Balance sheet: "debt", "asset", "equity", "cash"
- Other: "backlog", "bookings", "pipeline", "store", "employee"

Collect all unique series IDs. The goal is comprehensiveness — capture every metric Daloopa tracks for this company.

## 3. Pull 8 Quarters of Data
Pull the last 8 quarters for ALL discovered series. This gives enough history to compute both QoQ and YoY rates plus their second derivatives.

## 4. Compute Growth Rates and Inflections
For each series with sufficient data (at least 5 quarters):

**YoY Growth Rate** for each quarter:
- growth_t = (value_t - value_{t-4}) / |value_{t-4}|

**YoY Acceleration (second derivative):**
- accel_t = growth_t - growth_{t-1}
- Positive = accelerating, Negative = decelerating

**QoQ Sequential Growth** (for non-seasonal metrics):
- seq_growth_t = (value_t - value_{t-1}) / |value_{t-1}|

**QoQ Acceleration:**
- seq_accel_t = seq_growth_t - seq_growth_{t-1}

Skip series where values are too small (< 1% of revenue) or where data is sparse. For margin/ratio series (values between 0-1 or percentages), compute change in basis points rather than % change.

## 5. Rank Inflections
Rank all series by the magnitude of their most recent acceleration/deceleration:

**Top 10 Accelerating** — series with the largest positive acceleration in the most recent quarter. These are metrics that are improving faster than before.

**Top 10 Decelerating** — series with the largest negative acceleration (or deceleration). These are metrics where momentum is fading.

For each inflection, note:
- Series name
- Most recent value (with Daloopa citation)
- Current YoY growth rate
- Prior-quarter YoY growth rate
- Acceleration (the delta)
- Whether this is a new trend (1Q) or sustained (2-3Q in same direction)

## 6. Contextualize Key Inflections
For the top 5 most significant inflections (by magnitude and importance to the business):
- Search SEC filings for context on what's driving the change
- Try keywords related to the specific metric (e.g., if "Services Revenue" is accelerating, search for "services", "subscription", "recurring")
- Extract management commentary explaining the inflection
- Note whether the inflection aligns with or contradicts management guidance

## 7. Synthesize
Identify the narrative:
- Is the company broadly accelerating or decelerating?
- Are there divergent trends (e.g., revenue accelerating but margins decelerating)?
- Which inflections matter most for the investment case?
- Are operating KPIs leading or lagging the financial inflections?

## 8. Save Report
Save to `reports/{TICKER}_inflection.md`. Format:

```
# {Company Name} ({TICKER}) — Inflection Analysis
Generated: {date}

## Summary
{2-3 sentence overview: Is the company accelerating, decelerating, or mixed? What are the most important inflections?}

## Top Accelerating Metrics
| Rank | Metric | Latest Value | YoY Growth | Prior YoY Growth | Acceleration | Trend |
{table with Daloopa citations}

## Top Decelerating Metrics
| Rank | Metric | Latest Value | YoY Growth | Prior YoY Growth | Deceleration | Trend |
{table with Daloopa citations}

## Key Inflection Deep Dives

### 1. {Metric Name} — {Accelerating/Decelerating}
{Context from filings, management commentary, what's driving it}

### 2. {Metric Name} — {Accelerating/Decelerating}
{...}

{repeat for top 5}

## Divergences & Signals
{Analysis of divergent trends, leading indicators, and implications}

## Inflection Heatmap
| Metric | Q(-3) YoY | Q(-2) YoY | Q(-1) YoY | Q(latest) YoY | Direction |
{visual trend using arrows or labels: Accelerating / Steady / Decelerating}

Data sourced from Daloopa
```

All financial figures must use Daloopa citation format: [$X.XX million](https://daloopa.com/src/{fundamental_id})

Tell the user where the report was saved and highlight the 2-3 most notable inflections and what they signal.
