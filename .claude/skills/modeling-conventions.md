# Modeling Conventions Reference

Shared by the workbook-edit skills (`/port-replicate-model`, `/fix-debug-audit`), which work on a model the user already built. Two halves: how to read **the user's** conventions off their workbook, and the three-statement logic a model **should** follow. For the integrity checks themselves, see `fix-debug-audit/references/model-checks.md`.

---

## Section 1: The Cardinal Rule — Conform to the User's Model

Reformatting or restructuring someone's model is the fastest way to get the output thrown away. A model that comes back in the user's own conventions gets used; one in ours gets rebuilt by hand.

**Precedence, highest first:** what the user said in this conversation → what their workbook already does → the defaults in this file. Their convention conflicts with ours: theirs wins, every time. Their convention conflicts with something they just asked for: their words win — say plainly that this differs from the rest of the sheet.

## Section 2: Reading the User's Conventions

Read the header block, the row labels, and a **vertical slice across the period columns** for a few representative rows: one historical column, the actual→forecast boundary column, one forecast column. A single column cannot show a convention; the difference between columns is where it lives.

| Signal | What to record |
|---|---|
| **Period structure** | Periods across columns or down rows; quarterly/annual/mixed; where actuals end; where annual totals sit (beside each year's quarters or stacked to one side); label style (`1Q24`, `Q1 FY24`, `Mar-24`); fiscal vs calendar labels; spacer columns |
| **Units** | One basis for the sheet or per-row units. Read it off the header text ("$mm", "in thousands"), never infer it from magnitudes |
| **Number presentation** | Negatives in brackets or with a minus; decimals; percent as `0.42` or `42%` |
| **Sign convention** | Costs stored positive and subtracted, or negative and added — check a subtotal formula on **both** the income statement and the cash flow; a model can differ by statement |
| **Colour semantics** | Infer the meaning, don't assume ours. Typed cells blue and formulas black = standard. Everything black = they don't colour-code, and imposing it is a change they didn't ask for. Note what fills are used and on what kind of cell |
| **Derived rows** | Growth rows, margin rows, per-share, working-capital days — which they keep and where (under the line, or grouped in a block). Where forecast assumptions live |
| **Structure** | Section order, separators, indentation depth, bold subtotals, check rows and where they live |
| **Typed vs computed, row by row** | A row whose history is typed numbers gets typed numbers in new reported periods. A formula row keeps its formula. Forecast columns stay projection formulas |

**Resolving what you found:**
- Two columns disagree on style for the same kind of cell → drift, not a convention. Follow the majority; don't propagate the outlier.
- A signal is absent (no fills anywhere, no growth rows) → unknown, not prohibited. Apply the default for that one thing and say so.
- You could not read the formatting → say so and fall back to defaults. Never invent a style and present it as theirs.
- Never report a convention as observed when you inferred it from one cell.

**Never** restyle or re-lay-out cells you were not asked to touch, even to make them consistent with your work. Never "upgrade" their conventions to ours.

## Section 3: Matching a Daloopa Series to a Row Label

Match on **concept, not wording** — "Net sales" = "Revenue", "Income from operations" = "Operating income". `discover_company_series` keyword search is substring-based: put every label in **one** `keywords` list, and add parenthetical and singular/plural variants (`Income (loss) from operations`, `Segment`/`Segments`). Treat gross profit and FCF as derived when no reported series exists.

When a row carries a Daloopa link (`https://daloopa.com/src/{id}`), confirm the match by ID: pull the candidate series with `get_company_fundamentals` and find the datapoint whose `id` equals the link's ID. That confirms the series without guessing. A row with no confirmed series is left unchecked or blank — never guessed.

**Periods:** the API takes calendar quarters only (see `data-access.md` Section 1.5). `get_company_fundamentals` returns both `calendar_period` and `fiscal_period` — match each sheet column to the datapoint whose period label matches the column header's basis (fiscal headers → `fiscal_period`). **Units:** convert each figure to the unit the sheet's header states before comparing or writing.

## Section 4: Three-Statement Linkage — What the Model Should Do

Statements link through **formulas referencing the source cell**, never retyped values. Net income on the IS is referenced by the CF and the equity rollforward, not retyped.

**IS → BS**
- Net income → retained earnings (equity rollforward)
- Revenue → AR via DSO: `AR = DSO/91.25 × Revenue` (quarterly; `91.25 = 365/4`)
- COGS → inventory via DIO and → AP via DPO (same form)
- D&A reduces net PP&E
- Historical days figures use average balances; forecast inverts on the **ending** balance (inverting an average is circular). Whatever divisor a row uses, history and forecast must use the same one

**BS → CF (working capital)** — each CF line is the **negative** of the BS change for an asset, **positive** for a liability:
- `ΔAR → −(AR_t − AR_{t−1})`, `ΔInv → −(Inv_t − Inv_{t−1})`
- `ΔAP → +(AP_t − AP_{t−1})`, `ΔAccrued → +(Accrued_t − Accrued_{t−1})`

Sign errors here are the most common silent CF bug.

**CF → BS rollforwards** — these are what make the model balance:
- Cash: `Cash_t = Cash_{t−1} + OCF_t + NetInvesting_t + NetFinancing_t` (+FX)
- Equity: `Equity_t = Equity_{t−1} + NetIncome_t + SBC_t − Dividends_t − Buybacks_t + OptionProceeds_t`. SBC must be added back here — the CF adds it to cash, so equity must rise by the same amount (omit it and the balance breaks by the SBC)
- PP&E: `PPE_t = PPE_{t−1} + CapEx_t − Depreciation_t` (CapEx as a positive amount; depreciation, not combined D&A)
- Debt: `prior + issuance − repayment`; current + long-term portions sum to the schedule

**Two IS lines are outputs, not forecasts:** D&A falls out of the PP&E build; interest falls out of the debt schedule on the **beginning** balance (closing or average goes circular).

**Subtotals are computed in every column, history included** — a fetched subtotal makes the tie-out to reported a tautology.

## Section 5: Defaults (Only When the Workbook Shows Nothing)

| Item | Default |
|---|---|
| Typed inputs | Blue font (`FF0000FF`) |
| Formulas | Black font (`FF000000`) |
| Links to other tabs | Green font (`FF008000`) |
| A plug deliberately kept | Yellow fill (`FFFFFF00`), flagged in the reply |
| Negatives | Brackets |
| Units | One basis per statement, stated in the header |

Mark every default you applied as a default, not as something you observed.

## Section 6: Trust Rules

- **Never plug** a balance break or a tie-out gap — find the broken link, or report the gap.
- **Never fabricate** an unreported or restated figure. A labelled blank beats a wrong number.
- **Never overwrite the user's original file.** Every write goes to a copy in `reports/`.
