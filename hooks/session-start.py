"""
SessionStart hook — injects knowledge base context into every conversation.

Reads the knowledge base index and recent daily log, injects them as
additional context so Claude always "remembers" what it has learned.
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

MEMORY_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = MEMORY_ROOT / "knowledge"
DAILY_DIR = MEMORY_ROOT / "daily"
INDEX_FILE = KNOWLEDGE_DIR / "index.md"

_env_file = MEMORY_ROOT / "config.env"
_project_name = MEMORY_ROOT.parent.name
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        if line.startswith("PROJECT_NAME=") and not line.endswith("=auto"):
            _project_name = line.split("=", 1)[1].strip()
            break

MAX_CONTEXT_CHARS = 20_000
MAX_LOG_LINES = 30


def get_recent_log() -> str:
    """Read the most recent daily log (today or yesterday)."""
    today = datetime.now(timezone.utc).astimezone()
    for offset in range(2):
        date = today - timedelta(days=offset)
        log_path = DAILY_DIR / f"{date.strftime('%Y-%m-%d')}.md"
        if log_path.exists():
            lines = log_path.read_text(encoding="utf-8").splitlines()
            recent = lines[-MAX_LOG_LINES:] if len(lines) > MAX_LOG_LINES else lines
            return "\n".join(recent)
    return "(no recent daily log)"


def build_context() -> str:
    """Assemble the context to inject into the conversation."""
    parts = []
    today = datetime.now(timezone.utc).astimezone()
    parts.append(f"## Today\n{today.strftime('%A, %B %d, %Y')}")
    parts.append(f"## Project\n{_project_name}")

    if INDEX_FILE.exists():
        index_content = INDEX_FILE.read_text(encoding="utf-8")
        parts.append(f"## Knowledge Base Index\n\n{index_content}")
    else:
        parts.append("## Knowledge Base Index\n\n(empty — no articles compiled yet)")

    recent_log = get_recent_log()
    parts.append(f"## Recent Daily Log\n\n{recent_log}")

    context = "\n\n---\n\n".join(parts)
    if len(context) > MAX_CONTEXT_CHARS:
        context = context[:MAX_CONTEXT_CHARS] + "\n\n...(truncated)"
    return context


def main():
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": build_context(),
        }
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
