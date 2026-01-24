#!/usr/bin/env python3
"""
search_structures.py - Search structures on UserPromptSubmit

Searches structures.jsonl for matches against user's question keywords.
Injects relevant structures into context so Claude knows where to look.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Set

from config import get_worklog_dir, log_verbose


# Words to skip when extracting keywords
STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "to", "of",
    "in", "for", "on", "with", "at", "by", "from", "as", "into", "through",
    "and", "or", "but", "if", "then", "else", "when", "where", "why", "how",
    "all", "each", "every", "both", "few", "more", "most", "other", "some",
    "such", "no", "not", "only", "same", "so", "than", "too", "very", "just",
    "also", "now", "here", "there", "this", "that", "these", "those", "it",
    "its", "i", "me", "my", "we", "our", "you", "your", "he", "she", "they",
    "them", "what", "which", "who", "whom", "get", "make", "like", "want",
    "please", "thanks", "help", "show", "tell", "explain", "look", "see",
    "file", "files", "code", "function", "class", "method", "work", "works",
}


def extract_keywords(text: str) -> Set[str]:
    """Extract meaningful keywords from text."""
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return {w for w in words if w not in STOP_WORDS}


def load_structures(worklog_dir: Path) -> List[Dict]:
    """Load all structures from JSONL file."""
    structures_file = worklog_dir / "structures.jsonl"
    structures = []

    if structures_file.exists():
        with open(structures_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        structures.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

    return structures


def search_structures(structures: List[Dict], keywords: Set[str]) -> List[Dict]:
    """
    Search structures for keyword matches.
    Matches against: name, task_hint, file path
    Returns matched structures with relevance score.
    """
    if not keywords:
        return []

    matches = []

    for struct in structures:
        name = struct.get("name", "").lower()
        task_hint = struct.get("task_hint", "").lower()
        file_path = struct.get("file", "").lower()

        # Build searchable text
        searchable = f"{name} {task_hint} {file_path}"

        # Count keyword matches
        score = 0
        matched_keywords = []

        for keyword in keywords:
            if keyword in searchable:
                score += 1
                matched_keywords.append(keyword)
                # Bonus for name match (most relevant)
                if keyword in name:
                    score += 2

        if score > 0:
            matches.append({
                "struct": struct,
                "score": score,
                "matched": matched_keywords,
            })

    # Sort by score descending
    matches.sort(key=lambda x: x["score"], reverse=True)

    return matches[:5]  # Top 5 matches


def format_matches(matches: List[Dict]) -> str:
    """Format matches for context injection."""
    if not matches:
        return ""

    lines = ["**Relevant structures from previous work:**"]

    for match in matches:
        struct = match["struct"]
        name = struct.get("name", "")
        struct_type = struct.get("type", "")
        file_path = struct.get("file", "")
        task_hint = struct.get("task_hint", "")

        line = f"- `{name}` ({struct_type}) in `{file_path}`"
        if task_hint:
            line += f" — context: {task_hint}"
        lines.append(line)

    return "\n".join(lines)


def main():
    try:
        # Read hook input
        input_data = sys.stdin.read()
        if not input_data.strip():
            print(json.dumps({}))
            return

        data = json.loads(input_data)

        # Get user's prompt
        prompt = data.get("prompt", "")
        if not prompt:
            print(json.dumps({}))
            return

        # Extract keywords
        keywords = extract_keywords(prompt)
        if not keywords:
            print(json.dumps({}))
            return

        # Load and search structures
        worklog_dir = get_worklog_dir()
        structures = load_structures(worklog_dir)

        if not structures:
            print(json.dumps({}))
            return

        matches = search_structures(structures, keywords)

        if not matches:
            print(json.dumps({}))
            return

        # Format and output
        context = format_matches(matches)

        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": context
            }
        }

        log_verbose(f"✓ Found {len(matches)} relevant structures")
        print(json.dumps(output))

    except Exception:
        # Fail silently
        print(json.dumps({}))


if __name__ == "__main__":
    main()
