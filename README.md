# Daloopa Starter Kit for Claude Code

A ready-to-go financial analysis toolkit that connects Claude Code to [Daloopa's](https://daloopa.com) institutional-grade financial data. Built for hedge fund analysts (L/S equity, quant) who want AI-assisted fundamental research.

Produces two Wall Street deliverables: **Research Notes (.docx)** and **Excel Models (.xlsx)**.

## Prerequisites

- **Claude Code** — Install with `npm install -g @anthropic-ai/claude-code`
- **Daloopa account** — Sign up at [daloopa.com](https://daloopa.com) (for OAuth) or obtain an API key
- **Python 3.9+** — For infrastructure scripts (market data, charts, Excel/Word rendering)

## Quick Start

```bash
# 1. Clone the repo
git clone <repo-url> && cd investing

# 2. Install Python dependencies
pip3 install -r requirements.txt

# 3. Open in Claude Code
claude

# 4. Run the setup wizard
/setup
```

The `/setup` command will walk you through authenticating with Daloopa (OAuth opens in your browser), verifying the MCP connection, and running your first query.

**That's it.** On your first Daloopa tool call, OAuth will prompt you to log in via your browser. No API keys or `.env` files needed.

## Available Commands

### Building Block Skills (Markdown Reports)

| Command | Description | Example | Output |
|---------|-------------|---------|--------|
| `/setup` | Interactive setup wizard | `/setup` | — |
| `/earnings` | Full earnings analysis with guidance tracking | `/earnings AAPL` | `reports/AAPL_earnings_2025Q3.md` |
| `/tearsheet` | Quick one-page company overview | `/tearsheet MSFT` | `reports/MSFT_tearsheet.md` |
| `/industry` | Cross-company industry comparison | `/industry AAPL MSFT GOOG AMZN` | `reports/AAPL_MSFT_GOOG_AMZN_industry_comp.md` |
| `/bull-bear` | Bull/bear/base scenario framework | `/bull-bear TSLA` | `reports/TSLA_bull_bear.md` |
| `/guidance-tracker` | Track management guidance accuracy | `/guidance-tracker NVDA` | `reports/NVDA_guidance_tracker.md` |
| `/inflection` | Auto-detect metric accelerations/decelerations | `/inflection AAPL` | `reports/AAPL_inflection.md` |
| `/capital-allocation` | Buybacks, dividends, shareholder yield | `/capital-allocation MSFT` | `reports/MSFT_capital_allocation.md` |
| `/dcf` | DCF valuation with sensitivity analysis | `/dcf AAPL` | `reports/AAPL_dcf.md` |
| `/comps` | Trading comparables with peer multiples | `/comps AAPL` | `reports/AAPL_comps.md` |

### Wall Street Deliverables (.docx and .xlsx)

| Command | Description | Example | Output |
|---------|-------------|---------|--------|
| `/research-note` | Professional Word research note | `/research-note AAPL` | `reports/AAPL_research_note.docx` |
| `/model` | Multi-tab Excel financial model | `/model AAPL` | `reports/AAPL_model.xlsx` |
| `/initiate` | Initiate coverage (both outputs) | `/initiate AAPL` | `.docx` + `.xlsx` |
| `/update` | Refresh coverage with latest data | `/update AAPL` | Updated `.docx` + `.xlsx` |

All reports are saved to the `reports/` directory. You can also just ask Claude anything about a company — the commands are shortcuts for common workflows.

## MCP Servers

This project connects to two Daloopa MCP servers:

| Server | URL | Purpose |
|--------|-----|---------|
| `daloopa` | `mcp.daloopa.com/server/mcp` | Financial data — company fundamentals, KPIs, SEC filings |
| `daloopa-docs` | `docs.daloopa.com/mcp` | Daloopa knowledgebase — API docs, how-tos, usage help |

The **data server** provides 4 tools:

| Tool | Purpose |
|------|---------|
| `discover_companies` | Look up companies by ticker or name |
| `discover_company_series` | Find available financial metrics and KPIs for a company |
| `get_company_fundamentals` | Pull financial data for specific metrics and periods |
| `search_documents` | Search SEC filings (10-K, 10-Q, 8-K) for qualitative info |

The **docs server** lets Claude answer questions about the Daloopa API, data coverage, and platform features directly. A local copy of the docs is also available in `daloopa_docs/`.

Full docs: [docs.daloopa.com](https://docs.daloopa.com)

## Project Structure

```
├── .claude/
│   └── skills/                # Claude Code skill definitions
│       ├── data-access.md     # Shared data access reference
│       ├── setup/             # /setup — interactive setup wizard
│       ├── earnings/          # /earnings — earnings analysis
│       ├── tearsheet/         # /tearsheet — company one-pager
│       ├── industry/          # /industry — cross-company comp
│       ├── bull-bear/         # /bull-bear — scenario analysis
│       ├── guidance-tracker/  # /guidance-tracker — guidance vs actuals
│       ├── inflection/        # /inflection — acceleration/deceleration detection
│       ├── capital-allocation/# /capital-allocation — capital deployment
│       ├── dcf/               # /dcf — DCF valuation
│       ├── comps/             # /comps — trading comparables
│       ├── research-note/     # /research-note — Word document output
│       ├── model/             # /model — Excel model output
│       ├── initiate/          # /initiate — both outputs
│       └── update/            # /update — refresh coverage
├── infra/                     # Infrastructure scripts
│   ├── market_data.py         # Market data from yfinance/FRED
│   ├── chart_generator.py     # Professional chart generation
│   ├── projection_engine.py   # Forward financial projections
│   ├── excel_builder.py       # Multi-tab Excel model builder
│   ├── docx_renderer.py       # Word document renderer
│   └── report_differ.py       # Context diff for updates
├── templates/
│   └── research_note.docx     # Word template (Jinja2 tags)
├── scripts/
│   ├── create_template.py     # Generate the Word template
│   └── docs_crawler.py        # Re-crawl Daloopa docs
├── recipes/                   # Python recipe scripts for API access
├── daloopa_docs/              # API documentation (local copy)
├── reports/                   # Generated reports (gitignored)
│   ├── .charts/               # Generated charts
│   └── .tmp/                  # Context JSON files
├── .mcp.json                  # MCP server config
├── .env.example               # API key template
├── requirements.txt           # Python dependencies
├── CLAUDE.md                  # AI assistant instructions
└── README.md
```

## For API Key Users

If you prefer API key auth over OAuth (e.g., for headless/programmatic use):

1. Copy the env template:
   ```bash
   cp .env.example .env
   ```

2. Add your Daloopa API key to `.env`:
   ```
   DALOOPA_API_KEY=your_actual_key_here
   ```

3. Update the `daloopa` entry in `.mcp.json` to include the API key header:
   ```json
   {
     "mcpServers": {
       "daloopa": {
         "type": "url",
         "url": "https://mcp.daloopa.com/server/mcp",
         "headers": {
           "x-api-key": "${DALOOPA_API_KEY}"
         }
       },
       "daloopa-docs": {
         "type": "url",
         "url": "https://docs.daloopa.com/mcp"
       }
     }
   }
   ```

4. Restart Claude Code for the changes to take effect.

## Optional API Keys

| Key | Purpose | How to Get |
|-----|---------|------------|
| `FRED_API_KEY` | Risk-free rate for DCF/WACC | Free at [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html) |
| `FMP_API_KEY` | Fallback market data (250 calls/day) | Free at [financialmodelingprep.com](https://financialmodelingprep.com/developer) |

Add to `.env` if desired. Without FRED, DCF calculations default to a 4.5% risk-free rate.

## Refreshing Documentation

To re-crawl the Daloopa docs (e.g., after API updates):

```bash
python3 scripts/docs_crawler.py
```
