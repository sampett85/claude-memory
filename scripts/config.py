"""Path constants and configuration for mister-agent-memory."""

import os
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv

# ── Paths ──────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
DAILY_DIR = ROOT_DIR / "daily"
KNOWLEDGE_DIR = ROOT_DIR / "knowledge"
CONCEPTS_DIR = KNOWLEDGE_DIR / "concepts"
CONNECTIONS_DIR = KNOWLEDGE_DIR / "connections"
QA_DIR = KNOWLEDGE_DIR / "qa"
DIGESTS_DIR = KNOWLEDGE_DIR / "digests"
REPORTS_DIR = ROOT_DIR / "reports"
SCRIPTS_DIR = ROOT_DIR / "scripts"
HOOKS_DIR = ROOT_DIR / "hooks"
AGENTS_FILE = ROOT_DIR / "AGENTS.md"

INDEX_FILE = KNOWLEDGE_DIR / "index.md"
LOG_FILE = KNOWLEDGE_DIR / "log.md"
STATE_FILE = SCRIPTS_DIR / "state.json"

# Project root (parent of .memory/ or mister-agent-memory/)
PROJECT_DIR = ROOT_DIR.parent

# ── Load config.env ────────────────────────────────────────────────────
_env_file = ROOT_DIR / "config.env"
if _env_file.exists():
    load_dotenv(_env_file)

# ── User configuration ────────────────────────────────────────────────
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
COMPILE_AFTER_HOUR = int(os.getenv("COMPILE_AFTER_HOUR", "18"))

_obsidian_raw = os.getenv("OBSIDIAN_VAULT", "")
OBSIDIAN_VAULT = Path(os.path.expanduser(_obsidian_raw)) if _obsidian_raw else None

_project_name_raw = os.getenv("PROJECT_NAME", "auto")


def get_project_name() -> str:
    """Return the project name. If 'auto', derive from parent directory."""
    if _project_name_raw and _project_name_raw != "auto":
        return _project_name_raw
    return PROJECT_DIR.name


# ── Time helpers ───────────────────────────────────────────────────────

def now_iso() -> str:
    """Current time in ISO 8601 format."""
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def today_iso() -> str:
    """Current date in ISO 8601 format."""
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
