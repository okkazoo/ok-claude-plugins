#!/usr/bin/env python3
"""
load_context.py - Loads recent context on SessionStart hook

Reads the last few entries from index.md and outputs them as
additional context for the new session.
"""

import json
import os
import sys
from pathlib import Path


def get_worklog_dir() -> Path:
    """Get the worklog directory."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    return Path(project_dir) / ".claude" / "worklog"


def extract_recent_entries(content: str, max_entries: int = 5, max_chars: int = 1500) -> str:
    """Extract the most recent entries from index.md content."""
    if not content.strip():
        return ""

    # Split by entry headers (## YYYY-MM-DD)
    entries = []
    current_entry = []

    for line in content.split("\n"):
        if line.startswith("## ") and current_entry:
            entries.append("\n".join(current_entry))
            current_entry = [line]
        else:
            current_entry.append(line)

    if current_entry:
        entries.append("\n".join(current_entry))

    # Filter to only date entries (skip header)
    date_entries = [e for e in entries if e.strip().startswith("## 20")]

    # Take most recent entries (they're at the beginning after prepending)
    recent = date_entries[:max_entries]

    # Join and truncate to max chars
    result = "\n".join(recent)
    if len(result) > max_chars:
        result = result[:max_chars] + "\n... (truncated)"

    return result


def main():
    try:
        worklog_dir = get_worklog_dir()
        index_file = worklog_dir / "index.md"

        context = ""

        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                content = f.read()

            recent = extract_recent_entries(content)
            if recent:
                context = f"Recent worklog activity:\n\n{recent}"

        # Output in the format expected by SessionStart hook
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context
            }
        }

        print(json.dumps(output))

    except Exception:
        # On error, output empty context rather than failing
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": ""
            }
        }
        print(json.dumps(output))


if __name__ == "__main__":
    main()
