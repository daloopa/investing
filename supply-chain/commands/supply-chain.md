---
description: Create an interactive supply chain dashboard for any public company
argument-hint: Company ticker (e.g., "AAPL" or "TSLA" or "NVDA")
---

# Supply Chain Dashboard Generator

Generate an interactive supply chain map and financial dashboard as an HTML document.

**Request**: $ARGUMENTS

Follow the supply-chain skill workflow to produce a comprehensive interactive supply chain dashboard. The dashboard must:

1. **Identify the company**: Use `discover_companies` to find the company by ticker or name.
2. **Research supply chain**: Use Daloopa `search_documents` to find supplier mentions in 10-K, 10-Q filings. Simultaneously run web searches to identify key suppliers and customers.
3. **Map supplier relationships**: For each identified supplier, determine:
   - What they supply to the target company
   - Estimated % of target company's total COGS attributable to that supplier (with logic/citation)
   - What % of the supplier's revenue comes from the target company
4. **Map customer relationships**: Identify companies where the target is a major supplier.
5. **Pull financials & inventory**: For each company in the supply chain, pull 10 quarters of financial data (revenue, GP, NI, GM%) AND inventory breakdown (RM, WIP, FG, total) from Daloopa MCP.
6. **Inventory analysis**: Compute RM%, WIP%, FG% for each supplier. Build an inventory health overview table with stacked composition bars.
7. **Build interactive dashboard**: Generate a self-contained HTML file with:
   - Canvas-based tier-grouped network visualization (Tier 3 → Tier 2 → Tier 1 → Target → Customers)
   - Inventory Health Overview table with RM/WIP/FG composition bars
   - Supplier cards grouped by tier level, clickable to open detail overlays
   - Detail overlays with 10-quarter financials, inventory tables, and Canvas inventory-vs-GM% charts
   - Supply Chain Shock Analysis with narrative + impact matrix
   - Clean, newspaper-style design (light mode, serif/sans-serif professional typefaces)
   - DOM-safe JavaScript (createElement + textContent, no HTML-string injection)
8. **Deliver**: Write the HTML file to `~/Generated Stuff/[TICKER]-supply-chain.html` and open it in the browser.

Every financial figure must include a Daloopa citation hyperlink. The dashboard should be information-dense and analytically rigorous.
