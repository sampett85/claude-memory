"""
Weekly digest — summarizes the past 7 days of daily logs.

Reads all daily logs from the past week, sends to Claude for summarization,
and outputs a structured digest to knowledge/digests/.

Usage:
    uv run python scripts/digest.py
"""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from config import DIGESTS_DIR, DAILY_DIR, KNOWLEDGE_DIR, get_project_name, now_iso, today_iso
from utils import load_state, save_state

ROOT_DIR = Path(__file__).resolve().parent.parent


def get_week_logs(days: int = 7) -> list[tuple[str, str]]:
    """Read daily logs from the past N days. Returns list of (filename, content)."""
    today = datetime.now(timezone.utc).astimezone()
    logs = []
    for offset in range(days):
        date = today - timedelta(days=offset)
        log_path = DAILY_DIR / f"{date.strftime('%Y-%m-%d')}.md"
        if log_path.exists():
            content = log_path.read_text(encoding="utf-8")
            logs.append((log_path.name, content))
    return logs


async def generate_digest(logs: list[tuple[str, str]]) -> str:
    """Use Claude Agent SDK to generate a weekly digest."""
    from claude_agent_sdk import (
        AssistantMessage, ClaudeAgentOptions, ResultMessage, TextBlock, query,
    )

    project = get_project_name()
    today = datetime.now(timezone.utc).astimezone()
    week_start = today - timedelta(days=6)
    iso_week = today.strftime("%Y-W%W")

    log_content = ""
    source_files = []
    for filename, content in logs:
        log_content += f"\n\n## {filename}\n\n{content}"
        source_files.append(f"daily/{filename}")

    sources_yaml = "\n".join(f'  - "{s}"' for s in source_files)

    prompt = f"""You are a weekly digest generator. Summarize the past week's daily logs
into a structured weekly digest. Do NOT use any tools — just return plain text.

## Project
{project}

## Period
{week_start.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}

## Daily Logs

{log_content}

## Output Format

Return ONLY the markdown content (no code fences) in this exact format:

---
title: "Week {iso_week} Digest"
type: digest
project: {project}
period: "{week_start.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}"
sources:
{sources_yaml}
created: {today_iso()}
---

# Week {iso_week} Digest

## Key Decisions
- [Decisions made this week with rationale]

## Patterns & Insights
- [New patterns learned, techniques discovered]

## Unresolved Questions
- [Open questions that need follow-up]

## Action Items
- [TODOs carried forward]

## Tech Stack Changes
- [New tools, libraries, or approaches adopted]

Only include sections that have actual content. If a section has nothing,
omit it entirely."""

    response = ""
    try:
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                cwd=str(ROOT_DIR),
                allowed_tools=[],
                max_turns=2,
            ),
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response += block.text
    except Exception as e:
        print(f"Error generating digest: {e}")
        return ""

    return response


def main():
    logs = get_week_logs()
    if not logs:
        print("No daily logs found for the past 7 days.")
        return

    print(f"Found {len(logs)} daily log(s) from the past week.")
    print("Generating digest...")

    digest = asyncio.run(generate_digest(logs))
    if not digest:
        print("Failed to generate digest.")
        return

    today = datetime.now(timezone.utc).astimezone()
    iso_week = today.strftime("%Y-W%W")
    DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
    digest_path = DIGESTS_DIR / f"week-{iso_week}.md"
    digest_path.write_text(digest, encoding="utf-8")
    print(f"Digest saved to: {digest_path}")

    # Update index
    index_path = KNOWLEDGE_DIR / "index.md"
    if index_path.exists():
        index_content = index_path.read_text(encoding="utf-8")
        week_start = today - timedelta(days=6)
        new_row = f"| [[digests/week-{iso_week}]] | Weekly digest: {week_start.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')} | daily logs | {today_iso()} |"
        if f"week-{iso_week}" not in index_content:
            index_content = index_content.rstrip() + "\n" + new_row + "\n"
            index_path.write_text(index_content, encoding="utf-8")

    # Update state
    state = load_state()
    state["last_digest"] = now_iso()
    save_state(state)

    # Trigger Obsidian sync
    from sync import sync_to_obsidian
    count = sync_to_obsidian()
    if count > 0:
        print(f"Obsidian sync: {count} files synced")

    print("Done.")


if __name__ == "__main__":
    main()
