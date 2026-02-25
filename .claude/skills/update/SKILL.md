---
name: update
description: Refresh existing research note and Excel model with latest data
argument-hint: TICKER
---

Update existing coverage for the company specified by the user: $ARGUMENTS

**Before starting, read the `data-access.md` reference (co-located with this skill) for data access methods and `design-system.md` for formatting conventions.** Follow the data access detection logic and design system throughout this skill.

This skill refreshes existing deliverables with the latest quarterly data, highlights what changed, and re-renders both outputs.

## Phase 1 — Load Existing Context
Check for existing context files in `reports/.tmp/`:
- `reports/.tmp/{TICKER}_context.json` (research note context)
- `reports/.tmp/{TICKER}_model_context.json` (model context)

If neither exists, tell the user: "No existing coverage found for {TICKER}. Run `/initiate {TICKER}` first to create initial coverage." and stop.

Read the existing context(s) to understand what periods and data were previously gathered.

## Phase 2 — Identify New Data
Look up the company to find the latest available quarter.
Compare to the periods in existing context. Determine which new quarters need to be pulled.

If no new quarters are available, tell the user: "Coverage is already current through {latest_period}. No new data to update." and stop.

## Phase 3 — Pull Fresh Data
Pull data for ALL periods (not just new ones) to ensure consistency:
- Full Income Statement, Balance Sheet, Cash Flow
- Segments, KPIs, Guidance
- Share count, buyback activity

This refreshes the entire dataset, catching any Daloopa revisions to prior quarters.

## Phase 4 — Market Data Refresh
Get current prices, trading multiples, and risk-free rate (see data-access.md Section 2).

Also refresh peer multiples if comps data exists in context.

## Phase 5 — Re-run Projections
With updated historical data, re-run projections. If a projection engine is available (see data-access.md Section 5), use it. Otherwise project manually.

## Phase 6 — Diff Analysis
Save the new context alongside the old:
- Write new context to `reports/.tmp/{TICKER}_context_new.json`
- Run: `python infra/report_differ.py --old reports/.tmp/{TICKER}_context.json --new reports/.tmp/{TICKER}_context_new.json --output reports/.tmp/{TICKER}_diff.json`
- Read the diff to understand what changed

Key changes to highlight:
- Revenue/EPS beats or misses vs prior estimates
- Margin changes (expansion or compression)
- Guidance changes (raised, lowered, maintained)
- New KPI data points
- Share count changes (buyback acceleration/deceleration)
- Valuation changes (price moved, multiples shifted)

## Phase 7 — Update Qualitative Sections
Search filings for the new quarter(s):
- Earnings highlights and management commentary
- Updated guidance language
- New risk factors or strategic shifts
- Update investment thesis if data warrants it

Revise the executive summary and key findings to reflect the latest quarter.

## Phase 8 — Re-render Outputs
Update charts with new data points, then re-render:

**Research Note:**
1. Overwrite context: `reports/.tmp/{TICKER}_context.json`
2. Re-generate charts with updated data
3. Run: `python infra/docx_renderer.py --template templates/research_note.docx --context reports/.tmp/{TICKER}_context.json --output reports/{TICKER}_research_note.docx`

**Excel Model:**
1. Overwrite context: `reports/.tmp/{TICKER}_model_context.json`
2. Run: `python infra/excel_builder.py --context reports/.tmp/{TICKER}_model_context.json --output reports/{TICKER}_model.xlsx`

## Phase 9 — Change Summary
Present a clear summary of changes to the user:

```
## {TICKER} Coverage Update — {new_quarter} Added

### Key Changes
- Revenue: $XX.XB vs $XX.XB prior quarter (+X.X% QoQ, +X.X% YoY)
- EPS: $X.XX vs $X.XX guidance (beat/miss by X.X%)
- Gross Margin: XX.X% vs XX.X% prior quarter (+/- XXbps)
- {other notable changes}

### Projection Updates
- {what changed in forward estimates and why}

### Valuation Impact
- DCF implied price: $XXX (was $XXX, change of +/-X%)
- Comps implied range: $XXX - $XXX

### Files Updated
- Research note: reports/{TICKER}_research_note.docx
- Excel model: reports/{TICKER}_model.xlsx
- Diff report: reports/.tmp/{TICKER}_diff.json
```

All financial figures must use Daloopa citation format: [$X.XX million](https://daloopa.com/src/{fundamental_id})
