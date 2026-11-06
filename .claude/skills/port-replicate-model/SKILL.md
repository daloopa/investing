---
name: port-replicate-model
description: Replicate an existing model/template for a new company, linked to the user's data tab
argument-hint: "TICKER [instructions]"
---

Replicate an existing Excel model or template for the company specified by the user: $ARGUMENTS

**Before starting, read `../data-access.md` for data access methods, `../modeling-conventions.md` for the cardinal rule (conform to the user's style) and the linkage a model should follow, and `../fix-debug-audit/references/model-checks.md` for the checks used to verify the port.**

The common real ask is not "build from scratch" — it's *"make my model for company A work for company B"* and *"link the historicals to the DATA tab I already pulled."* This skill covers both, because they almost always come together. Match the template's structure, formatting and formula logic exactly; swap only the company's data, segments and KPIs.

## Inputs

| Input | Form | Required |
|---|---|---|
| `TICKER` | The **new** company's ticker, first word of the arguments | Yes — ask if missing |
| `instructions` | Free text after the ticker | No |

Instructions can name tabs ("follow `TNL Model`, build in `HGV`", "use Sheet1 as the source data"), set limits ("only change the grey hardcoded cells"), call out incidental references ("update the ticker in B2 and the Thesis tab"), or give a workbook path. Anything named there overrides detection.

Examples: `/port-replicate-model HGV` · `/port-replicate-model USB only change the grey cells` · `/port-replicate-model SHW the computer crashed, continue the SHW tab`

## Step 0 — Resolve and Announce

1. **Workbook.** A path in the instructions; otherwise the most recently modified `.xlsx`/`.xlsm` in `reports/`, then the working directory — skipping files this toolkit generated (names ending `_port_YYYYMMDD`, `_audit_YYYYMMDD`, `_model`, `_comp_sheet`). If none is found, ask for the path.
2. **Sheets.** `python infra/workbook_tools.py tabs WORKBOOK` — each sheet's used range, cell mix (input / formula / text), whether it's blank, and which sheets its formulas read from. Carry any `warning` (charts, pivots, external links) into the announce line.
3. **Detect the roles** (instructions override every one):
   - **Data tab** — a sheet named `DATA`, `Daloopa`, `Input` or `Sheet1`, or a mostly-input sheet that the model sheet `reads_from`. May not exist.
   - **Source (template)** — the populated model sheet: most formula cells, not the data tab.
   - **Target** — a sheet whose name contains the new ticker; else a blank sheet; else the source itself.
   - **Shape:**
     | Target state | Shape |
     |---|---|
     | Blank, or doesn't exist yet (created next to the source) | `build` — replicate into a blank tab |
     | Same sheet as the source | `in-place` — swap data, not structure |
     | Partly filled, named for the new ticker | `resume` — complete only what's missing |
4. **Companies.** `discover_companies(keywords=["TICKER"])` for the new company → `company_id`, `latest_calendar_quarter`, `latest_fiscal_quarter`. Identify the template's company from its header rows, tab name or Daloopa links (needed to spot leftover references later).
5. **Announce** in one line, e.g.:
   > *Workbook `TNL_HGV.xlsx` · source `TNL Model` → target `HGV` (blank) · data: link to `DATA` · mode: build · new company HGV (Hilton Grand Vacations)*

   Continue to Steps 1–3 (reading only), then wait for approval at Step 4 before writing anything.

## Step 1 — Study the Template

`python infra/workbook_tools.py read WORKBOOK "Source"` (the used range; use `--max-cells` or sub-ranges for very large sheets) and capture, exhaustively:
- **Structure:** section order, row labels, subtotal rows, the period header rows, the actual→forecast boundary, and how tabs reference each other (`refs` on the source shows exactly which data-tab cells it reads).
- **Formula logic:** which cells are formulas vs typed; how historicals are sourced (linked to the data tab by `INDEX/MATCH` or direct refs, or typed); how the statements link; the forecast formulas.
- **Formatting and conventions:** fonts, fills, number formats, colour semantics, column widths, freeze panes — per `../modeling-conventions.md` Section 2. If formatting can't be read, say so and use Section 5 defaults; never invent a style.

For `resume`, also `read` the partial target and **diff it against the template** row by row: what's done stays as it is — no restyling, no rebuilding.

## Step 2 — Map Template Lines to the New Company

Map on **concept, not wording** ("Net sales" = "Revenue"; `../modeling-conventions.md` Section 3):
1. **Find series — one call.** `discover_company_series(company_id, keywords=[every template row label that holds data, plus parenthetical and singular/plural variants], calendar_periods=[...])`.
2. **Fetch — one call.** `get_company_fundamentals(company_id, calendar_periods=[the template's historical periods, re-anchored to the new company's latest_calendar_quarter], series_ids=[...])`. Keep every datapoint's `id` for citations and links.
3. **Handle reporting differences explicitly.** Where the new company reports a segment/KPI the template lacks → **add a row**. Where the template has one the new company doesn't report → **blank or remove it** — never fabricate. Flag every add/remove.
4. **Preserve the driver logic** even when the names change (a units × price structure stays units × price, with the new company's metrics).

**Periods:** the template's columns are relabelled for the new company's fiscal calendar (map with the fiscal↔calendar offset from `discover_companies`; the API takes calendar quarters only — `../data-access.md` Section 1.5). **Units:** convert to the unit basis the template states in its header.

## Step 3 — Decide Link vs Write (Data Sourcing)

Match the template's choice, and honour where the user already staged data:
- **Link to the user's data tab** (preferred when one exists): write formulas that reference it — typically `INDEX/MATCH` on row label + period header, matching how the template already does it. In `in-place`, **re-point** the existing formulas to the new company's rows (same relative structure).
- **Stage data first, then link.** If the data tab holds the *old* company's data or none for the new one:
  - `in-place`: refresh the data tab itself with the new company's figures.
  - `build`: the template still needs its own data, so create a new data tab `DATA_{TICKER}` with the same layout as the existing one and link the target to it.
  Write each figure from `get_company_fundamentals`; if the existing data tab's cells carry Daloopa links, give the new cells links too (`"link": "https://daloopa.com/src/{id}"`). Never link to data that isn't there yet.
- **Write values directly** into the model only when there is no data tab to link to, or the template types its actuals.
- **Keep the template's typed-vs-formula pattern:** if it types grey historical cells and formulas everything else, do the same. Forecast columns stay formulas.

## Step 4 — Present the Plan and Wait

Before writing anything, show:
- The announce line (Step 0) — the user can correct any detected role here.
- **Line mapping table:** template label → new company series (with a sample value and citation) → treatment (link / write / formula / blank). Mark every **added** and **removed** row.
- **Data sourcing:** link vs write, and which data tab (existing, refreshed, or new `DATA_{TICKER}`).
- **Conventions to replicate** — observed vs defaulted.
- Limits honoured (e.g. "only grey cells") and incidental references to update.

Wait for approval. Apply any corrections, then build.

## Step 5 — Build into the Target

Assemble one change list in `reports/.tmp/{workbook_stem}_port_changes.json` (schema in the docstring of `infra/workbook_tools.py`), in this order:
1. **Target sheet** — `build` with a missing target: `{"add_sheet": "HGV", "after": "TNL Model"}`; then `{"sheet": "HGV", "layout_from": "TNL Model"}` for column widths, row heights and freeze panes.
2. **Data tab** — new `DATA_{TICKER}` or the refreshed one: labels, period headers, figures.
3. **Formatting** — `copy_format_from` the template's ranges onto the target's, block by block so added/removed rows line up (a row added for a new segment copies the format of its sibling row).
4. **Labels, values, formulas** — every formula re-pointed to the new company's data, never the template's.
5. **Incidental references** the user called out (ticker in a header cell, a "Thesis" tab cell).

Write into the **target only** (plus the data tab from Step 3). In `in-place` with a limit like "only grey cells", touch nothing else.

**Inserting rows in place:** the tool doesn't shift existing formulas when rows are inserted. In `in-place`, put an added row in an empty row inside its section if one exists; otherwise list it as a manual step ("insert a row below row 24 for *Rental revenue*, then …") rather than shifting the sheet.

Run `python infra/workbook_tools.py apply WORKBOOK reports/.tmp/{stem}_port_changes.json --label port` → `reports/{stem}_port_{YYYYMMDD}.xlsx`. The original is never touched; for follow-up passes on the copy, use `--in-place`.

## Step 6 — Verify

1. **No leftover template references:** `python infra/workbook_tools.py refs OUTPUT "Target"` — no reference to the template company's data rows or tab remains (unless the template linked there on purpose, e.g. a shared assumptions tab).
2. **Spot-check linked historicals:** for 3–5 key rows (revenue, operating income, a KPI), recompute what each linked cell resolves to from the data written in Step 5 and confirm it equals the new company's Daloopa figure.
3. **Recompute the checks yourself** (`model-checks.md`): the template's own check rows (balance check, tie-outs), statement footing, and segment sum vs total revenue. State the expected value of each — e.g. *"HGV!F95 (balance check) should read 0.0 in every column."*
4. **Recalculate when possible:** `python infra/workbook_tools.py recalc OUTPUT --cells "HGV!F95:Q95" ...`.
   - `recalculated: true` → compare with the expected values; a mismatch means a broken reference from the port — fix it before reporting.
   - `recalculated: false` → say the values recalculate when the file is opened in Excel, and that the user should confirm the expected values there.

## Output

Tell the user:
- Where the workbook was saved: `reports/{stem}_port_{YYYYMMDD}.xlsx` (the original is unchanged).
- The shape, source → target, and data sourcing used.
- **Every structural change:** rows added/removed for reporting differences, a new data tab, manual steps left.
- The check results: expected values, and recalculated values when available.
- Anything not done (unresolved series, unreported periods left blank) and why.
- Any `warning` from `tabs`/`apply` (charts, pivots, external links that may not have survived).

All Daloopa figures cited in the reply use the citation format: [$X.XX million](https://daloopa.com/src/{fundamental_id})

## Discipline

- Conform to the template's style — never restyle or re-lay-out cells you weren't asked to touch.
- Never clobber a formula you weren't asked to change.
- Never fabricate a segment, KPI or period the new company doesn't report — blank it and flag it.
- Never overwrite the user's original file.
