#!/bin/bash
# Sync shared skill files from the project repo to the plugin repo.
# Phase 1: Copy 10 building block skills + design-system.md (identical between repos)
# Phase 2: Transform 5 deliverable skills via claude -p (adapt infra → plugin-compatible)
# Run from the project root: bash scripts/sync_plugin.sh

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="$PROJECT_DIR/../daloopa-plugin"
TRANSFORM_PROMPT="$PROJECT_DIR/scripts/transform_skill_prompt.md"

if [ ! -d "$PLUGIN_DIR" ]; then
    echo "Error: Plugin repo not found at $PLUGIN_DIR"
    echo "Clone the plugin repo first, then re-run this script."
    exit 1
fi

if [ ! -f "$TRANSFORM_PROMPT" ]; then
    echo "Error: Transformation prompt not found at $TRANSFORM_PROMPT"
    exit 1
fi

# Check claude CLI is available
if ! command -v claude &> /dev/null; then
    echo "Error: 'claude' CLI not found. Install Claude Code first."
    exit 1
fi

TRANSFORM_RULES=$(cat "$TRANSFORM_PROMPT")
PHASE2_FAILURES=0
PHASE2_WARNINGS=0

# ─────────────────────────────────────────────────
# Phase 1: Copy building block skills (unchanged)
# ─────────────────────────────────────────────────
echo "Phase 1: Copying shared building block skills..."
echo ""

SHARED_SKILLS="tearsheet earnings earnings-prep earnings-flash bull-bear guidance-tracker industry inflection capital-allocation dcf comps precedent-transactions supply-chain unit-economics working-capital"

for skill in $SHARED_SKILLS; do
    src="$PROJECT_DIR/.claude/skills/$skill/SKILL.md"
    dst="$PLUGIN_DIR/skills/$skill/SKILL.md"
    if [ -f "$src" ]; then
        mkdir -p "$(dirname "$dst")"
        cp "$src" "$dst"
        echo "  ✓ $skill"
    else
        echo "  ✗ $skill — source not found"
    fi
done

# Shared design system
cp "$PROJECT_DIR/.claude/skills/design-system.md" "$PLUGIN_DIR/skills/design-system.md"
echo "  ✓ design-system.md"

echo ""

# ─────────────────────────────────────────────────
# Phase 2: Transform deliverable skills via claude -p
# ─────────────────────────────────────────────────
echo "Phase 2: Transforming deliverable skills for plugin..."
echo ""

# Infra patterns that should NOT appear in transformed output
INFRA_PATTERNS="python infra/|excel_builder|comp_builder|docx_renderer|deck_renderer|pdf_renderer|report_differ|projection_engine|chart_generator"

transform_skill() {
    local skill_name="$1"
    local extra_instructions="$2"
    local extra_context="$3"

    local src="$PROJECT_DIR/.claude/skills/$skill_name/SKILL.md"
    local dst="$PLUGIN_DIR/skills/$skill_name/SKILL.md"

    if [ ! -f "$src" ]; then
        echo "  ✗ $skill_name — source not found, skipping"
        PHASE2_FAILURES=$((PHASE2_FAILURES + 1))
        return 1
    fi

    local skill_content
    skill_content=$(cat "$src")

    # Assemble the full prompt
    local prompt="$TRANSFORM_RULES

## Skill-Specific Instructions

$extra_instructions

${extra_context:+## Reference Context

$extra_context

}## Source SKILL.md to Transform

$skill_content

---

Return ONLY the transformed SKILL.md, starting with YAML frontmatter. No explanation or code fences."

    echo "  ⏳ $skill_name — transforming via claude..."

    local output
    output=$(echo "$prompt" | claude -p --model sonnet --max-turns 1 --no-session-persistence 2>/dev/null)
    local exit_code=$?

    if [ $exit_code -ne 0 ]; then
        echo "  ✗ $skill_name — claude command failed (exit code $exit_code)"
        PHASE2_FAILURES=$((PHASE2_FAILURES + 1))
        return 1
    fi

    # Validate: minimum length
    local output_len=${#output}
    if [ "$output_len" -lt 500 ]; then
        echo "  ✗ $skill_name — output too short ($output_len chars), skipping"
        PHASE2_FAILURES=$((PHASE2_FAILURES + 1))
        return 1
    fi

    # Validate: check for leftover infra references
    local infra_matches
    infra_matches=$(echo "$output" | grep -cE "$INFRA_PATTERNS" || true)
    if [ "$infra_matches" -gt 0 ]; then
        echo "  ⚠ $skill_name — WARNING: output still contains $infra_matches infra reference(s)"
        PHASE2_WARNINGS=$((PHASE2_WARNINGS + 1))
    fi

    # Validate: check data-access.md reference exists (should not be ../data-access.md)
    if ! echo "$output" | grep -q "data-access.md"; then
        echo "  ⚠ $skill_name — WARNING: no data-access.md reference found"
        PHASE2_WARNINGS=$((PHASE2_WARNINGS + 1))
    fi

    # Validate: check for raw markdown output instructions (design system forbids this)
    local markdown_matches
    markdown_matches=$(echo "$output" | grep -ciE "present.*(as|in) (structured |formatted )?markdown|output.*markdown|deliver.*markdown" || true)
    if [ "$markdown_matches" -gt 0 ]; then
        echo "  ⚠ $skill_name — WARNING: output instructs markdown delivery ($markdown_matches match(es)); design system requires HTML"
        PHASE2_WARNINGS=$((PHASE2_WARNINGS + 1))
    fi

    # Write output
    mkdir -p "$(dirname "$dst")"
    echo "$output" > "$dst"
    echo "  ✓ $skill_name ($output_len chars)"
    return 0
}

# --- research-note ---
transform_skill "research-note" \
    "This skill originally outputs a .docx Word document via docx_renderer.py with a Word template.
In the plugin version:
- Replace the .docx rendering step with a styled HTML report using the HTML Report Template from design-system.md (full CSS inlined, zero dependencies). Never output raw markdown — the design system explicitly forbids it.
- Remove all references to templates/research_note.docx.
- Remove file-save steps (reports/ directory). Present the HTML report directly in the response.
- Keep all analytical phases, data gathering, and qualitative sections intact."

# --- build-model ---
transform_skill "build-model" \
    "This skill originally outputs an .xlsx Excel model via excel_builder.py.
In the plugin version:
- Replace the Excel rendering step with a React artifact that uses SheetJS (xlsx library) to build and download the .xlsx file directly in the user's browser.
- Preserve the exact same tab structure (Income Statement, Balance Sheet, Cash Flow, Segments, KPIs, Projections, DCF, Summary).
- Replace projection_engine.py usage with inline methodology — the LLM does the math directly.
- Replace chart_generator.py usage with well-formatted data tables.
- Remove file-save steps (reports/ directory)."

# --- comp-sheet ---
transform_skill "comp-sheet" \
    "This skill originally outputs a multi-company comp sheet .xlsx via comp_builder.py.
In the plugin version:
- Replace the comp_builder.py rendering step with a React artifact that uses SheetJS (xlsx library) to build and download the .xlsx file directly in the user's browser.
- Preserve the exact same 8-tab structure.
- Remove file-save steps (reports/ directory)."

# --- ib-deck ---
# Copy reference files to plugin, then transform with references as context
IB_REF_SRC="$PROJECT_DIR/.claude/skills/ib-deck/references"
IB_REF_DST="$PLUGIN_DIR/skills/ib-deck/references"
if [ -d "$IB_REF_SRC" ]; then
    mkdir -p "$IB_REF_DST"
    cp "$IB_REF_SRC"/*.md "$IB_REF_DST/" 2>/dev/null || true
    echo "  ✓ ib-deck/references/ copied"
fi

# Build reference context for ib-deck
IB_CONTEXT=""
for ref_file in "$IB_REF_SRC"/*.md; do
    if [ -f "$ref_file" ]; then
        ref_name=$(basename "$ref_file")
        IB_CONTEXT="${IB_CONTEXT}### $ref_name
$(cat "$ref_file")

"
    fi
done

transform_skill "ib-deck" \
    "This skill originally outputs an HTML pitch deck and then renders it to PDF via deck_renderer.py.
In the plugin version:
- The HTML deck IS the final deliverable. Remove the PDF rendering step entirely.
- Instruct the user to open the HTML in a browser and print to PDF if they need a PDF.
- Keep the reference files (references/slide-templates.md, references/financial-components.md, references/ib-advisory-patterns.md) — they are copied alongside the skill.
- Keep all 14 slide types and analytical depth intact.
- Remove file-save steps (reports/ directory). Present the HTML directly." \
    "$IB_CONTEXT"

# --- initiate ---
# Include research-note and build-model SKILL.md as context so initiate can reference the adapted sub-workflows
INITIATE_CONTEXT=""
for sub_skill in research-note build-model; do
    sub_dst="$PLUGIN_DIR/skills/$sub_skill/SKILL.md"
    if [ -f "$sub_dst" ]; then
        INITIATE_CONTEXT="${INITIATE_CONTEXT}### Transformed $sub_skill/SKILL.md
$(cat "$sub_dst")

"
    fi
done

transform_skill "initiate" \
    "This skill originally orchestrates both research-note (.docx) and build-model (.xlsx) from a single data pass.
In the plugin version:
- The research note output becomes a styled HTML report using the HTML Report Template from design-system.md (full CSS inlined, zero dependencies). Never output raw markdown — the design system explicitly forbids it.
- The Excel model output becomes a React artifact with SheetJS (matching the transformed build-model skill).
- Remove all context JSON serialization to reports/.tmp/ — no filesystem persistence.
- Remove file-save steps (reports/ directory).
- The transformed versions of research-note and build-model are provided below as reference for how those sub-workflows now work in the plugin." \
    "$INITIATE_CONTEXT"

# --- update (SKIPPED) ---
echo ""
echo "  ⊘ update — SKIPPED (requires prior filesystem state from /initiate;"
echo "    not feasible in a stateless plugin context)"

echo ""

# ─────────────────────────────────────────────────
# Phase 3: Summary
# ─────────────────────────────────────────────────
echo "═══════════════════════════════════════════════"
echo "Sync complete."
echo ""
echo "Phase 1: 15 building block skills + design-system.md copied"
echo "Phase 2: 5 deliverable skills transformed ($PHASE2_FAILURES failures, $PHASE2_WARNINGS warnings)"
echo ""

if [ $PHASE2_FAILURES -gt 0 ]; then
    echo "⚠ Some transformations failed. Re-run or check claude CLI availability."
fi

if [ $PHASE2_WARNINGS -gt 0 ]; then
    echo "⚠ Some transformed files have warnings. Review for leftover infra references."
fi

echo ""
echo "Files NOT synced (maintained separately):"
echo "  - skills/data-access.md (plugin version is simplified)"
echo "  - skills/setup/SKILL.md (plugin-specific)"
echo "  - .claude-plugin/plugin.json"
echo "  - .mcp.json"
echo "  - README.md"
