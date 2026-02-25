---
name: equity-note
description: This skill should be used when the user asks to "write a research note", "generate an equity note", "create a company note", "build a stock note", "deep dive note", "equity research note", "stock analysis note", "write a note on [ticker]", "note on [company]", or needs a comprehensive single-stock equity research document. Also triggers on requests mentioning "research note", "equity note", "stock note", "company deep dive", "deep dive analysis", or "equity analysis" for any company ticker. Use this for any research note request — it is the primary equity research note generator.
---

This skill generates a professional, institutional-grade equity research note as a self-contained HTML document. The note combines deep fundamental financial data from Daloopa MCP with qualitative research from web search and SEC filing analysis.

The output matches the analytical depth of a buy-side research note at a top-tier long/short equity fund — information-dense, every financial figure hyperlinked to its Daloopa source, and structured around the key question: "What do I need to believe to buy or short this stock?"

## Output Format

The final deliverable is a **single self-contained HTML file** with:
- Embedded CSS (no external dependencies)
- Print-to-PDF support via `@media print` styles
- A "Download as PDF" button at the top (uses `window.print()`)
- All financial figures hyperlinked to Daloopa source citations
- Professional WSJ/financial newspaper aesthetic

Write the file to `~/Generated Stuff/[TICKER]-note.html` (or user-specified location), then open it with `open`.

---

## RESEARCH WORKFLOW

This is a multi-phase research process. Do NOT skip phases or produce shallow analysis. Each phase builds on the previous one. Maximize parallelism across independent API calls.

### Phase 1: Company Identification & Scoping

1. Use `discover_companies` with the ticker symbol to get the `company_id`, `latest_calendar_quarter`, and `latest_fiscal_quarter`.
2. Determine the research scope:
   - **Quarters to pull**: Last 8-12 quarters (covering ~2-3 years of history)
   - **Annual periods**: Last 2-3 fiscal years
   - **Guidance periods**: Current and next fiscal year

### Phase 2: Financial Data Collection (Daloopa MCP)

Run these searches in batches using `discover_company_series` to collect series IDs, then retrieve data with `get_company_fundamentals`. Run independent searches in parallel.

**Income Statement (Priority 1):**
- Search keywords: "revenue", "net sales", "cost of goods", "gross profit", "operating income", "net income", "EPS", "diluted EPS"
- Also search: "R&D", "SG&A", "operating expense", "depreciation", "amortization", "EBITDA"

**Margins & Ratios (Priority 1):**
- Search keywords: "gross margin", "operating margin", "net margin", "EBITDA margin"

**Balance Sheet (Priority 2):**
- Search keywords: "cash", "total debt", "net debt", "total assets", "shareholders equity", "book value"

**Cash Flow (Priority 2):**
- Search keywords: "operating cash flow", "capital expenditure", "capex", "free cash flow"

**Guidance (Priority 1):**
- Search keywords: "guidance", "outlook", "forecast", "target"
- Track guidance evolution across quarters (initial → revised → latest)

**Company-Specific KPIs (Priority 1):**
- Search for industry-specific metrics relevant to the company. Examples:
  - Manufacturing/Industrial: "bookings", "backlog", "capacity", "ASP", "units shipped"
  - SaaS/Tech: "ARR", "subscribers", "net retention", "DAU", "MAU", "RPO"
  - Retail/Consumer: "same-store sales", "comp sales", "traffic", "ticket size"
  - Financials: "NIM", "net interest margin", "provision", "loan growth"
  - Healthcare: "pipeline", "patients", "scripts", "approvals"
  - Energy: "production", "reserves", "realized price", "breakeven"
- Identify the 3-5 most important operational KPIs for the company

**Segment Data (Priority 2):**
- Search keywords: "segment", "division", "product line", "geographic"

### Phase 3: Qualitative Research

Run these concurrently where possible:

**Web Search (use WebSearch tool):**
- `"[TICKER] [company name] news 2025 2026"` — recent headlines
- `"[TICKER] analyst upgrade downgrade price target"` — analyst sentiment
- `"[TICKER] catalysts risks"` — forward-looking events
- `"[company name] industry outlook [sector]"` — macro/industry context
- `"[TICKER] earnings reaction"` — market reaction to recent results
- `"[TICKER] management commentary strategy"` — strategic direction
- Search for any major company-specific events (product launches, M&A, regulatory actions, executive changes)

**Document Search (use Daloopa `search_documents`):**
- Keywords: ["guidance", "outlook"] — management's forward view
- Keywords: ["risk", "uncertainty"] — disclosed risk factors
- Keywords: ["margin", "cost", "pricing"] — cost structure commentary
- Keywords: ["capital allocation", "buyback", "dividend"] — shareholder returns
- Keywords: ["competition", "market share"] — competitive positioning
- Industry-specific keywords (e.g., ["bookings", "backlog"] for industrials, ["churn", "retention"] for SaaS)

### Phase 4: Synthesis & Analysis

Before writing the HTML, organize research into these analytical frameworks:

1. **Executive Summary**: 1 paragraph capturing the core tension/thesis. What makes this stock interesting RIGHT NOW?
2. **Five Key Tensions**: The 5 most important bull/bear debates, each in one line with color-coded sentiment (green=positive, red=negative, amber=mixed)
3. **News Timeline**: 6-10 most impactful events from the last 6-12 months, reverse chronological, with sentiment tags
4. **Financial Trends**: Identify inflection points, trajectory changes, seasonal patterns
5. **Guidance Evolution**: Track how management guidance has changed over time (raised = bullish, cut = bearish)
6. **Cost/Margin Drivers**: What's driving margin expansion or compression? Quantify the key COGS/OpEx drivers
7. **Industry-Specific Deep Dive**: The 1-2 most critical operational themes for this company
8. **Catalysts**: Organized by timeframe (0-3mo, 3-12mo, 1-3yr) with HIGH/MED/LOW priority
9. **Bull/Bear Framework**: 4-6 specific, falsifiable beliefs for each side with price targets
10. **Monitoring Checklist**: Quantitative + qualitative metrics to track going forward

---

## HTML TEMPLATE & DESIGN SYSTEM

Generate the HTML following this exact design system. The aesthetic is "Wall Street Journal meets Bloomberg terminal" — clean, professional, information-dense, no decorative elements.

### Complete CSS Design System

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @media print {
    body { margin: 0; }
    .no-print { display: none !important; }
    .page-break { page-break-before: always; }
    @page { margin: 0.6in 0.7in; size: letter; }
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1a1a1a; font-size: 9.5px; line-height: 1.5; background: #fff; }
  .container { max-width: 850px; margin: 0 auto; padding: 30px; }
  h1 { font-size: 22px; font-weight: 700; margin-bottom: 2px; }
  h2 { font-size: 13px; font-weight: 700; margin: 18px 0 8px 0; padding-bottom: 4px; border-bottom: 2px solid #111; text-transform: uppercase; letter-spacing: 0.5px; }
  h3 { font-size: 11px; font-weight: 700; margin: 12px 0 5px 0; }
  .subtitle { color: #666; font-size: 11px; margin-bottom: 4px; }
  .date { color: #999; font-size: 9px; }
  .header-row { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 3px solid #111; padding-bottom: 8px; margin-bottom: 16px; }
  .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 10px 0; }
  .kpi { border: 1px solid #ddd; border-radius: 4px; padding: 6px 8px; }
  .kpi-label { font-size: 8px; color: #888; text-transform: uppercase; letter-spacing: 0.3px; }
  .kpi-val { font-size: 13px; font-weight: 700; color: #111; }
  table { width: 100%; border-collapse: collapse; margin: 6px 0; font-size: 8.5px; }
  th { background: #f5f5f5; font-weight: 600; text-align: right; padding: 4px 5px; border-bottom: 1.5px solid #ccc; color: #444; }
  th:first-child { text-align: left; }
  td { padding: 3.5px 5px; border-bottom: 1px solid #eee; text-align: right; font-variant-numeric: tabular-nums; }
  td:first-child { text-align: left; color: #444; font-weight: 500; }
  .highlight-row { background: #f9f9f9; }
  .red { color: #c0392b; }
  .green { color: #1a8a4a; }
  .amber { color: #b8860b; }
  .bold { font-weight: 700; }
  .section-box { border: 1px solid #ddd; border-radius: 4px; padding: 10px 12px; margin: 8px 0; }
  .alert-box { border: 1.5px solid #c0392b; border-radius: 4px; padding: 10px 12px; margin: 8px 0; background: #fdf2f2; }
  .bull-box { border: 1.5px solid #1a8a4a; border-radius: 4px; padding: 10px 12px; background: #f0fdf4; }
  .bear-box { border: 1.5px solid #c0392b; border-radius: 4px; padding: 10px 12px; background: #fdf2f2; }
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .event { display: flex; gap: 8px; margin-bottom: 6px; padding-bottom: 6px; border-bottom: 1px solid #f0f0f0; }
  .event-date { font-family: 'Courier New', monospace; font-size: 8.5px; color: #888; width: 80px; flex-shrink: 0; }
  .event-tag { font-size: 7.5px; font-weight: 700; padding: 1px 5px; border-radius: 3px; display: inline-block; margin-right: 4px; }
  .tag-pos { background: #d4edda; color: #155724; }
  .tag-neg { background: #f8d7da; color: #721c24; }
  .tag-mix { background: #fff3cd; color: #856404; }
  .tag-up { background: #e2e3f1; color: #383d6e; }
  .event-title { font-weight: 600; font-size: 9px; }
  .event-desc { font-size: 8.5px; color: #666; margin-top: 1px; }
  .catalyst-item { margin-bottom: 6px; }
  .priority { font-size: 7.5px; font-weight: 700; padding: 1px 5px; border-radius: 3px; display: inline-block; margin-right: 4px; }
  .p-high { background: #f8d7da; color: #721c24; }
  .p-med { background: #fff3cd; color: #856404; }
  .p-low { background: #d4edda; color: #155724; }
  .footnote { font-size: 8px; color: #999; margin-top: 6px; font-style: italic; }
  .dl-btn { display: inline-block; padding: 12px 28px; background: #111; color: #fff; border: none; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer; margin: 20px 0; }
  .dl-btn:hover { background: #333; }
  ul { padding-left: 14px; }
  li { margin-bottom: 3px; }
  .daloopa-src { font-size: 7.5px; color: #999; }
  a { color: #2563eb; text-decoration: none; }
</style>
</head>
<body>
```

---

## DOCUMENT STRUCTURE (10 Sections)

The HTML document follows this exact section order. Every section is mandatory unless noted.

### Section 1: Print Button Bar
```html
<div class="no-print" style="text-align:center; padding: 20px; background: #f8f8f8; border-bottom: 1px solid #ddd;">
  <button class="dl-btn" onclick="window.print()">Download as PDF</button>
  <p style="font-size:12px; color:#888; margin-top:6px;">Click above or use Ctrl+P / Cmd+P &rarr; Save as PDF</p>
</div>
```

### Section 2: Header Row
```html
<div class="container">
<div class="header-row">
  <div>
    <h1>[TICKER] &mdash; [Full Company Name]</h1>
    <div class="subtitle">Deep Dive Equity Analysis</div>
  </div>
  <div style="text-align:right">
    <div class="date">Prepared [Full Date, e.g., February 25, 2026]</div>
    <div class="date">Data through [Latest Quarter, e.g., Q3 2025] &middot; [Next Catalyst, e.g., Q4 Earnings Mar 5, 2026]</div>
    <div class="date">Data sourced from <a href="https://daloopa.com">Daloopa</a></div>
  </div>
</div>
```

### Section 3: KPI Grid (8 Boxes)
Always include these 6 standard KPIs + 2 company-specific KPIs:

| Position | KPI | Source |
|----------|-----|--------|
| 1 | Market Cap | Web search |
| 2 | Stock Price | Web search |
| 3 | Forward P/E | Web search / calculated |
| 4 | Consensus Rating + Avg PT | Web search |
| 5 | TTM Revenue | Daloopa (sum last 4 quarters) |
| 6 | TTM Net Income | Daloopa (sum last 4 quarters) |
| 7 | Company-Specific KPI 1 | Daloopa or web |
| 8 | Company-Specific KPI 2 | Daloopa or web |

Company-specific KPI examples by sector:
- **Tech/SaaS**: ARR, Net Retention Rate
- **Industrial/Mfg**: Contracted Backlog, Capacity (GW/units)
- **Retail**: Same-Store Sales Growth, Store Count
- **Financials**: NIM, CET1 Ratio
- **Pharma**: Pipeline Drugs in Phase III, Patent Cliff Year
- **Energy**: Production (boe/d), Proved Reserves
- **REIT**: FFO/Share, Occupancy Rate

```html
<div class="kpi-grid">
  <div class="kpi"><div class="kpi-label">Market Cap</div><div class="kpi-val">~$XXB</div></div>
  <div class="kpi"><div class="kpi-label">Stock Price</div><div class="kpi-val">~$XXX</div></div>
  <div class="kpi"><div class="kpi-label">Forward P/E</div><div class="kpi-val">~XXx</div></div>
  <div class="kpi"><div class="kpi-label">Consensus</div><div class="kpi-val">[Rating]</div><div class="daloopa-src">Avg PT $XXX</div></div>
  <div class="kpi"><div class="kpi-label">TTM Revenue</div><div class="kpi-val">~$X.XB</div></div>
  <div class="kpi"><div class="kpi-label">TTM Net Income</div><div class="kpi-val">~$X.XB</div></div>
  <div class="kpi"><div class="kpi-label">[Industry KPI 1]</div><div class="kpi-val">[Value]</div><div class="daloopa-src">[optional context]</div></div>
  <div class="kpi"><div class="kpi-label">[Industry KPI 2]</div><div class="kpi-val">[Value]</div><div class="daloopa-src">[optional context]</div></div>
</div>
```

### Section 4: Executive Summary
One paragraph capturing what makes this stock interesting RIGHT NOW — the core tension. Follow with "Five Key Tensions" — the 5 most critical bull/bear debates in the stock.

```html
<h2>Executive Summary</h2>
<p>[1 dense paragraph: Company positioning, secular themes, key narrative, current inflection point]</p>

<h3>Five Key Tensions</h3>
<ul>
  <li><span class="[red|green|amber] bold">[Label]:</span> [One-line data-backed statement]</li>
  <li><span class="[red|green|amber] bold">[Label]:</span> [One-line data-backed statement]</li>
  <li><span class="[red|green|amber] bold">[Label]:</span> [One-line data-backed statement]</li>
  <li><span class="[red|green|amber] bold">[Label]:</span> [One-line data-backed statement]</li>
  <li><span class="[red|green|amber] bold">[Label]:</span> [One-line data-backed statement]</li>
</ul>
```

Rules for Five Key Tensions:
- Alternate between green (bullish) and red (bearish) tensions
- Every tension must include a specific data point
- Labels should be punchy: "Revenue accelerating", "Margins compressing", "Guidance cut", "Backlog growing"
- Include Daloopa citation links where applicable

### Section 5: Key News & Events Timeline
6-10 events from the last 6-12 months, reverse chronological. Include any upcoming catalyst as the first entry. End with a Policy/Macro Backdrop box if relevant.

```html
<h2>Key News &amp; Events Timeline</h2>

<!-- UPCOMING event first (if applicable) -->
<div class="event">
  <div class="event-date">[Mon DD, YYYY]</div>
  <div>
    <span class="event-tag tag-up">UPCOMING</span>
    <span class="event-title">[Event Title]</span>
    <div class="event-desc">[Key expectations, consensus estimates, what to watch]</div>
  </div>
</div>

<!-- Past events, most recent first -->
<div class="event">
  <div class="event-date">[Mon DD, YYYY]</div>
  <div>
    <span class="event-tag tag-[pos|neg|mix]">[POSITIVE|NEGATIVE|MIXED]</span>
    <span class="event-title">[Headline]</span>
    <div class="event-desc">[1-2 sentences with specific data points, stock reaction if notable]</div>
  </div>
</div>
<!-- Repeat for 6-10 events -->

<!-- Policy/Macro box (include if relevant to thesis) -->
<div class="section-box" style="margin-top:10px">
  <h3 style="margin-top:0">Policy / Macro Backdrop</h3>
  <p>[Key policy, regulatory, or macro factors affecting the company. Be specific.]</p>
</div>
```

Event tag rules:
- `tag-up` / `UPCOMING`: Future dated events (earnings, FDA dates, regulatory decisions)
- `tag-pos` / `POSITIVE`: Clear positive for the stock (beat, upgrade, contract win, favorable ruling)
- `tag-neg` / `NEGATIVE`: Clear negative (miss, downgrade, guidance cut, adverse ruling, executive departure)
- `tag-mix` / `MIXED`: Ambiguous signal (beat on revenue, miss on margins; raise guidance but cut another metric)

### Section 6: Financial Analysis
This is the data-dense core. Two mandatory sub-sections:

#### 6a: Quarterly Income Statement
Table spanning 8-12 quarters. Every financial figure from Daloopa MUST be hyperlinked.

Mandatory rows: Net Sales, COGS, **Gross Profit** (highlight-row), Gross Margin %, Operating Income, Op Margin %, Net Income, **Diluted EPS** (highlight-row).

Optional rows (include if data available and relevant): EBITDA, D&A, Interest Expense, Tax Rate.

```html
<div class="page-break"></div>
<h2>Financial Analysis</h2>
<h3>Quarterly Income Statement ($M except EPS)</h3>
<table>
  <thead>
    <tr><th style="text-align:left">Metric</th><th>Q1&rsquo;23</th><th>Q2&rsquo;23</th><!-- ... --></tr>
  </thead>
  <tbody>
    <tr><td>Net Sales</td><td><a href="https://daloopa.com/src/[id]">[val]</a></td><!-- ... --></tr>
    <tr><td>COGS</td><td><a href="https://daloopa.com/src/[id]">[val]</a></td><!-- ... --></tr>
    <tr class="highlight-row"><td><strong>Gross Profit</strong></td><td><a href="https://daloopa.com/src/[id]">[val]</a></td><!-- ... --></tr>
    <tr><td>Gross Margin %</td><td>[calc]%</td><!-- ... --></tr>
    <tr><td>Op Income</td><td><a href="https://daloopa.com/src/[id]">[val]</a></td><!-- ... --></tr>
    <tr><td>Op Margin %</td><td>[calc]%</td><!-- ... --></tr>
    <tr><td>Net Income</td><td><a href="https://daloopa.com/src/[id]">[val]</a></td><!-- ... --></tr>
    <tr class="highlight-row"><td><strong>Diluted EPS</strong></td><td><a href="https://daloopa.com/src/[id]">$[val]</a></td><!-- ... --></tr>
  </tbody>
</table>
```

#### 6b: Guidance Evolution
Track how management guidance has evolved across quarters for the current fiscal year. Show initial guidance → each quarterly update → latest.

```html
<h3>[Year] Guidance Evolution</h3>
<table>
  <thead><tr><th style="text-align:left">Item</th><th>Initial ([Quarter])</th><th>[Q Update]</th><th>[Q Update]</th><th>Latest</th></tr></thead>
  <tbody>
    <tr>
      <td>Revenue ($B)</td>
      <td><a href="https://daloopa.com/src/[id]">$X.X</a>&ndash;<a href="https://daloopa.com/src/[id]">$X.X</a></td>
      <!-- subsequent updates -->
    </tr>
    <!-- Op Income, EPS, CapEx, Net Cash, or other guided metrics -->
  </tbody>
</table>
<p class="footnote">[Commentary on direction of guidance changes and what they signal]</p>
```

Guidance items to track (include all that are available):
- Revenue
- Operating Income / EBIT
- EPS
- CapEx
- Free Cash Flow
- Net Cash / Debt
- Any company-specific guided metric (e.g., bookings for FSLR, subscriber adds for streaming)

### Section 7: Cost Structure & Margin Analysis
Deep dive into what's driving margins. This section should explain WHY margins are expanding or compressing.

Sub-sections (include all that are relevant):

**7a: Key COGS/Margin Drivers**
Table showing the biggest cost drivers and their QoQ or YoY change. Use red for cost headwinds, green for tailwinds/offsets.

```html
<h2>Cost Structure &amp; Margin Analysis</h2>
<h3>Key COGS Drivers</h3>
<table>
  <thead><tr><th style="text-align:left">Driver</th><th>[Period 1]</th><th>[Period 2]</th></tr></thead>
  <tbody>
    <tr><td>[Cost item 1]</td><td class="red"><a href="https://daloopa.com/src/[id]">+$XXM</a></td><td>...</td></tr>
    <tr><td>[Cost item 2]</td><td class="green"><a href="https://daloopa.com/src/[id]">&ndash;$XXM</a></td><td>...</td></tr>
  </tbody>
</table>
```

**7b: Two-Column Analysis Boxes**
Use for any important margin sub-analysis. Examples:
- Tax credit / subsidy trends (e.g., Section 45X for solar, R&D credits for tech)
- ASP / pricing power trends
- Mix shift analysis (product, geographic, customer)
- Input cost trends (commodities, labor, components)

```html
<div class="two-col" style="margin-top:10px">
  <div class="section-box">
    <h3 style="margin-top:0">[Sub-analysis title]</h3>
    <!-- Table or content -->
  </div>
  <div class="section-box">
    <h3 style="margin-top:0">[Sub-analysis title]</h3>
    <!-- Table or content -->
  </div>
</div>
```

**7c: Operating Expenses Breakdown**
```html
<h3>Operating Expenses ([Latest Quarter])</h3>
<table>
  <thead><tr><th style="text-align:left">Item</th><th>Amount</th><th>% of Revenue</th></tr></thead>
  <tbody>
    <tr><td>R&amp;D</td><td><a href="https://daloopa.com/src/[id]">$XXM</a></td><td>X.X%</td></tr>
    <tr><td>SG&amp;A</td><td><a href="https://daloopa.com/src/[id]">$XXM</a></td><td>X.X%</td></tr>
    <!-- Add any notable items: restructuring, start-up costs, impairments -->
  </tbody>
</table>
<p class="footnote">[Commentary on notable OpEx trends]</p>
```

### Section 8: Industry-Specific Deep Dive
This section adapts based on the company's industry. Include the 1-2 most critical operational themes with data tables.

#### Manufacturing / Industrial
```html
<h2>Bookings &amp; Backlog Analysis</h2>
<!-- Alert box if trend is alarming -->
<div class="alert-box">
  <h3 style="margin-top:0; color:#c0392b">[Alarming Headline]</h3>
  <table><!-- bookings data --></table>
  <p style="margin-top:6px">[Context]</p>
</div>
<!-- Backlog trajectory table -->
<!-- Pipeline by geography table -->
```

#### SaaS / Technology
```html
<h2>Subscription &amp; Growth Metrics</h2>
<!-- ARR / MRR trajectory table -->
<!-- Net retention rate trend -->
<!-- Customer count / cohort analysis -->
<!-- RPO / deferred revenue analysis -->
```

#### Retail / Consumer
```html
<h2>Store Performance &amp; Consumer Trends</h2>
<!-- Same-store sales trajectory -->
<!-- Store count / openings / closures -->
<!-- Traffic vs. ticket size decomposition -->
<!-- Inventory turns / days -->
```

#### Financials / Banks
```html
<h2>Credit Quality &amp; Net Interest Income</h2>
<!-- NIM trajectory -->
<!-- Provision for credit losses trend -->
<!-- Loan growth by category -->
<!-- CET1 / capital ratios -->
```

#### Healthcare / Pharma
```html
<h2>Pipeline &amp; Product Portfolio</h2>
<!-- Pipeline summary table (drug, indication, phase, expected milestone) -->
<!-- Key product revenue trends -->
<!-- Patent cliff timeline -->
```

#### Energy
```html
<h2>Production &amp; Reserves</h2>
<!-- Production volume trends (oil, gas, NGL) -->
<!-- Realized pricing vs. benchmark -->
<!-- Reserve replacement ratio -->
<!-- Breakeven analysis -->
```

Use the `alert-box` class for any metric showing an alarming trend. Use `section-box` for neutral analysis. Include `footnote` paragraphs with analytical commentary.

### Section 9: Forward Catalysts
Organized by timeframe with priority tags. 3-4 catalysts per timeframe.

```html
<div class="page-break"></div>
<h2>Forward Catalysts</h2>

<h3>Near-Term (0&ndash;3 months)</h3>
<div class="catalyst-item"><span class="priority p-high">HIGH</span> <strong>[Catalyst]</strong><br><span style="color:#666">[Why it matters, what consensus expects, what the market will react to]</span></div>
<!-- 2-4 near-term catalysts -->

<h3>Medium-Term (3&ndash;12 months)</h3>
<div class="catalyst-item"><span class="priority p-[high|med]">[HIGH|MED]</span> <strong>[Catalyst]</strong><br><span style="color:#666">[Description]</span></div>
<!-- 2-4 medium-term catalysts -->

<h3>Long-Term (1&ndash;3 years)</h3>
<div class="catalyst-item"><span class="priority p-[high|med|low]">[PRIORITY]</span> <strong>[Catalyst]</strong><br><span style="color:#666">[Description]</span></div>
<!-- 2-3 long-term catalysts -->
```

Priority rules:
- `p-high`: Binary event that can move the stock 5%+ (earnings, FDA decision, major contract, regulatory ruling)
- `p-med`: Structural factor that will play out over time (capacity ramp, market share shift, margin normalization)
- `p-low`: Background factor worth monitoring (macro shifts, competitor actions, policy risk)

### Section 10: What You Need to Believe (Bull vs Bear)
Two-column layout. Each side has 4-6 numbered, falsifiable beliefs with evidence, ending with a price target and valuation math.

```html
<h2>What You Need to Believe</h2>

<div class="two-col">
  <div class="bull-box">
    <h3 style="margin-top:0; color:#1a8a4a; font-size:13px;">To Go Long [TICKER] Today</h3>
    <p><strong>1. [Falsifiable belief].</strong> [2-3 sentences of evidence, data points, and reasoning]</p>
    <p style="margin-top:6px"><strong>2. [Belief].</strong> [Evidence]</p>
    <p style="margin-top:6px"><strong>3. [Belief].</strong> [Evidence]</p>
    <p style="margin-top:6px"><strong>4. [Belief].</strong> [Evidence]</p>
    <!-- Optional 5th and 6th beliefs -->
    <p style="margin-top:10px; border-top: 1px solid #1a8a4a44; padding-top: 6px;">
      <strong style="color:#1a8a4a">Bull Target: $XXX&ndash;$XXX</strong><br>
      [Valuation math: XX-XXx on [year]E EPS of $XX. Upside XX-XX% from current levels.]
    </p>
  </div>
  <div class="bear-box">
    <h3 style="margin-top:0; color:#c0392b; font-size:13px;">To Short [TICKER] Today</h3>
    <p><strong>1. [Falsifiable belief].</strong> [2-3 sentences of evidence]</p>
    <p style="margin-top:6px"><strong>2. [Belief].</strong> [Evidence]</p>
    <p style="margin-top:6px"><strong>3. [Belief].</strong> [Evidence]</p>
    <p style="margin-top:6px"><strong>4. [Belief].</strong> [Evidence]</p>
    <!-- Optional 5th and 6th beliefs -->
    <p style="margin-top:10px; border-top: 1px solid #c0392b44; padding-top: 6px;">
      <strong style="color:#c0392b">Bear Target: $XXX&ndash;$XXX</strong><br>
      [Valuation math: If [year] disappoints at $XX EPS, XXx P/E = $XXX. Downside XX-XX%.]
    </p>
  </div>
</div>
```

Bull/Bear rules:
- **Be balanced**: Equal analytical rigor on both sides. Don't cheerload OR fearmonger.
- **Be specific**: Every belief must reference concrete data. "Margins will improve" is wrong. "GM recovers from 38% to 45%+ as Louisiana start-up costs ($37M/Q) normalize by mid-2026" is correct.
- **Be falsifiable**: Each belief should be testable. In 6 months, you should be able to say whether it proved true or false.
- **Include valuation math**: Bull and bear targets must show the math (multiple × earnings estimate = price target).
- **Asymmetry analysis**: If bull upside is 30% and bear downside is 35%, note the risk/reward skew.

### Section 11: Monitoring Framework
Two-column: 5-7 quantitative metrics + 5-7 qualitative factors.

```html
<h2>Monitoring Framework</h2>
<div class="two-col">
  <div class="section-box">
    <h3 style="margin-top:0">Quantitative Monitors</h3>
    <ol>
      <li>[Metric] &mdash; [what to watch for / threshold]</li>
      <!-- 5-7 items -->
    </ol>
  </div>
  <div class="section-box">
    <h3 style="margin-top:0">Qualitative Monitors</h3>
    <ol>
      <li>[Factor] &mdash; [what to watch for]</li>
      <!-- 5-7 items -->
    </ol>
  </div>
</div>
```

Quantitative monitors should be specific: "Quarterly net bookings — has the trend inflected positive?" not just "Watch bookings."

### Section 12: Footer
```html
<div style="margin-top:20px; padding-top:10px; border-top:2px solid #111; font-size:8px; color:#999; text-align:center;">
  Data sourced from <a href="https://daloopa.com">Daloopa</a>. All financial figures link to original source filings. Prepared [Date]. Not investment advice.
</div>

</div><!-- end container -->
</body>
</html>
```

---

## CRITICAL RULES

### Citation Rules
- EVERY financial figure from Daloopa MUST be wrapped in `<a href="https://daloopa.com/src/{fundamental_id}">[value]</a>`
- Use the `id` field from `get_company_fundamentals` response as the `fundamental_id`
- Calculated metrics (margins, growth rates, ratios computed from raw data) do NOT need citation links
- Document search results must cite: `<a href="https://marketplace.daloopa.com/document/{document_id}">[Filing]</a>`
- Never fabricate fundamental IDs — only use IDs returned from the API

### Financial Formatting
- Revenue/income in millions: `1,595` (with comma separator, no decimal)
- Revenue/income in billions (KPI grid): `~$5.05B`
- EPS: `$4.24` (two decimal places)
- Margins: `38.3%` (one decimal place)
- Multiples: `12x` (no decimal for round, `12.5x` for half)
- Ranges: use `&ndash;` HTML entity for en-dash (e.g., `$4.95&ndash;$5.2B`)
- Use `&rsquo;` for apostrophes in quarter labels (e.g., `Q3&rsquo;25`)
- Use `&mdash;` for em-dashes in text
- Use `&middot;` for middle dots in inline separators

### Color-Coding Rules
- `.green` for positive: beats, upgrades, margin expansion, bookings growth, guidance raises
- `.red` for negative: misses, downgrades, margin compression, guidance cuts, cost headwinds
- `.amber` for mixed: ambiguous signals, uncertain outcomes
- `.bold` combined with color for emphasis on key figures
- In Five Key Tensions: use `<span class="red bold">` or `<span class="green bold">` for the label

### Content Quality Standards
- **Be specific**: Every claim must have a data point. "Revenue grew" is wrong. "Revenue grew 47% YoY to $1.59B" is correct.
- **Be balanced**: Present both bull and bear cases with equal analytical rigor.
- **Be forward-looking**: Catalysts and monitoring framework are as important as historical financials.
- **Be skeptical of management**: Track guidance accuracy. If management repeatedly cuts guidance, flag prominently.
- **Quantify everything**: Bull/bear targets must include valuation math. Catalysts must have timeline and impact estimates.

### Page Breaks
Insert `<div class="page-break"></div>` before:
- The Financial Analysis section (Section 6)
- The Forward Catalysts section (Section 9)

---

## EXECUTION SEQUENCE

Follow this exact sequence:

1. **discover_companies** → get company_id, latest quarters
2. **discover_company_series** → batch search for all needed series IDs (run multiple keyword searches in parallel)
3. **get_company_fundamentals** → pull financial data for all identified series across target periods
4. **search_documents** → pull qualitative insights from filings (run in parallel with step 5)
5. **WebSearch** → gather recent news, analyst views, stock price, market cap, consensus (run multiple searches in parallel)
6. **Synthesize** → organize all data into the 10-section framework
7. **Write HTML** → generate the complete self-contained HTML file using the design system
8. **Save & Open** → write to `~/Generated Stuff/[TICKER]-note.html` and open in browser

For steps 2-5, maximize parallelism — run independent searches concurrently.

After writing the file, always end with:
> Data sourced from Daloopa
