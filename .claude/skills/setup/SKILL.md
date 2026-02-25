---
name: setup
description: Walk through initial setup and authentication for this Daloopa starter kit
---

Walk the user through setting up this Daloopa starter kit step by step. Be conversational and helpful.

## Step 1: Verify Claude Code
Confirm Claude Code is running (if the user is seeing this, it is — tell them they're good).

## Step 2: Install Python Dependencies
Check if required packages are installed. Offer to install them:
```
pip3 install -r requirements.txt
```
This installs: requests, beautifulsoup4, html2text, yfinance, openpyxl, python-docx, docxtpl, matplotlib, fredapi.

These are needed for market data, chart generation, Excel model building, and Word document rendering.

## Step 3: Daloopa Authentication
Ask the user which authentication method they'd like to use:

**Option A: OAuth (Recommended)**
- The `.mcp.json` is already configured for OAuth
- On the next MCP tool call, a browser window will open for Daloopa login
- No additional configuration needed
- Just make sure they have a Daloopa account at daloopa.com

**Option B: API Key**
- Ask the user for their Daloopa API key
- Create/update `.env` with their key: `DALOOPA_API_KEY=<their_key>`
- Update the `daloopa` entry in `.mcp.json` to include the API key header (keep the `daloopa-docs` entry as-is):
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
- Tell them they'll need to restart Claude Code for the change to take effect

## Step 4: Optional API Keys
Ask if they want to configure optional API keys for enhanced functionality:

**FRED API Key** (recommended for DCF/valuation work):
- Free at https://fred.stlouisfed.org/docs/api/api_key.html
- Used for risk-free rate in WACC calculations
- Without it, a default rate of 4.5% is used
- Add to `.env`: `FRED_API_KEY=<their_key>`

**FMP API Key** (optional fallback for market data):
- 250 free calls/day at https://financialmodelingprep.com/developer
- Fallback if yfinance is unavailable
- Add to `.env`: `FMP_API_KEY=<their_key>`

## Step 5: Verify MCP Connection
This project connects to two Daloopa MCP servers:
- **daloopa** (`mcp.daloopa.com/server/mcp`) — Financial data (fundamentals, KPIs, SEC filings)
- **daloopa-docs** (`docs.daloopa.com/mcp`) — Daloopa knowledgebase (API docs, how-tos, usage help)

Run a quick test by calling `discover_companies` with a well-known ticker like "AAPL" to confirm the data MCP server is connected and responding. Show the user the result.

## Step 6: Verify Market Data
Run a quick test: `python infra/market_data.py quote AAPL`
This should return current price, market cap, etc. from yfinance.

## Step 7: Create Word Template
Run: `python scripts/create_template.py`
This creates the research note template at `templates/research_note.docx`.

## Step 8: Quick Tour
Tell the user about the available slash commands:

**Building Block Skills** (markdown reports):
- `/earnings TICKER` — Full earnings analysis with guidance tracking
- `/tearsheet TICKER` — Quick one-page company overview
- `/industry TICKER1 TICKER2 ...` — Cross-company comparison
- `/bull-bear TICKER` — Bull/bear/base scenario framework
- `/guidance-tracker TICKER` — Track management guidance accuracy
- `/inflection TICKER` — Auto-detect metric accelerations/decelerations
- `/capital-allocation TICKER` — Buybacks, dividends, shareholder yield
- `/dcf TICKER` — DCF valuation with sensitivity analysis
- `/comps TICKER` — Trading comparables with peer multiples

**Investment Deliverables** (.docx, .xlsx, .pdf):
- `/research-note TICKER` — Professional Word research note
- `/build-model TICKER` — Multi-tab Excel financial model
- `/initiate TICKER` — Both research note + Excel model (initiating coverage)
- `/update TICKER` — Refresh existing coverage with latest data
- `/ib-deck TICKER` — Institutional-grade pitch deck (HTML → PDF)

All output is saved to the `reports/` directory.

Suggest they try `/tearsheet AAPL` as a quick first test to see everything working end-to-end.
