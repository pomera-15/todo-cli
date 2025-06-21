# Todo CLI

A simple and efficient command-line todo management tool written in Python.

## Features

- 📝 Add, list, complete, delete, and edit todos
- 🎯 Priority levels (high, medium, low)
- 🏷️ Tag support for categorization
- 📅 Due date management with smart notifications
- 🎨 Color-coded output (can be disabled with NO_COLOR=1)
- ⌨️ Interactive selection with arrow keys
- 📄 JSON storage format for reliable data handling
- 🚀 No external dependencies - uses only Python standard library

## Installation

### Quick Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/todo-cli.git
cd todo-cli
```

2. Run the setup script:
```bash
./setup.sh
```

This will give you three options:
- Symlink to `/usr/local/bin` (requires sudo)
- Shell alias (user-specific)
- Add to PATH

### Manual Setup

If you prefer manual setup, you can create an alias:

```bash
alias todo='python3 /path/to/todo-cli/todo.py'
alias td='python3 /path/to/todo-cli/todo.py'
```

## Usage

### Basic Commands

```bash
# Add a new todo
td a "Write documentation" -p high -t work -d 2024-12-31

# List todos
td l                    # Simple list
td l -s due            # Sort by due date
td l -s priority -g    # Sort by priority and group
td l --show-completed  # Include completed todos

# Complete a todo (interactive selection)
td d

# Delete a todo (interactive selection)
td rm

# Edit a todo (interactive selection)
td e
```

### Command Reference

- **Add**: `todo add "task" [-p high|medium|low] [-t tag1,tag2] [-d YYYY-MM-DD]`
- **List**: `todo list [--show-completed] [--filter-tag TAG] [-s due|priority|created|age] [-g]`
- **Complete**: `todo done [ID]` (interactive if ID not provided)
- **Delete**: `todo delete [ID]` (interactive if ID not provided)
- **Edit**: `todo edit [ID] [new_text]` (interactive if ID not provided)

### Short Aliases

- `a` → add
- `l`, `ls` → list
- `d` → done
- `e` → edit
- `rm`, `del` → delete

## Data Storage

Todos are stored in `~/.todo/todos.json` in JSON format:

```json
[
  {
    "id": 1,
    "task": "Task description",
    "priority": "high",
    "tags": ["work", "urgent"],
    "due_date": "2024-12-31",
    "created_at": "2024-12-20T10:30:00.000000",
    "completed_at": null
  }
]
```

The JSON format ensures reliable data parsing and allows for easy backup/restore.

## Interactive Mode

When using `done`, `delete`, or `edit` without an ID:
- Use ↑/↓ or j/k to navigate
- Press Enter to select
- Press q to cancel

## Requirements

- Python 3.8 or higher
- No external dependencies

## Testing

Run the test suite to verify functionality:

```bash
python3 -m unittest tests.test_todo -v
```

Tests cover:
- TodoItem creation, completion, and JSON serialization
- TodoManager CRUD operations and persistence
- Data filtering and sorting
- Error handling and edge cases

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.