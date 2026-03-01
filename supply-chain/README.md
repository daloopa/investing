# Supply Chain Dashboard — Claude Code Plugin

A Claude Code plugin that generates interactive, self-contained supply chain dashboards for any public company. Maps upstream suppliers (Tier 1, 2, 3), downstream customers, and quantifies financial interdependencies at each layer.

![License](https://img.shields.io/badge/license-MIT-blue)

## What It Does

Given a company ticker, the plugin:

1. **Identifies 8–15 key suppliers** through SEC filings (10-K/10-Q), Daloopa document search, and web research
2. **Pulls 10 quarters of financial data** (revenue, gross profit, net income, gross margin) for every company in the chain
3. **Pulls 10 quarters of inventory data** (raw materials, WIP, finished goods) and computes composition percentages
4. **Estimates supply chain concentration** — what % of the target's COGS each supplier represents, and what % of each supplier's revenue comes from the target
5. **Classifies suppliers by tier** — Critical/Sole-source, Major Component, Specialty
6. **Generates a single HTML file** with no external dependencies

## Dashboard Features

- **Canvas network visualization** — tier-grouped columns (Tier 3 → Tier 2 → Tier 1 → Target → Customers) with clickable nodes
- **Inventory Health Overview** — stacked RM/WIP/FG composition bars for all suppliers
- **Supplier cards by tier** — grouped under tier headings, clickable to open detail overlays
- **Detail overlays** — 10-quarter financials table, 10-quarter inventory table, Canvas stacked bar chart with GM% line overlay
- **Supply Chain Shock Analysis** — narrative on most exposed/resilient suppliers + impact matrix (Revenue Impact, Margin Impact, Inventory Risk)
- **Concentration analysis** — supplier concentration, revenue dependency, geographic exposure, single-source flags
- **Daloopa citations** — every financial figure hyperlinks to its source filing
- **Print to PDF** — built-in button using `window.print()`
- **DOM-safe JavaScript** — all DOM construction uses `createElement`/`textContent`/`appendChild`, zero `innerHTML`

## Requirements

- [Claude Code](https://claude.ai/claude-code) CLI
- **Daloopa MCP server** configured in your Claude Code settings — this plugin uses Daloopa's financial data API for all company financials, inventory data, and document search

## Installation

### From GitHub

Add to your Claude Code plugins by cloning into your plugins directory:

```bash
# Clone into Claude Code plugins directory
git clone https://github.com/tlijr/supply-chain.git ~/.claude/plugins/supply-chain
```

Then restart Claude Code. The plugin will be auto-discovered.

### Manual

Copy the entire repo into `~/.claude/plugins/supply-chain/` and ensure the directory structure looks like:

```
~/.claude/plugins/supply-chain/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   └── supply-chain.md
├── skills/
│   └── supply-chain/
│       └── SKILL.md
└── README.md
```

## Usage

In Claude Code, run:

```
/supply-chain AAPL
```

Replace `AAPL` with any public company ticker. The plugin will research the supply chain, pull financials from Daloopa, and generate an interactive dashboard at:

```
~/Generated Stuff/[TICKER]-supply-chain.html
```

The file opens automatically in your default browser.

## Example Output

Dashboards have been generated and tested for:
- **AAPL** — Apple supply chain (TSMC, Foxconn/Hon Hai, Broadcom, Samsung, Corning, etc.)
- **TSLA** — Tesla supply chain (Panasonic, LG Energy, Samsung SDI, Infineon, NXP, STM, etc.)

## How It Works

The plugin follows a multi-phase research workflow:

| Phase | Description |
|-------|-------------|
| 1 | Target company identification + financials from Daloopa |
| 2 | Supplier identification via SEC filings, Daloopa docs, web research |
| 3 | Supplier financial analysis — 10Q financials + inventory for each supplier |
| 4 | Customer/downstream analysis |
| 5 | Tier 2 supplier research (suppliers' suppliers) |
| 6 | Shock analysis — dependency classification + impact matrix |
| 7 | HTML generation — single self-contained file, DOM-safe JS |

All phases maximize parallelism across independent API calls.

## Design

The dashboard aesthetic is **"Financial Times meets clean data visualization"**:

- Light mode, off-white backgrounds
- Serif headlines (Georgia), sans-serif body (system-ui)
- Minimal color: black text, gray borders, blue links, green/red for financial sentiment only
- Information-dense with clear hierarchy
- Responsive layout

## Data Sources

- **[Daloopa](https://daloopa.com)** — financial fundamentals, inventory data, SEC filing search (via MCP)
- **Web research** — supplier identification, revenue concentration estimates, industry reports
- **SEC filings** — 10-K/10-Q supplier disclosures, customer concentration data

## License

MIT
