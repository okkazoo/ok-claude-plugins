#!/usr/bin/env python3
"""
PreToolUse Hook: Search knowledge before entering plan mode

When Claude enters plan mode, search knowledge.json for relevant patterns
and files based on conversation context, so Claude has existing knowledge
before designing an implementation plan.
"""

import json
import sys
import re
from pathlib import Path

STOP_WORDS = {
    'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'can', 'need', 'to', 'of', 'in',
    'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
    'this', 'that', 'these', 'those', 'it', 'its', 'i', 'me', 'my', 'you',
    'your', 'we', 'our', 'they', 'them', 'their', 'what', 'which', 'who',
    'how', 'why', 'when', 'where', 'and', 'but', 'or', 'if', 'then',
    'use', 'using', 'find', 'search', 'look', 'check', 'get', 'make',
    'help', 'want', 'need', 'please', 'plan', 'mode', 'enter', 'design',
    'implement', 'implementation', 'create', 'add', 'feature', 'let',
    'going', 'now', 'first', 'start', 'begin', 'approach', 'properly'
}


def extract_keywords(text):
    """Extract meaningful keywords from text."""
    words = re.findall(r'[a-zA-Z0-9_-]+', text.lower())
    keywords = set()
    for word in words:
        if len(word) >= 3 and word not in STOP_WORDS:
            keywords.add(word)
    return keywords


def search_knowledge(keywords):
    """Search knowledge.json for matching patterns and files."""
    matches = {'patterns': [], 'files': []}
    knowledge_json = Path('.claude/knowledge/knowledge.json')

    if not knowledge_json.exists():
        return matches

    try:
        data = json.loads(knowledge_json.read_text(encoding='utf-8'))
    except:
        return matches

    type_icons = {
        'solution': '[OK]',
        'tried-failed': '[X]',
        'gotcha': '[!]',
        'best-practice': '[*]'
    }

    # Search patterns
    for p in data.get('patterns', []):
        pattern_text = p.get('pattern', '').lower()
        context = p.get('context', '')
        if isinstance(context, list):
            context = ' '.join(context)
        context = context.lower()

        all_text = pattern_text + ' ' + context
        overlap = sum(1 for kw in keywords if kw in all_text)

        if overlap >= 2:
            ptype = p.get('type', 'other')
            icon = type_icons.get(ptype, '*')
            matches['patterns'].append({
                'score': overlap,
                'text': f"{icon} {p.get('pattern', '')}",
                'type': ptype
            })

    # Search files by keywords and title
    for filepath, info in data.get('files', {}).items():
        file_keywords = set(kw.lower() for kw in info.get('keywords', []))
        title = info.get('title', filepath).lower()
        description = info.get('description', '').lower()

        # Score based on keyword overlap and title matches
        kw_overlap = len(keywords & file_keywords)
        title_overlap = sum(1 for kw in keywords if kw in title)
        desc_overlap = sum(1 for kw in keywords if kw in description)
        total_score = kw_overlap * 2 + title_overlap + desc_overlap

        if total_score >= 2:
            matched_kws = list(keywords & file_keywords)[:3]
            matches['files'].append({
                'score': total_score,
                'path': filepath,
                'title': info.get('title', filepath),
                'keywords': matched_kws
            })

    # Sort by score
    matches['patterns'].sort(key=lambda x: x['score'], reverse=True)
    matches['files'].sort(key=lambda x: x['score'], reverse=True)

    return matches


def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except:
        print(json.dumps({"continue": True}))
        return

    # Check if knowledge base exists
    knowledge_json = Path('.claude/knowledge/knowledge.json')
    if not knowledge_json.exists():
        print(json.dumps({"continue": True}))
        return

    # Extract context from conversation
    # The hook receives conversation_context or we can look at recent messages
    context_text = ""

    # Try to get conversation context
    conv_context = input_data.get('conversation_context', '')
    if conv_context:
        context_text = conv_context

    # Also check for any prompt/description in tool input
    tool_input = input_data.get('tool_input', {})
    if isinstance(tool_input, dict):
        for key in ['prompt', 'description', 'query', 'task']:
            if key in tool_input:
                context_text += ' ' + str(tool_input[key])

    # If no context available, try to read from recent assistant thinking
    if not context_text:
        # Fall back to showing recent journeys
        context_text = ""

    keywords = extract_keywords(context_text)

    # If we have keywords, search; otherwise show recent files
    if len(keywords) >= 2:
        matches = search_knowledge(keywords)
    else:
        matches = {'patterns': [], 'files': []}

    msg_parts = []

    # Show matched patterns
    if matches['patterns']:
        msg_parts.append(">> RELEVANT PATTERNS FOUND:")
        for p in matches['patterns'][:5]:
            msg_parts.append(f"  {p['text']}")

    # Show matched files
    if matches['files']:
        if msg_parts:
            msg_parts.append("")
        msg_parts.append(">> RELEVANT KNOWLEDGE FILES:")
        for f in matches['files'][:5]:
            msg_parts.append(f"  - {f['title']}")
            msg_parts.append(f"    Path: {f['path']}")
            if f['keywords']:
                msg_parts.append(f"    Matched: {', '.join(f['keywords'])}")

    # If no matches but knowledge exists, show what's available
    if not matches['patterns'] and not matches['files']:
        try:
            data = json.loads(knowledge_json.read_text(encoding='utf-8'))
            pattern_count = len(data.get('patterns', []))
            file_count = len(data.get('files', {}))

            if pattern_count > 0 or file_count > 0:
                msg_parts.append(">> KNOWLEDGE BASE AVAILABLE:")
                if pattern_count:
                    msg_parts.append(f"  - {pattern_count} patterns indexed")
                if file_count:
                    msg_parts.append(f"  - {file_count} knowledge files")
                msg_parts.append("  Use /knowledge-search <query> to find relevant entries")
        except:
            pass

    if msg_parts:
        msg_parts.append("")
        msg_parts.append("Read relevant files before designing your plan.")
        print(json.dumps({
            "continue": True,
            "message": "\n".join(msg_parts)
        }))
    else:
        print(json.dumps({"continue": True}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(json.dumps({"continue": True}))
