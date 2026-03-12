# Auto-generated MCP prompt functions from .claude/skills/
# Source: https://github.com/daloopa/investing
#
# Each function returns a prompt string that instructs an LLM to perform
# the same analysis as the corresponding Claude Code skill, using only
# Daloopa MCP tools (no file system, no infra scripts).
#
# Skills converted: earnings, tearsheet, industry, bull_bear, guidance_tracker,
#   inflection, capital_allocation, dcf, comps, supply_chain, research_note,
#   build_model, comp_sheet, ib_deck, initiate
# Skipped: setup (interactive setup wizard — not an analytical skill)
# Skipped: update (requires prior context JSON from file system — not portable to MCP prompt)
# Shared references inlined: data-access.md, design-system.md
# Date: 2026-03-09

from app.daloopa_mcp import daloopa_mcp

# ============================================================================
# Shared prompt blocks — composed into per-skill prompts via f-strings.
# At runtime each function's f-string interpolates the relevant blocks
# to build a self-contained prompt the LLM receives.
# ============================================================================

_DALOOPA_TOOLS = """\
## Daloopa MCP Tools

| Operation | Tool |
|---|---|
| Find company by ticker/name | `discover_companies(keywords=["TICKER"])` → returns `company_id`, `latest_calendar_quarter`, `latest_fiscal_quarter` |
| Find available series/metrics | `discover_company_series(company_id, keywords, periods)` |
| Pull financial data | `get_company_fundamentals(company_id, periods, series_ids)` |
| Search SEC filings | `search_documents(keywords, company_ids, periods)` |
"""

_PERIOD_DETERMINATION = """\
## Period Determination

After `discover_companies`, capture `latest_calendar_quarter` and `latest_fiscal_quarter`. Use `latest_calendar_quarter` to calculate all period arrays:

| Need | Calculation |
|---|---|
| Last 4 quarters | Work backward 4Q from `latest_calendar_quarter` |
| Last 8 quarters | Work backward 8Q from `latest_calendar_quarter` |
| Last 10 quarters | Work backward 10Q from `latest_calendar_quarter` |
| Last 4Q + YoY | 8 quarters: latest 4 + same 4 one year prior |
| Document search (recent) | Latest 2 quarters from `latest_calendar_quarter` |

Example: if `latest_calendar_quarter` = "2025Q4", last 8Q = ["2024Q1", "2024Q2", "2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3", "2025Q4"]

**NEVER assume the current calendar date determines the latest available quarter — always use the field returned by `discover_companies`.**

### Fiscal Year Context
- **Single-company analysis**: Use `fiscal_period` labels when presenting data (e.g., "FQ1'26" for Apple's Oct-Dec quarter).
- **Multi-company comparison**: Use `calendar_period` labels to normalize across different fiscal year ends.
- **API input is always calendar quarters** — never pass `latest_fiscal_quarter` values to the API. Always calculate period arrays from `latest_calendar_quarter`.
"""

_CITATIONS = """\
## Citation Requirements (MANDATORY)

Every Daloopa-sourced figure MUST include a citation link. No exceptions.

Format: `[$X.XX million](https://daloopa.com/src/{fundamental_id})`

- Capture `fundamental_id` (the `id` field) from every `get_company_fundamentals` response
- Carry IDs through to ALL output — tables, prose, computations
- Computed values (margins, growth rates) cite their underlying inputs
- Document citations: `[Document Name](https://marketplace.daloopa.com/document/{document_id})`
"""

_NUMBER_FMT = """\
## Number Formatting

| Type | Format | Example |
|------|--------|---------|
| Currency (large) | `$X.Xbn` or `$X,XXXmm` | `$95.4bn`, `$2,345mm` |
| Currency (small) | `$X.XX` or `$X,XXX` | `$6.08`, `$1,234` |
| Percentages | One decimal + `%` | `42.3%` |
| Multiples | One decimal + `x` | `8.5x EV/EBITDA` |
| Growth rates | Signed + `%` + context | `+12.3% YoY` |
| Basis points | Signed + `bps` | `+150bps` |
| Share counts | `X.XXbn` or `X,XXXmm` shares | `15.33bn shares` |

Right-align all numbers in tables. Never display raw unformatted numbers.
"""

_TABLE_CONV = """\
## Table Conventions

- **Columns** = time periods (left to right, chronological)
- **Rows** = metrics (grouped by category: P&L, margins, per-share, balance sheet)
- Include YoY growth rates as sub-rows in italics
- Highlight beats/misses: `$1.52 (beat +3.2%)`
- Source row at bottom: `Source: Daloopa (company filings)`
- Group related metrics — no single-metric tables
"""

_ANALYTICAL_VOICE = """\
## Analytical Density

Every data point includes three layers:
1. **The data point** — with Daloopa citation
2. **Context** — vs. prior period, peers, guidance, consensus
3. **Implication** — margin expansion, deceleration, thesis risk

## Commentary Blocks

After every major data table, 2-3 sentence interpretation:
1. What the data shows — trend, inflection, anomaly
2. Why it matters — positioning, estimate risk, thesis confirmation
3. What to watch — catalyst, guidance change, peer divergence
4. What could go wrong — risks, sustainability

## Analyst's Perspective

Write as a long/short equity investor doing fundamental research.
- **Be critical, not promotional.** Management narratives are marketing until proven by data.
- **Challenge the numbers.** Look for quality-of-earnings issues: pulled-forward revenue, unsustainable margins, aggressive accounting.
- **Be honest about valuation.** Don't anchor to current price.
- **Flag red flags explicitly.** Deteriorating cash conversion, GAAP vs non-GAAP gaps, rising DSOs, guidance cuts disguised as conservatism.
- **Assign conviction.** Don't hedge when data is clear. Use "decelerating," "deteriorating," "unsustainable," "mispriced" when warranted.
- **Separate signal from noise.** 10bps margin fluctuation = noise; 300bps = signal.
"""

_MARKET_DATA = """\
## Market Data

Gather using the following resolution order (use the first available source):
1. **MCP tools** — Check available tools for any MCP server that provides market data (stock quotes, multiples, historical prices). This is the preferred path.
2. **Infra scripts** — If no market-data MCP is available, use `python infra/market_data.py` as fallback (quote, multiples, history, peers, risk-free-rate subcommands).
3. **Web search** — If neither MCP nor infra scripts are available, use web search.
4. **Defaults** — If no source is available, use defaults (beta=1.0, risk-free rate=4.5%) and note the limitation.

Data needed:
- **Stock quote**: Current price, market cap, shares outstanding, beta
- **Trading multiples**: Trailing P/E, Forward P/E, EV/EBITDA, P/S, P/B, dividend yield
- **Historical prices**: OHLCV for trend analysis (if needed)
- **Peer multiples**: Side-by-side multiples for comparable companies
- **Risk-free rate**: 10Y Treasury yield (for WACC/DCF)
"""

_CONSENSUS = """\
## Consensus Estimates (Optional)

When available, consensus estimates add context:
- **Consensus revenue / EPS** — beat/miss vs. Street
- **Forward estimates (NTM)** — forward P/E, forward EV/EBITDA
- **Estimate revisions** — expectations trending up/down/stable
- **Price targets** — consensus target and range

If not available, skip and note "consensus data not available."
"""

_KPI_TAXONOMY = """\
Think about what KPIs matter most for THIS company's business model:
- **SaaS/Cloud**: ARR, net revenue retention, RPO/cRPO, customers >$100K, cloud gross margin
- **Consumer Tech**: DAU/MAU, ARPU, engagement, installed base, paid subscribers
- **E-commerce/Marketplace**: GMV, take rate, active buyers/sellers, order frequency
- **Retail**: same-store sales, store count, average ticket, transactions
- **Telecom/Media**: subscribers, churn, ARPU, content spend
- **Hardware**: units shipped, ASP, attach rate, installed base
- **Financial Services**: AUM, NIM, loan growth, credit quality, fee income ratio
- **Pharma/Biotech**: pipeline stage, patient starts, scripts, market share
- **Industrials/Energy**: backlog, book-to-bill, utilization, production volumes, reserves"""

_GUIDANCE_RULES = """\
## Guidance vs Actuals Offset Rules

- **Quarterly guidance**: Q(N) guidance applies to Q(N+1) results
- **Annual guidance from Q1/Q2/Q3**: Applies to current fiscal year
- **Annual guidance from Q4**: Applies to NEXT fiscal year
- NEVER compare same-quarter guidance to same-quarter actual
"""

_HTML_TEMPLATE = """\
## HTML Report Output

Present the analysis as a **complete, self-contained HTML document** using the template below. The HTML must include all CSS inlined in a `<style>` tag — no external dependencies.

**Citation format in HTML:**
- Financial figures: `<a href="https://daloopa.com/src/{fundamental_id}">$X.XX million</a>`
- Document citations: `<a href="https://marketplace.daloopa.com/document/{document_id}">Document Name</a>`

### HTML Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
:root {
    --navy: #1B2A4A;
    --steel-blue: #4A6FA5;
    --gold: #C5A55A;
    --green: #27AE60;
    --red: #C0392B;
    --light-gray: #F8F9FA;
    --mid-gray: #E9ECEF;
    --dark-gray: #6C757D;
    --near-black: #343A40;
}
@page { size: A4; margin: 20mm 15mm; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Arial, sans-serif; font-size: 12px; line-height: 1.6; color: var(--near-black); max-width: 100%; margin: 0 auto; padding: 20px 40px; }
h1 { font-size: 24px; font-weight: bold; color: var(--navy); border-bottom: 3px solid var(--navy); padding-bottom: 8px; margin-top: 0; margin-bottom: 16px; }
h2 { font-size: 18px; font-weight: bold; color: var(--navy); border-bottom: 1px solid var(--mid-gray); padding-bottom: 4px; margin-top: 24px; margin-bottom: 12px; }
h3 { font-size: 14px; font-weight: bold; color: var(--steel-blue); margin-top: 16px; margin-bottom: 8px; }
p { margin-bottom: 8px; }
a { color: var(--steel-blue); text-decoration: none; }
strong { font-weight: 600; }
em { font-style: italic; color: var(--dark-gray); }
blockquote { border-left: 4px solid var(--steel-blue); background: var(--light-gray); padding: 12px 16px; margin: 12px 0; font-size: 11px; }
table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 11px; font-variant-numeric: tabular-nums; }
thead { background: var(--navy); color: white; }
th { padding: 8px 10px; text-align: left; font-weight: 600; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; }
td { padding: 6px 10px; border-bottom: 1px solid var(--mid-gray); }
td:not(:first-child), th:not(:first-child) { text-align: right; }
tr:nth-child(even) { background: var(--light-gray); }
tr:hover { background: #EDF2F7; }
ul, ol { padding-left: 20px; margin-bottom: 8px; }
li { margin-bottom: 4px; }
hr { border: none; border-top: 1px solid var(--mid-gray); margin: 20px 0; }
.footer { text-align: center; font-size: 9px; color: var(--dark-gray); font-style: italic; margin-top: 24px; padding-top: 8px; border-top: 1px solid var(--mid-gray); }
    </style>
</head>
<body>

<!-- Report content goes here -->

<div class="footer">Data sourced from Daloopa</div>
</body>
</html>
```
"""

_EXCEL_ARTIFACT = """\
## Excel Output via Artifact

Create a React artifact that builds and downloads the .xlsx in-browser:
- Use SheetJS (`import * as XLSX from "xlsx"`) to construct the workbook — the package name is "xlsx", NOT "sheetjs"
- Create the sheets listed below with headers in row 1, data from row 2
- Apply number formatting (currency, percentages, multiples), column widths, frozen header rows
- Include a prominent "Download .xlsx" button using the base64 + data URI method (see below)
- Show interactive HTML table previews of key sheets above the download button
- Include Daloopa citation hyperlinks in cells where supported

CRITICAL — Download method (sandbox-safe):
```js
const wbout = XLSX.write(wb, { bookType: "xlsx", type: "base64" });
const a = document.createElement("a");
a.href = "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64," + wbout;
a.download = "file.xlsx";
document.body.appendChild(a);
a.click();
document.body.removeChild(a);
```
NEVER use `XLSX.writeFile()` or `URL.createObjectURL()` — both are blocked in the artifact sandbox.
"""


# ============================================================================
# /setup — SKIPPED
# Interactive setup wizard for Claude Code auth. Not an analytical skill.
# ============================================================================


# ============================================================================
# 1. ANALYTICAL HTML SKILLS
# ============================================================================


@daloopa_mcp.prompt
def earnings(ticker: str) -> str:
    """Earnings"""
    return f"""\
Perform a comprehensive earnings analysis for {ticker}.

{_DALOOPA_TOOLS}
{_PERIOD_DETERMINATION}
{_CITATIONS}
{_NUMBER_FMT}
{_TABLE_CONV}
{_ANALYTICAL_VOICE}
{_GUIDANCE_RULES}

## Analysis Steps

### 1. Company Lookup
Look up {ticker} using `discover_companies`. Capture:
- `company_id`
- `latest_calendar_quarter` — anchor for all period calculations below
- `latest_fiscal_quarter`
- Firm name for report attribution (default: "Daloopa")

### 2. Core Financial Metrics
Calculate 8 quarters backward from `latest_calendar_quarter`. Search for and pull:

**Income Statement:** Revenue, Gross Profit, Operating Income/EBIT, EBITDA (compute as Op Income + D&A if not reported — label "(calc.)"), Net Income, Diluted EPS, SG&A, R&D.

**Cash Flow:** Operating Cash Flow, CapEx, Free Cash Flow (OCF - CapEx — label "(calc.)"), D&A.

Mark derived metrics "(calc.)". Flag one-time items with footnotes.

### 3. Company-Specific KPIs
{_KPI_TAXONOMY}

Search by name, plus cast a wider net. Also search for segment/product and geographic revenue breakdowns. Pull same 8-quarter period. Note gaps.

### 4. Growth & Margins
- YoY revenue growth for each of the last 4 quarters
- Gross, operating, EBITDA, net margin trends over 8 quarters
- EPS growth YoY for each of the last 4 quarters
- Segment and geographic revenue YoY growth (most recent quarter)
- KPI growth rates where applicable
- Note seasonality if applicable

### 4.5. Cost Structure & Margin Drivers

**COGS Analysis:** Pull product/services COGS if available. Identify 3-5 biggest cost items and YoY trends. Is COGS growing faster or slower than revenue?

**OpEx Breakdown:** R&D and SG&A separately for 8 quarters. Compute R&D % and SG&A % of revenue trends. Flag quarters where OpEx growth exceeds revenue growth (operating deleverage).

**Margin Driver Synthesis:** For each major margin (gross, operating, net), 1-2 sentences on drivers: pricing power vs cost inflation, mix shift, scale leverage, one-time items, FX impact.

### 5. Guidance vs Actuals
Search for guidance series (revenue, EPS, margin, OpEx, KPI guidance). If available:
- Pull guidance and actuals; apply +1 quarter offset
- Calculate beat/miss amounts and percentages
- Note patterns (consistent beats, narrows, etc.)
- For directional guidance, compare against actual growth rate
If no formal guidance exists, note that.

### 6. Consensus Context
If consensus estimates are available: consensus revenue/EPS vs actual (beat/miss vs Street), estimate revision trends, note source. If unavailable, note "consensus data not available."

### 7. Management Commentary
Search SEC filings via `search_documents` with multiple keyword sets:
- "results" or "record" — earnings highlights
- "outlook" or "guidance" — forward commentary
- Strategy-specific terms for {ticker} (e.g., "AI", "cloud", "subscribers")
- If empty, try broader single-keyword searches

Extract: results/drivers, forward outlook, segment highlights, notable call-outs, direct quotes with document citations.

### 7.5. News Context
Web search for:
1. "{ticker} [company name] earnings [latest quarter]" — analyst reactions
2. "{ticker} analyst price target" — sell-side sentiment

Distill into 3-5 bullets: stock reaction, analyst takeaways, price target changes, macro context.

### 7.6. Forward Outlook & Revenue Drivers

**Forward Guidance:** What is management guiding? Conservative or aggressive vs historical beat rate, run rate, consensus? How does it compare to trailing trends?

**Revenue Decomposition:** Volume vs price vs mix. Unit economics: units x ASP, subscribers x ARPU, GMV x take rate. What must happen for growth to sustain?

**KPI Trajectory:** Connect KPI trends to revenue outlook. Flag backlog/RPO/deferred revenue as leading indicators. Note KPI-to-revenue divergences.

**Trend Synthesis:** Accelerating, decelerating, or plateau over 4-8 quarters? Most important metric to watch next quarter? Are KPIs leading or lagging financials?

**Risks:** What could break? 2-3 biggest risks: competitive, macro, product cycle, regulatory, concentration.

### 7.7. Read-Throughs & Competitive Implications

Every company's earnings contain signal about adjacent companies — suppliers, customers, competitors, and the broader industry.

**Identify the Read-Through Universe:**
- **Suppliers**: If revenue/COGS/CapEx changed materially, which suppliers feel it? (e.g., AAPL iPhone strength → TSMC, Broadcom, Corning benefit)
- **Customers**: If this company is a major input, what do pricing/volume trends imply? (e.g., TSMC price increases → margin pressure for AAPL, AMD, NVDA)
- **Direct competitors**: How does this quarter compare to peers? Gaining or losing share?
- **Indirect competitors / substitutes**: Demand shifting between categories?
- **Industry bellwether signals**: What do results say about the macro/sector?

**For each read-through (aim for 5-8), state:**
1. **The affected company** (ticker + name)
2. **The specific data point** from this earnings that creates the read-through — cite the Daloopa figure
3. **The implication** — bullish or bearish for the adjacent company, and why
4. **Confidence level** — direct/disclosed (high) or inferred/estimated (moderate)?

**Sequencing context:** Note whether {ticker} reported before or after peers this earnings season. If early, read-throughs are predictions; if late, compare against what peers already reported.

**Web research:** Run 1-2 searches to validate:
- "{ticker} earnings read through implications" — analyst commentary on cross-company signals
- "{ticker} [peer ticker] competitive positioning" — specific competitive dynamics

Present grouped by relationship type: Suppliers / Customers / Competitors / Industry. Each read-through = 2-3 sentences with data citation, affected name, and implication.

## Output

{_HTML_TEMPLATE}

Include these sections in the HTML report:
- Executive summary (2-3 sentences + 2-3 most notable findings)
- Core financial metrics table (8 quarters, periods as columns)
- Segment and geographic revenue tables
- KPI table (with gap notes)
- Margin trends table (8 quarters) + cost structure commentary
- YoY growth rates table (last 4 quarters)
- Guidance vs actuals table (if applicable) with pattern analysis
- News context
- Forward outlook and revenue drivers
- Management commentary with quotes and document citations
- Read-throughs & competitive implications (grouped by Suppliers / Customers / Competitors / Industry)

Highlight 2-3 findings with critical lens: quality of earnings, red flags, what the market is missing.
"""


@daloopa_mcp.prompt
def tearsheet(ticker: str) -> str:
    """Tearsheet"""
    return f"""\
Generate a concise company tearsheet for {ticker}. Quick one-page overview — the snapshot an analyst pulls up before a meeting.

{_DALOOPA_TOOLS}
{_PERIOD_DETERMINATION}
{_CITATIONS}
{_NUMBER_FMT}
{_TABLE_CONV}
{_ANALYTICAL_VOICE}

## Analysis Steps

### 1. Company Lookup
Look up {ticker} using `discover_companies`. Capture:
- `company_id`
- `latest_calendar_quarter` — anchor for all period calculations below
- `latest_fiscal_quarter`
- Firm name for report attribution (default: "Daloopa")

### 2. Key Financials
Calculate periods backward from `latest_calendar_quarter` (8 quarters total: last 4 + year-ago for each to enable YoY). Revenue, Gross Profit, Operating Income, EBITDA (compute as Op Income + D&A if needed — "(calc.)"), Net Income, Diluted EPS, Operating Cash Flow, CapEx, Free Cash Flow (OCF - CapEx — "(calc.)").

### 3. Key Operating KPIs
Strictly **business-driver metrics** — NOT financial statement items.

{_KPI_TAXONOMY}

Search by name plus wider net. Also search segment/product and geographic revenue.

If the company discloses few KPIs, acknowledge the gap explicitly. Always search broadly — try "installed", "active", "subscriber", segment-level margins.

### 3b. Capital Return
Pull share count, share repurchases, dividends paid. Separate section from KPIs.

### 4. Key Ratios
Show 4-quarter trend with YoY for EACH quarter: Gross Margin %, Operating Margin %, EBITDA Margin %, Net Margin %, Revenue Growth YoY, EPS Growth YoY. Note seasonality if applicable.

### 5. Recent Developments
Search most recent 2 quarters of filings via `search_documents`:
- "results" / "record" — earnings highlights
- "outlook" / "guidance" — forward commentary
- Strategy-specific terms for {ticker}

Extract: business description (2-3 sentences), key developments, management priorities, notable quotes. 3-5 bullets max.

### 6. Five Key Tensions
5 most critical bull/bear debates. Each is one line framing both sides. Alternate bullish/bearish leaning. Every tension references a specific data point.

### 7. News Snapshot
Web search for recent context. Distill into 3-5 key events from last 6 months: date, one-line headline, sentiment tag (Positive / Negative / Mixed / Upcoming).

### 8. What to Watch
**Quantitative Monitors** — 5 metrics with thresholds:
"Metric: current value → bull threshold / bear threshold"
Choose the 5 that matter most for THIS company's thesis.

## Output

{_HTML_TEMPLATE}

Include these sections in the HTML report:
1. Company Overview (2-3 sentences)
2. Five Key Tensions (numbered, with data citations)
3. Key Financials table (4 quarters, derived metrics marked "(calc.)")
4. Segment / Geographic Breakdown table
5. Key Operating KPIs table (business-driver only; note gaps)
6. Capital Return table
7. Margins & Growth table (each quarter's YoY)
8. Recent Developments (bullets with document citations)
9. News Snapshot (3-5 events with sentiment tags)
10. What to Watch (5 quantitative monitors)

Close with 2-3 sentence honest assessment: biggest risk, valuation warranted?
"""


@daloopa_mcp.prompt
def industry(tickers: str) -> str:
    """Industry"""
    return f"""\
Perform an industry comparison across these companies: {tickers}

(Tickers are space-separated. Look up each one.)

{_DALOOPA_TOOLS}
{_PERIOD_DETERMINATION}
{_CITATIONS}
{_NUMBER_FMT}
{_TABLE_CONV}
{_ANALYTICAL_VOICE}

## Analysis Steps

### 1. Company Lookups
Look up all tickers using `discover_companies`. For each company, capture:
- `company_id`
- `latest_calendar_quarter` — use the earliest `latest_calendar_quarter` across all companies as the anchor for period calculations
- `latest_fiscal_quarter`
- Note each company's fiscal year end — critical for calendar quarter alignment
- Firm name for report attribution (default: "Daloopa")

### 2. Comparable Financial Metrics
Calculate 8 quarters backward from the anchor `latest_calendar_quarter`. For each company, pull:

**Income Statement:** Revenue, Gross Profit/Margin, Operating Income/Margin, EBITDA (compute if needed — "(calc.)"), Net Income/Margin, Diluted EPS, R&D Expense, Stock-Based Compensation.

**Cash Flow:** Operating Cash Flow, CapEx, Free Cash Flow (OCF - CapEx — "(calc.)"), D&A.

### 3. Company-Specific KPIs
{_KPI_TAXONOMY}

For each company, discover and pull the most relevant KPIs. Note which are common across the group (apples-to-apples) vs unique. For mixed-sector comparisons, focus on KPIs for largest revenue segments.

### 4. Normalize & Compare
- **Calendar quarter alignment is critical.** Map fiscal quarters to calendar quarters.
- Build side-by-side comparison tables
- Calculate margins for ALL 4 recent quarters (not just latest)
- Calculate YoY growth rates for each of the last 4 quarters

### 5. Ranking & Analysis
- Rank companies on each key metric (revenue growth, margins, FCF yield, etc.)
- Identify leader and laggard per metric
- Flag outliers (unusually high/low margins, accelerating/decelerating growth)
- Compute R&D % of revenue and SBC % of revenue per company
- Show segment YoY growth rates for most recent quarter
- Flag one-time items that distort comparisons

### 6. Document Search
For each company, search most recent 2 quarters via `search_documents` with multiple queries:
- "competition" / "market share" — competitive positioning
- "industry" / "market" / "demand" — industry trends
- "differentiate" / "advantage" — strategic differentiation
- "growth" / "opportunity" — growth strategy
- "macro" / "headwind" / "tariff" — headwinds

Extract per company: competitive position, strategic priorities, industry/macro commentary, references to competitors. If sparse, try broader keywords.

## Output

{_HTML_TEMPLATE}

Include these sections in the HTML report:
- Summary header listing all companies with fiscal year ends
- Side-by-side financial metrics table (last 4 calendar quarters, companies as columns)
- Trailing 4Q totals for revenue, operating income, net income, EPS, OCF, CapEx, FCF
- Margin trend table: gross, operating, net for ALL 4 quarters per company
- Growth table: Revenue YoY and EPS YoY for each of last 4 quarters per company
- R&D and SBC comparison: % of revenue per company
- Segment revenue tables per company with YoY growth
- KPI comparison (common vs company-specific)
- Cash flow comparison: OCF, CapEx, FCF, CapEx % of revenue
- Rankings summary table
- Competitive insights from filings with document citations
- Calendar quarter alignment note

Give a clear competitive verdict: Who is winning/losing? Strongest position and why? Most vulnerable? Structurally mispriced? Don't hedge — rank honestly.
"""


@daloopa_mcp.prompt
def bull_bear(ticker: str) -> str:
    """Bull / Bear"""
    return f"""\
Build a bull/bear/base case scenario framework for {ticker}.

{_DALOOPA_TOOLS}
{_PERIOD_DETERMINATION}
{_CITATIONS}
{_NUMBER_FMT}
{_TABLE_CONV}
{_ANALYTICAL_VOICE}

## Analysis Steps

### 1. Company Lookup
Look up {ticker} using `discover_companies`. Capture:
- `company_id`
- `latest_calendar_quarter` — anchor for all period calculations below
- `latest_fiscal_quarter`
- Firm name for report attribution (default: "Daloopa")

### 2. Historical Financial Baseline
Calculate 8 quarters backward from `latest_calendar_quarter`. Pull: Revenue, Gross Profit/Margin, Operating Income/Margin, EBITDA (compute if needed — "(calc.)"), Net Income, Diluted EPS, Operating Cash Flow, CapEx, Free Cash Flow (OCF - CapEx — "(calc.)"), Segment revenue, Geographic revenue.

Compute trailing 4Q totals for revenue, EBITDA, net income, EPS, FCF — these are the scenario baseline. Flag one-time items.

### 3. Key Operating KPIs
{_KPI_TAXONOMY}

Search and pull those KPIs — building blocks for bottoms-up scenario math. Also pull capital allocation data: share count, buybacks, dividends.

### 4. Qualitative Research
Search filings via `search_documents` with multiple queries:
- "risk" / "uncertainty" / "challenge" — risk factors
- "growth" / "opportunity" / "expansion" — growth drivers
- "competition" / "market share" — competitive dynamics
- "outlook" / "guidance" / "expect" — management outlook
- "repurchase" / "dividend" — capital allocation
- "tariff" / "regulatory" — macro/regulatory

### 5. Consensus Positioning
If consensus available: note where consensus revenue/EPS sits vs your base case, whether market is positioned closer to bull or bear, recent revision trends. If unavailable, skip.

### 6. Construct Three Scenarios

For each scenario, build a **bottoms-up revenue model** showing segment-level assumptions (units x ASP, subscribers x ARPU, segment growth rates). Show the math.

**Bull Case:** Most favorable realistic trajectory. Revenue acceleration, margin expansion, KPI improvement, favorable macro/competitive shifts. Quantify using historical highs. Show segment build. List catalysts. Consider buyback amplification of EPS.

**Base Case:** Extrapolation of current trends. Continuation of recent growth, stable margins, steady KPI progression. Most likely scenario grounded in last 4-8 quarters. Show segment build. Reference historical analogs.

**Bear Case:** Realistic downside risks. Revenue deceleration, margin compression, KPI deterioration, competitive/macro headwinds. Quantify using historical lows and filing risk factors. Show segment build. List risks. Consider capital allocation in downturns.

**Probability Weighting:** Don't default to 25/50/25. Assign probabilities informed by the most recent data:
- If recent results accelerating → weight bull higher
- If macro headwinds intensifying → weight bear higher
- Explain your reasoning

**Be honest about which scenario is most likely.** Don't default to bullish framing. If the bear case is more probable, say so clearly. If the bull case requires multiple things to go right simultaneously, acknowledge that compounds the risk.

## Output

{_HTML_TEMPLATE}

Include these sections in the HTML report:
- Company overview and current state
- Historical financial data table (8 quarters, with computed EBITDA/FCF)
- Trailing 4Q totals as scenario baseline
- Segment and geographic revenue tables
- KPI trends table
- Capital allocation summary
- Three scenario sections each with: key assumptions, bottoms-up segment build, implied revenue/margin/EPS trajectory, implied KPI trajectory, catalysts/risks
- Probability-weighted summary with reasoning
- Risk factors and growth drivers from filings (document citations)
- Summary comparison table across scenarios
- Key swing factors — 3-5 variables that determine which scenario plays out

Highlight: most likely scenario and why, key swing factors, where the market is currently positioned.
"""


@daloopa_mcp.prompt
def guidance_tracker(ticker: str) -> str:
    """Guidance Tracker"""
    return f"""\
Track management guidance accuracy for {ticker}.

{_DALOOPA_TOOLS}
{_PERIOD_DETERMINATION}
{_CITATIONS}
{_NUMBER_FMT}
{_TABLE_CONV}
{_ANALYTICAL_VOICE}
{_GUIDANCE_RULES}

## Analysis Steps

### 1. Company Lookup
Look up {ticker} using `discover_companies`. Capture:
- `company_id`
- `latest_calendar_quarter` — anchor for all period calculations below
- `latest_fiscal_quarter`
- Firm name for report attribution (default: "Daloopa")

### 2. Discover Guidance Series
Search with keywords: "guidance", "outlook", "estimate", "forecast", "target".

**Financial guidance:** Revenue, EPS, operating income/margin, EBITDA, segment revenue, CapEx, FCF guidance.

**Operational KPI guidance** (often more informative than financial): subscriber/user count, unit shipments, ARPU/ASP, same-store sales, GMV/bookings, net revenue retention, store openings, production volume guidance. Search explicitly: "subscriber guidance", "unit guidance", "ARPU guidance", etc.

### 3. Pull Guidance Data
Calculate 8+ quarters backward from `latest_calendar_quarter`. Pull all discovered guidance series for those periods.

### 4. Pull Actual Results
For each guidance metric, pull corresponding actual result series for the same periods.

### 5. Build Guidance vs Actuals Tracker
Apply offset rules:
- Quarterly: Q(N) guidance → Q(N+1) actual
- Annual from Q1/Q2/Q3 → current FY actual
- Annual from Q4 → next FY actual

For each pair: guidance value, actual value, delta (actual - guidance), beat/miss % ((actual - guidance) / |guidance| x 100), classification (Beat / In-line / Miss using +/-1% threshold).

### 6. Pattern Analysis
- Overall beat rate (% of quarters actual > guidance)
- Average beat/miss magnitude
- Trend in accuracy (tighter? more conservative? less reliable?)
- Metrics where management is notably conservative or aggressive
- Guidance range width trends

**Management credibility assessment:** If consistently beating by similar margin, call out sandbagging — 100% beat rate may mean guidance is uninformative. If guidance cut/missed, assess whether management acknowledged honestly. Flag patterns where qualitative language didn't translate to results.

### 7. Commentary from Filings
Search via `search_documents`:
- "guidance" / "outlook" — explicit guidance language
- "similar to" / "consistent with" / "growth rate" — qualitative/directional guidance
- "change" / "methodology" / "no longer providing" — methodology changes
- "assumes" / "includes" / "excludes" — assumptions behind guidance

Extract direct quotes with document citations.

### 7.5. Guidance Read-Throughs to Adjacent Companies

When a company raises, cuts, or materially changes its guidance, the implications often matter more for adjacent names than for the company itself.

**For each major guidance change identified in the tracker, analyze implications for adjacent companies:**

- **Suppliers**: Revenue/CapEx guidance changes directly affect supplier order books. A CapEx raise = purchase orders for equipment/component suppliers. A revenue guide-down signals softer demand upstream.
- **Customers**: If this company supplies critical inputs, pricing or capacity guidance affects customer margins. Price increases = margin headwind. Capacity expansion = supply relief.
- **Competitors**: Guidance on market growth, pricing, or demand is often the most honest signal about the competitive landscape. Guiding for share gains = direct share loss for competitors.
- **Channel partners / distributors**: Volume guidance changes affect channel inventory and distributor revenue.

**For each read-through (aim for 4-6), state:**
1. **The guidance data point** — which metric changed, by how much, in which quarter's call
2. **The affected company** (ticker + name)
3. **The implication** — bullish or bearish, with specific logic
4. **Timing** — next-quarter impact or multi-quarter trend?

**Focus on highest-signal guidance changes:**
- Raises after conservatism → strong inflection signal
- "Reaffirmed" when market expected a raise → often more bearish than an explicit cut
- New metrics being guided on (or old metrics withdrawn) → management redirecting attention
- Segment-level guidance changes → more specific read-throughs than consolidated figures
- KPI guidance (subscriber adds, unit volumes, ARPU) → most direct read-through to suppliers and competitors

**Web research:** Search "{ticker} guidance change implications read through" for analyst commentary on cross-company signals.

Present as a structured section after Pattern Analysis, grouped by guidance change (each major guide raise/cut gets its own sub-block with read-throughs beneath).

## Output

{_HTML_TEMPLATE}

Include these sections in the HTML report:
- Summary with company name, ticker, period covered
- Quarter mapping reference table showing +1 offset explicitly
- Main tracker table: Guidance Source, Metric, Guidance, Actual Period, Actual, Delta, Beat/Miss (with Daloopa citations)
- Summary statistics (beat rate, avg beat/miss by metric)
- Pattern analysis narrative
- Guidance read-throughs to adjacent companies (grouped by guidance change, with affected tickers and implications)
- Key guidance quotes from filings with document citations

Highlight key patterns (e.g., "beat revenue guidance 7 of 8 quarters by avg 2.3%"). Include honest credibility verdict: is guidance informative or performative?
"""


@daloopa_mcp.prompt
def inflection(ticker: str) -> str:
    """Inflection"""
    return f"""\
Detect the biggest financial and operating inflections for {ticker}.

{_DALOOPA_TOOLS}
{_PERIOD_DETERMINATION}
{_CITATIONS}
{_NUMBER_FMT}
{_TABLE_CONV}
{_ANALYTICAL_VOICE}

## Analysis Steps

### 1. Company Lookup
Look up {ticker} using `discover_companies`. Capture:
- `company_id`
- `latest_calendar_quarter` — anchor for all period calculations below
- `latest_fiscal_quarter`
- Firm name for report attribution (default: "Daloopa")

### 2. Broad Series Discovery
Cast a wide net to discover ALL available series. Search with multiple keyword sets:
- Financial: "revenue", "income", "profit", "margin", "eps", "cash flow"
- Operating: "subscriber", "user", "customer", "unit", "arpu", "retention"
- Segment: "segment", "product", "service", "geographic"
- Balance sheet: "debt", "asset", "equity", "cash"
- Other: "backlog", "bookings", "pipeline", "store", "employee"

Collect all unique series IDs. Goal is comprehensiveness.

### 3. Pull 8 Quarters
Calculate 8 quarters backward from `latest_calendar_quarter`. Pull all discovered series for those periods. This gives enough history to compute both QoQ and YoY rates plus their second derivatives.

### 4. Compute Growth Rates and Inflections
For each series with 5+ quarters of data:

**YoY Growth:** growth_t = (value_t - value_t-4) / |value_t-4|

**YoY Acceleration (second derivative):** accel_t = growth_t - growth_t-1. Positive = accelerating, negative = decelerating.

**QoQ Sequential Growth:** seq_growth_t = (value_t - value_t-1) / |value_t-1|

**QoQ Acceleration:** seq_accel_t = seq_growth_t - seq_growth_t-1

Skip series with values < 1% of revenue or sparse data. For margin/ratio series, use basis point changes.

### 5. Rank Inflections
**Top 10 Accelerating** — largest positive acceleration in most recent quarter.
**Top 10 Decelerating** — largest negative acceleration (momentum fading).

For each: series name, most recent value (cited), current YoY growth, prior-quarter YoY growth, acceleration delta, whether new trend (1Q) or sustained (2-3Q).

### 6. Contextualize Key Inflections
For top 5 most significant inflections:
- Search filings via `search_documents` for context on drivers
- Use keywords related to the specific metric
- Extract management commentary
- Note alignment/contradiction with guidance

### 7. Synthesize
- Broadly accelerating or decelerating?
- Divergent trends (e.g., revenue accelerating but margins decelerating)?
- Which inflections matter most for the investment case?
- Are operating KPIs leading or lagging financial inflections?

**Sustainability assessment:** For positive inflections — durable or one-time comp effect? Organic or pull-forward/easy comps? For negative — structural or temporary? Investing through it (good) or cutting to protect margins (potentially bad)?

## Output

{_HTML_TEMPLATE}

Include these sections in the HTML report:
- Summary (2-3 sentences: accelerating/decelerating/mixed, key inflections)
- Top Accelerating Metrics table (Rank, Metric, Latest Value, YoY Growth, Prior YoY, Acceleration, Trend)
- Top Decelerating Metrics table (same columns)
- Key Inflection Deep Dives (top 5 with filing context)
- Divergences & Signals analysis
- Inflection Heatmap table (metric x last 4 quarters YoY with direction labels)

Highlight 2-3 most notable inflections and what they signal.
"""


@daloopa_mcp.prompt
def capital_allocation(ticker: str) -> str:
    """Capital Allocation"""
    return f"""\
Perform a deep dive into capital allocation for {ticker}.

{_DALOOPA_TOOLS}
{_PERIOD_DETERMINATION}
{_CITATIONS}
{_NUMBER_FMT}
{_TABLE_CONV}
{_ANALYTICAL_VOICE}
{_MARKET_DATA}

## Analysis Steps

### 1. Company Lookup
Look up {ticker} using `discover_companies`. Capture:
- `company_id`
- `latest_calendar_quarter` — anchor for all period calculations below
- `latest_fiscal_quarter`
- Firm name for report attribution (default: "Daloopa")

### 2. Market Data
Get current stock price, market cap, shares outstanding for {ticker}. Needed for yields and per-share metrics. If unavailable, note that market-derived metrics cannot be computed.

### 3. Capital Allocation Data
Calculate 8 quarters backward from `latest_calendar_quarter`. Pull:

**Shares & Buybacks:** Diluted shares outstanding, share repurchase amounts ($), shares retired (units if available).

**Dividends:** Dividends per share, total dividend payments, special dividends.

**Cash Flow:** Operating Cash Flow, CapEx, Free Cash Flow (OCF - CapEx — "(calc.)"), D&A.

**Balance Sheet:** Cash and equivalents, short-term investments, total debt, net debt (Total Debt - Cash - Investments — "(calc.)").

**M&A:** Search for "acquisition", "purchase of business", "investment" series.

### 4. Compute Capital Allocation Metrics
For each quarter:

**Shareholder Returns:** Total buyback, total dividend, total return = buybacks + dividends, shareholder yield = (buybacks + dividends) / market cap (annualized), buyback yield, dividend yield.

**FCF Deployment:** FCF payout ratio = total return / FCF, CapEx % of revenue, CapEx % of OCF, FCF margin.

**Leverage:** Net debt / EBITDA, net debt / equity, interest coverage (if available), cash % of market cap.

**Share Count Dynamics:** QoQ and YoY share count change, implied buyback rate, years to retire X% at current pace.

### 5. Qualitative Research
Search filings via `search_documents`:
- "repurchase program" / "share repurchase" — buyback program
- "dividend" / "capital return" — dividend policy
- "acquisition" / "strategic" — M&A strategy
- "capital allocation" / "priorities" — framework
- "debt" / "refinance" — debt management

Extract: authorized programs (remaining $), dividend policy, M&A philosophy, stated priorities, strategy changes, direct quotes with citations.

### 6. Historical Analysis & Value Judgment
Analyze 8-quarter trend:
- Buyback activity accelerating or decelerating?
- Buying back more at lower prices (disciplined) or higher (less disciplined)?
- Dividend growth rate
- Shift between CapEx, buybacks, dividends, debt repayment over time
- FCF conversion trend

**Honestly assess value creation vs destruction:**
- Buybacks at all-time highs with deteriorating fundamentals = value destruction
- Under-investing in CapEx/R&D to fund buybacks = long-term competitiveness risk
- FCF payout > 100% = unsustainable (funding with debt/cash drawdown)
- Compare implied buyback return (1/P×E) to organic reinvestment returns

### 6.5. Reinvestment Assessment
Pull 8 quarters: R&D expense (R&D % revenue), CapEx (CapEx % revenue), key growth KPIs per sector taxonomy.

{_KPI_TAXONOMY}

**Assess adequacy:** Is R&D/revenue declining while buybacks increase? Is CapEx/revenue declining in a capital-intensive business? Are growth KPIs deteriorating while capital returns are at record levels?

**Value creation vs extraction verdict:** Is capital allocation creating long-term value or extracting it?

## Output

{_HTML_TEMPLATE}

Include these sections in the HTML report:
- Summary (2-3 sentences: how company deploys capital, key takeaways)
- Current Snapshot table (market cap, trailing 4Q FCF, FCF yield, shareholder yield, net debt/EBITDA, remaining authorization)
- Cash Flow & FCF table (8 quarters: OCF, CapEx, FCF, FCF margin)
- Share Repurchases & Dividends table (8 quarters)
- Shareholder Yield Analysis table (8 quarters)
- Leverage & Balance Sheet table (8 quarters)
- Capital Allocation Framework (from filings with citations)
- Reinvestment Assessment table + analysis
- Buyback Discipline Analysis
- M&A Activity
- Key Observations (3-5 bullets)

Highlight the capital allocation story.
"""


@daloopa_mcp.prompt
def dcf(ticker: str) -> str:
    """DCF"""
    return f"""\
Build a discounted cash flow (DCF) valuation for {ticker}.

{_DALOOPA_TOOLS}
{_PERIOD_DETERMINATION}
{_CITATIONS}
{_NUMBER_FMT}
{_TABLE_CONV}
{_ANALYTICAL_VOICE}
{_MARKET_DATA}

## Analysis Steps

### 1. Company Lookup
Look up {ticker} using `discover_companies`. Capture:
- `company_id`
- `latest_calendar_quarter` — anchor for all period calculations below
- `latest_fiscal_quarter`
- Firm name for report attribution (default: "Daloopa")

### 2. Market Data
Get: current price, market cap, shares outstanding, beta, 10Y Treasury yield (risk-free rate). If unavailable, use defaults (beta=1.0, Rf=4.5%).

### 3. Historical Financials
Calculate 8 quarters backward from `latest_calendar_quarter`. Pull: Revenue, Operating Income, Net Income, Diluted EPS, Operating Cash Flow, CapEx, FCF (OCF - CapEx — "(calc.)"), D&A, Tax expense and pre-tax income (for effective tax rate), Interest expense, Total debt, Cash and equivalents, Shares outstanding. Also pull segment revenue and guidance series.

### 4. Calculate WACC

**Cost of Equity (CAPM):** Rf + Beta x ERP (ERP = 5.5% standard assumption).

**Cost of Debt:** Interest Expense / Average Total Debt. After-tax = Cost of debt x (1 - effective tax rate). Default 5.0% pre-tax if unavailable.

**Capital Structure:** Market cap for equity weight, total debt for debt weight.

**WACC** = (E/V) x Re + (D/V) x Rd x (1-t). Show all inputs clearly.

### 5a. KPI-Driven Revenue Build (Preferred)
Attempt bottoms-up revenue build using operational KPIs — this is significantly more defensible than top-down.

{_KPI_TAXONOMY}

Pull segment revenue + segment KPIs. For each segment with KPI data, project revenue using unit economics:
- Hardware: projected units x projected ASP
- Subscription: projected subscribers x projected ARPU (net of churn)
- Marketplace: projected GMV x projected take rate
- Services/recurring: growth rate from retention + customer adds

Sum segments for total revenue, 5 years. Show the build so reader can challenge individual assumptions.

### 5b. Top-Down FCF Projections (Fallback)
If KPIs sparse: Revenue = management guidance near-term, then decay to 3% long-term. FCF Margin = trailing average, adjusted for trends. FCF = Revenue x FCF Margin. Note this is less reliable.

### 6. Terminal Value
Perpetuity growth: Terminal FCF = Year 5 FCF x (1 + g). Terminal Value = Terminal FCF / (WACC - g). Terminal growth = 2.5-3.0% (must not exceed long-term GDP). Discount to present.

### 7. Implied Valuation
- PV of projected FCFs + PV of terminal value = Enterprise Value
- Equity Value = EV - Net Debt
- Implied Share Price = Equity Value / Shares Outstanding
- Compare to current price: upside/downside %
- Implied EV/EBITDA, implied P/E
- Terminal value as % of total (flag if > 80%)

### 8. Sensitivity Analysis
**WACC x Terminal Growth matrix:** WACC = base +/- 2% in 0.5% steps (7 rows). Terminal growth = 1.5% to 4.0% in 0.5% steps (6 columns). Each cell = implied share price. Highlight base case and current market price.

Also: Revenue Growth x FCF Margin sensitivity if data supports it.

### 9. Consensus Sanity Check
If consensus available: compare projected revenue/EPS path to consensus for 1-2 years. Note divergences. If implied price far from consensus target, explain why. If unavailable, skip.

### 10. Sanity Checks & Self-Challenge
- Implied price >2x or <0.5x current → examine assumptions
- Terminal value >85% of total → highly sensitive to terminal assumptions
- WACC < Rf or > 15% → check capital structure inputs
- Compare implied multiples to historical trading range

**Challenge your own assumptions:** Build from fundamentals first, THEN compare to market price. Stress-test: what if growth mean-reverts? What if the cycle peaks? State what must go right for bull and wrong for bear. If DCF only "works" with aggressive terminal growth or low WACC, say so.

## Output

{_HTML_TEMPLATE}

Include these sections in the HTML report:
- Summary table (current price, implied price, upside/downside, WACC, terminal growth, TV % of total)
- WACC Calculation table (all components with sources)
- Historical FCF table (8 quarters with citations)
- FCF Projections table (5 years with assumptions)
- Valuation Bridge table (PV FCFs + PV TV → EV → Equity → Price)
- Sensitivity table (WACC x terminal growth matrix, base case bolded)
- Key Assumptions & Risks
- Sanity Checks

Summarize: implied vs current price, key drivers, biggest sensitivity.
"""


@daloopa_mcp.prompt
def comps(ticker: str) -> str:
    """Comps"""
    return f"""\
Build a trading comparables analysis for {ticker}.

{_DALOOPA_TOOLS}
{_PERIOD_DETERMINATION}
{_CITATIONS}
{_NUMBER_FMT}
{_TABLE_CONV}
{_ANALYTICAL_VOICE}
{_MARKET_DATA}

## Analysis Steps

### 1. Company Lookup
Look up {ticker} using `discover_companies`. Capture:
- `company_id`
- `latest_calendar_quarter` — anchor for all period calculations below
- `latest_fiscal_quarter`
- Firm name for report attribution (default: "Daloopa")

### 2. Identify Peer Group
Identify 5-10 comparable companies based on: direct competitors, business model peers, size peers, growth profile peers. Prioritize relevance over size. List tickers with 1-sentence justification each.

### 3. Target Company Fundamentals
Calculate 4 quarters backward from `latest_calendar_quarter`. Pull from Daloopa: Revenue (trailing 4Q total), EBITDA (trailing 4Q; compute from Op Income + D&A if needed — "(calc.)"), Net Income (trailing 4Q), Diluted EPS (trailing 4Q sum), Free Cash Flow (trailing 4Q; OCF - CapEx — "(calc.)"), Revenue YoY growth (most recent Q), Operating Margin, Net Margin.

### 4. Peer Market Multiples
For each peer, get trading multiples: P/E (trailing + forward), EV/EBITDA, P/S, P/B, dividend yield, PEG ratio, price, market cap, enterprise value. If a peer fails, drop and note why.

### 5. Peer Fundamentals from Daloopa
For each peer available in Daloopa:
- Look up the company
- Calculate 4 quarters backward from `latest_calendar_quarter`. Pull revenue, operating income, net income for those periods.
- Compute revenue growth YoY, operating margin, net margin

For peers not in Daloopa, use market data multiples only and note limitation.

### 5.5. Peer Operational KPIs
{_KPI_TAXONOMY}

For target + all Daloopa-available peers, discover and pull company-specific KPIs (trailing 4Q). Build sparse matrix. Note which are comparable across the group vs company-specific. Add to comps table where comparable.

### 6. Build Comps Table
Main table columns: Company, Ticker, Mkt Cap, EV, P/E, Fwd P/E, EV/EBITDA, P/S, Rev Growth, Op Margin, Net Margin, FCF Yield.

Sort by market cap descending. Include: **Peer median** row, **Peer mean** row, **Target** row (highlighted), target's percentile rank per metric.

### 7. Implied Valuation
Apply peer median and mean multiples to target fundamentals:

| Methodology | Multiple | Target Metric | Implied EV/Equity | Implied Share Price |

For EV-based: Implied EV - Net Debt = Equity Value. For equity-based: direct. Compute range (min to max) and central tendency.

### 8. Consensus Forward Estimates
If available: NTM revenue/EPS for target and peers, forward P/E and EV/EBITDA, note where target's forward multiples sit vs group, flag estimate revision trends. If unavailable, use trailing only.

### 9. Premium/Discount Analysis
For each multiple: target vs peer median as % premium/discount. Assess whether justified:
- Growth differential (higher growth = premium)
- Margin differential (higher margins = premium)
- Market position
- Risk profile

**Be honest:** A company can deserve a premium and still be overvalued if premium stretched too far. If growth decelerating toward peer levels, flag derating risk. Don't default to "premium justified because market leader." Reference KPI outperformance as justification (or lack thereof).

## Output

{_HTML_TEMPLATE}

Include these sections in the HTML report:
- Summary (2-3 sentences: relative valuation, cheap or expensive and why)
- Peer Group Selection table with rationale
- Comparables Table (full, with target highlighted, median/mean rows)
- Target vs Peer Premium/Discount table
- Implied Valuation table (by methodology + range)
- Premium/Discount Justification analysis
- Peer Operational KPIs table (sparse, footnoted)
- Key Observations (3-5 bullets)

Highlight: relative position, implied valuation range, most relevant multiple.
"""


@daloopa_mcp.prompt
def supply_chain(ticker: str) -> str:
    """Supply Chain"""
    return f"""\
Generate an interactive supply chain dashboard for {ticker}, mapping upstream (supplier) and downstream (customer) relationships and quantifying financial interdependencies in both directions.

The output enables an analyst to understand: Who are the critical suppliers and customers? Where is concentration risk on both sides? Which suppliers depend heavily on this company for revenue? Which customers depend on this company's products as critical inputs? How does a shock propagate both upstream (demand shock to suppliers) and downstream (supply disruption to customers)?

{_DALOOPA_TOOLS}
{_PERIOD_DETERMINATION}
{_CITATIONS}
{_NUMBER_FMT}
{_TABLE_CONV}
{_ANALYTICAL_VOICE}
{_MARKET_DATA}

## Research Workflow

This is a multi-phase research process. Each phase builds on the previous one. Maximize parallelism across independent API calls.

### Phase 1: Target Company Identification

1. Use `discover_companies` with "{ticker}" to get `company_id`, `latest_calendar_quarter`, and `latest_fiscal_quarter`. Note the firm name for report attribution (default: "Daloopa").
2. Pull key financials for the target company:
   - Use `discover_company_series` with keywords: ["revenue", "cost of goods", "gross profit", "operating income", "net income", "total cost"]
   - Calculate 4 quarters backward from `latest_calendar_quarter`. Use `get_company_fundamentals` for those periods to get TTM figures.
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
- "[ticker] [company name] key suppliers list" — supplier identification
- "[ticker] supply chain analysis suppliers" — analyst/industry reports
- "[ticker] 10-K supplier disclosure" — SEC filing analysis
- "[company name] supply chain map" — industry supply chain maps
- "[company name] supplier concentration risk" — risk analysis
- "[company name] who manufactures for [company]" — manufacturing partners
- "[company name] component suppliers" — component-level supply chain

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
   - Web search: "[supplier name] [target company] revenue percentage customer"
   - Web search: "[supplier name] 10-K customer concentration"
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
3. **Pull 10 quarters** using `get_company_fundamentals`. Calculate 10 quarters backward from `latest_calendar_quarter`.
   - Example: if `latest_calendar_quarter` = "2025Q4", pull ["2023Q3", "2023Q4", "2024Q1", "2024Q2", "2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3", "2025Q4"]
4. **Compute inventory composition**: For each quarter, calculate RM%, WIP%, FG% of total inventory
   - High WIP% can signal production bottlenecks
   - Rising FG% can signal demand weakness
   - Rising RM% can signal supply hoarding or procurement buildup
5. **Handle missing data gracefully**: Some suppliers may not report full inventory breakdowns — show what's available and note gaps
6. **Multi-currency handling**: Note the reporting currency for each company (USD, NTD, KRW, EUR, etc.) and display with appropriate units (e.g., "NTD B" for TSMC, "KRW T" for Samsung)

Run inventory and financial series pulls in parallel across all companies.

### Phase 4: Customer / Downstream Identification

The downstream side requires the same research rigor as the upstream side. Run these concurrently to build a comprehensive customer list:

**4a. Daloopa Document Search (target company filings):**
- Search keywords: ["customer", "contract", "agreement", "channel"] across last 2-4 quarters
- Search keywords: ["customer concentration", "significant customer", "major customer"] across last 2-4 quarters — many companies disclose customers >10% of revenue
- Search keywords: ["distribution", "retail partner", "reseller", "licensee"] across last 2-4 quarters
- Search keywords: ["accounts receivable", "contract asset", "deferred revenue"] — concentration in A/R often reveals customer dependency even when not explicitly named
- Search the company's 10-K specifically for customer disclosures and segment end-market breakdowns

**4b. Web Research:**
- "[ticker] [company name] major customers list" — direct customer identification
- "[ticker] customer concentration revenue breakdown" — analyst/industry reports
- "[ticker] 10-K customer disclosure" — SEC filing analysis
- "[company name] who buys from [company name]" — downstream identification
- "[company name] channel partners distributors" — channel analysis
- "[company name] end market exposure" — end-market breakdown

**4c. Industry-Specific Customer Research:**
For each industry, search for the known critical downstream relationships:
- **Semiconductors**: Which OEMs depend on these chips? (e.g., NVDA → hyperscalers MSFT/AMZN/GOOG, QCOM → smartphone OEMs AAPL/Samsung, AVGO → networking OEMs Cisco/Arista)
- **Components/Materials**: Which assemblers or product companies use these inputs? (e.g., Corning → AAPL/Samsung for glass, TSMC → fabless semis NVDA/AMD/AAPL)
- **Software/Platform**: Who builds on this platform? (e.g., MSFT Azure → ISVs, AAPL App Store → developers, Salesforce → SI partners)
- **Consumer products**: Channel partners (carriers, retailers, e-commerce) and enterprise customers
- **Industrial/B2B**: End-market verticals (auto, aerospace, medical, telecom)
- **Pharma/Biotech**: Distributors (McKesson, AmerisourceBergen), PBMs, hospital systems

**4d. Customer Financial Analysis:**

For each identified customer (aim for 6-10 key customers):

1. **Discover the customer** using `discover_companies` with their ticker
2. **Pull key financials** from Daloopa:
   - `discover_company_series` with keywords: ["revenue", "net income", "gross margin", "cost of goods", "operating income"]
   - `get_company_fundamentals` for last 4 quarters
3. **Determine revenue attribution** (what % of target's revenue comes from this customer):
   - Search Daloopa documents for the target company: keywords ["[customer name]", "customer", "concentration", "accounts receivable"]
   - Web search: "[target company] [customer name] revenue percentage"
   - Web search: "[target company] 10-K customer concentration"
   - Many companies disclose customers that account for >10% of revenue in their 10-K
4. **Determine input criticality** (what % of customer's COGS comes from target):
   - This is the inverse of the supplier analysis: if the target sells $X to a customer with $Y in COGS, then input share = X/Y
   - Search for: "[customer name] [target company] supplier dependence" or "[customer name] key inputs components"
   - Flag whether the target's product is a critical, hard-to-substitute input vs. a commodity with alternatives
5. **Assess switching costs**: Can the customer easily replace the target company's product?
   - **High switching cost**: Custom/proprietary integration, long qualification cycles, regulatory requirements (e.g., TSMC's process node — customers can't easily switch foundries mid-design)
   - **Medium switching cost**: Some integration required but alternatives exist with 6-12 month transition
   - **Low switching cost**: Commodity input, multiple qualified alternatives, short switching timeline
6. **Business & product description**: What does the target supply to this customer? Be specific (e.g., "A17 Pro and M4 SoCs fabricated on TSMC's 3nm process" not just "chips")

### Phase 4e: Customer Inventory & 10-Quarter Financial Data

Mirror Phase 3b for the customer side. For each identified customer (6-10 companies), pull **10 quarters** of data:

1. **Discover inventory series** using `discover_company_series` with keywords: ["raw material", "work in process", "finished good", "inventory", "inventories"]
   - Look for separate RM, WIP, FG series, plus a total inventory series
2. **Discover financial series** using `discover_company_series` with keywords: ["revenue", "gross profit", "net income", "gross margin"]
3. **Pull 10 quarters** using `get_company_fundamentals` with the same 10 calendar quarters as the target company and suppliers (calculated from `latest_calendar_quarter`)
4. **Compute inventory composition**: RM%, WIP%, FG% of total inventory
   - For customers, inventory signals have different meaning:
   - Rising RM% at a customer → they're stocking up on target company's inputs (bullish for target's near-term revenue, but may mean future destocking)
   - Falling RM% → customer is drawing down inventory, may signal reduced orders ahead
   - Rising FG% at a customer → demand for the customer's end product is softening, which will flow back upstream to the target
5. **Handle missing data gracefully**: Some customers may not report inventory breakdowns — show what's available
6. **Multi-currency handling**: Same as suppliers — note reporting currency

Run customer inventory and financial series pulls in parallel, and in parallel with supplier pulls where possible.

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
  - What target company supplies to them (specific products/services)
  - Estimated % of target revenue from this customer (with source/logic)
  - Estimated % of customer COGS from target (input criticality, with source)
  - Switching cost assessment (High/Medium/Low with reasoning)
  - TTM Revenue, COGS, Net Income, Gross Margin
  - Market cap
  - Relationship summary (exclusive? multi-source? long-term contract? spot?)
  - 10-quarter financials: Revenue, Gross Profit, Net Income, GM% (with Daloopa citation IDs)
  - 10-quarter inventory: RM, WIP, FG, Total, RM%, WIP%, FG% (with Daloopa citation IDs)
  - Reporting currency and unit (e.g., USD $M, EUR M, JPY B)

TIER 2 CUSTOMERS (for top 3-5 Tier 1 customers — who do THEY sell to?):
  For each Tier 1 customer, their key customers with basic data
  This traces the value chain forward: Target → Customer → End Market

TIER 2 SUPPLIERS (for top 3-5 Tier 1 suppliers):
  For each Tier 1 supplier, their key suppliers with basic data
```

### Phase 6b: Upstream Shock Analysis (Demand Shock → Suppliers)

Prepare a narrative analysis of how a demand shock at {ticker} would ripple upstream through the supplier chain:

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

### Phase 6c: Downstream Shock Analysis (Supply Disruption → Customers)

Prepare a narrative analysis of how a supply disruption at {ticker} (production halt, quality issue, capacity constraint, export ban) would ripple downstream through the customer chain:

1. **Classify each customer by input criticality**:
   - **Critical input**: Target's product is a key component with no drop-in replacement; disruption halts customer production (e.g., TSMC to Apple — no alternative foundry for A-series chips)
   - **Important input**: Target is a significant but not sole supplier; customer can partially substitute with 3-6 month lead time
   - **Supplementary input**: Target provides a non-critical input; customer has multiple qualified alternatives

2. **Assess downstream disruption for each customer**:
   - **Input Criticality** (High/Medium/Low): How essential is the target's product to the customer's operations?
   - **Switching Cost** (High/Medium/Low): How long and expensive to qualify an alternative? Are there contractual lock-ins?
   - **Revenue at Risk**: What portion of the customer's revenue depends on products that use the target's inputs?
   - **Inventory Buffer**: Does the customer hold significant RM inventory of the target's product? How many weeks/months of supply?
   - **Alternative Sources**: Who else could supply this? What's the capacity gap?

3. **Build a downstream impact matrix table** with columns: Customer, Category, Input Criticality, Switching Cost, Revenue at Risk, Inventory Buffer, Overall Disruption Risk

4. **Write narrative sections**:
   - "Most Vulnerable Customers" — customers who would face production disruption or revenue loss
   - "Customers with Alternatives" — those who can substitute away from the target
   - "Pricing Power Implications" — if the target faces a supply constraint, which customers have the leverage to secure allocation vs. which get cut first?
   - "Channel Inventory Signals" — what customer inventory levels (especially RM%) tell you about near-term order patterns for the target company
   - "Second-Order Downstream Effects" — how end consumers or Tier 2 customers would be affected

## Output Format

Present as a **complete, self-contained HTML document** with all CSS and JavaScript inlined. No external dependencies.

The HTML document must include:

- **Page header** with company name, ticker, date
- **KPI bar** — target company TTM Revenue, COGS, Gross Margin, Market Cap, # Suppliers, # Customers
- **Tier-grouped supply chain visualization** — columns: Tier 3 → Tier 2 → Tier 1 → Target → Customers, with connection lines
- **Tab bar** switching between: Overview, Suppliers, Customers, Tier 2 Deep Dive, Shock Analysis
- **Inventory Health Overview table** — for all suppliers: RM%, WIP%, FG% of total inventory as stacked colored bars, plus latest total inventory value
- **Supplier cards grouped by tier** — Tier 1 (Critical/Sole-source), Tier 2 (Major Component), Tier 3 (Specialty) with click-to-expand detail overlays containing:
  - 10-quarter financial table (Revenue, Gross Profit, Net Income, Gross Margin %)
  - 10-quarter inventory breakdown table (RM, WIP, FG, Total, RM%, WIP%, FG%)
  - Canvas chart: stacked bar inventory composition with Gross Margin % line overlay
  - Business description and relationship to target
- **Customer cards grouped by category** — Channel Partners, Enterprise/B2B, End-Market Exposure — with matching click-to-expand detail overlays
- **Upstream Shock Analysis** section with impact matrix table
- **Downstream Shock Analysis** section with impact matrix table
- **Methodology notes** and source citations
- **"Download as PDF" button** (uses `window.print()`)
- **All financial figures hyperlinked to Daloopa source citations**

**DOM Safety**: All JavaScript MUST use `createElement()` + `textContent` + `appendChild()` for DOM construction. NEVER use `innerHTML`, `outerHTML`, or any HTML-string injection methods.

### HTML/CSS Template

Use this CSS (extends the design-system palette):

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{ticker} Supply Chain Dashboard</title>
<style>
:root {{
    --navy: #1B2A4A;
    --steel-blue: #4A6FA5;
    --gold: #C5A55A;
    --green: #27AE60;
    --red: #C0392B;
    --light-gray: #F8F9FA;
    --mid-gray: #E9ECEF;
    --dark-gray: #6C757D;
    --near-black: #343A40;
    --bg: var(--light-gray);
    --surface: #ffffff;
    --border: var(--mid-gray);
    --border-light: var(--light-gray);
    --text-primary: var(--near-black);
    --text-secondary: var(--dark-gray);
    --text-tertiary: #8a8a85;
    --accent: var(--steel-blue);
    --green-bg: #f0f9f2;
    --red-bg: #fef2f2;
    --amber: #92600a;
    --amber-bg: #fefce8;
    --blue-bg: #eff6ff;
    --node-supplier: var(--mid-gray);
    --node-customer: #dde8f0;
    --node-target: var(--navy);
    --sans: "Segoe UI", -apple-system, BlinkMacSystemFont, Arial, sans-serif;
    --mono: "SF Mono", "Fira Code", "Fira Mono", "Roboto Mono", monospace;
}}
@media print {{
    .no-print {{ display: none !important; }}
    .interactive {{ pointer-events: none; }}
    @page {{ margin: 0.5in; size: landscape; }}
}}
* {{ box-sizing: border-box; }}
body {{
    font-family: var(--sans);
    font-size: 12px;
    line-height: 1.6;
    color: var(--text-primary);
    max-width: 100%;
    margin: 0;
    padding: 0;
    background: var(--bg);
}}
.page-header {{
    background: var(--surface);
    border-bottom: 3px solid var(--navy);
    padding: 24px 40px 16px;
}}
.page-header h1 {{
    font-size: 28px; font-weight: 700; color: var(--navy);
    letter-spacing: -0.5px; line-height: 1.2; margin: 0;
}}
.page-header .subtitle {{ font-size: 14px; color: var(--text-secondary); margin-top: 4px; }}
.page-header .dateline {{ font-size: 12px; color: var(--text-tertiary); margin-top: 8px; font-family: var(--mono); }}
.container {{ max-width: 1400px; margin: 0 auto; padding: 24px 40px; }}
h2 {{ font-size: 20px; font-weight: 700; margin: 32px 0 16px; padding-bottom: 6px; border-bottom: 1px solid var(--mid-gray); color: var(--navy); }}
h3 {{ font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: var(--steel-blue); margin: 20px 0 10px; }}
a {{ color: var(--accent); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.kpi-bar {{ display: flex; gap: 0; border: 1px solid var(--border); border-radius: 6px; overflow: hidden; background: var(--surface); margin: 16px 0; }}
.kpi-item {{ flex: 1; padding: 12px 16px; border-right: 1px solid var(--border-light); text-align: center; }}
.kpi-item:last-child {{ border-right: none; }}
.kpi-label {{ font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-tertiary); font-weight: 600; }}
.kpi-value {{ font-size: 18px; font-weight: 700; margin-top: 2px; font-variant-numeric: tabular-nums; }}
.kpi-sub {{ font-size: 11px; color: var(--text-tertiary); margin-top: 1px; }}
/* Supply Chain Visualization */
.chain-view {{ display: flex; gap: 24px; align-items: flex-start; margin: 20px 0; overflow-x: auto; padding-bottom: 16px; }}
.chain-column {{ min-width: 280px; flex-shrink: 0; }}
.chain-column-header {{ font-family: var(--sans); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: var(--text-tertiary); margin-bottom: 12px; padding-bottom: 6px; border-bottom: 1px solid var(--border); text-align: center; }}
.chain-arrow {{ display: flex; align-items: center; justify-content: center; color: var(--text-tertiary); font-size: 24px; min-width: 40px; padding-top: 40px; flex-shrink: 0; }}
/* Company Cards */
.company-card {{
    background: var(--surface); border: 1px solid var(--border); border-radius: 6px;
    padding: 14px 16px; margin-bottom: 10px; cursor: pointer;
    transition: border-color 0.15s, box-shadow 0.15s;
}}
.company-card:hover {{ border-color: var(--text-secondary); box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
.company-card.target-card {{ background: var(--navy); color: white; border-color: var(--navy); }}
.company-card.target-card .card-ticker {{ color: rgba(255,255,255,0.7); }}
.company-card.target-card .card-metric-label {{ color: rgba(255,255,255,0.5); }}
.company-card.target-card .card-metric-value {{ color: white; }}
.company-card.target-card .card-desc {{ color: rgba(255,255,255,0.7); }}
.company-card.expanded {{ border-color: var(--steel-blue); box-shadow: 0 2px 12px rgba(74,111,165,0.15); }}
.company-card.supplier-card {{ border-left: 3px solid var(--node-supplier); }}
.company-card.customer-card {{ border-left: 3px solid var(--node-customer); }}
.card-header {{ display: flex; justify-content: space-between; align-items: flex-start; }}
.card-name {{ font-size: 16px; font-weight: 700; line-height: 1.2; }}
.card-ticker {{ font-family: var(--mono); font-size: 11px; color: var(--text-tertiary); margin-top: 2px; }}
.card-badge {{ font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 3px; white-space: nowrap; }}
.badge-pct-high {{ background: var(--red-bg); color: var(--red); }}
.badge-pct-med {{ background: var(--amber-bg); color: var(--amber); }}
.badge-pct-low {{ background: var(--green-bg); color: var(--green); }}
.card-supplies {{ font-size: 12px; color: var(--text-secondary); margin-top: 6px; line-height: 1.4; }}
.card-metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border-light); }}
.card-metric-label {{ font-size: 9px; text-transform: uppercase; letter-spacing: 0.3px; color: var(--text-tertiary); }}
.card-metric-value {{ font-size: 13px; font-weight: 700; font-variant-numeric: tabular-nums; }}
.card-desc {{ font-size: 12px; color: var(--text-secondary); margin-top: 8px; line-height: 1.45; }}
/* Expanded Detail Panel */
.detail-panel {{ display: none; margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border-light); }}
.company-card.expanded .detail-panel {{ display: block; }}
.detail-section {{ margin-bottom: 14px; }}
.detail-section h4 {{ font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-tertiary); margin-bottom: 6px; }}
/* Relationship Bars */
.relationship-bar {{ height: 8px; background: var(--border-light); border-radius: 4px; overflow: hidden; margin: 4px 0; }}
.relationship-fill {{ height: 100%; border-radius: 4px; transition: width 0.3s; }}
.fill-red {{ background: var(--red); }}
.fill-amber {{ background: var(--amber); }}
.fill-green {{ background: var(--green); }}
.fill-blue {{ background: var(--accent); }}
/* Drill-down button */
.drill-btn {{ display: inline-block; font-size: 11px; font-weight: 600; color: var(--accent); cursor: pointer; padding: 4px 0; border: none; background: none; font-family: var(--sans); }}
.drill-btn:hover {{ text-decoration: underline; }}
/* Risk indicators */
.risk-tag {{ display: inline-block; font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 3px; }}
.risk-high {{ background: var(--red-bg); color: var(--red); }}
.risk-med {{ background: var(--amber-bg); color: var(--amber); }}
.risk-low {{ background: var(--green-bg); color: var(--green); }}
/* Tabs */
.tab-bar {{ display: flex; gap: 0; border-bottom: 2px solid var(--border); margin-bottom: 20px; }}
.tab {{ padding: 10px 20px; font-size: 13px; font-weight: 600; color: var(--text-tertiary); cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: color 0.15s, border-color 0.15s; font-family: var(--sans); background: none; border-top: none; border-left: none; border-right: none; }}
.tab:hover {{ color: var(--text-primary); }}
.tab.active {{ color: var(--text-primary); border-bottom-color: var(--text-primary); }}
.tab-content {{ display: none; }}
.tab-content.active {{ display: block; }}
/* Concentration Table */
.conc-table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin: 12px 0; }}
.conc-table th {{ font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-tertiary); font-weight: 600; text-align: left; padding: 6px 10px; border-bottom: 2px solid var(--border); background: var(--bg); }}
.conc-table th:not(:first-child) {{ text-align: right; }}
.conc-table td {{ padding: 8px 10px; border-bottom: 1px solid var(--border-light); font-variant-numeric: tabular-nums; }}
.conc-table td:not(:first-child) {{ text-align: right; }}
.conc-table tr:hover {{ background: var(--blue-bg); }}
.conc-table .row-total {{ font-weight: 700; border-top: 2px solid var(--border); background: var(--bg); }}
/* Methodology / Source Notes */
.methodology-box {{ background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 16px 20px; margin: 16px 0; font-size: 12px; color: var(--text-secondary); line-height: 1.5; }}
.methodology-box h4 {{ font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-tertiary); margin-bottom: 8px; }}
/* Links & References */
.source-tag {{ font-size: 9px; color: var(--text-tertiary); font-style: italic; }}
/* Footer */
.page-footer {{ margin-top: 40px; padding: 16px 0; border-top: 3px solid var(--navy); font-size: 11px; color: var(--text-tertiary); text-align: center; }}
/* Print / Download button */
.dl-btn {{ display: inline-block; padding: 10px 24px; background: var(--navy); color: white; border: none; border-radius: 5px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: var(--sans); }}
.dl-btn:hover {{ background: var(--steel-blue); }}
/* Two-column layout */
.two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
@media (max-width: 800px) {{
    .two-col {{ grid-template-columns: 1fr; }}
    .chain-view {{ flex-direction: column; }}
    .chain-arrow {{ transform: rotate(90deg); padding-top: 0; }}
}}
</style>
</head>
```

### JavaScript Pattern

Include tab switching, card expand/collapse, and drill-down navigation:

```javascript
function switchTab(tabId) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  document.querySelector(`[data-tab="${{tabId}}"]`).classList.add('active');
  document.getElementById(tabId).classList.add('active');
}}
function toggleCard(cardId) {{
  document.getElementById(cardId).classList.toggle('expanded');
}}
function drillDown(companyTicker) {{
  switchTab('tier2');
  const section = document.getElementById('tier2-' + companyTicker);
  if (section) {{
    section.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    section.style.outline = '2px solid var(--accent)';
    setTimeout(() => {{ section.style.outline = 'none'; }}, 2000);
  }}
}}
```

Data sourced from Daloopa
"""


# ============================================================================
# 2. DELIVERABLE SKILLS
# ============================================================================


@daloopa_mcp.prompt
def research_note(ticker: str) -> str:
    """Research Note"""
    return f"""\
Generate a comprehensive research note for {ticker}. This is the most thorough single-company analysis — equivalent to an institutional initiation note.

NOTE: The original skill produces a .docx Word document via infra scripts. This prompt produces the full analytical content as structured markdown. For .docx rendering, use the project repo's `infra/docx_renderer.py`.

{_DALOOPA_TOOLS}
{_PERIOD_DETERMINATION}
{_CITATIONS}
{_NUMBER_FMT}
{_TABLE_CONV}
{_ANALYTICAL_VOICE}
{_MARKET_DATA}
{_CONSENSUS}

## Analysis Phases

### Phase A — Company Setup
Look up {ticker} using `discover_companies`. Capture:
- `company_id`
- `latest_calendar_quarter` — anchor for all period calculations
- `latest_fiscal_quarter`
- Firm name for report attribution (default: "Daloopa")

Get current stock price, market cap, shares outstanding, beta, and trading multiples for {ticker} (see market data resolution order above).

### Phase B — Core Financials + Cost Structure
Calculate 8 quarters backward from `latest_calendar_quarter`. Pull Income Statement: Revenue, Gross Profit, Operating Income, Net Income, Diluted EPS, EBITDA (compute if needed — "(calc.)"), SG&A, R&D.

Cash Flow & Balance Sheet: Operating Cash Flow, CapEx, FCF (OCF - CapEx — "(calc.)"), Cash, Total Debt, Net Debt, D&A.

**For every value, record its fundamental_id for citations.**

Compute margins and YoY growth. Every Daloopa number must include citation link.

**Cost Structure:** Search for cost-related series ("cost of goods", "materials", "manufacturing"). Identify 3-5 biggest cost items. Pull R&D and SG&A separately, compute % of revenue trends. For each major margin, identify expansion/compression drivers.

### Phase C — KPIs, Segments & Industry Deep Dive
{_KPI_TAXONOMY}

Search for company-specific KPIs, segment revenue, geographic revenue, share count, buybacks. Pull the same 8 quarters (from `latest_calendar_quarter`).

**Industry Deep Dive** — determine sector and apply:
- Manufacturing: bookings, backlog, book-to-bill, capacity utilization
- SaaS: ARR/MRR, net retention, customer cohort, RPO/deferred revenue
- Retail: same-store sales, store count, traffic vs ticket, inventory health
- Financials: NIM, provisions, loan growth, capital ratios
- Healthcare: pipeline summary, product revenue, patent cliff
- Energy: production volumes, realized pricing, reserves, breakeven

### Phase D — Guidance Track Record
Search for guidance series. Pull guidance and actuals. Apply +1 quarter offset. Compute beat/miss rates and patterns.

{_GUIDANCE_RULES}

### Phase E — What You Need to Believe
Using trailing 4Q totals and segment trends, build **falsifiable bull/bear beliefs**:

**Bull Beliefs (4-6):** Each with bold statement + 2-3 sentences of evidence with citations. Each must be testable with observable data within 6 months.

**Bear Beliefs (4-6):** Same format for downside case.

**Valuation Math:** Bull target = forward multiple x forward earnings. Bear target = same with bear assumptions. Show the math.

**Risk/Reward:** Compare bull upside % vs bear downside %. Flag significant asymmetry. State which side has better risk/reward.

### Phase F — Capital Allocation
Pull buyback, dividend, share count, FCF data. Compute shareholder yield, FCF payout ratio, net leverage.

### Phase G — Valuation

**DCF:** Calculate WACC (CAPM), project FCF 5 years, terminal value, implied share price, sensitivity table.

**Comps:** Identify 5-8 peers. Get peer trading multiples. Include forward multiples if consensus available. Compute implied valuation range.

### Phase H — Qualitative Research + News & Catalysts

**SEC Filings:** Search for risk factors, growth drivers, competitive dynamics, management outlook, strategic topics. Organize into risks (ranked), investment thesis, company description.

**News (web search):** 4 queries covering recent headlines, analyst sentiment, catalysts/risks, industry outlook. Organize into:
- News timeline: 6-10 key events, reverse chronological, with sentiment tags
- Forward catalysts: near-term (0-3mo HIGH), medium-term (3-12mo MEDIUM), long-term (1-3yr LOW)
- Policy backdrop: macro/regulatory context (if material)

### Phase I — Charts
Describe what charts would be produced (the LLM receiving this prompt cannot generate images, but should describe the data): Revenue trend, margin trend, segment pie, DCF sensitivity heatmap.

### Phase J — Synthesis + Tensions + Monitoring

**Core Synthesis:** Executive summary (3-4 sentences with directional view), variant perception (where is consensus wrong?), key findings (top 3-5), red flags.

**Five Key Tensions:** 5 bull/bear debates, each one line, alternating lean, citing data.

**Monitoring Framework:**
- Quantitative: 5-7 metrics with thresholds ("Metric: value → bull threshold / bear threshold")
- Qualitative: 5-7 factors (management tone, competitive dynamics, regulatory, concentration, capital allocation)

## Output

Present the complete research note as structured markdown with these sections:
1. Cover: company name, ticker, date, price, market cap
2. Five Key Tensions
3. Executive Summary + Key Metrics table
4. Investment Thesis + Variant Perception
5. Company Description
6. News Timeline
7. Financial Analysis tables (8Q) + margin analysis + OpEx breakdown
8. Industry Deep Dive
9. Segment and Geographic tables
10. KPI tables
11. Guidance Track Record
12. What You Need to Believe (bull/bear beliefs + valuation math + risk/reward)
13. Forward Catalysts + Policy Backdrop
14. Capital Allocation commentary
15. Valuation (DCF summary + sensitivity + Comps)
16. Risks (ranked)
17. Monitoring Framework (quantitative + qualitative)

Data sourced from Daloopa
"""


@daloopa_mcp.prompt
def build_model(ticker: str) -> str:
    """Build Model"""
    return f"""\
Build a comprehensive Excel financial model for {ticker}.

{_DALOOPA_TOOLS}
{_PERIOD_DETERMINATION}
{_CITATIONS}
{_NUMBER_FMT}
{_TABLE_CONV}
{_MARKET_DATA}
{_CONSENSUS}
{_EXCEL_ARTIFACT}

## Analysis Phases

### Phase 1 — Company Setup
Look up {ticker} using `discover_companies`. Capture:
- `company_id`
- `latest_calendar_quarter` — anchor for all period calculations
- `latest_fiscal_quarter`
- Firm name for report attribution (default: "Daloopa")

Get current stock price, market cap, shares outstanding, beta, and trading multiples.

### Phase 2 — Comprehensive Data Pull
Calculate periods backward from `latest_calendar_quarter`. Pull as much data as Daloopa has for this company. Target 8-16 quarters.

**Income Statement:** Revenue, COGS, Gross Profit, R&D, SG&A, Total OpEx, Operating Income, Interest Expense/Income, Pre-tax Income, Tax Expense, Net Income, Diluted EPS, Diluted Shares, EBITDA (or compute), D&A.

**Balance Sheet:** Cash, Short-term Investments, AR, Inventory, Total Current Assets, PP&E, Goodwill, Total Assets, AP, Short-term Debt, Long-term Debt, Total Liabilities, Total Equity.

**Cash Flow:** OCF, CapEx, D&A, Acquisitions, Dividends Paid, Share Repurchases, FCF.

**Segments:** Revenue by segment, operating income by segment if available.

**KPIs:** All company-specific operating metrics.

**Guidance:** All guidance series and corresponding actuals.

### Phase 3 — Market Data & Peers
Identify 5-8 peers with trading multiples. Get risk-free rate. Include NTM estimates if consensus available.

### Phase 4 — Projections
Project 4-8 quarters forward:
- Revenue: guidance + decay to long-term growth
- Margins: mean-revert to trailing averages
- CapEx, D&A, tax rate, share count: trailing trends

Show all assumptions clearly.

### Phase 5 — DCF Inputs
- WACC (CAPM: Rf + Beta x ERP; cost of debt from interest/debt)
- 5-year FCF projections (annualized from quarterly)
- Terminal value (perpetuity growth 2.5-3%)
- Sensitivity matrix: WACC (7 values) x terminal growth (6 values)

### Phase 6 — Build Excel

Create the workbook with these sheets:

1. **Dashboard** — Key metrics summary, current price, implied values
2. **Income Statement** — Full P&L with historical + projected quarters, margins as sub-rows
3. **Balance Sheet** — Full BS with historical quarters
4. **Cash Flow** — Full CF with historical + projected, FCF computation
5. **Segments** — Revenue by segment with growth rates
6. **KPIs** — All operating metrics with trends
7. **Projections** — Forward estimates with editable assumption cells (highlight in yellow)
8. **DCF** — WACC calculation, FCF projections, terminal value, valuation bridge, sensitivity matrix
9. **Comps** — Peer multiples table with median/mean, implied valuation

{_EXCEL_ARTIFACT}

## Output

Present the model as a React artifact with SheetJS that builds the .xlsx with all 9 sheets above. Include:
- Download button for the .xlsx file
- HTML table previews of Dashboard, Income Statement, and DCF sheets
- Summary: trailing revenue, projected growth, implied DCF value, peer-implied range
- Note that yellow cells in Projections tab are editable inputs

All Daloopa-sourced figures use citation format.

Data sourced from Daloopa
"""


@daloopa_mcp.prompt
def comp_sheet(ticker: str) -> str:
    """Comp Sheet"""
    return f"""\
Build a multi-company industry comp sheet Excel model for {ticker} and its peers.

{_DALOOPA_TOOLS}
{_PERIOD_DETERMINATION}
{_CITATIONS}
{_NUMBER_FMT}
{_TABLE_CONV}
{_MARKET_DATA}
{_CONSENSUS}
{_EXCEL_ARTIFACT}

## Analysis Steps

### 1. Company & Peer Setup
Look up the target company by ticker using `discover_companies`. Capture `company_id`, `latest_calendar_quarter` (anchor for all period calculations), and `latest_fiscal_quarter`. Note the firm name for report attribution (default: "Daloopa").

Then identify 6-10 comparable companies (direct competitors, business model peers, size peers, growth peers). Look up all company_ids. List with justification.

### 2. Deep Data Gathering
For EACH company (target + all peers), pull from Daloopa:

**Calculate 8 quarters backward from `latest_calendar_quarter`. Pull financials:** Revenue, Gross Profit, Operating Income, Net Income, Diluted EPS, OCF, CapEx, D&A, FCF (OCF - CapEx), R&D, SG&A.

**Segment revenue** (all segments, 8 quarters).

**Company-specific KPIs:**
{_KPI_TAXONOMY}

**Market data** per company: price, market cap, EV, shares, beta, all trading multiples (P/E trailing+forward, EV/EBITDA, P/S, P/B, EV/FCF, dividend yield).

### 3. KPI Discovery & Mapping
Build coverage matrix: which KPIs for which companies. Group into categories: Segment Revenue, Growth KPIs, Unit Economics, Efficiency, Engagement. Flag comparable vs company-specific.

### 4. Compute Derived Metrics
Per company: Gross/Operating/Net/FCF margin (each Q), Revenue/EPS YoY (each Q), Net Debt, Net Debt/EBITDA, FCF Yield, Shareholder Yield.

**Implied valuation:** For each methodology (P/E, EV/EBITDA, P/S, EV/FCF): peer median multiple x target metric = implied value → implied share price. Compute median implied price.

### 5. Build Excel

Create the workbook with 8 sheets:

1. **Comp Summary** — All companies, multiples, implied valuation one-pager
2. **Revenue Drivers** — Unit economics decomposition per company (trailing 4Q)
3. **Operating KPIs** — Cross-company KPI comparison matrix
4. **Financial Summary** — Side-by-side income statements (trailing 4Q)
5. **Growth & Margins** — Trend analysis (up to 8Q)
6. **Valuation Detail** — Implied prices by methodology, premium/discount
7. **Balance Sheet & Capital** — Leverage and capital returns
8. **Raw Data** — Full quarterly appendix per company

{_EXCEL_ARTIFACT}

## Output

Present as a React artifact with SheetJS building the .xlsx with all 8 sheets. Include:
- Download button
- HTML preview of Comp Summary and Valuation Detail sheets
- Summary: target positioning vs peers (growth, margins, valuation), most differentiated KPIs, implied valuation range, key risk

All Daloopa-sourced figures use citation format.

Data sourced from Daloopa
"""


@daloopa_mcp.prompt
def ib_deck(ticker: str, category: str = "ib-advisory") -> str:
    """IB Deck"""
    return f"""\
Build an institutional-grade pitch deck for {ticker}.

Category: {category} (options: "ib-advisory" for M&A/fairness opinions, "activist-ls" for shareholder campaigns/investment memos)

{_DALOOPA_TOOLS}
{_PERIOD_DETERMINATION}
{_CITATIONS}
{_NUMBER_FMT}
{_TABLE_CONV}
{_ANALYTICAL_VOICE}
{_MARKET_DATA}
{_CONSENSUS}
{_HTML_TEMPLATE}

## Phases

### Phase 1 — Requirements
Determine deck scope based on category:
- **IB Advisory**: M&A advisory, fairness opinions, board presentations. Navy/steel/gold palette. "CONFIDENTIAL" marking.
- **Activist / L-S Equity**: Shareholder campaigns, investment memos. Navy/blue/orange palette.

**Firm Attribution:**
- Firm name defaults to "Daloopa". If the user specifies a firm name in their prompt, use that instead.
- **NEVER hallucinate a firm name** (Goldman Sachs, Morgan Stanley, JPMorgan, etc.).
- Include firm name on the cover slide and in all slide footers.

### Phase 2 — Data Gathering
Look up the company by ticker using `discover_companies`. Capture `company_id`, `latest_calendar_quarter`, and `latest_fiscal_quarter`. Use `latest_calendar_quarter` to anchor all period calculations.

Use Daloopa MCP for all financial data. Target comprehensive coverage:
- **5+ years of quarterly financials** — calculate 20+ quarters backward from `latest_calendar_quarter` (income statement, balance sheet, cash flow)
- Segment and geographic breakdowns
- All company-specific KPIs
- 6-10 peers with trading multiples and Daloopa fundamentals
- Guidance and consensus estimates
- SEC filings: risk factors, growth drivers, M&A commentary, strategic language

Get market data for target and all peers: price, market cap, shares, beta, multiples, historical prices for TSR.

### Phase 3 — Analysis
- **Valuation**: DCF (WACC, 5Y FCF, terminal, sensitivity), comps table, implied range
- **Scenarios**: Bull/base/bear with bottoms-up segment builds — be honest about most likely
- **Capital allocation**: Buybacks, dividends, yield, leverage — flag value-destructive patterns
- **Projections**: 3-5 year forward — challenge assumptions

**Critical assessment:** The deck should present an honest analytical view, not a promotional pitch. If the valuation looks stretched, say so. If growth is decelerating, show it clearly. If risks are material, give them proper weight. Institutional investors will dismiss analysis that reads as advocacy rather than research.

### Phase 4 — Build Presentation
Structure as 14 slides. Present each as a section with content:

1. **Cover** — Company name, deck title, date, "Prepared by {{FIRM_NAME}}", "CONFIDENTIAL" marking (if IB Advisory)
2. **Disclaimer** — Standard legal boilerplate
3. **Table of Contents** — Numbered sections
4. **Section Divider: Situation Overview**
5. **Executive Summary** — Two columns: situation overview + key findings
6. **Company Overview** — KPI callout row (4-6 key metrics), business description, segment breakdown table
7. **Financial Summary** — Dense table: income statement + margins + per-share + growth rates (8+ quarters)
8. **Section Divider: Valuation Analysis**
9. **Peer Benchmarking** — Full comps table (6-10 peers, multiples, footnoted)
10. **Valuation Analysis** — Football field description (horizontal bars per methodology with ranges) + methodology summary
11. **DCF Detail** — Projection table + sensitivity matrix + WACC assumptions
12. **Section Divider: Conclusion**
13. **Scenario Analysis** — Bull/base/bear comparison + metric table
14. **Appendix** — Raw data tables

Every content slide must have 2-3+ data-rich elements. No sparse slides. All figures with Daloopa citations.

**Slide footer** (on every slide except cover): left="Prepared by {{FIRM_NAME}}", center="CONFIDENTIAL" (if IB Advisory), right="Page N". Replace {{FIRM_NAME}} with user-specified firm or "Daloopa" (default). NEVER hallucinate a firm name.

## Output

Present as a **complete, self-contained HTML document** using the design-system CSS template above. Use CSS `@page` with landscape orientation, 16:9 aspect ratio (1280x720px per slide). Each slide is a `<div class="slide">` with `page-break-after: always`.

Every content slide must include KPI callout rows, dense tables, football field chart (CSS-only horizontal bars), sensitivity matrices, etc. All figures with Daloopa citations.

Summarize: key findings, implied valuation range, number of slides.

Data sourced from Daloopa
"""


# ============================================================================
# 3. COMPOSITE SKILLS
# ============================================================================


@daloopa_mcp.prompt
def initiate(ticker: str) -> str:
    """Initiate"""
    return f"""\
Initiate coverage on {ticker}. Produce both a comprehensive research note AND an Excel financial model from a single data-gathering pass.

NOTE: The original skill produces .docx + .xlsx via infra scripts. This prompt produces: (1) full research note content as structured markdown, and (2) the Excel model as a React artifact with SheetJS.

{_DALOOPA_TOOLS}
{_PERIOD_DETERMINATION}
{_CITATIONS}
{_NUMBER_FMT}
{_TABLE_CONV}
{_ANALYTICAL_VOICE}
{_MARKET_DATA}
{_CONSENSUS}
{_GUIDANCE_RULES}
{_EXCEL_ARTIFACT}

## Phases

### Phase 1 — Company Setup
Look up {ticker} using `discover_companies`. Capture:
- `company_id`
- `latest_calendar_quarter` — anchor for all period calculations
- `latest_fiscal_quarter`
- Firm name for report attribution (default: "Daloopa")

Get market data: price, market cap, shares, beta, multiples, risk-free rate.

### Phase 2 — Comprehensive Data Gathering
Calculate 8-16 quarters backward from `latest_calendar_quarter`. Pull the superset needed for both outputs:

**Full Income Statement:** Revenue, COGS, Gross Profit, R&D, SG&A, Total OpEx, Operating Income, Interest, Pre-tax Income, Tax, Net Income, Diluted EPS, Shares, EBITDA/D&A.

**Full Balance Sheet:** Cash, Investments, AR, Inventory, Current Assets, PP&E, Goodwill, Total Assets, AP, Short/Long Debt, Total Liabilities, Equity.

**Full Cash Flow:** OCF, CapEx, D&A, Acquisitions, Dividends, Buybacks, FCF.

**Segments:** Revenue and operating income by segment.

**Geographic:** Revenue by geography.

**KPIs:**
{_KPI_TAXONOMY}

**Guidance:** All guidance series and actuals.

### Phase 3 — Peer Analysis
Identify 5-8 peers. Get trading multiples. Include NTM estimates if consensus available. Pull peer fundamentals from Daloopa (revenue growth, margins).

### Phase 4 — Projections
Project 4-8 quarters forward: Revenue (guidance + decay), margins (mean-revert), CapEx, D&A, tax, share count (trailing trends). Show assumptions.

### Phase 5 — DCF Valuation
WACC (CAPM), 5-year FCF projections, terminal value (perpetuity growth 2.5-3%), implied share price, sensitivity table (WACC x terminal growth).

### Phase 6 — Qualitative Research
Search filings for: risk factors, growth drivers, competitive dynamics, management outlook, capital allocation strategy, company-specific strategic topics. Extract: business description, risks (ranked), investment thesis, catalysts.

### Phase 7 — What You Need to Believe
Build falsifiable bull/bear beliefs:
- 4-6 bull beliefs with evidence and citations (testable in 6 months)
- 4-6 bear beliefs with evidence and citations
- Valuation math for each side: forward multiple x earnings = target
- Risk/reward asymmetry assessment

### Phase 8 — Synthesis
Executive summary (3-4 sentences with directional view), variant perception, key findings (top 3-5), five key tensions, monitoring framework (quantitative + qualitative).

News context: web search for recent headlines, analyst sentiment, catalysts, industry outlook. Organize into timeline, forward catalysts, policy backdrop.

## Output — Part 1: Research Note

Present the complete research note as structured markdown with all sections:
Cover, Five Key Tensions, Executive Summary, Investment Thesis, Company Description, News Timeline, Financial Analysis (8Q tables + margins + OpEx), Industry Deep Dive, Segments/Geographic, KPIs, Guidance Track Record, What You Need to Believe, Catalysts, Capital Allocation, Valuation (DCF + Comps), Risks, Monitoring Framework.

## Output — Part 2: Excel Model

Create a React artifact with SheetJS building the .xlsx with 9 sheets:
1. Dashboard, 2. Income Statement, 3. Balance Sheet, 4. Cash Flow, 5. Segments, 6. KPIs, 7. Projections (yellow editable cells), 8. DCF, 9. Comps

Include download button and HTML previews.

Summary: key valuation range (DCF + comps), top 3 findings.

Data sourced from Daloopa
"""
