# Echo - Autonomous Knowledge Capture for Claude Code

Echo remembers your codebase. It automatically captures code structures, search patterns, and activity to help Claude navigate your project faster across sessions.

## What Echo Captures

- **Code Structures**: Classes, functions, components detected on file creation/edit
- **Search Patterns**: Successful Grep/Glob patterns and where they found results
- **Activity Log**: Every task and file modification, chronologically organized
- **Project Map**: Consolidated structure.md generated fresh each session

## Installation

### From GitHub

```bash
# Add as a marketplace
/plugin marketplace add okkazoo/echo

# Install globally (available in all projects)
/plugin install echo@okkazoo/echo --scope user
```

Or install per-project:
```bash
/plugin install echo@okkazoo/echo --scope project
```

### Development Mode

```bash
claude --plugin-dir /path/to/echo
```

## How It Works

### Hooks

| Hook | Script | Purpose |
|------|--------|---------|
| `SessionStart` | `consolidate_structure.py` | Verifies & consolidates knowledge, outputs structure.md |
| `UserPromptSubmit` | `capture_task.py` | Logs user prompts |
| `PostToolUse` | `capture_edit.py` | Logs file changes |
| `PostToolUse` | `capture_structure.py` | Detects class/function definitions |
| `PostToolUse` | `capture_search.py` | Logs successful search patterns |
| `Stop` | `session_summary.py` | Generates activity summary |

### Data Storage

All data stored in `$CLAUDE_PROJECT_DIR/.claude/echo/`:

```
.claude/echo/
├── structure.md       # Consolidated project structure (regenerated each session)
├── index.md           # Human-readable activity log (newest first)
├── structures.jsonl   # Raw structure captures (classes, functions, etc.)
├── searches.jsonl     # Search pattern history
├── logs/
│   └── YYYY-MM-DD.jsonl  # Daily raw edit logs
├── .current_tasks     # Temporary task buffer
└── .processed         # Deduplication tracking
```

### Verbose Output

Echo shows feedback when capturing knowledge:

```
✓ Learned: AuthManager, login, validate in auth.py
✓ Search: "authentication" → src/auth/
✓ Task: Fix the login redirect issue...
✓ Modified: auth.py
```

To silence, set `WORKLOG_VERBOSE=0` or create `.claude/echo/config.json`:
```json
{"verbose": false}
```

## Usage

### Automatic (Background)

Echo works silently in the background:
- Structures captured on every Write/Edit
- Searches captured on every Grep/Glob
- Tasks captured on every prompt
- Knowledge consolidated at session start

### Query Echo

Ask Claude:
- "What do you remember about this project?"
- "Where is the authentication code?"
- "What did we work on recently?"
- "Show me the project structure"

Or use the skill:
```
/echo
```

## Example Output

**structure.md** (auto-generated):
```markdown
# Project Structure (auto-generated)
*Last updated: 2026-01-21 14:30*

## Known Structures

### `src/auth/`
- `auth.py`: AuthManager (class), login (function), validate_token (function)
- `middleware.py`: require_auth (function)

### `src/components/`
- `Layout.jsx`: Layout (component), Sidebar (component)

## Search Hints
*Patterns that found results in these directories:*
- `src/auth/`: "authentication", "login", "token"
- `src/components/`: "Layout", "component"

## Recent Activity
## 2026-01-21 14:30
**Task**: Fix the login redirect issue
- **Modified**: `src/auth/auth.py`
```

## Configuration

| Variable | Description |
|----------|-------------|
| `CLAUDE_PROJECT_DIR` | Project root (auto-set by Claude Code) |
| `WORKLOG_VERBOSE` | Set to `0` to silence output |

## Requirements

- Python 3.6+
- No external dependencies

## License

MIT
