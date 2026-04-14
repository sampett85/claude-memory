# Claude Memory

Personal knowledge base that automatically captures insights from Claude Code conversations, compiles them into structured markdown articles, and syncs to Obsidian.

Enhanced fork of [coleam00/claude-memory-compiler](https://github.com/coleam00/claude-memory-compiler) with:
- **Project-scoped memory** — auto-tags articles with your project name
- **Obsidian sync** — mirrors knowledge to your Obsidian vault on compile
- **Auto-tagging** — detects tech stack and domain tags automatically
- **Weekly digests** — summarizes what you learned each week
- **Easy install** — one command to set up in any project

## Quick Start

```bash
# In any project directory:
git clone https://github.com/sampett85/claude-memory.git .memory
cd .memory && ./install.sh
```

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Claude Code subscription

## How It Works

1. **Session starts** — your knowledge base index is injected into Claude's context
2. **You work normally** — Claude Code captures conversations automatically
3. **Session ends** — insights are extracted and saved to daily logs
4. **After 6 PM** — daily logs are compiled into structured knowledge articles
5. **Articles sync to Obsidian** — browse with graph view, search, and Dataview

## Manual Commands

Run from inside `.memory/`:

| Command | What it does |
|---------|-------------|
| `uv run python scripts/compile.py` | Compile daily logs into knowledge articles |
| `uv run python scripts/query.py "question"` | Search your knowledge base |
| `uv run python scripts/digest.py` | Generate weekly digest |
| `uv run python scripts/lint.py` | Run health checks |
| `uv run python scripts/sync.py` | Sync to Obsidian manually |

## Configuration

Edit `config.env` (created by install.sh):

```env
OBSIDIAN_VAULT=~/Desktop/Mister-Obsidian-Vault
TIMEZONE=Asia/Kolkata
COMPILE_AFTER_HOUR=18
PROJECT_NAME=auto
```

## Costs

| Operation | Cost |
|-----------|------|
| Memory flush (per session) | ~$0.02-0.05 |
| Compile one daily log | ~$0.45-0.65 |
| Query | ~$0.15-0.25 |
| Weekly digest | ~$0.20-0.35 |
| Lint (with contradictions) | ~$0.15-0.25 |

## License

MIT
