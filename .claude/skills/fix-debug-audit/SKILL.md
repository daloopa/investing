---
name: fix-debug-audit
description: Diagnose and fix an existing model — balance breaks, audits, restatements, targeted edits
argument-hint: "[RANGE] [instructions]"
---

Diagnose an **existing, user-built** Excel model as requested by the user: $ARGUMENTS

**Before starting, read `../data-access.md` for data access methods, `../modeling-conventions.md` for how to read the user's conventions and the linkage a model should follow, and `references/model-checks.md` (in this skill's directory) for the integrity checks and how to read a failure.**

The deliverable is a *finding* (and, when asked, a fix) — not a new model. You are handed an unknown workbook and must localize the problem, not re-derive the model.

## Inputs

Both inputs are optional. Everything else is detected (Step 0).

| Input | Form | Default |
|---|---|---|
| `RANGE` | `Sheet!A1:Z99`, `'My Sheet'!B10:M80`, or a sheet name | The main model sheet's used range — or, for a balance break, the rows around the off check |
| `instructions` | Free text after the range | Audit, report only |

Examples: `/fix-debug-audit` · `/fix-debug-audit Model!B10:M80 fix it` · `/fix-debug-audit why doesn't the balance sheet balance?` · `/fix-debug-audit IS!C5:N60 convert INR crore to million`

A workbook path (`.xlsx`/`.xlsm`) in the instructions overrides workbook detection. A ticker in the instructions overrides ticker detection.

## Step 0 — Resolve and Announce

1. **Workbook.** A path in `$ARGUMENTS`; otherwise the most recently modified `.xlsx`/`.xlsm` in `reports/`, then the working directory — skipping files this toolkit generated (names ending `_audit_YYYYMMDD`, `_port_YYYYMMDD`, `_model`, `_comp_sheet`). If none is found, ask for the path.
2. **Sheets.** `python infra/workbook_tools.py tabs WORKBOOK`. The main model sheet is the one named in the range, else the sheet with the most formula cells. If `tabs` returns a `warning` (charts, pivots, external links), carry it into the reply.
3. **Task** — inferred from the instructions; exactly one of:

   | Task | Triggered by | Section |
   |---|---|---|
   | `balance-break` | "doesn't balance", "doesn't tie", "check is off", "balance check" | Task A |
   | `restatement` | "restated", "resegmented", "recast", "new segment structure" | Task C |
   | `edit` | a concrete transformation: convert units, re-base, wrap in IFERROR, flip signs, rename labels | Task D |
   | `audit` | everything else ("audit", "review", "check", "find errors", nothing at all) | Task B |

   A balance break found during an audit is localized with Task A as part of the audit.
4. **Fix or report.** Fix only when the instructions ask for it ("fix", "correct", "repair", or any `edit` task). "Don't change anything" / "just review" means report only — write nothing. Default: report only. Fixes always go to a copy, never the original.
5. **Ticker** (needed for the source check and restatements). In order: a ticker in the instructions → Daloopa links in the sheet (`daloopa_id` from `read`, resolved in Task B) → the file or tab name → a company name in the sheet's header rows. Confirm with `discover_companies`. If none resolves and the task needs one, ask.
6. **Announce** in one line before any analysis, e.g.:
   > *Workbook `HGV_model.xlsx` · sheet `Model` · range `B10:M80` · task: audit · mode: fix (writes to a copy) · ticker HGV*

   **Report-only:** continue immediately. **Fix mode:** wait for the user to confirm the line before writing anything.

## Step 1 — Read

- `python infra/workbook_tools.py read WORKBOOK "Sheet!RANGE"` on the audited range, **plus** the same rows' neighbouring columns and the header rows that name each column's period. It returns, per cell: `kind` (formula / input / text), formula and `cached` value, number format, font, fill, link, and `daloopa_id` when the cell links to `daloopa.com/src/{id}`.
- `python infra/workbook_tools.py refs WORKBOOK "Sheet!RANGE"`, then `read` only what those formulas reference — never the whole workbook.
- `cached` is the last value Excel calculated. It is `null` for a file last saved by a script; note that instead of treating it as zero.
- From the header rows, record each column's period, the actual→forecast boundary, and the unit basis (see `../modeling-conventions.md` Section 2).

## Task A — Balance-Break Localization

When the balance check (or any tie) is off, localize it rather than re-deriving the model:
- **Where it starts.** The first column where the break appears points at the period that introduced it.
- **Sign and size** — read against the signature table in `references/model-checks.md`:
  - Exactly a line-item amount → a line missing from a subtotal, or double-counted.
  - Small/round amount (e.g. 0.5) or ×1000 → rounding or a unit mismatch.
  - Growing each period → a rollforward is wrong (cumulative), not a one-period hardcode.
  - Constant from the first forecast column onward → a stock re-based with no matching flow; diff the first forecast column against the last actual.
- **Walk the rollforwards backwards** — the four usual causes first: (1) a working-capital sign, (2) SBC missing from the equity rollforward, (3) a CF flow missing from the cash rollforward, (4) a stock re-based with no matching flow. Read `references/model-checks.md` before a systematic pass.
- **Trace dependents** of the off cell (`refs`, then `read`) to the offending input. **Never plug the difference** — report the broken link and its fix.

## Task B — Audit

Run the checks below on every cell of the range **before** writing anything. In fix mode, fix what they find in that range only, in this order. A cell that passes every check stays as it is.

1. **Sort the cells:** formula, formula pasted as a value, typed input, typed total.
2. **Pasted formulas get the neighbours' formula back.** When the cells on both sides in the same row hold the same formula (shifted by column), a typed number between them is that formula pasted as a value — a long decimal tail, or a value equal to what the formula gives in this column, confirms it. Restore exactly that formula, in a reported column as much as a forecast one, even when the older columns hold zeros. That decision is final: these cells never go to the source check and are never set to zero.
3. **Typed inputs in reported periods go to the source check — always, and before any write.** Reading the sheet cannot tell an altered figure from a correct one; only Daloopa can. An audit that skipped this is unfinished. See *Source check* below. Only inputs that disagree with Daloopa change.
4. **Typed totals get the formula their row uses.**
5. **Existing formulas change only when the fix is certain:** an error value, a broken or blank reference, or a total that leaves out a line of its own section. A formula its author may have meant — an extra term, a link to another row, a forecast-style formula in a reported column — is the author's: report it and leave it.
6. **Formatting** follows each cell's kind *after* steps 2–5 (a restored formula takes the formula cells' look). Compare each cell's font name, size, colour, bold, fill and number format with cells of the **same kind** beside it in its row. Fix only the attribute that differs, on that cell only, with a `format` change. Never re-apply what already matches, and never use `copy_format_from` for an audit fix — it brings every attribute of the source, including link styling or a column highlight the cell never had.
7. **Report** any total that still differs from the total Daloopa reports, with both figures — the gap is a finding, never a reason to change an input or a restored formula.

**Also look for:**
- **Formula integrity:** `#REF!`/`#VALUE!`/`#DIV/0!`/`#NAME?`, broken cross-sheet references, links to other workbooks.
- **Hardcodes kept deliberately** in a calculated row: flag as a plug; if the user wants it kept, mark it in the sheet's plug colour (default yellow fill).
- **Sign inconsistencies:** a cost positive in one period and negative in another; a CF working-capital sign that contradicts the BS change.
- **Drift between cells that should be identical** (e.g. a summary-tab figure vs its source row) — flag the mismatch and both values.
- **Unit/period inconsistencies:** a column in the wrong unit; a mislabeled fiscal period.

### Source check (Daloopa MCP)

Check every remaining typed number in a reported (actual) column of the range against Daloopa. Estimate and forecast columns, and formula cells, are not checked.

1. **Company and periods.** `discover_companies(keywords=["TICKER"])` → `company_id`, `latest_calendar_quarter`, `latest_fiscal_quarter`. Map each audited column header to a calendar quarter using the fiscal↔calendar offset between those two fields (`../data-access.md` Section 1.5 — the API takes calendar quarters only).
2. **Find the series — one call.** `discover_company_series(company_id, keywords=[every audited row label, plus parenthetical and singular/plural variants], calendar_periods=[...])`. Take a series only where it matches a label unambiguously (`../modeling-conventions.md` Section 3).
3. **Fetch — one call.** `get_company_fundamentals(company_id, calendar_periods=[audited periods], series_ids=[every candidate series])`.
4. **Confirm linked rows by ID.** For a cell with a `daloopa_id`, the series is the one whose returned datapoint `id` equals it. If no fetched datapoint matches, the row is "not checked — link not resolved", never guessed. Unlinked rows use the label match from step 2; a row with no match is "not checked — no series".
5. **Compare** each cell with its datapoint after converting to the sheet's unit and sign convention (a cost shown negative may be stored positive). A difference beyond the rounding of the cell's displayed precision is a finding: name the cell, the sheet's figure, and Daloopa's figure with its citation link.
6. **Fix** (fix mode only) by writing Daloopa's figure into the wrong cell as a plain `value` change — keep the format, and **add no link** unless the cell already had one (an existing link is kept automatically). Never fix by copying a neighbour, back-solving from a total, changing the total, or changing a formula to make a total tie.

## Task C — Restatement Reconciliation

When the company restated (resegmentation, asset sale, new segment structure), prior periods must be recast:
- Identify what changed with `search_documents(keywords=["restated", "recast", "segment"], company_ids=[company_id], calendar_periods=[recent 2-4 quarters])`, and pull the restated series with `discover_company_series` + `get_company_fundamentals`.
- **Recast the affected historical periods** to the new structure. Where the company only restated forward, hold the old basis for older periods and label the break.
- **Reconcile** sum-of-quarters to the fiscal-year total, and the new segment sum to total revenue; flag any residual rather than forcing it.
- Where the company didn't disclose a restated figure, leave it blank and say so — never fabricate the recast number.

## Task D — Targeted In-Place Edits

Apply precisely to the requested range only — these are the requests most likely to damage neighbouring work if the range creeps.
- **Unit conversion:** INR crore → INR million = ×10; lakh → million = ÷10; $K → $M = ÷1000. Rescale typed values (or wrap formulas with the factor) **and update the unit label in the header** — never leave mixed units in one statement.
- **Re-base a derived row** ("base every y/y row on column J"): rewrite only the base reference across the row; keep the rest of the formula and the number format.
- **Wrap in IFERROR:** `=IFERROR(<existing formula>, "")`, or `0` where the row feeds a sum.
- **Sign fixes** ("make these costs negative"): apply the sheet's own convention consistently, then check the subtotal formulas still add up after the flip.
- **Label find-replace:** a straight text edit; don't touch labels outside the range.

## Writing Fixes (Fix Mode Only)

1. Write the change list to `reports/.tmp/{workbook_stem}_audit_changes.json` — a JSON array, one entry per change (`{"cell": "Model!C14", "value": 1234.5}`, `{"cell": "Model!F30", "formula": "=F28-F29"}`, `{"cell": "Model!F30", "format": {"font_color": "FF000000"}}`). The full schema is in the docstring of `infra/workbook_tools.py`.
2. `python infra/workbook_tools.py apply WORKBOOK reports/.tmp/{stem}_audit_changes.json --label audit` — saves `reports/{stem}_audit_{YYYYMMDD}.xlsx`. The original is never touched. For follow-up passes on that copy, use `--in-place`.
3. If `apply` returns a `warning`, include it in the reply.

## Verify

Always, in fix mode or not:
1. **Recompute the affected checks yourself.** For each check the findings touch (balance check, the tie-out, the rollforward), recompute its value per period from the cells' values with the fixes applied, and state the expected result — e.g. *"After these changes, Model!F95 (balance check) should read 0.0 in every column (was 12.4 from 2025Q1)."* In report-only mode, state what the check would read if the suggested fixes were made.
2. **If fixes were written,** run `python infra/workbook_tools.py recalc reports/{stem}_audit_{YYYYMMDD}.xlsx --cells "Model!F95:M95"` for those check cells.
   - `recalculated: true` → compare with your expected values. A mismatch means a fix was wrong or a link was missed — investigate before reporting.
   - `recalculated: false` (LibreOffice not installed) → say the values recalculate when the file is opened in Excel, and that the user should confirm the expected values there.

## Output

Reply in the terminal with:
1. The **announce line** from Step 0.
2. **Findings**, grouped by kind (formula integrity, pasted formulas, values vs Daloopa, formatting, signs, drift, units) — each with location (cell/range), what's wrong, and the fix. Group, don't list cell-by-cell when a whole row shares the issue. Daloopa figures carry citations: [$X.XX million](https://daloopa.com/src/{fundamental_id}).
3. **Changes made** (fix mode): what changed, and the output path. Report-only: the suggested changes.
4. **Checks:** which ran, passed, failed; the expected value of each affected check (and the recalculated value when available). A check that couldn't be built is listed as such.
5. **Left alone:** anything found but not changed — outside the range, a formula the author may have meant, a row with no resolved series — with why.

## Discipline

- Localize, don't rebuild — find the specific broken cell or link.
- Honor read-only requests: report-only writes nothing at all.
- Never plug a break or fabricate a restated figure; a labelled gap beats a wrong number.
- Write inside the audited range only.
- Never overwrite the user's original file.
