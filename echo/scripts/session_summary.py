#!/usr/bin/env python3
"""
session_summary.py - Generates session summary on Stop hook

Combines current tasks with today's file changes to create a
human-readable summary prepended to the index file.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from config import get_worklog_dir, log_verbose


def get_logs_dir() -> Path:
    """Get the logs subdirectory."""
    return get_worklog_dir() / "logs"


def load_current_tasks(worklog_dir: Path) -> List[Dict[str, Any]]:
    """Load tasks from .current_tasks file."""
    tasks_file = worklog_dir / ".current_tasks"
    tasks = []

    if tasks_file.exists():
        with open(tasks_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        tasks.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

    return tasks


def load_todays_edits(logs_dir: Path) -> List[Dict[str, Any]]:
    """Load today's edits from the daily log file."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = logs_dir / f"{today}.jsonl"
    edits = []

    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        edits.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

    return edits


def load_processed_entries(worklog_dir: Path) -> set:
    """Load set of already processed entry timestamps."""
    processed_file = worklog_dir / ".processed"
    processed = set()

    if processed_file.exists():
        with open(processed_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    processed.add(line)

    return processed


def save_processed_entries(worklog_dir: Path, processed: set):
    """Save processed entry timestamps."""
    processed_file = worklog_dir / ".processed"
    with open(processed_file, "w", encoding="utf-8") as f:
        for ts in sorted(processed):
            f.write(ts + "\n")


def generate_summary(tasks: List[Dict], edits: List[Dict], processed: set) -> tuple:
    """Generate markdown summary from tasks and edits, skipping already processed."""
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M")

    # Filter out already processed entries
    new_tasks = [t for t in tasks if t.get("ts") not in processed]
    new_edits = [e for e in edits if e.get("ts") not in processed]

    # If nothing new to report, return empty
    if not new_tasks and not new_edits:
        return "", set()

    lines = [f"## {timestamp}"]

    # Add task prompts
    if new_tasks:
        # Use the most recent task as the main task description
        main_task = new_tasks[-1].get("prompt", "")
        if len(main_task) > 100:
            main_task = main_task[:100] + "..."
        lines.append(f"**Task**: {main_task}")

    # Group edits by operation type
    created = []
    modified = []

    for edit in new_edits:
        file_path = edit.get("file_path", "")
        description = edit.get("description", "")
        operation = edit.get("operation", "modified")

        # Make path relative if possible
        try:
            project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
            rel_path = os.path.relpath(file_path, project_dir)
            if not rel_path.startswith(".."):
                file_path = rel_path
        except ValueError:
            pass

        entry = f"`{file_path}`"
        if description:
            entry += f" - {description}"

        if operation == "created":
            created.append(entry)
        else:
            modified.append(entry)

    # Add file changes
    for item in created:
        lines.append(f"- **Created**: {item}")

    for item in modified:
        lines.append(f"- **Modified**: {item}")

    lines.append("")  # Blank line after entry

    # Track which entries we've now processed
    newly_processed = set()
    for t in new_tasks:
        newly_processed.add(t.get("ts", ""))
    for e in new_edits:
        newly_processed.add(e.get("ts", ""))

    return "\n".join(lines), newly_processed


def prepend_to_index(worklog_dir: Path, summary: str):
    """Prepend summary to index.md, creating if needed."""
    index_file = worklog_dir / "index.md"

    existing_content = ""
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            existing_content = f.read()

    # Add header if new file
    if not existing_content.strip():
        header = "# Worklog\n\nAutomatically generated activity log.\n\n"
        new_content = header + summary
    else:
        # Find where to insert (after the header, before first ## entry)
        # Look for first "## " which marks the first date entry
        if "## " in existing_content:
            # Insert new summary after header but before first entry
            parts = existing_content.split("## ", 1)
            if len(parts) == 2:
                new_content = parts[0] + summary + "## " + parts[1]
            else:
                new_content = existing_content + "\n" + summary
        else:
            new_content = existing_content + "\n" + summary

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(new_content)


def clear_current_tasks(worklog_dir: Path):
    """Clear the current tasks file after summarizing."""
    tasks_file = worklog_dir / ".current_tasks"
    if tasks_file.exists():
        tasks_file.unlink()


def main():
    try:
        worklog_dir = get_worklog_dir()
        logs_dir = get_logs_dir()

        # Load data
        tasks = load_current_tasks(worklog_dir)
        edits = load_todays_edits(logs_dir)
        processed = load_processed_entries(worklog_dir)

        # Generate and save summary
        summary, newly_processed = generate_summary(tasks, edits, processed)

        if summary:
            prepend_to_index(worklog_dir, summary)

            # Update processed entries
            processed.update(newly_processed)
            save_processed_entries(worklog_dir, processed)

            # Verbose output
            task_count = len([t for t in tasks if t.get("ts") in newly_processed])
            edit_count = len([e for e in edits if e.get("ts") in newly_processed])
            log_verbose(f"✓ Session saved: {task_count} tasks, {edit_count} edits")

        # Clear current tasks
        clear_current_tasks(worklog_dir)

    except Exception:
        # Fail silently - never break the workflow
        pass


if __name__ == "__main__":
    main()
