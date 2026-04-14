#!/usr/bin/env bash
set -euo pipefail

# Claude Memory — Install Script
# Run from inside the .memory/ directory after cloning

MEMORY_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$MEMORY_DIR")"
CLAUDE_DIR="$PROJECT_DIR/.claude"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"

echo "=== Claude Memory Setup ==="
echo "Memory dir: $MEMORY_DIR"
echo "Project dir: $PROJECT_DIR"
echo ""

# Step 1: Install Python dependencies
echo "1. Installing dependencies..."
uv sync
echo "   Done."
echo ""

# Step 2: Create config.env from template
if [ ! -f "$MEMORY_DIR/config.env" ]; then
    echo "2. Creating config.env..."
    cp "$MEMORY_DIR/config.env.template" "$MEMORY_DIR/config.env"

    # Prompt for Obsidian vault path
    read -rp "   Obsidian vault path [~/Desktop/Mister-Obsidian-Vault]: " vault_path
    vault_path="${vault_path:-~/Desktop/Mister-Obsidian-Vault}"
    sed -i.bak "s|OBSIDIAN_VAULT=.*|OBSIDIAN_VAULT=$vault_path|" "$MEMORY_DIR/config.env"

    # Prompt for timezone
    read -rp "   Timezone [Asia/Kolkata]: " tz
    tz="${tz:-Asia/Kolkata}"
    sed -i.bak "s|TIMEZONE=.*|TIMEZONE=$tz|" "$MEMORY_DIR/config.env"

    rm -f "$MEMORY_DIR/config.env.bak"
    echo "   Created config.env"
else
    echo "2. config.env already exists — skipping."
fi
echo ""

# Step 3: Create/merge .claude/settings.json
echo "3. Setting up Claude Code hooks..."
mkdir -p "$CLAUDE_DIR"

HOOKS_JSON='{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "uv run --directory .memory python hooks/session-start.py",
            "timeout": 15
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "uv run --directory .memory python hooks/pre-compact.py",
            "timeout": 10
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "uv run --directory .memory python hooks/session-end.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}'

if [ -f "$SETTINGS_FILE" ]; then
    echo "   WARNING: $SETTINGS_FILE already exists."
    echo "   Please manually merge the hooks from config.env.template."
    echo "   Hook commands:"
    echo "     SessionStart: uv run --directory .memory python hooks/session-start.py"
    echo "     SessionEnd:   uv run --directory .memory python hooks/session-end.py"
    echo "     PreCompact:   uv run --directory .memory python hooks/pre-compact.py"
else
    echo "$HOOKS_JSON" > "$SETTINGS_FILE"
    echo "   Created $SETTINGS_FILE"
fi
echo ""

# Step 4: Create initial knowledge base files
echo "4. Initializing knowledge base..."
mkdir -p "$MEMORY_DIR/knowledge/concepts" \
         "$MEMORY_DIR/knowledge/connections" \
         "$MEMORY_DIR/knowledge/qa" \
         "$MEMORY_DIR/knowledge/digests" \
         "$MEMORY_DIR/daily" \
         "$MEMORY_DIR/reports"

if [ ! -f "$MEMORY_DIR/knowledge/index.md" ]; then
    cat > "$MEMORY_DIR/knowledge/index.md" << 'EOF'
# Knowledge Base Index

| Article | Summary | Compiled From | Updated |
|---------|---------|---------------|---------|
EOF
fi

if [ ! -f "$MEMORY_DIR/knowledge/log.md" ]; then
    echo "# Build Log" > "$MEMORY_DIR/knowledge/log.md"
fi

echo "   Done."
echo ""

# Step 5: Print usage instructions
PROJECT_NAME="$(basename "$PROJECT_DIR")"
echo "=== Setup Complete ==="
echo ""
echo "Claude Memory is now active for project: $PROJECT_NAME"
echo ""
echo "What happens automatically:"
echo "  - Session start: knowledge base index injected into context"
echo "  - Session end: conversations captured and flushed to daily logs"
echo "  - Pre-compact: context rescued before summarization"
echo "  - After 6 PM: daily logs auto-compiled into knowledge articles"
echo ""
echo "Manual commands (run from project root):"
echo "  cd .memory && uv run python scripts/compile.py        # compile daily logs now"
echo "  cd .memory && uv run python scripts/query.py \"question\" # search knowledge base"
echo "  cd .memory && uv run python scripts/digest.py          # generate weekly digest"
echo "  cd .memory && uv run python scripts/lint.py            # health check"
echo "  cd .memory && uv run python scripts/sync.py            # sync to Obsidian"
