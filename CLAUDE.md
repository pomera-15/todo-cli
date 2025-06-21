# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a CLI-based todo management tool written in Python that stores data in human-readable Markdown format. The application uses only Python standard library (no external dependencies).

## Setup

Run `./setup.sh` to enable the `todo` and `td` commands globally. This will offer three options:
1. Symlink to /usr/local/bin (requires sudo) - creates both `todo` and `td` commands
2. Shell alias (user-specific) - adds both `todo` and `td` aliases
3. Wrapper script with PATH modification - creates both wrapper scripts

## Key Features

- **Inline Selection**: Interactive mode doesn't clear the screen, selections happen inline
- **Compact Display**: Minimal, single-line format for todos
- **Smart Sorting**: Default is simple list, with options for due date, priority, etc.

## Key Commands

```bash
# After setup, you can use either 'todo' or 'td':
todo add "Task description" -p high -t work,urgent -d 2024-12-31
td add "Task description" -p high -t work,urgent -d 2024-12-31

# Short commands work with both:
td a "Task"        # Same as 'todo add'
td l               # Same as 'todo list' (simple display)
td l -s due        # Sort by due date
td l -s priority   # Sort by priority  
td l -g            # Group by priority
td d               # Same as 'todo done' (interactive)
td e               # Same as 'todo edit' (interactive)
td rm              # Same as 'todo delete' (interactive)

# Interactive mode (arrow keys to select):
todo done          # Select with arrow keys, Enter to confirm
todo delete        # Select with arrow keys, Enter to confirm  
todo edit          # Select with arrow keys, Enter to confirm

# Direct ID mode (backwards compatible):
todo done <ID>
todo delete <ID>
todo edit <ID> "New description"

# Without setup:
python3 todo.py <command> [options]
```

## Architecture

### Core Classes

1. **TodoItem** (todo.py:11-41)
   - Data model for individual todos
   - Handles markdown serialization via `to_markdown()`

2. **TodoManager** (todo.py:44-176)
   - CRUD operations and persistence logic
   - Parses and saves to `~/.todo/todos.md`
   - Uses regex to parse markdown format

### Data Storage

Todos are stored in Markdown format at `~/.todo/todos.md`:

```markdown
# TODOs

## YYYY-MM-DD

### [ ] [ID: N] Task description
- Priority: high|medium|low
- Tags: tag1, tag2
- Due: YYYY-MM-DD
- Created: YYYY-MM-DD HH:MM:SS
```

The format is human-editable - users can modify the file directly.

## Development Notes

- Python 3.8+ required (uses type hints)
- No test framework implemented yet (tests/ directory planned)
- The specification.md file contains the original Japanese requirements
- Future enhancements planned: subtasks, recurring tasks, archiving, statistics