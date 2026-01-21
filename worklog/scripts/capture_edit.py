#!/usr/bin/env python3
"""
capture_edit.py - Captures file edits on PostToolUse hook

Receives JSON via stdin when Write, Edit, or MultiEdit tools are used.
Logs the file changes to daily log files.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def get_worklog_dir() -> Path:
    """Get the worklog directory, creating it if needed."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    worklog_dir = Path(project_dir) / ".claude" / "worklog"
    worklog_dir.mkdir(parents=True, exist_ok=True)
    return worklog_dir


def get_logs_dir() -> Path:
    """Get the logs subdirectory, creating it if needed."""
    logs_dir = get_worklog_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def main():
    try:
        # Read hook input from stdin
        input_data = sys.stdin.read()
        if not input_data.strip():
            return

        data = json.loads(input_data)

        # Extract tool information from PostToolUse hook
        # PostToolUse provides: {"tool_name": "...", "tool_input": {...}, ...}
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        # Only process file modification tools
        if tool_name not in ("Write", "Edit", "MultiEdit"):
            return

        # Extract file path and description
        file_path = tool_input.get("file_path", "")
        description = tool_input.get("description", "")

        if not file_path:
            return

        # Determine operation type
        # Write = new file or overwrite, Edit/MultiEdit = modification
        operation = "created" if tool_name == "Write" else "modified"

        # Prepare the log entry
        entry = {
            "ts": datetime.now().isoformat(),
            "tool": tool_name,
            "operation": operation,
            "file_path": file_path,
            "description": description
        }

        # Write to today's log file
        logs_dir = get_logs_dir()
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = logs_dir / f"{today}.jsonl"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    except Exception:
        # Fail silently - never break the workflow
        pass


if __name__ == "__main__":
    main()
