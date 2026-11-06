# Model Integrity Checks

The mechanical checks a three-statement model can run on itself, and how to read a failure. Used by `/fix-debug-audit` for balance-break localization and audits, and by `/port-replicate-model` to verify a port.

## Two Kinds of Row — Never Mix Them

A **check** asserts an identity that holds regardless of what the business does. It failing means the model is wrong, and you fix it.

A **warning sign** states a fact about the business — negative cash, negative equity, a covenant threshold crossed, a margin collapsing. You report it. You never "fix" one by editing an assumption, and you never fold it into the pass/fail block.

## How a Check Is Read

- One signed difference per check per period. The magnitude and sign are the diagnosis; a true/false collapses that away.
- Compare against a small tolerance, never exact zero — arithmetic over large balances leaves floating-point residue.
- Two tolerance regimes: the model's own arithmetic should tie to rounding noise; a comparison against reported figures needs about `n_components × half a display unit` of slack, because the source rounds each component before totalling.
- The per-period result is what turns "the model is broken" into "the model breaks in 2027Q2".

## The Battery — Run in This Order

**1. Statement footing** — first; a cross-statement failure is meaningless while a statement doesn't foot to itself.
- Each subtotal equals the sum of its components, on all three statements.
- Section totals sum to the statement total; `CFO + CFI + CFF + FX = net change in cash`.
- Segment revenue sums to consolidated revenue; geographic revenue does too.

**2. Computed vs reported** (historical columns only).
- Each computed subtotal against the figure Daloopa reports for the same period. A difference materially larger than the rounding bound means a component row is missing from the model.

**3. Rollforwards** — these localise a problem to one account, which the balance check cannot.
- Retained earnings: `prior + net income − dividends`. Two traps: use net income **attributable to the parent** (consolidated leaves a gap equal to minority interest), and don't subtract a dividend figure that is already negative — the difference is then exactly twice the dividend.
- Total equity: `prior + net income + OCI + SBC + option proceeds − buybacks − dividends`. Check components separately where the model carries them.
- PP&E: `prior + capex − depreciation ± disposals ± impairment`. Subtract **depreciation**, not combined D&A, or the model over-depreciates by exactly the amortisation.
- Debt: `prior + issuance − repayment`; current + long-term must sum to the schedule. The split can be wrong while the total is right.
- Share count: `prior + issuance + vesting − repurchases`. Basic ≤ diluted; equal in a loss period. A buyback that hits cash and equity but not the share count leaves every balance right and only EPS wrong.

**4. Cash**
- BS cash equals CF ending cash; CF opening cash equals last period's BS cash.
- In **historical** columns, check whether the two lines are the same concept before touching anything: BS "cash and cash equivalents" vs CF "cash, cash equivalents and restricted cash" differ by restricted cash. That's a reporting difference to bridge with a labelled row — not a wiring bug.

**5. Cash flow against the balance sheet**
- Each working-capital CF line equals the negative of the BS change for an asset, positive for a liability.
- In **forecast** columns this must tie exactly. In **historical** columns expect legitimate differences (acquisitions, FX, reclassifications) — carry them in a labelled reconciling line; never force a reported figure to tie.
- Each non-cash add-back (D&A, SBC, deferred tax, impairment, gain on disposal) appears everywhere it belongs with the same magnitude.

**6. Quarters against the annual column** — by row type:
- Flow rows: four quarters sum to the year.
- Balance rows: the year equals Q4, never a sum.
- Ratio, margin, per-share rows: recomputed from annual components, not aggregated.
- Do **not** check that quarterly EPS sums to annual EPS — it legitimately fails.
- A 1–2% gap in one year is usually a 53-week year; historical quarters that don't sum to a restated year are a vintage mismatch. Neither is a defect.

**7. Balance sheet balances** — `Total assets − (Total liabilities + Total equity)`, every period. Run it **last**: it has dozens of causes and localises nothing on its own.

**8. Formula shape** — catches what no value check can:
- No cell errors (`#REF!`, `#VALUE!`, `#DIV/0!`, `#NAME?`, `#N/A`).
- Every cell in a row shares one formula shape. A typed number inside an otherwise-formula row is the single highest-yield thing to look for, and it is invisible to every value check.
- Each subtotal's range spans all its components — a row inserted at the edge of a `SUM` range is silently excluded.
- No dangling links to other workbooks; no circular references.
- An error parked on the untaken branch of an `IF` shows nothing today and detonates on one input change.

**The plug test** — a balance sheet that balances under every scenario, including ones you deliberately break, is not balancing; something is absorbing the error. A line defined as "total minus everything else" is the plug.

## Reading a Difference — The Shape Names the Cause

| Signature across periods | Cause |
|---|---|
| Exactly twice some line item | That item's sign is wrong |
| Grows every period by the same recurring amount | Item on one statement, missing from another (cumulative rollforward error) |
| Identical in every period | One-time error — the opening balance, or the first forecast column's link back |
| Constant from the first forecast column onward | A stock re-based at the actual→forecast boundary with no matching flow — diff the first forecast column against the last actual line by line |
| Exactly one line item | That row is missing from a subtotal's range |
| Small/round (e.g. 0.5) or ×1000 | Rounding, or a unit mismatch (one cell in $K, the rest in $M) |
| Zero in history, non-zero from the first forecast column | Logic error; the data is fine |
| Non-zero in history | Data error; the formulas are innocent until history ties |
| Always zero, even when you break a link | A plug |
| Many checks failing together | A block copied one row/column off, or a shifted period header — check the axis first |

**The four usual causes of a balance break:** (1) a working-capital sign, (2) SBC missing from the equity rollforward, (3) a CF flow missing from the cash rollforward, (4) a stock re-based with no matching flow. Check these first.

## Reporting

State which checks ran, which passed, which failed and what was done about each, and which could not be built at all (a PP&E rollforward is uncheckable if the model never separated depreciation from amortisation). A check silently skipped reads exactly like a check that passed. Never report a model as "verified"; report what was checked.
