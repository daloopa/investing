---
name: ib-deck
description: Generate an institutional-grade investment banking pitch deck (HTML → PDF)
argument-hint: TICKER [--category ib-advisory|activist-ls]
---

Build an institutional-grade pitch deck for the company specified by the user: $ARGUMENTS

**Before starting, read the `data-access.md` reference (co-located with this skill) for data access methods and `design-system.md` for formatting conventions.** Also read the reference files in this skill's `references/` directory for slide templates and components.

This is a project-only skill that generates a self-contained HTML presentation and renders it to PDF.

## Phase 1 — Requirements

Determine the deck category and scope:

**Category** (infer from context, or default to IB Advisory):
- **IB Advisory** — M&A advisory, fairness opinions, board presentations. Navy/steel/gold palette. "CONFIDENTIAL" marking.
- **Activist / L-S Equity** — Shareholder campaigns, investment memos as decks. Navy/blue/orange or navy/sky/green palette.

**Gather from the user or infer:**
- Target company (ticker)
- Purpose (M&A pitch, fairness opinion, investment memo, activist campaign)
- Key thesis or strategic rationale
- Specific slides needed (or use the default 14-slide deck)

## Phase 2 — Data Gathering

Use Daloopa MCP for all financial data. Target comprehensive coverage:
- **5+ years of quarterly financials** (income statement, balance sheet, cash flow)
- **Segment and geographic breakdowns**
- **All company-specific operating KPIs**
- **6-10 peers** — get trading multiples and fundamentals from Daloopa + market data (see data-access.md Section 2)
- **Guidance and consensus** (see data-access.md Section 3)
- **SEC filings** — risk factors, growth drivers, M&A commentary, strategic language

Get market data for the target and all peers:
- Current price, market cap, shares outstanding, beta, trading multiples
- Historical price data for TSR comparison

## Phase 3 — Analysis

Run the core analyses needed for the deck:
- **Valuation**: DCF (WACC, 5Y FCF projections, terminal value, sensitivity), comps table, implied valuation range
- **Scenario analysis**: Bull/base/bear with bottoms-up segment builds — be honest about which scenario is most likely
- **Capital allocation**: Buybacks, dividends, shareholder yield, leverage — flag any value-destructive patterns
- **Financial projections**: 3-5 year forward estimates — challenge assumptions, don't just extrapolate

**Critical assessment:** The deck should present an honest analytical view, not a promotional pitch. If the valuation looks stretched, say so. If growth is decelerating, show it clearly. If risks are material, give them proper weight. Institutional investors will dismiss analysis that reads as advocacy rather than research.

## Phase 4 — Build Presentation

Generate a self-contained HTML file following the templates in `references/slide-templates.md`. Use components from `references/financial-components.md`.

**Slide structure** (default 14-slide deck — adapt based on purpose):

1. **Cover** — Company name, deck title, date, "CONFIDENTIAL" (if IB Advisory)
2. **Disclaimer** — Standard legal boilerplate
3. **Table of Contents** — Numbered sections
4. **Section Divider: Situation Overview**
5. **Executive Summary** — Two-column: situation overview + key findings
6. **Company Overview** — KPI callout row + business description + segment breakdown
7. **Financial Summary** — Dense income statement + margins + per-share + growth rates
8. **Section Divider: Valuation Analysis**
9. **Peer Benchmarking** — Full comps table (6-10 peers, trading multiples, footnoted)
10. **Valuation Analysis** — Football field chart + methodology summary
11. **DCF Detail** — Projection table + sensitivity matrix + assumptions
12. **Section Divider: Conclusion**
13. **Scenario Analysis** — Bull/base/bear bars + metric comparison table
14. **Appendix** — Raw data tables, dense formatting

**Key rules:**
- Every content slide must have minimum 2-3 data-rich elements (tables, charts, commentary)
- No sparse slides — fill the space with analysis
- All financial figures must include Daloopa citations
- Follow design-system.md for colors, typography, number formatting
- Use CSS `@page` with landscape orientation, 16:9 aspect ratio (1280×720px per slide)
- Each slide is a `<div class="slide">` with `page-break-after: always`

See `references/ib-advisory-patterns.md` for valuation methodology templates.

## Phase 5 — Render PDF

1. Save the HTML to `reports/{TICKER}_deck.html`
2. Run: `python infra/deck_renderer.py --input reports/{TICKER}_deck.html --output reports/{TICKER}_deck.pdf`
3. If rendering fails, the HTML file is still usable (open in any browser)

## Output

Tell the user:
- Where the PDF was saved: `reports/{TICKER}_deck.pdf`
- Where the HTML source was saved: `reports/{TICKER}_deck.html`
- 2-3 sentence summary of the deck's key findings
- Implied valuation range
- How many slides were generated

All financial figures must use Daloopa citation format: [$X.XX million](https://daloopa.com/src/{fundamental_id})
