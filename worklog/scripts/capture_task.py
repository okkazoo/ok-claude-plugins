#!/usr/bin/env python3
"""
capture_task.py - Captures user prompts on UserPromptSubmit hook

Receives JSON via stdin with the user's prompt and logs it to .current_tasks
for later inclusion in session summaries.
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


def main():
    try:
        # Read hook input from stdin
        input_data = sys.stdin.read()
        if not input_data.strip():
            return

        data = json.loads(input_data)

        # Extract the prompt from the hook input
        # UserPromptSubmit provides: {"prompt": "...", ...}
        prompt = data.get("prompt", "")

        # Skip very short prompts (likely not meaningful tasks)
        if len(prompt.strip()) < 10:
            return

        # Prepare the task entry
        entry = {
            "ts": datetime.now().isoformat(),
            "prompt": prompt.strip()
        }

        # Append to current tasks file
        worklog_dir = get_worklog_dir()
        tasks_file = worklog_dir / ".current_tasks"

        with open(tasks_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    except Exception:
        # Fail silently - never break the workflow
        pass


if __name__ == "__main__":
    main()
