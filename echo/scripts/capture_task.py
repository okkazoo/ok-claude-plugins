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

from config import get_worklog_dir, log_verbose


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

        # Verbose output
        short_prompt = prompt[:50] + "..." if len(prompt) > 50 else prompt
        log_verbose(f"✓ Task: {short_prompt}")

    except Exception:
        # Fail silently - never break the workflow
        pass


if __name__ == "__main__":
    main()
