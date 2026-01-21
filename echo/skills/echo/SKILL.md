# Echo Skill

## Triggers
- "what do you remember"
- "recent changes"
- "what did we modify"
- "where did we leave off"
- "work history"
- "what files changed"
- "what have we been working on"
- "show activity"
- "project structure"
- "where is the code for"

## Instructions

Echo is Claude's memory of your codebase. When the user asks about recent work, project structure, or where things are:

### 1. Check Structure Knowledge
Read `.claude/echo/structure.md` for:
- Known classes, functions, components by directory
- Search patterns that worked before
- Recent activity summary

### 2. Check Activity Log
Read `.claude/echo/index.md` for:
- Chronological summary of all sessions
- Task prompts and files modified
- What the user was working on

### 3. For Detailed File History
```bash
grep "filename" .claude/echo/logs/*.jsonl
```

### 4. For Raw Structure Data
```bash
cat .claude/echo/structures.jsonl | tail -20
```

## Example Responses

**"What do you remember about this project?"**
> "Based on Echo's memory:
>
> **Structure:**
> - `src/auth/` - AuthManager class, login/logout functions
> - `src/components/` - Layout, Header, Sidebar components
> - `src/api/` - API routes and handlers
>
> **Recent work:**
> - Yesterday you were fixing the yellow outline styling in Layout.css
> - Before that, keyboard shortcuts in Layout.jsx
>
> **Search hints:**
> - Authentication code → `src/auth/`
> - Component styling → `src/components/*.css`"

**"Where's the code for user login?"**
> "Echo remembers: login-related code is in `src/auth/` - specifically the `login` function in `auth.py` and `AuthManager` class."

## When No Memory Exists

If `.claude/echo/` doesn't exist or is empty:
> "Echo hasn't captured any knowledge yet. As you work, I'll automatically learn:
> - Code structures (classes, functions, components)
> - Successful search patterns
> - File modification history
>
> This builds up over sessions to help me navigate your codebase faster."
