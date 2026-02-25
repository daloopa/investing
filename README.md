# Daloopa Starter Kit for Claude Code

A ready-to-go financial analysis toolkit that connects Claude Code to [Daloopa's](https://daloopa.com) institutional-grade financial data. Built for hedge fund analysts (L/S equity, quant) who want AI-assisted fundamental research.

Produces investment deliverables: **Research Notes (.docx)**, **Excel Models (.xlsx)**, **PDF Reports**, and **Pitch Decks (.pdf)**.

## Prerequisites

- **Claude Code** — Install with `npm install -g @anthropic-ai/claude-code`
- **Daloopa account** — Sign up at [daloopa.com](https://daloopa.com)
- **Python 3.9+** — For infrastructure scripts (market data, charts, Excel/Word/PDF rendering)

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/daloopa/investing.git && cd investing

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

### Building Block Skills (Markdown + PDF Reports)

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

### Investment Deliverables (.docx, .xlsx, .pdf)

| Command | Description | Example | Output |
|---------|-------------|---------|--------|
| `/research-note` | Professional Word research note | `/research-note AAPL` | `reports/AAPL_research_note.docx` |
| `/build-model` | Multi-tab Excel financial model | `/build-model AAPL` | `reports/AAPL_model.xlsx` |
| `/initiate` | Initiate coverage (both outputs) | `/initiate AAPL` | `.docx` + `.xlsx` |
| `/update` | Refresh coverage with latest data | `/update AAPL` | Updated `.docx` + `.xlsx` |
| `/ib-deck` | Institutional-grade pitch deck | `/ib-deck AAPL` | `reports/AAPL_deck.pdf` |

All reports are saved to the `reports/` directory. You can also just ask Claude anything about a company — the commands are shortcuts for common workflows.

## Plugin

The 10 building block analysis skills are also available as a standalone **Claude Code plugin** that works in any project — no Python infrastructure needed, just a Daloopa account.

See [`../daloopa-plugin/`](../daloopa-plugin/) or install from the Claude Code marketplace.

## Data Access

### MCP Server (Default — Interactive with Claude Code)

Two MCP servers are pre-configured in `.mcp.json`:

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

By default, authentication is via OAuth — a browser window opens on your first tool call. No API keys needed.

If you prefer API key auth for the MCP server (e.g., headless environments), update `.mcp.json`:

```json
{
  "mcpServers": {
    "daloopa": {
      "type": "http",
      "url": "https://mcp.daloopa.com/server/mcp",
      "headers": {
        "x-api-key": "${DALOOPA_API_KEY}"
      }
    },
    "daloopa-docs": {
      "type": "http",
      "url": "https://docs.daloopa.com/mcp"
    }
  }
}
```

Then add your key to `.env`:
```
DALOOPA_API_KEY=your_api_key_here
```

### Direct REST API (Programmatic — Python Scripts)

The same API key also works with the [Daloopa REST API](https://docs.daloopa.com) directly. The `recipes/` directory contains Python scripts for headless automation, batch processing, or building custom pipelines.

| Script | Purpose |
|--------|---------|
| `recipes/company_fundamentals.py` | Look up companies, discover series, fetch fundamentals |
| `recipes/document_search.py` | Search SEC filings for keywords |
| `recipes/export_csv.py` | Bulk export fundamentals to CSV |
| `recipes/download_model.py` | Download pre-built Excel models |
| `recipes/industry_analysis.py` | Cross-industry comparisons via taxonomy |
| `recipes/taxonomy_comparison.py` | Standardized metric comparisons across companies |
| `recipes/poll_for_updates.py` | Monitor companies for new earnings releases |
| `recipes/series_continuation.py` | Track deprecated series and their replacements |

All scripts use `recipes/daloopa_client.py` for authentication (Basic Auth with email + API key).

**Setup for API access:**

```bash
cp .env.example .env
# Edit .env with your credentials:
#   DALOOPA_EMAIL=you@example.com
#   DALOOPA_API_KEY=your_api_key_here
```

Then run any recipe:
```bash
python3 recipes/company_fundamentals.py AAPL
python3 recipes/document_search.py "AI revenue" --companies AAPL MSFT
python3 recipes/export_csv.py AAPL
```

The Claude Code skills auto-detect which access method is available and use whichever is configured. See `.claude/skills/data-access.md` for details.

Full API docs: [docs.daloopa.com](https://docs.daloopa.com)

## Project Structure

```
├── .claude/
│   └── skills/                # Claude Code skill definitions
│       ├── data-access.md     # Shared data access reference
│       ├── design-system.md   # Formatting and styling conventions
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
│       ├── ib-deck/           # /ib-deck — pitch deck builder
│       ├── research-note/     # /research-note — Word document output
│       ├── build-model/       # /build-model — Excel model output
│       ├── initiate/          # /initiate — both outputs
│       └── update/            # /update — refresh coverage
├── recipes/                   # Python scripts for direct API access
│   ├── daloopa_client.py      # Shared HTTP client with auth
│   ├── company_fundamentals.py
│   ├── document_search.py
│   ├── export_csv.py
│   ├── download_model.py
│   ├── industry_analysis.py
│   ├── taxonomy_comparison.py
│   ├── poll_for_updates.py
│   └── series_continuation.py
├── infra/                     # Infrastructure scripts (used by skills)
│   ├── market_data.py         # Market data from yfinance/FRED
│   ├── chart_generator.py     # Professional chart generation (6 types)
│   ├── projection_engine.py   # Forward financial projections
│   ├── excel_builder.py       # Multi-tab Excel model builder
│   ├── docx_renderer.py       # Word document renderer
│   ├── pdf_renderer.py        # Markdown → styled PDF
│   ├── deck_renderer.py       # HTML deck → PDF
│   └── report_differ.py       # Context diff for updates
├── templates/
│   └── research_note.docx     # Word template (Jinja2 tags)
├── scripts/
│   ├── create_template.py     # Generate the Word template
│   ├── sync_plugin.sh         # Sync shared skills to plugin repo
│   └── docs_crawler.py        # Re-crawl Daloopa docs
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
