| name | description | argument-hint |
|------|-------------|---------------|
| convert-skills-to-prompts | Convert all Claude Code skills into MCP prompt functions | (none) |

Convert every skill in `.claude/skills/` into a Python MCP prompt function, producing a single output file `prompts.py` with one `@daloopa_mcp.prompt` function per skill.

**This is a conversion task, not a rewrite.** The analytical logic, calculations, data requirements, and output structure of each skill must be preserved exactly. What changes is the execution context: from Claude Code (file system, local scripts, MCP tools) to MCP prompt (MCP tools only, no file system, no local scripts).

---

## Step 0: Read All Source Files

Read these files first — you need them all loaded before you start converting:

1. **Shared references:**
   - `.claude/skills/data-access.md` — data access patterns, tool signatures, citation rules
   - `.claude/skills/design-system.md` — formatting, analytical voice, HTML template, color palette

2. **Every skill file:**
   - `.claude/skills/*/SKILL.md` — read all of them

3. **Note the full skill list from the directory listing.** Some skills may reference other skills (e.g., `/initiate` calls `/research-note` + `/build-model`, `/update` references prior output). Capture these dependencies.

---

## Step 1: Understand the Two Shared References

Before converting any skill, analyze `data-access.md` and `design-system.md` to build a dependency map. Each skill uses different parts of these files.

### data-access.md — Section Inventory

Identify these sections and what each provides:

| Section | Content | MCP Prompt Relevance |
|---------|---------|---------------------|
| Section 1: Daloopa MCP Tools | Tool signatures: `discover_companies`, `discover_company_series`, `get_company_fundamentals`, `search_documents` | **ALWAYS INLINE** — every skill needs these |
| Section 1: API Script Fallback | `python recipes/company_fundamentals.py` etc. | **ALWAYS DROP** — no file system in MCP prompt context |
| Section 2: External Market Data | Stock quotes, trading multiples, historical prices, peer multiples, risk-free rate | **CONDITIONAL** — only inline for skills that use market data |
| Section 2: Market Data Resolution Order | MCP → infra scripts → web search → defaults | **ALWAYS INLINE** — preserve the full 4-step resolution order (MCP tools → infra scripts → web search → defaults) |
| Section 3: Consensus Estimates | Consensus revenue/EPS, forward estimates, revisions, price targets | **CONDITIONAL** — only inline if the skill doesn't already handle consensus in its own steps |
| Section 4: Citation Requirements | Daloopa citation format, fundamental_id linking, document citations | **ALWAYS INLINE** — mandatory for all skills |
| Section 5: Infrastructure Tools | market_data.py, chart_generator.py, projection_engine.py, excel_builder.py, docx_renderer.py, etc. | **ALWAYS DROP** — not available in MCP prompt context |

### design-system.md — Section Inventory

| Section | Content | MCP Prompt Relevance |
|---------|---------|---------------------|
| Number Formatting | `$X.Xbn`, `42.3%`, `8.5x`, etc. | **ALWAYS INLINE** — all skills output financial data |
| Analytical Density | Three-layer convention (data + context + implication) | **ALWAYS INLINE** — defines output quality |
| Table Conventions | Columns = periods, rows = metrics, grouping rules | **ALWAYS INLINE** — all skills produce tables |
| Commentary Blocks | Post-table interpretation requirement | **ALWAYS INLINE** — all analytical skills |
| Analyst's Perspective | Critical voice, red flags, conviction, signal vs noise | **INLINE FOR ANALYTICAL SKILLS** — not needed for /setup or pure data-export skills |
| Color Palette | Hex codes for charts and HTML | **INLINE FOR HTML SKILLS** — needed for the 11 analytical HTML report skills |
| Chart Styling | Chart types, grid lines, labels | **DROP** — chart_generator.py not available in MCP context |
| Output Formats | .html, .docx, .xlsx, .pdf mapping | **DROP** — MCP prompts don't write files |
| Typography | Font sizes, header styling | **INLINE FOR HTML SKILLS** — needed for styled HTML output |
| HTML Report Template | Full CSS template (~100 lines) | **INLINE FOR HTML SKILLS** — the 11 analytical skills produce HTML, so they need the full template |

---

## Step 2: Per-Skill Conversion Process

For EACH skill, follow this process:

### 2a. Read the Skill and Identify Its Nature

Read the skill's `SKILL.md`. Classify it:

- **Analytical HTML report** (earnings, tearsheet, industry, bull-bear, guidance-tracker, inflection, capital-allocation, dcf, comps, ib-deck, supply-chain): Produces analysis with tables, commentary, scenarios. Output is a complete self-contained HTML document.
- **File-based deliverable** (research-note, build-model, comp-sheet): Produces .docx or .xlsx using infra scripts. These need the MOST adaptation since the rendering pipeline doesn't exist in MCP context.
- **Composite skill** (initiate, update): Orchestrates other skills. Needs to reference other prompts or inline the sub-workflows.
- **Utility** (setup): May not make sense as an MCP prompt at all.

### 2b. Analyze Dependencies on Shared References

For this specific skill, determine:

1. **Does it use market data?** (Look for: stock price, multiples, EV/EBITDA, P/E, beta, WACC, peer multiples, historical prices)
   - YES → inline simplified market data section from data-access.md Section 2
   - NO → omit

2. **Does it use consensus estimates?** (Look for: consensus, Street expectations, beat/miss, forward estimates, estimate revisions)
   - YES, and the skill already has its own consensus step → DON'T double-inline from data-access.md Section 3
   - YES, but the skill just says "see data-access.md" → inline Section 3
   - NO → omit

3. **Does it use `search_documents`?** (Look for: SEC filings, qualitative research, risk factors, management commentary)
   - YES → ensure document citation format is included
   - NO → can omit document citation format (keep fundamental citation)

4. **Does it reference infra scripts?** (Look for: chart_generator.py, projection_engine.py, excel_builder.py, docx_renderer.py, comp_builder.py, deck_renderer.py, market_data.py)
   - YES → these must be adapted. See Step 2d.

5. **Does it produce HTML output?** (Look for: "Save to reports/*.html", "HTML report template", "design-system.md CSS")
   - YES → decide whether to include the HTML/CSS template. See output format decision below.
   - NO → omit HTML template

6. **Does it reference other skills?** (Look for: `/research-note`, `/build-model`, or similar cross-references)
   - YES → inline the sub-workflow or reference the other prompt function

### 2c. Decide Output Format

The original skills produce files (.html, .docx, .xlsx, .pdf). MCP prompts return text to a client. For each skill type:

- **HTML report skills** (including ib-deck, supply-chain): The prompt should instruct the LLM to produce the analysis as a **complete, self-contained HTML document** using the design-system.md CSS template. Inline the full HTML template in the prompt so the LLM produces styled HTML matching the original skill's output format.
- **Excel skills** (.xlsx): Instruct the LLM to produce a React artifact with SheetJS that builds and downloads the file in-browser (see "Excel Output via Artifacts" in Step 2d).
- **Word skills** (.docx): Produce the full analytical content as structured text/markdown — binary rendering still requires the infra scripts or a capable client.

### 2d. Adapt Infrastructure Dependencies

When a skill references infra scripts, adapt as follows:

| Original Reference | MCP Prompt Adaptation |
|---|---|
| `python infra/chart_generator.py ...` | Drop chart generation. Keep the data and analysis that would feed the chart. Describe what chart would be produced (type, axes, data series) so the client can render if capable. |
| `python infra/projection_engine.py ...` | Inline the projection logic as instructions. The skill should describe HOW to project (growth rates, assumptions, methodology) rather than calling a script. The LLM does the math. |
| `python infra/market_data.py ...` | Replace with the full market data resolution order: MCP tools → `python infra/market_data.py` fallback → web search → defaults |
| `python infra/excel_builder.py ...` | Instruct the LLM to build a React artifact using SheetJS that constructs the .xlsx in-browser with a download button. See "Excel Output via Artifacts" below. |
| `python infra/docx_renderer.py ...` | Produce the document content as structured text/markdown. Note that .docx rendering requires the project repo or a client that supports document generation. |
| `python infra/comp_builder.py ...` | Same as excel_builder — React artifact with SheetJS. See "Excel Output via Artifacts" below. |
| `python infra/deck_renderer.py ...` | Produce the deck content as structured sections/slides. |
| `Save to reports/{TICKER}_xxx.html` | Replace with "Present as a complete, self-contained HTML document using the design-system template" |
| `Save context JSON to reports/.tmp/` | Drop — no file system |

### Excel Output via Artifacts

For skills that originally produce .xlsx files (build-model, comp-sheet, and the Excel portion of initiate/update), the prompt should instruct the LLM to create a **React artifact** that:

1. Builds the workbook in-browser using SheetJS (`import * as XLSX from 'sheetjs'`)
2. Constructs multiple tabs/sheets matching the original skill's sheet structure
3. Applies formatting: column widths, number formats, header styling, frozen panes where appropriate
4. Provides a prominent download button that triggers the .xlsx download
5. Also renders a preview of the key sheets as HTML tables so the user can see the data before downloading

The prompt should include the sheet structure (tab names, what goes in each tab, column layout) from the original skill so the LLM knows exactly what to build.

Example pattern to include in the prompt:

```
When presenting the Excel model, create a React artifact that:
- Uses SheetJS (`import * as XLSX from 'sheetjs'`) to build the workbook
- Creates these sheets: [list from original skill]
- Each sheet should have: headers in row 1, data starting row 2, number-formatted columns
- Include a "Download .xlsx" button that generates and downloads the file
- Show an interactive preview of the key sheets as HTML tables above the download button
- All Daloopa-sourced values should include hyperlink citations in the spreadsheet cells where SheetJS supports it
```

This gives users the same .xlsx deliverable as the Claude Code skill, just built client-side instead of via infra scripts.

### 2e. Handle Composite Skills

For skills that orchestrate others (like `/initiate` = `/research-note` + `/build-model`):

- If both sub-skills exist as prompts, the composite prompt should describe the full combined workflow inline (don't reference other prompt functions — the LLM can't call them)
- Merge the sub-workflows into a single coherent sequence, deduplicating shared data-pull steps

For `/update` which references prior output:
- The prompt should accept prior analysis as input context (add a parameter) OR instruct the LLM to pull fresh data and produce a complete new analysis
- Don't assume file system access to read prior reports

---

## Step 3: Build Each Prompt Function

For each skill, produce a Python function following this template:

```python
@daloopa_mcp.prompt
def skill_name(ticker: str) -> str:
    """Display Name"""
    return f"""[PROMPT CONTENT]
"""
```

The docstring is used as the **display name** in MCP clients (e.g., Claude). Without it, `bull_bear` renders as "Bull bear" — the docstring overrides this to show "Bull / Bear" instead. Use proper title case and formatting:

| Function | Docstring |
|----------|-----------|
| `earnings` | `"""Earnings"""` |
| `tearsheet` | `"""Tearsheet"""` |
| `industry` | `"""Industry"""` |
| `bull_bear` | `"""Bull / Bear"""` |
| `guidance_tracker` | `"""Guidance Tracker"""` |
| `inflection` | `"""Inflection"""` |
| `capital_allocation` | `"""Capital Allocation"""` |
| `dcf` | `"""DCF"""` |
| `comps` | `"""Comps"""` |
| `supply_chain` | `"""Supply Chain"""` |
| `research_note` | `"""Research Note"""` |
| `build_model` | `"""Build Model"""` |
| `comp_sheet` | `"""Comp Sheet"""` |
| `ib_deck` | `"""IB Deck"""` |
| `initiate` | `"""Initiate"""` |

### Prompt Structure (for each skill)

Every prompt should have these sections in order:

```
1. TASK STATEMENT
   - What to build, for which company ({ticker})
   - One sentence, mirrors the skill's description

2. DATA ACCESS (inlined from data-access.md, filtered per Step 2b)
   - Daloopa MCP tool signatures (always)
   - Market data instructions (if needed)
   - Citation requirements (always)

3. FORMATTING CONVENTIONS (inlined from design-system.md, filtered per Step 2b)
   - Number formatting (always)
   - Analytical density (always for analytical skills)
   - Table conventions (always)
   - Commentary blocks (always for analytical skills)
   - Analyst's perspective (for analytical skills)

4. ANALYSIS STEPS
   - The skill's core steps, preserved exactly
   - Infra script references adapted per Step 2d
   - File save instructions replaced with "present as response"

5. OUTPUT SPECIFICATION
   - What the response should contain (mirrors the skill's output section)
   - Adapted for text response vs. file output
   - "Data sourced from Daloopa" footer
```

### Inlining Rules

- **DO** inline content verbatim from shared references when it's needed. Don't paraphrase the citation format or number formatting rules — copy them exactly.
- **DON'T** inline content the skill doesn't use. Every inlined line is tokens spent on every invocation.
- **DON'T** include URLs to the shared reference files. The LLM cannot fetch them.
- **DO** preserve every analytical step, every data requirement, every calculation from the original skill. The prompt must produce identical analytical output to the Claude Code skill.
- **DO** keep the skill's specific instructions about interpretation, conviction, and honesty (e.g., bull-bear's "don't default to 25/50/25" and "be honest about which scenario is most likely").

---

## Step 4: Assemble Output File

Create `prompts.py` with:

```python
# Auto-generated MCP prompt functions from .claude/skills/
# Source: https://github.com/daloopa/investing
#
# Each function returns a prompt string that instructs an LLM to perform
# the same analysis as the corresponding Claude Code skill, using only
# Daloopa MCP tools (no file system, no infra scripts).
#
# Skills converted: [list them]
# Shared references inlined: data-access.md, design-system.md
# Date: [today]

from app.daloopa_mcp import daloopa_mcp

# --- Prompt functions below ---
```

Then one function per skill, in this order:
1. Analytical HTML skills: earnings, tearsheet, industry, bull_bear, guidance_tracker, inflection, capital_allocation, dcf, comps, ib_deck, supply_chain
2. Deliverable skills: research_note, build_model, comp_sheet
3. Composite skills: initiate

**Skip `/setup`** — it's an interactive setup wizard for Claude Code auth, not an analytical skill. Note in a comment why it was skipped.

**Skip `/update`** — it requires prior context JSON from the file system and re-renders .docx/.xlsx using infra scripts. Not portable to MCP prompt context. Note in a comment why it was skipped.

---

## Step 5: Validate

After generating `prompts.py`, review each function:

1. **Completeness**: Does the prompt contain every analytical step from the original skill? Diff mentally against the source SKILL.md.
2. **No dead references**: Does the prompt reference any file paths, infra scripts, or local commands that don't exist in MCP context?
3. **No missing citations**: Does the prompt include the citation requirements section?
4. **No missing formatting**: Does the prompt include number formatting rules?
5. **No redundant inlining**: Is there content inlined from shared references that this specific skill doesn't use?
6. **Argument handling**: Does the function signature match the skill's expected arguments? Most take `ticker: str`, but `/industry` takes multiple tickers. Check each skill's argument-hint.

If any check fails, fix the function before moving on.

---

## Notes for the Human

After running this skill, you'll have `prompts.py` with all prompt functions. A few things to be aware of:

- **Token cost**: Each prompt inlines its dependencies, so longer skills (dcf, comps) will have larger prompt strings. This is intentional — it avoids runtime fetches. If token cost is a concern, you can extract the shared sections (data access, formatting) into a separate base prompt and compose them, but that adds complexity.
- **Output format**: The 11 HTML skills (earnings, tearsheet, industry, bull-bear, guidance-tracker, inflection, capital-allocation, dcf, comps, ib-deck, supply-chain) produce complete styled HTML documents matching the original skill output. The HTML template with full CSS is inlined in each prompt. Excel skills (.xlsx) produce React artifacts with SheetJS that build and download the file in-browser.
- **File deliverables**: The research-note skill produces structured markdown (original .docx requires infra scripts). Excel (.xlsx) deliverables are fully handled via SheetJS artifacts.
- **Composite skills**: `/initiate` and `/update` inline their sub-workflows. If you later change `/research-note` or `/build-model`, you'll need to regenerate the composite prompts.
