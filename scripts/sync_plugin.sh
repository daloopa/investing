#!/bin/bash
# Sync shared skill files from the project repo to the plugin repo.
# Run from the project root: bash scripts/sync_plugin.sh

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="$PROJECT_DIR/../daloopa-plugin"

if [ ! -d "$PLUGIN_DIR" ]; then
    echo "Error: Plugin repo not found at $PLUGIN_DIR"
    echo "Clone the plugin repo first, then re-run this script."
    exit 1
fi

echo "Syncing shared skills from project → plugin..."

# Shared building block skills (9 skills — identical between repos)
SHARED_SKILLS="tearsheet earnings bull-bear guidance-tracker industry inflection capital-allocation dcf comps"

for skill in $SHARED_SKILLS; do
    src="$PROJECT_DIR/.claude/skills/$skill/SKILL.md"
    dst="$PLUGIN_DIR/skills/$skill/SKILL.md"
    if [ -f "$src" ]; then
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
echo "Done. Files NOT synced (maintained separately):"
echo "  - skills/data-access.md (plugin version is simplified)"
echo "  - skills/setup/SKILL.md (plugin-specific)"
echo "  - .claude-plugin/plugin.json"
echo "  - .mcp.json"
echo "  - README.md"
