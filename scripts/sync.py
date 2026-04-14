"""
Obsidian sync — copies knowledge/ articles to the Obsidian vault.

Reads OBSIDIAN_VAULT from config.env, copies all markdown files from
knowledge/ to <vault>/Claude-Memory/<project-name>/, preserving
subdirectory structure.

Usage:
    uv run python scripts/sync.py
"""

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import KNOWLEDGE_DIR, OBSIDIAN_VAULT, get_project_name


def sync_to_obsidian() -> int:
    """Copy knowledge base to Obsidian vault. Returns number of files synced."""
    if not OBSIDIAN_VAULT:
        return 0

    project = get_project_name()
    target_dir = OBSIDIAN_VAULT / "Claude-Memory" / project

    if not OBSIDIAN_VAULT.exists():
        print(f"Warning: Obsidian vault not found at {OBSIDIAN_VAULT}")
        return 0

    count = 0
    for md_file in KNOWLEDGE_DIR.rglob("*.md"):
        rel = md_file.relative_to(KNOWLEDGE_DIR)
        dest = target_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(md_file, dest)
        count += 1

    return count


def main():
    if not OBSIDIAN_VAULT:
        print("OBSIDIAN_VAULT not configured in config.env — skipping sync.")
        return

    count = sync_to_obsidian()
    project = get_project_name()
    target = OBSIDIAN_VAULT / "Claude-Memory" / project
    print(f"Synced {count} files to {target}")


if __name__ == "__main__":
    main()
