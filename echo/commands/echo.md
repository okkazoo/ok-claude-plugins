---
description: Show what Echo remembers about this project
---

Read Echo's knowledge files and summarize what's known about this project.

1. **Structure knowledge** - Read `.claude/echo/structure.md` for:
   - Known classes, functions, components by directory
   - Search patterns that worked before

2. **Activity log** - Read `.claude/echo/index.md` for:
   - Recent tasks and file changes
   - What the user was working on

3. **For specific file history**:
```bash
grep "filename" .claude/echo/logs/*.jsonl
```

Present the information showing:
- Project structure overview
- Recent activity
- Search hints for navigation

If no Echo data exists yet, inform the user that knowledge capture will begin automatically as they work.
