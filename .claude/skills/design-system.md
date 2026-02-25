# Design System

Shared formatting and styling reference for all skills. Follow these conventions for every output — markdown reports, PDF, Word documents, and decks.

## Number Formatting

| Type | Format | Example |
|------|--------|---------|
| Currency (large) | `$X.Xbn` or `$X,XXXmm` | `$95.4bn`, `$2,345mm` |
| Currency (small) | `$X.XX` or `$X,XXX` | `$6.08`, `$1,234` |
| Percentages | One decimal + `%` suffix | `42.3%` |
| Multiples | One decimal + `x` suffix | `8.5x EV/EBITDA` |
| Growth rates | Signed + `%` suffix + context | `+12.3% YoY` |
| Basis points | Signed + `bps` | `+150bps` |
| Share counts | `X.XXbn` or `X,XXXmm` shares | `15.33bn shares` |

Right-align all numbers in tables. Never display raw unformatted numbers.

## Analytical Density

Every data point should include three layers where possible:

1. **The data point itself** — with Daloopa citation
2. **Context** — vs. prior period, vs. peers, vs. guidance, vs. consensus
3. **Implication** — what it suggests (margin expansion, deceleration, thesis risk)

Example:
> Revenue: [$95.4bn](https://daloopa.com/src/123) (+6.1% YoY, beat consensus by +2.3%) — acceleration from +4.8% last quarter driven by iPhone 16 cycle

Avoid single-metric tables. Combine related metrics: Revenue + Revenue Growth + Gross Margin in one table.

## Table Conventions

- **Columns** = time periods (left to right, chronological)
- **Rows** = metrics (grouped by category: P&L, margins, per-share, balance sheet)
- Include YoY growth rates as sub-rows in italics
- Highlight beats/misses with notation: `$1.52 (beat +3.2%)`
- Source citation row at bottom of every table: `Source: Daloopa (company filings)`
- Group related metrics together — no single-metric tables

## Commentary Blocks

After every major data table, include a 2-3 sentence interpretive commentary block:

1. **What the data shows** — trend, inflection, anomaly
2. **Why it matters** — competitive positioning, estimate revision risk, thesis confirmation/challenge
3. **What to watch** — upcoming catalyst, guidance change, peer divergence
4. **What could go wrong** — risks to the trend, bear case interpretation, sustainability concerns

## Analyst's Perspective

All analysis is written from the perspective of a **long/short equity investor** conducting fundamental research. This means:

**Be critical, not promotional.** Management narratives are marketing until proven by the data. When results look good, ask: Is this sustainable? Is it one-time? Is the market already pricing it in? When trends look bad, ask: Is this cyclical or structural? Is management acknowledging the problem or hiding behind adjusted metrics?

**Challenge the numbers.** Look for quality-of-earnings issues: revenue pulled forward, unsustainable margin drivers (e.g., under-investing in R&D, favorable one-time items), channel stuffing signals, aggressive accounting changes. A beat isn't bullish if it's low-quality.

**Be honest about valuation.** Don't anchor to the current stock price and work backwards. If a DCF implies 50% upside, say so — but also say what has to go right. If a stock trades at 40x earnings with decelerating growth, say that's expensive. The analysis should help the reader decide whether to own the stock, not confirm whatever they already believe.

**Flag red flags explicitly.** When you see concerning patterns — deteriorating cash conversion, growing gap between GAAP and non-GAAP, rising DSOs, management selling stock, guidance cuts disguised as "conservatism," buybacks at all-time highs — call them out clearly.

**Assign conviction.** Don't hide behind balanced language when the data points in a clear direction. If the bear case is more likely, say so. If growth is clearly decelerating, don't soften it with "remains resilient." Use precise language: "decelerating," "deteriorating," "unsustainable," "mispriced" when warranted.

**Separate signal from noise.** Not every data point matters equally. Highlight what changes the thesis and deprioritize what doesn't. A 10bps margin fluctuation is noise; a 300bps margin decline is signal.

## Report Structure

- **Header**: Company name, ticker, date
- **Executive summary first**: 3-5 key takeaways, each one sentence
- **Daloopa citations on every financial figure** — no uncited numbers
- **"Data sourced from Daloopa" footer** on every report
- Section ordering follows each skill's defined structure

## Color Palette

Consistent across charts, PDF, deck, and model:

| Role | Color | Hex |
|------|-------|-----|
| Primary | Navy | `#1B2A4A` |
| Secondary | Steel Blue | `#4A6FA5` |
| Accent | Gold | `#C5A55A` |
| Positive | Forest Green | `#27AE60` |
| Negative | Crimson | `#C0392B` |
| Light Gray | — | `#F8F9FA` |
| Mid Gray | — | `#E9ECEF` |
| Dark Gray | — | `#6C757D` |
| Near Black | — | `#343A40` |

Chart color sequence: Navy, Steel Blue, Gold, then grays.

## Chart Styling

All charts follow these rules:
- Grid lines: light gray (`#E9ECEF`), no box border
- Labels: 11px, gray (`#6C757D`)
- Title: 14px bold, navy
- Source citation below every chart: `Source: Daloopa (company filings)`
- Adjacent commentary block required for every chart

Standard chart types:
1. **Time-series** — Revenue, margins, EPS, KPIs over quarters. Bar + line combo.
2. **Waterfall** — Bridge from base to target value (revenue walk, value creation, EPS bridge)
3. **Football field** — Horizontal range bars comparing valuation methodologies
4. **Pie** — Segment revenue/profit breakdown, geographic mix
5. **Scenario bar** — Bull/base/bear comparison
6. **DCF sensitivity** — WACC vs terminal growth heatmap

## Typography (Rendered Outputs — PDF, Deck, Docx)

- Primary font: system sans-serif stack (Segoe UI, -apple-system, Arial)
- Headers: bold, 18-28px, navy (`#1B2A4A`)
- Body: 12-13px, dark gray (`#343A40`)
- Table cells: 11px, tabular-nums for number alignment
- Citations: 8-9px italic
- Slide content (deck): 11-14px with generous line-height
