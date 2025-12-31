# Knowledge Base Plugin for Claude Code

Persistent knowledge management for Claude Code projects with work-in-progress tracking, checkpoints, and auto-indexing.

## Features

- **Work-in-Progress Tracking**: Save progress between sessions with `/ok:wip`
- **Checkpoints**: Create restore points before risky changes
- **Auto-Indexing**: Code symbols and knowledge automatically indexed
- **Pre-Search Context**: Knowledge surfaced before searches via hooks

## Installation

```bash
# Add marketplace
/plugin marketplace add okkazoo/claude-knowledge-plugin

# Install plugin
/plugin install ok@okkazoo/claude-knowledge-plugin
```

## Commands

| Command | Description |
|---------|-------------|
| `/ok:init` | Initialize knowledge base in current project |
| `/ok:wip` | Save work-in-progress |
| `/ok:wip -f <text>` | Save a fact directly |
| `/ok:wip -list` | List existing journeys |
| `/ok:checkpoint [desc]` | Create restore point |
| `/ok:knowledge` | Show knowledge base status |
| `/ok:knowledge -reset` | Reset knowledge base |

## Hooks

- **session-start**: Injects git status and active journeys on startup
- **pre-search**: Searches indexes before Grep/Glob, surfaces relevant patterns
- **auto-index**: Updates code symbol index after file edits

## Directory Structure

After running `/ok:init`:

```
.claude/knowledge/
├── journey/      # Work-in-progress entries
├── facts/        # Quick facts, gotchas
├── patterns/     # Extracted solutions
├── checkpoints/  # State snapshots
├── versions/     # Version history
├── coderef.json  # Code symbol index
└── knowledge.json # Knowledge index
```

## Quick Start

1. Install the plugin
2. Run `/ok:init` in your project
3. Use `/ok:wip` to save progress as you work
4. Use `/ok:checkpoint` before risky changes

## Authors

- OKKazoo

## License

MIT
