---
description: Show recent work activity and file changes
---

Read the worklog index at `.claude/worklog/index.md` and summarize recent activity.

If the user asks about a specific file, grep the logs directory for details:
```bash
grep "filename" .claude/worklog/logs/*.jsonl
```

Present the information in a clear, chronological format showing:
- What tasks/prompts were executed
- Which files were created or modified
- When the activity occurred

If no worklog exists yet, inform the user that activity tracking will begin automatically.
