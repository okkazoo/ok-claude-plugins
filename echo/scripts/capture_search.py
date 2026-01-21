#!/usr/bin/env python3
"""
capture_search.py - Captures successful Grep/Glob searches

Logs search patterns and where they found results, building up
a "search hint" index for future sessions.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Set

from config import get_worklog_dir, log_verbose


def extract_directories(file_paths: List[str], max_dirs: int = 3) -> List[str]:
    """Extract unique parent directories from file paths."""
    dirs: Set[str] = set()
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

    for fp in file_paths:
        try:
            # Make relative
            rel = os.path.relpath(fp, project_dir)
            if rel.startswith(".."):
                continue
            # Get parent directory
            parent = str(Path(rel).parent)
            if parent and parent != ".":
                dirs.add(parent)
        except ValueError:
            continue

    # Return most common/shortest directories
    sorted_dirs = sorted(dirs, key=lambda d: (d.count(os.sep), len(d)))
    return sorted_dirs[:max_dirs]


def main():
    try:
        input_data = sys.stdin.read()
        if not input_data.strip():
            return

        data = json.loads(input_data)

        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        tool_result = data.get("tool_result", {})

        if tool_name not in ("Grep", "Glob"):
            return

        # Extract pattern
        pattern = tool_input.get("pattern", "")
        if not pattern or len(pattern) < 2:
            return

        # Extract results - tool_result format varies
        # Could be a string with file paths or a structured result
        result_str = str(tool_result)

        # Skip if no results found
        if "No matches found" in result_str or "0 matches" in result_str:
            return

        # Try to extract file paths from result
        # Results often contain file paths, one per line or in a list
        files_found = []

        if isinstance(tool_result, dict):
            # Structured result
            files_found = tool_result.get("files", [])
            if not files_found:
                # Try parsing from content
                content = tool_result.get("content", "")
                if content:
                    files_found = [line.strip() for line in content.split("\n")
                                   if line.strip() and os.path.sep in line or "/" in line]
        elif isinstance(tool_result, str):
            # String result - extract file-like paths
            for line in tool_result.split("\n"):
                line = line.strip()
                # Look for file paths (contains / or \ and has extension-like suffix)
                if ("/" in line or "\\" in line) and "." in line:
                    # Clean up - take just the path part
                    parts = line.split(":")
                    if parts:
                        files_found.append(parts[0])

        if not files_found:
            return

        # Extract key directories
        directories = extract_directories(files_found)
        if not directories:
            return

        # Log the search pattern and where it was found
        worklog_dir = get_worklog_dir()
        searches_file = worklog_dir / "searches.jsonl"

        entry = {
            "ts": datetime.now().isoformat(),
            "tool": tool_name,
            "pattern": pattern,
            "directories": directories,
            "file_count": len(files_found),
        }

        with open(searches_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        # Verbose output
        dirs_str = ", ".join(directories[:2])
        if len(directories) > 2:
            dirs_str += f" +{len(directories) - 2}"
        log_verbose(f"✓ Search: \"{pattern[:30]}\" → {dirs_str}")

    except Exception:
        # Fail silently
        pass


if __name__ == "__main__":
    main()
