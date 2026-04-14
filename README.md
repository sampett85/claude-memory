# Mister Agent Memory

Personal knowledge base that automatically captures insights from Claude Code conversations, compiles them into structured markdown articles, and syncs to Obsidian.

- **Project-scoped memory** — auto-tags articles with your project name
- **Obsidian sync** — mirrors knowledge to your Obsidian vault on compile
- **Auto-tagging** — detects tech stack and domain tags automatically
- **Weekly digests** — summarizes what you learned each week
- **Easy install** — one command to set up in any project

---

## Prerequisites

Before you begin, make sure you have:

1. **Python 3.12+** installed ([download](https://www.python.org/downloads/))
2. **uv** package manager installed:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. **Claude Code** subscription with CLI access ([docs](https://docs.anthropic.com/en/docs/claude-code))

---

## Step 1: Clone into Your Project

Navigate to any project directory where you want to enable memory, then clone this repo as a `.memory` subdirectory:

```bash
cd /path/to/your-project
git clone https://github.com/sampett85/mister-agent-memory.git .memory
```

This keeps the memory system self-contained inside `.memory/` without cluttering your project root.

---

## Step 2: Run the Install Script

```bash
cd .memory
./install.sh
```

The installer will:
1. Install Python dependencies via `uv sync`
2. Create `config.env` from the template (prompts you for Obsidian vault path and timezone)
3. Set up Claude Code hooks in your project's `.claude/settings.json`
4. Initialize the knowledge base directory structure

> **Note:** If `.claude/settings.json` already exists, the installer will print the hook commands for you to merge manually instead of overwriting your file.

---

## Step 3: Configure (Optional)

Edit `.memory/config.env` to customize:

```env
# Path to your Obsidian vault (~ is expanded automatically)
OBSIDIAN_VAULT=~/Desktop/Mister-Obsidian-Vault

# Your timezone (used for timestamps and compile scheduling)
TIMEZONE=Asia/Kolkata

# Hour (24h format) after which daily compilation auto-triggers
COMPILE_AFTER_HOUR=18

# Project name: "auto" detects from parent directory, or set manually
PROJECT_NAME=auto
```

---

## Step 4: Use Claude Code Normally

Once installed, everything works automatically through Claude Code hooks:

### What happens behind the scenes

| Event | What fires | What it does |
|-------|-----------|--------------|
| **You start a session** | `session-start.py` | Loads your knowledge base index into Claude's context so it remembers past insights |
| **You work normally** | Nothing extra | Just code, debug, and chat as usual |
| **Context gets compacted** | `pre-compact.py` | Captures conversation context before Claude summarizes it (prevents losing intermediate insights in long sessions) |
| **You end a session** | `session-end.py` | Extracts key insights from the conversation and saves them to today's daily log (`daily/YYYY-MM-DD.md`) |
| **After 6 PM** | Auto-compilation | Daily logs are compiled into structured knowledge articles in `knowledge/` |
| **Obsidian sync** | Auto after compile | Articles are mirrored to your Obsidian vault |

You don't need to do anything manually for day-to-day use. Just work with Claude Code and the knowledge base builds itself.

---

## Step 5: Explore Your Knowledge Base

### Browse in Obsidian

Point your Obsidian vault at the `knowledge/` directory. You get:
- **Graph view** — see how concepts connect
- **Backlinks** — discover relationships between articles
- **Search** — find anything across your knowledge base
- **Dataview** — query articles by tags, dates, or projects

### Browse as Markdown

Your knowledge base lives in plain markdown files:

```
.memory/knowledge/
├── index.md              # Master catalog — start here
├── log.md                # Chronological build log
├── concepts/             # Atomic knowledge articles
├── connections/          # Cross-cutting insights linking 2+ concepts
├── qa/                   # Saved query answers
└── digests/              # Weekly summaries
```

Read `knowledge/index.md` for a table of every article with one-line summaries.

---

## Step 6: Run Manual Commands (When Needed)

All commands are run from inside the `.memory/` directory:

```bash
cd .memory
```

### Compile Daily Logs into Knowledge Articles

```bash
uv run python scripts/compile.py              # compile new/changed logs only
uv run python scripts/compile.py --all        # force recompile everything
uv run python scripts/compile.py --file daily/2026-04-01.md  # compile a specific log
uv run python scripts/compile.py --dry-run    # preview without writing
```

### Query Your Knowledge Base

```bash
uv run python scripts/query.py "What auth patterns do I use?"
uv run python scripts/query.py "How did I set up the database?" --file-back
```

The `--file-back` flag saves the answer as a Q&A article in `knowledge/qa/`, making your knowledge base smarter over time.

### Run Health Checks

```bash
uv run python scripts/lint.py                    # all 7 checks
uv run python scripts/lint.py --structural-only  # skip LLM check (free, instant)
```

Checks for: broken wikilinks, orphan pages, uncompiled daily logs, stale articles, missing backlinks, sparse articles, and contradictions.

Reports are saved to `reports/lint-YYYY-MM-DD.md`.

### Generate Weekly Digest

```bash
uv run python scripts/digest.py
```

Summarizes the week's daily logs into a digest article covering key decisions, patterns, unresolved questions, and action items.

### Sync to Obsidian

```bash
uv run python scripts/sync.py
```

Manually mirrors the knowledge base to your configured Obsidian vault. This happens automatically after compilation, but you can trigger it anytime.

---

## How It All Fits Together

```
You work with Claude Code
        │
        ▼
  [session-start.py] ── loads knowledge index into context
        │
        ▼
  You code, debug, chat normally
        │
        ▼
  [session-end.py] ── extracts insights → daily/YYYY-MM-DD.md
        │
        ▼
  [compile.py] ── daily logs → knowledge articles (auto after 6 PM)
        │
        ▼
  [sync.py] ── mirrors to Obsidian vault
        │
        ▼
  Next session starts with your full knowledge base loaded
```

---

## Project Structure

```
your-project/
├── .claude/
│   └── settings.json        # Hook configuration (created by install.sh)
├── .memory/                  # This repo — self-contained
│   ├── AGENTS.md             # Full schema + technical reference
│   ├── README.md             # This file
│   ├── config.env            # Your configuration
│   ├── config.env.template   # Default config template
│   ├── pyproject.toml        # Python dependencies
│   ├── install.sh            # One-command setup
│   ├── daily/                # Raw conversation logs (immutable)
│   ├── knowledge/            # Compiled knowledge base (LLM-owned)
│   │   ├── index.md          # Master catalog
│   │   ├── log.md            # Build log
│   │   ├── concepts/         # Atomic knowledge articles
│   │   ├── connections/      # Cross-cutting insights
│   │   ├── qa/               # Saved query answers
│   │   └── digests/          # Weekly summaries
│   ├── scripts/              # CLI tools
│   │   ├── compile.py        # Compile daily logs → knowledge
│   │   ├── query.py          # Ask your knowledge base
│   │   ├── lint.py           # 7 health checks
│   │   ├── flush.py          # Background insight extraction
│   │   ├── sync.py           # Obsidian sync
│   │   ├── digest.py         # Weekly digest generator
│   │   ├── config.py         # Path constants
│   │   └── utils.py          # Shared helpers
│   ├── hooks/                # Claude Code hooks
│   │   ├── session-start.py  # Injects knowledge into sessions
│   │   ├── session-end.py    # Captures conversations
│   │   └── pre-compact.py    # Rescues context before compaction
│   └── reports/              # Lint reports
└── your-project-files...
```

---

## Estimated Costs

All operations use the Claude API through Claude Code's built-in credentials. No separate API key needed.

| Operation | Cost |
|-----------|------|
| Memory flush (per session end) | ~$0.02-0.05 |
| Compile one daily log | ~$0.45-0.65 |
| Query (without file-back) | ~$0.15-0.25 |
| Query (with file-back) | ~$0.25-0.40 |
| Full lint (with contradictions) | ~$0.15-0.25 |
| Structural lint only | $0.00 |
| Weekly digest | ~$0.20-0.35 |

---

## Troubleshooting

### Hooks not firing?
- Make sure `.claude/settings.json` exists in your **project root** (not inside `.memory/`)
- Verify the hook commands point to the right path: `uv run --directory .memory python hooks/session-start.py`

### Knowledge base not compiling?
- Check that it's past your `COMPILE_AFTER_HOUR` (default: 6 PM)
- Run manually: `cd .memory && uv run python scripts/compile.py`
- Check `scripts/state.json` for hash mismatches

### Obsidian not syncing?
- Verify `OBSIDIAN_VAULT` path in `config.env` is correct
- Run manually: `cd .memory && uv run python scripts/sync.py`

### "CLAUDE_INVOKED_BY" errors?
- This is a recursion guard — it prevents the memory system from trying to capture its own sessions
- This is normal and expected when flush.py runs

---

## License

MIT
