# Worklog Plugin for Claude Code

Autonomous activity tracking that logs all file changes and user tasks across sessions without relying on Claude to decide what's worth remembering.

## Features

- **Automatic Task Capture**: Every user prompt is logged automatically
- **File Change Tracking**: All Write, Edit, and MultiEdit operations are recorded
- **Session Summaries**: Human-readable markdown summaries generated at session end
- **Context Loading**: Recent activity automatically provided at session start
- **Per-Project Storage**: All data stored in `.claude/worklog/` within each project

## Installation

### From GitHub (Recommended)

```bash
# Add as a marketplace
/plugin marketplace add okkazoo/worklog

# Install globally (available in all projects)
/plugin install worklog@okkazoo/worklog --scope user
```

Or install per-project (shared with team via git):
```bash
/plugin install worklog@okkazoo/worklog --scope project
```

### Development Mode

To test locally without installing:
```bash
claude --plugin-dir /path/to/worklog
```

## How It Works

### Hooks

| Hook | Script | Purpose |
|------|--------|---------|
| `UserPromptSubmit` | `capture_task.py` | Logs user prompts to `.current_tasks` |
| `PostToolUse` | `capture_edit.py` | Logs file changes to daily log files |
| `Stop` | `session_summary.py` | Generates markdown summary in `index.md` |
| `SessionStart` | `load_context.py` | Provides recent activity as context |

### Data Storage

All data is stored in `$CLAUDE_PROJECT_DIR/.claude/worklog/`:

```
.claude/worklog/
├── index.md           # Human-readable activity log (newest first)
├── logs/
│   └── YYYY-MM-DD.jsonl  # Daily raw edit logs
├── .current_tasks     # Temporary task buffer (cleared after summary)
└── .processed         # Tracks which entries have been summarized
```

### Index Format

```markdown
# Worklog

Automatically generated activity log.

## 2026-01-21 14:30
**Task**: Add authentication to the API
- **Created**: `src/auth/middleware.py` - Authentication middleware
- **Modified**: `src/api/routes.py` - Added auth decorators

## 2026-01-21 10:15
**Task**: Fix database connection pooling
- **Modified**: `src/db/pool.py` - Increased pool size
```

## Usage

### Automatic (Background)

The plugin works automatically in the background:
- Tasks are captured on every prompt
- File changes are logged on every edit
- Summaries are generated when sessions end
- Context is loaded when sessions start

### Manual Query

Ask Claude about recent activity:
- "What did we work on recently?"
- "Show me the recent changes"
- "Where did we leave off?"
- "What files changed?"

Or use the command:
```
/worklog
```

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `CLAUDE_PROJECT_DIR` | Project root directory (auto-set by Claude Code) |
| `CLAUDE_PLUGIN_ROOT` | Plugin installation directory (auto-set by Claude Code) |

### Customization

- Modify `capture_task.py` to change the minimum prompt length (default: 10 chars)
- Modify `session_summary.py` to adjust summary format
- Modify `load_context.py` to change context limits (default: 5 entries, 1500 chars)

## Requirements

- Python 3.6+
- No external dependencies (stdlib only)

## License

MIT
