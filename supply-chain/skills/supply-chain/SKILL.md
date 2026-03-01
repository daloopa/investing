---
name: supply-chain
description: This skill should be used when the user asks to "map a supply chain", "show supply chain", "supply chain analysis", "supplier analysis", "who supplies [company]", "supply chain dashboard", "supply chain map", "vendor analysis", "supply chain visualization", or needs to understand the supplier/customer network of any public company. Also triggers on requests mentioning "supply chain risk", "supplier concentration", "customer concentration", "key suppliers", "key customers", or "supply chain dependencies" for any company ticker. Use this for any supply chain mapping or analysis request.
---

This skill generates a professional, interactive supply chain dashboard as a self-contained HTML document. It maps the upstream (supplier) and downstream (customer) relationships for a target company, quantifying financial interdependencies at each layer.

The output enables an analyst to understand: Who are the critical suppliers? Where is concentration risk? Which suppliers depend heavily on this company for revenue? Can I trace the chain deeper — from Tier 1 to Tier 2 suppliers?

## Output Format

The final deliverable is a **single self-contained HTML file** with:
- Embedded CSS and JavaScript (no external dependencies)
- **Tier-grouped Canvas network visualization** — columns: Tier 3 → Tier 2 → Tier 1 → Target → Customers, with connection lines. Clickable nodes open detail overlays.
- **Inventory Health Overview table** — for all suppliers: RM%, WIP%, FG% of total inventory shown as stacked colored bars, plus latest total inventory value
- **Supplier cards grouped by tier** — Tier 1 (Critical/Sole-source), Tier 2 (Major Component), Tier 3 (Specialty) with click-to-expand detail overlays
- **Detail overlays** for each supplier containing:
  - 10-quarter financial table (Revenue, Gross Profit, Net Income, Gross Margin %)
  - 10-quarter inventory breakdown table (Raw Materials, WIP, Finished Goods, Total, RM%, WIP%, FG%)
  - Canvas chart: stacked bar chart of inventory composition with Gross Margin % line overlay
  - Business description and relationship to target company
- **Supply Chain Shock Analysis** section — narrative analysis of how a demand/supply shock to the target company ripples through the supply chain, with an impact matrix table (Revenue Impact, Margin Impact, Overall Risk per supplier)
- Clean newspaper-style design (light mode, professional typefaces)
- All financial figures hyperlinked to Daloopa source citations
- A "Download as PDF" button (uses `window.print()`)

**DOM Safety**: All JavaScript MUST use `createElement()` + `textContent` + `appendChild()` for DOM construction. NEVER use `innerHTML`, `outerHTML`, or any HTML-string injection methods. Use helper functions like `ce(tag)`, `ca(el, attrs)`, `cA(parent, children)` to keep code compact.

Write the file to `~/Generated Stuff/[TICKER]-supply-chain.html` (or user-specified location), then open it with `open`.

---

## RESEARCH WORKFLOW

This is a multi-phase research process. Each phase builds on the previous one. Maximize parallelism across independent API calls.

### Phase 1: Target Company Identification

1. Use `discover_companies` with the ticker symbol to get the `company_id`, `latest_calendar_quarter`, and `latest_fiscal_quarter`.
2. Pull key financials for the target company:
   - Use `discover_company_series` with keywords: ["revenue", "cost of goods", "gross profit", "operating income", "net income", "total cost"]
   - Use `get_company_fundamentals` for the last 4 quarters to get TTM figures
3. Note the target company's total COGS / cost of revenue (TTM) — this is the denominator for supplier % calculations.

### Phase 2: Supplier Identification

Run these concurrently to build a comprehensive supplier list:

**2a. Daloopa Document Search:**
- Search keywords: ["supplier", "vendor", "purchase", "procurement"] across last 2-4 quarters
- Search keywords: ["supply agreement", "supply chain", "manufacturing"] across last 2-4 quarters
- Search keywords: ["sole source", "single source", "key supplier"] across last 2-4 quarters
- Search keywords: ["concentration", "significant supplier"] across last 2-4 quarters
- Search the company's 10-K specifically for supplier disclosures

**2b. Web Research:**
- `"[TICKER] [company name] key suppliers list 2025 2026"` — supplier identification
- `"[TICKER] supply chain analysis suppliers"` — analyst/industry reports
- `"[TICKER] 10-K supplier disclosure"` — SEC filing analysis
- `"[company name] supply chain map"` — industry supply chain maps
- `"[company name] supplier concentration risk"` — risk analysis
- `"[company name] who manufactures for [company]"` — manufacturing partners
- `"[company name] component suppliers"` — component-level supply chain

**2c. Industry-Specific Supplier Research:**
For each industry, search for the known critical supply chain relationships:
- **Tech/Hardware**: semiconductor foundries (TSMC, Samsung), display (Samsung, LG, BOE), memory (Samsung, SK Hynix, Micron), sensors/cameras (Sony), glass (Corning), connectors (Amphenol), batteries (CATL, LG Energy), PCB/assembly (Foxconn/Hon Hai, Pegatron, Luxshare)
- **Automotive**: battery (CATL, Panasonic, LG Energy), semiconductors (Infineon, NXP, ON Semi, TI), steel (Nippon, POSCO), tires (Michelin, Bridgestone), glass (AGC, Saint-Gobain)
- **Pharma**: CDMOs (Lonza, Samsung Biologics, Catalent), API suppliers, packaging, distribution
- **Retail**: brand suppliers, logistics (FedEx, UPS), packaging
- **Energy**: equipment (Baker Hughes, Schlumberger), pipe (Tenaris), chemicals

### Phase 3: Supplier Financial Analysis

For each identified supplier (aim for 8-15 key suppliers):

1. **Discover the supplier** using `discover_companies` with their ticker
2. **Pull key financials** from Daloopa:
   - `discover_company_series` with keywords: ["revenue", "net income", "gross margin", "operating margin"]
   - `get_company_fundamentals` for last 4 quarters
3. **Determine revenue concentration**:
   - Search Daloopa documents for the supplier: keywords ["[target company name]", "customer", "concentration"]
   - Web search: `"[supplier name] [target company] revenue percentage customer"`
   - Web search: `"[supplier name] 10-K customer concentration"`
   - Many suppliers disclose their top customers in 10-K filings — look for "customers that accounted for 10% or more of revenue"
4. **Determine COGS attribution** (what % of target's costs is this supplier):
   - This is often estimated. Use logic like:
     - If Apple's COGS is ~$200B TTM and TSMC's revenue from Apple is ~$70B, then TSMC = ~35% of COGS
     - Cite the source of each estimate (analyst report, 10-K disclosure, industry research)
   - Flag when this is an estimate vs. a disclosed figure
5. **Business & product description**: What does this supplier provide? Be specific (e.g., "5nm/3nm chip fabrication for A-series and M-series SoCs" not just "semiconductors")

### Phase 3b: Inventory & 10-Quarter Financial Data

For the target company AND each identified supplier (8-15 companies), pull **10 quarters** of data:

1. **Discover inventory series** using `discover_company_series` with keywords: ["raw material", "work in process", "finished good", "inventory", "inventories"]
   - Look for separate RM, WIP, FG series, plus a total inventory series
   - Some companies report "carrying amount" breakdowns — use those for RM/WIP/FG splits
2. **Discover financial series** using `discover_company_series` with keywords: ["revenue", "gross profit", "net income", "gross margin"]
3. **Pull 10 quarters** using `get_company_fundamentals` with periods spanning Q3 of 2.5 years ago through the latest available quarter
   - Example: if latest is Q4'25, pull ["2023Q3", "2023Q4", "2024Q1", "2024Q2", "2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3", "2025Q4"]
4. **Compute inventory composition**: For each quarter, calculate RM%, WIP%, FG% of total inventory
   - High WIP% can signal production bottlenecks
   - Rising FG% can signal demand weakness
   - Rising RM% can signal supply hoarding or procurement buildup
5. **Handle missing data gracefully**: Some suppliers may not report full inventory breakdowns — show what's available and note gaps
6. **Multi-currency handling**: Note the reporting currency for each company (USD, NTD, KRW, EUR, etc.) and display with appropriate units (e.g., "NTD B" for TSMC, "KRW T" for Samsung)

Run inventory and financial series pulls in parallel across all companies.

### Phase 4: Customer / Downstream Analysis

Research where the target company is itself a supplier:

1. **Web search**: `"[company name] major customers B2B"`, `"who does [company name] supply to"`, `"[company name] enterprise customers"`
2. **Daloopa document search**: keywords ["customer", "contract", "agreement", "enterprise", "license"]
3. For each major customer identified:
   - What product/service does the target company supply?
   - Estimated % of customer's costs attributable to the target company
   - Pull the customer's key financials from Daloopa

### Phase 5: Tier 2 Supplier Research

For the top 3-5 most important Tier 1 suppliers, repeat a lighter version of Phase 2-3:

1. Identify their key suppliers (Tier 2 to the original target)
2. Pull basic financials
3. Determine what they supply and rough revenue/cost relationships
4. This enables the "drill deeper" functionality in the dashboard

### Phase 6: Data Assembly & Synthesis

Before writing HTML, organize all data into this structure:

```
TARGET COMPANY:
  - Name, ticker, description
  - TTM Revenue, COGS, Gross Profit, Net Income, Gross Margin, Op Margin
  - Market cap, stock price (from web)

TIER 1 SUPPLIERS (sorted by estimated % of target COGS, descending):
  For each:
  - Name, ticker, description
  - What they supply (specific products/components)
  - Estimated % of target company COGS (with source/logic)
  - % of supplier revenue from target company (with source)
  - TTM Revenue, Net Income, Gross Margin
  - Market cap
  - Relationship summary (sole source? multi-source? critical?)
  - Their key suppliers (Tier 2) if researched
  - 10-quarter financials: Revenue, Gross Profit, Net Income, GM% (with Daloopa citation IDs)
  - 10-quarter inventory: RM, WIP, FG, Total, RM%, WIP%, FG% (with Daloopa citation IDs)
  - Reporting currency and unit (e.g., USD $M, NTD B, KRW T)

TIER 1 CUSTOMERS (sorted by estimated % of target revenue, descending):
  For each:
  - Name, ticker, description
  - What target company supplies to them
  - Estimated % of target revenue from this customer
  - Estimated % of customer COGS from target
  - TTM Revenue, Net Income

TIER 2 SUPPLIERS (for top 3-5 Tier 1 suppliers):
  For each Tier 1 supplier, their key suppliers with basic data
```

### Phase 6b: Supply Chain Shock Analysis

Prepare a narrative analysis of how a shock to the target company would ripple through the supply chain:

1. **Classify each supplier by dependency level**:
   - **High dependency**: Target company is >20% of supplier's revenue → severe impact from demand shock
   - **Moderate dependency**: Target is 10-20% of revenue → meaningful but manageable impact
   - **Low dependency**: Target is <10% of revenue → diversified, minimal direct impact

2. **Assess shock propagation for each supplier**:
   - **Revenue Impact** (High/Medium/Low): Based on % of revenue from target
   - **Margin Impact** (High/Medium/Low): Based on operating leverage, fixed costs, ability to find replacement demand
   - **Inventory Risk**: Suppliers with high FG% are more exposed to demand shocks; those with high RM% face supply-side risk
   - **Substitutability**: Can the target switch to alternatives? Can the supplier find other customers?

3. **Build an impact matrix table** with columns: Supplier, Tier, Revenue Dependency, Revenue Impact, Margin Impact, Overall Risk

4. **Write narrative sections**:
   - "Most Exposed Suppliers" — 2-3 paragraphs on suppliers facing highest risk
   - "Resilient Suppliers" — suppliers with diversified revenue bases
   - "Second-Order Effects" — how Tier 2 suppliers would be indirectly affected
   - "Key Monitoring Metrics" — what an analyst should watch (inventory days, order backlog, etc.)

---

## HTML TEMPLATE & DESIGN SYSTEM

Generate the HTML following this design system. The aesthetic is "Financial Times meets clean data visualization" — light background, serif headlines, sans-serif body, minimal decoration, maximum information density.

### Design Principles
- **Light mode only** — white/off-white backgrounds
- **Newspaper typography**: Serif for headlines (Georgia, "Times New Roman"), sans-serif for body and data (system-ui, -apple-system, "Segoe UI", Helvetica)
- **Minimal color palette**: Black text, subtle gray borders, blue for links, green/red only for financial sentiment
- **Information density**: Show data compactly but with clear hierarchy
- **Interactive but not flashy**: Smooth transitions, click-to-expand, no animations for animation's sake

### Core CSS

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[TICKER] Supply Chain Dashboard</title>
<style>
  @media print {
    body { margin: 0; }
    .no-print { display: none !important; }
    .interactive { pointer-events: none; }
    @page { margin: 0.5in; size: landscape; }
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #fafaf8;
    --surface: #ffffff;
    --border: #e0ddd8;
    --border-light: #f0ede8;
    --text-primary: #1a1a1a;
    --text-secondary: #555550;
    --text-tertiary: #8a8a85;
    --accent: #2563eb;
    --green: #1a7a3a;
    --green-bg: #f0f9f2;
    --red: #b91c1c;
    --red-bg: #fef2f2;
    --amber: #92600a;
    --amber-bg: #fefce8;
    --blue-bg: #eff6ff;
    --node-supplier: #e8e4df;
    --node-customer: #dde8f0;
    --node-target: #1a1a1a;
    --serif: Georgia, "Times New Roman", "Noto Serif", serif;
    --sans: system-ui, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
    --mono: "SF Mono", "Fira Code", "Fira Mono", "Roboto Mono", monospace;
  }

  body {
    font-family: var(--sans);
    color: var(--text-primary);
    background: var(--bg);
    font-size: 14px;
    line-height: 1.55;
    -webkit-font-smoothing: antialiased;
  }

  /* Layout */
  .page-header {
    background: var(--surface);
    border-bottom: 3px solid var(--text-primary);
    padding: 24px 40px 16px;
  }
  .page-header h1 {
    font-family: var(--serif);
    font-size: 32px;
    font-weight: 700;
    letter-spacing: -0.5px;
    line-height: 1.2;
  }
  .page-header .subtitle {
    font-family: var(--sans);
    font-size: 14px;
    color: var(--text-secondary);
    margin-top: 4px;
  }
  .page-header .dateline {
    font-size: 12px;
    color: var(--text-tertiary);
    margin-top: 8px;
    font-family: var(--mono);
  }

  .container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 24px 40px;
  }

  /* Section Headers */
  h2 {
    font-family: var(--serif);
    font-size: 20px;
    font-weight: 700;
    margin: 32px 0 16px;
    padding-bottom: 6px;
    border-bottom: 2px solid var(--text-primary);
    letter-spacing: -0.3px;
  }
  h3 {
    font-family: var(--sans);
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--text-secondary);
    margin: 20px 0 10px;
  }

  /* KPI Bar */
  .kpi-bar {
    display: flex;
    gap: 0;
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
    background: var(--surface);
    margin: 16px 0;
  }
  .kpi-item {
    flex: 1;
    padding: 12px 16px;
    border-right: 1px solid var(--border-light);
    text-align: center;
  }
  .kpi-item:last-child { border-right: none; }
  .kpi-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
    font-weight: 600;
  }
  .kpi-value {
    font-size: 18px;
    font-weight: 700;
    margin-top: 2px;
    font-variant-numeric: tabular-nums;
  }
  .kpi-sub {
    font-size: 11px;
    color: var(--text-tertiary);
    margin-top: 1px;
  }

  /* Supply Chain Visualization */
  .chain-view {
    display: flex;
    gap: 24px;
    align-items: flex-start;
    margin: 20px 0;
    overflow-x: auto;
    padding-bottom: 16px;
  }
  .chain-column {
    min-width: 280px;
    flex-shrink: 0;
  }
  .chain-column-header {
    font-family: var(--sans);
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-tertiary);
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border);
    text-align: center;
  }
  .chain-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-tertiary);
    font-size: 24px;
    min-width: 40px;
    padding-top: 40px;
    flex-shrink: 0;
  }

  /* Company Cards */
  .company-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px 16px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: border-color 0.15s, box-shadow 0.15s;
  }
  .company-card:hover {
    border-color: var(--text-secondary);
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }
  .company-card.target-card {
    background: var(--text-primary);
    color: white;
    border-color: var(--text-primary);
  }
  .company-card.target-card .card-ticker { color: rgba(255,255,255,0.7); }
  .company-card.target-card .card-metric-label { color: rgba(255,255,255,0.5); }
  .company-card.target-card .card-metric-value { color: white; }
  .company-card.target-card .card-desc { color: rgba(255,255,255,0.7); }
  .company-card.expanded { border-color: var(--accent); box-shadow: 0 2px 12px rgba(37,99,235,0.1); }
  .company-card.supplier-card { border-left: 3px solid var(--node-supplier); }
  .company-card.customer-card { border-left: 3px solid var(--node-customer); }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }
  .card-name {
    font-family: var(--serif);
    font-size: 16px;
    font-weight: 700;
    line-height: 1.2;
  }
  .card-ticker {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--text-tertiary);
    margin-top: 2px;
  }
  .card-badge {
    font-size: 10px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 3px;
    white-space: nowrap;
  }
  .badge-pct-high { background: var(--red-bg); color: var(--red); }
  .badge-pct-med { background: var(--amber-bg); color: var(--amber); }
  .badge-pct-low { background: var(--green-bg); color: var(--green); }

  .card-supplies {
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 6px;
    line-height: 1.4;
  }

  .card-metrics {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid var(--border-light);
  }
  .card-metric-label {
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    color: var(--text-tertiary);
  }
  .card-metric-value {
    font-size: 13px;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
  }

  .card-desc {
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 8px;
    line-height: 1.45;
  }

  /* Expanded Detail Panel */
  .detail-panel {
    display: none;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border-light);
  }
  .company-card.expanded .detail-panel { display: block; }

  .detail-section {
    margin-bottom: 14px;
  }
  .detail-section h4 {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
    margin-bottom: 6px;
  }

  .relationship-bar {
    height: 8px;
    background: var(--border-light);
    border-radius: 4px;
    overflow: hidden;
    margin: 4px 0;
  }
  .relationship-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s;
  }
  .fill-red { background: var(--red); }
  .fill-amber { background: var(--amber); }
  .fill-green { background: var(--green); }
  .fill-blue { background: var(--accent); }

  /* Drill-down button */
  .drill-btn {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    color: var(--accent);
    cursor: pointer;
    padding: 4px 0;
    border: none;
    background: none;
    font-family: var(--sans);
  }
  .drill-btn:hover { text-decoration: underline; }

  /* Concentration Table */
  .conc-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    margin: 12px 0;
  }
  .conc-table th {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
    font-weight: 600;
    text-align: left;
    padding: 6px 10px;
    border-bottom: 2px solid var(--border);
    background: var(--bg);
  }
  .conc-table th:not(:first-child) { text-align: right; }
  .conc-table td {
    padding: 8px 10px;
    border-bottom: 1px solid var(--border-light);
    font-variant-numeric: tabular-nums;
  }
  .conc-table td:not(:first-child) { text-align: right; }
  .conc-table tr:hover { background: var(--blue-bg); }
  .conc-table .row-total {
    font-weight: 700;
    border-top: 2px solid var(--border);
    background: var(--bg);
  }

  /* Risk indicator */
  .risk-tag {
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    padding: 1px 6px;
    border-radius: 3px;
  }
  .risk-high { background: var(--red-bg); color: var(--red); }
  .risk-med { background: var(--amber-bg); color: var(--amber); }
  .risk-low { background: var(--green-bg); color: var(--green); }

  /* Tabs for switching views */
  .tab-bar {
    display: flex;
    gap: 0;
    border-bottom: 2px solid var(--border);
    margin-bottom: 20px;
  }
  .tab {
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-tertiary);
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: color 0.15s, border-color 0.15s;
    font-family: var(--sans);
    background: none;
    border-top: none;
    border-left: none;
    border-right: none;
  }
  .tab:hover { color: var(--text-primary); }
  .tab.active {
    color: var(--text-primary);
    border-bottom-color: var(--text-primary);
  }
  .tab-content { display: none; }
  .tab-content.active { display: block; }

  /* Methodology / Source Notes */
  .methodology-box {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 16px 20px;
    margin: 16px 0;
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.5;
  }
  .methodology-box h4 {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
    margin-bottom: 8px;
  }

  /* Links & References */
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }

  .source-tag {
    font-size: 9px;
    color: var(--text-tertiary);
    font-style: italic;
  }

  /* Footer */
  .page-footer {
    margin-top: 40px;
    padding: 16px 0;
    border-top: 3px solid var(--text-primary);
    font-size: 11px;
    color: var(--text-tertiary);
    text-align: center;
  }

  /* Print button */
  .dl-btn {
    display: inline-block;
    padding: 10px 24px;
    background: var(--text-primary);
    color: white;
    border: none;
    border-radius: 5px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    font-family: var(--sans);
  }
  .dl-btn:hover { background: #333; }

  /* Two-column layout */
  .two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }
  @media (max-width: 800px) {
    .two-col { grid-template-columns: 1fr; }
    .chain-view { flex-direction: column; }
    .chain-arrow { transform: rotate(90deg); padding-top: 0; }
  }
</style>
</head>
```

### Core JavaScript Pattern

The dashboard uses vanilla JavaScript for interactivity. Include these functions in a `<script>` tag at the end of the body:

```javascript
<script>
// Tab switching
function switchTab(tabId) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
  document.getElementById(tabId).classList.add('active');
}

// Card expand/collapse
function toggleCard(cardId) {
  const card = document.getElementById(cardId);
  card.classList.toggle('expanded');
}

// Navigate to tier 2 view for a specific supplier
function drillDown(companyTicker) {
  // Switch to the tier-2 tab and scroll to the relevant section
  switchTab('tier2');
  const section = document.getElementById('tier2-' + companyTicker);
  if (section) {
    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    section.style.outline = '2px solid var(--accent)';
    setTimeout(() => { section.style.outline = 'none'; }, 2000);
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  // Set first tab active
  const firstTab = document.querySelector('.tab');
  if (firstTab) firstTab.click();
});
</script>
```

---

## DOCUMENT STRUCTURE

The HTML document has these sections. Every section is mandatory.

### Section 1: Print Button Bar
```html
<div class="no-print" style="text-align:center; padding:16px; background:var(--surface); border-bottom:1px solid var(--border);">
  <button class="dl-btn" onclick="window.print()">Download as PDF</button>
  <span style="font-size:12px; color:var(--text-tertiary); margin-left:12px;">or Cmd+P &rarr; Save as PDF</span>
</div>
```

### Section 2: Page Header
```html
<div class="page-header">
  <h1>[TICKER] &mdash; Supply Chain Map</h1>
  <div class="subtitle">[Full Company Name] &middot; Interactive Supply Chain Analysis</div>
  <div class="dateline">Prepared [Date] &middot; Data sourced from <a href="https://daloopa.com">Daloopa</a> &middot; TTM through [Latest Quarter]</div>
</div>
```

### Section 3: Target Company KPI Bar
Show 6 KPIs for the target company:
```html
<div class="container">
  <div class="kpi-bar">
    <div class="kpi-item"><div class="kpi-label">TTM Revenue</div><div class="kpi-value">$XXB</div></div>
    <div class="kpi-item"><div class="kpi-label">TTM COGS</div><div class="kpi-value">$XXB</div></div>
    <div class="kpi-item"><div class="kpi-label">Gross Margin</div><div class="kpi-value">XX.X%</div></div>
    <div class="kpi-item"><div class="kpi-label">Suppliers Mapped</div><div class="kpi-value">XX</div></div>
    <div class="kpi-item"><div class="kpi-label">Top 5 = % of COGS</div><div class="kpi-value">~XX%</div></div>
    <div class="kpi-item"><div class="kpi-label">Key Customers</div><div class="kpi-value">XX</div></div>
  </div>
```

### Section 4: Page Layout

The dashboard uses a **single scrollable page** (no tabs) with the following vertical order:
1. KPI bar (target company overview)
2. Canvas network visualization
3. Inventory Health Overview table
4. Supplier cards grouped by tier
5. Supply Chain Shock Analysis (narrative + impact matrix)
6. Concentration Analysis summary
7. Footer

Each supplier card is clickable — opening a **full-screen detail overlay** with 10-quarter financials, inventory tables, and Canvas charts. The overlay is dismissed with × or backdrop click.

### Section 5: Canvas Network Visualization

Replace the HTML card-based chain view with a **Canvas-based tier-grouped network**:

- Use a `<canvas>` element spanning the full container width, ~420px height
- **Column layout**: Tier 3 (left) → Tier 2 → Tier 1 → Target (center) → Customers (right)
- Draw each company as a rounded rectangle node with ticker label
- Draw connection lines (bezier curves or straight lines) between related nodes
- Color-code by tier: Target = dark (#1a1a1a), Tier 1 = coral (#d46b5c), Tier 2 = steel blue (#5b8db8), Tier 3 = muted sage, Customers = blue-gray
- **Clickable nodes**: Track click coordinates with a `click` event listener on the canvas, determine which node was clicked via hit-testing, then open the detail overlay for that company
- Column headers ("TIER 1", "TIER 2", "TARGET", etc.) drawn as text above each column
- Responsive: redraw on `window.resize`

```javascript
// Example network drawing function pattern:
function drawNetwork() {
  const cv = document.getElementById('networkCanvas');
  const ctx = cv.getContext('2d');
  cv.width = cv.parentElement.clientWidth;
  cv.height = 420;
  ctx.clearRect(0, 0, cv.width, cv.height);

  // Define columns: x positions for each tier
  const cols = {
    tier3: cv.width * 0.08,
    tier2: cv.width * 0.28,
    tier1: cv.width * 0.48,
    target: cv.width * 0.68,
    customers: cv.width * 0.88
  };

  // Draw column headers, nodes, and connection lines
  // Store node positions for hit-testing on click
}
```

### Section 5b: Inventory Health Overview

Below the network, add an **Inventory Health Overview** table showing all suppliers:

```
| Company | Ticker | Total Inventory | RM% | WIP% | FG% | Composition Bar |
```

- The "Composition Bar" column renders a stacked horizontal bar (RM = blue, WIP = amber, FG = green) using inline CSS `background: linear-gradient(...)`
- Sort by total inventory descending or by FG% descending (highest FG% = most demand-shock exposure)
- Include the target company at the top of the table
- Each inventory value must link to its Daloopa citation

### Section 5c: Supplier Cards by Tier

Below the inventory overview, render supplier cards grouped under tier headings:

```
── TIER 1 · Critical / Sole-Source ──────
[Card: TSMC]  [Card: Samsung]  [Card: Broadcom]  ...

── TIER 2 · Major Component ─────────────
[Card: Qualcomm]  [Card: Skyworks]  [Card: TXN]  ...

── TIER 3 · Specialty ───────────────────
[Card: Corning]  [Card: Cirrus Logic]  ...
```

Each card shows: Company name, ticker, what they supply, TTM revenue, gross margin, estimated % of target COGS, a colored dot for tier. Clicking a card opens the detail overlay.

### Section 6: Detail Overlay

When a user clicks a supplier card or network node, show a **full-screen overlay** with comprehensive detail:

**Structure:**
- Fixed overlay div covering the viewport with semi-transparent backdrop
- Close button (×) in top-right corner
- Content area with three sub-sections:

**6a. Financial History Table (10 Quarters)**
```
| Metric        | Q3'23 | Q4'23 | Q1'24 | ... | Q4'25 |
|---------------|-------|-------|-------|-----|-------|
| Revenue       | $XXB  | $XXB  | ...   |     |       |
| Gross Profit  | $XXB  | $XXB  | ...   |     |       |
| Net Income    | $XXB  | $XXB  | ...   |     |       |
| Gross Margin  | XX.X% | XX.X% | ...   |     |       |
```
- Every value must be a Daloopa citation link: `<a href="https://daloopa.com/src/{id}">$value</a>`
- Display currency unit in header (e.g., "USD $M", "NTD B", "KRW T")

**6b. Inventory Breakdown Table (10 Quarters)**
```
| Metric           | Q3'23 | Q4'23 | ... |
|------------------|-------|-------|-----|
| Raw Materials    | $XXM  | $XXM  | ... |
| Work in Process  | $XXM  | $XXM  | ... |
| Finished Goods   | $XXM  | $XXM  | ... |
| Total Inventory  | $XXM  | $XXM  | ... |
| RM%              | XX%   | XX%   | ... |
| WIP%             | XX%   | XX%   | ... |
| FG%              | XX%   | XX%   | ... |
```
- Absolute values are Daloopa citation links; percentages are computed (no link needed)

**6c. Canvas Chart — Inventory Composition vs. Gross Margin**
- **Stacked bar chart**: Each bar represents a quarter. Segments = RM (blue), WIP (amber), FG (green), stacked to total inventory value
- **Line overlay**: Gross Margin % plotted as a line with dots on the right Y-axis (0-100%)
- **Left Y-axis**: Inventory value in reporting currency
- **X-axis**: Quarter labels (Q3'23, Q4'24, etc.)
- Draw using Canvas 2D API with `createElement('canvas')`, NOT any charting library
- Include a legend below the chart

### Section 7: Supply Chain Shock Analysis

A dedicated section (below the supplier cards) analyzing how a shock to the target company would propagate:

**7a. Narrative Analysis** — 3-4 paragraphs covering:
- "Most Exposed Suppliers" — those with highest revenue dependency on target
- "Resilient Suppliers" — diversified revenue, low target concentration
- "Second-Order Effects" — how Tier 2/3 suppliers are indirectly affected
- "Key Monitoring Metrics" — inventory days, order backlogs, WIP trends to watch

**7b. Impact Matrix Table**
```
| Supplier | Tier | Rev. from Target | Revenue Impact | Margin Impact | Inventory Risk | Overall |
|----------|------|------------------|---------------|---------------|----------------|---------|
| TSMC     | 1    | ~25%             | HIGH          | MEDIUM        | LOW            | HIGH    |
| ...      |      |                  |               |               |                |         |
```
- Color-code risk cells: HIGH = red background, MEDIUM = amber, LOW = green
- Sort by Overall Risk descending

### Section 8: Concentration Analysis

Summary of supplier and revenue concentration with risk flags:
- Supplier concentration: flag any supplier >20% of COGS
- Revenue dependency: flag any supplier where target is >25% of their revenue
- Geographic concentration: note country exposure (Taiwan, China, South Korea, etc.)
- Single-source dependencies: list sole-source suppliers

### Section 10: Footer
```html
  <div class="page-footer">
    Data sourced from <a href="https://daloopa.com">Daloopa</a>. All financial figures link to original source filings.
    Prepared [Date]. Supply chain relationships are based on public filings, analyst research, and industry reports. Not investment advice.
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
- Calculated metrics (margins, growth rates, % estimates derived from multiple sources) do NOT need citation links
- Document search results must cite: `<a href="https://marketplace.daloopa.com/document/{document_id}">[Filing]</a>`
- Never fabricate fundamental IDs — only use IDs returned from the API
- For estimated figures (% of COGS, % of revenue), always explain the methodology in the detail panel

### Financial Formatting
- Revenue/income in billions: `$XXB` or `$X.XB`
- Revenue/income in millions: `$X,XXX` (with comma separator)
- Margins: `XX.X%` (one decimal place)
- Percentages for supply chain: `~XX%` (use tilde for estimates)
- Use `&ndash;` for ranges, `&mdash;` for em-dashes, `&middot;` for separators

### Concentration Risk Classification
- **HIGH** (red): >15% of COGS, sole/single source, or geopolitical risk
- **MED** (amber): 5-15% of COGS, limited alternatives, or moderate switching costs
- **LOW** (green): <5% of COGS, multiple alternatives, easy to switch

### Supply Chain Data Quality
- Always distinguish between **disclosed** (from 10-K, investor reports) and **estimated** (from analyst research, proportional analysis)
- When estimating % of COGS, show your math: "TSMC Apple revenue ~$70B (per TSMC 10-K customer disclosure) / Apple TTM COGS ~$200B = ~35%"
- Use `~` prefix for all estimates
- Include source attribution for every data point in the detail panel
- If a figure cannot be reliably estimated, say "Not disclosed" rather than guessing

### Interactivity Rules
- Every company card and network node must be clickable to open a detail overlay
- Detail overlays show: 10-quarter financials, 10-quarter inventory breakdown, Canvas inventory chart, business description
- Close overlay with × button or clicking the backdrop
- Network visualization must redraw on window resize
- All interactions must be smooth and not reload the page

### DOM Safety Rules (CRITICAL)
- ALL JavaScript DOM construction MUST use `createElement()` + `textContent` + `appendChild()`
- NEVER use `innerHTML`, `outerHTML`, or any HTML-string-based injection methods
- NEVER use DOM write/writeln methods
- Define compact helper functions to keep DOM construction code readable:
  - `ce(tag)` → `document.createElement(tag)`
  - `ca(el, attrs)` → sets attributes/textContent on an element
  - `cA(parent, children)` → appends array of children to parent
- This is required because security hooks will block the file if HTML-string injection is detected

---

## EXECUTION SEQUENCE

Follow this exact sequence:

1. **discover_companies** → get target company_id
2. **discover_company_series + get_company_fundamentals** → pull target company financials (revenue, COGS, margins) AND inventory series for 10 quarters
3. **search_documents + WebSearch** → identify suppliers (run in parallel, multiple queries)
4. **discover_companies** → look up each identified supplier by ticker (batch all at once)
5. **discover_company_series** → for each supplier, pull BOTH financial series (revenue, GP, NI, GM) AND inventory series (RM, WIP, FG, total) — batch these in parallel
6. **get_company_fundamentals** → pull 10 quarters of data for all suppliers (batch in parallel, group series_ids per company)
7. **search_documents + WebSearch** → determine revenue concentration for each supplier (parallel)
8. **WebSearch** → identify customers where target is a supplier
9. **discover_companies + get_company_fundamentals** → pull customer financials
10. **Repeat lighter version of 3-6** for Tier 2 (top 3-5 Tier 1 suppliers' suppliers)
11. **Shock Analysis** → classify suppliers by dependency, assess propagation, build impact matrix
12. **Synthesize** → organize all data (financials, inventory breakdowns, shock analysis) into the framework
13. **Write HTML** → generate the complete self-contained HTML file using DOM-safe JavaScript (no HTML-string injection)
14. **Save & Open** → write to `~/Generated Stuff/[TICKER]-supply-chain.html` and open in browser

For steps 2-10, maximize parallelism — run independent searches and API calls concurrently. The 10-quarter pull is the most data-intensive step; batch aggressively.

After writing the file, always end with:
> Data sourced from Daloopa
