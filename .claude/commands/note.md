---
description: Generate a professional equity research note for any public company
argument-hint: Company ticker (e.g., "AAPL" or "NVDA" or "TSLA")
---

# Equity Research Note Generator

Generate an institutional-grade equity research note as an HTML document.

**Request**: $ARGUMENTS

Follow the equity-note skill workflow to produce a comprehensive deep dive research note. The note must cover:

1. **Identify the company**: Use `discover_companies` to find the company by ticker or name.
2. **Deep financial research**: Pull comprehensive financial data from Daloopa MCP — income statement, margins, guidance evolution, balance sheet, cash flow, segment data, and industry-specific KPIs — across the last 8-12 quarters. Simultaneously run web searches for recent news, analyst commentary, catalysts, and industry context.
3. **Document search**: Use Daloopa `search_documents` for management commentary, guidance evolution, risk factors, and strategic outlook from SEC filings.
4. **Synthesize and write**: Generate a self-contained HTML file following the exact template and design system in the equity-note skill — header, KPIs, executive summary, news timeline, financial tables with Daloopa citations, cost/margin analysis, industry-specific deep dive, forward catalysts, bull/bear framework, and monitoring checklist.
5. **Deliver**: Write the HTML file to `~/Generated Stuff/[TICKER]-note.html` and open it in the browser.

Every financial figure must include a Daloopa citation hyperlink `https://daloopa.com/src/{fundamental_id}`. The note should be information-dense and analytically rigorous.
