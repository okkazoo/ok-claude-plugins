# Worklog Skill

## Triggers
- "recent changes"
- "what did we modify"
- "where did we leave off"
- "work history"
- "what files changed"
- "what have we been working on"
- "show activity"
- "session history"

## Instructions

When the user asks about recent work activity, file changes, or where they left off:

1. **Read the worklog index** at `.claude/worklog/index.md` in the project directory
   - This contains a chronological summary of all sessions, newest first
   - Each entry shows the task prompt and files created/modified

2. **For more detail about specific files**, grep the logs directory:
   ```bash
   grep "filename" .claude/worklog/logs/*.jsonl
   ```

3. **Summarize the activity** in a helpful way:
   - What was the user working on?
   - Which files were touched?
   - Any patterns or ongoing work?

4. **If the index doesn't exist**, inform the user that no worklog history exists yet. The worklog will start capturing activity automatically going forward.

## Example Response

"Based on your worklog, here's your recent activity:

**Today (2026-01-21)**
- You were working on the authentication module
- Modified: `src/auth/login.py`, `src/auth/middleware.py`
- Created: `tests/test_auth.py`

**Yesterday (2026-01-20)**
- Refactored the database connection pool
- Modified: `src/db/pool.py`

Would you like more details on any of these changes?"
