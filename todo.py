#!/usr/bin/env python3
import argparse
import os
import re
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import sys
import tty
import termios
import select

# Check if terminal supports colors
NO_COLOR = os.environ.get('NO_COLOR') is not None or not sys.stdout.isatty()


class TodoItem:
    def __init__(self, id: int, task: str, priority: str = 'medium', 
                 tags: List[str] = None, due_date: Optional[date] = None,
                 created_at: datetime = None, completed_at: Optional[datetime] = None):
        self.id = id
        self.task = task
        self.priority = priority
        self.tags = tags or []
        self.due_date = due_date
        self.created_at = created_at or datetime.now()
        self.completed_at = completed_at
        
    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None
        
    def complete(self):
        self.completed_at = datetime.now()
        
    def to_markdown(self) -> str:
        checkbox = "[x]" if self.is_completed else "[ ]"
        lines = [f"### {checkbox} [ID: {self.id}] {self.task}"]
        lines.append(f"- Priority: {self.priority}")
        if self.tags:
            lines.append(f"- Tags: {', '.join(self.tags)}")
        if self.due_date:
            lines.append(f"- Due: {self.due_date}")
        if self.completed_at:
            lines.append(f"- Completed: {self.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"- Created: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        return '\n'.join(lines)


class TodoManager:
    def __init__(self, todo_dir: Path = None):
        self.todo_dir = todo_dir or Path.home() / '.todo'
        self.todo_file = self.todo_dir / 'todos.md'
        self.todos: List[TodoItem] = []
        self._ensure_dir()
        self._load_todos()
        
    def _ensure_dir(self):
        self.todo_dir.mkdir(exist_ok=True)
        if not self.todo_file.exists():
            self.todo_file.write_text("# TODOs\n\n")
            
    def _get_next_id(self) -> int:
        if not self.todos:
            return 1
        return max(todo.id for todo in self.todos) + 1
        
    def _load_todos(self):
        content = self.todo_file.read_text()
        self.todos = []
        
        # Parse markdown content
        todo_blocks = re.findall(r'### \[([ x])\] \[ID: (\d+)\] (.+?)(?=\n### |\n## |\Z)', 
                                content, re.DOTALL)
        
        for completed, id_str, block in todo_blocks:
            lines = block.strip().split('\n')
            task = lines[0]
            
            # Parse attributes
            priority = 'medium'
            tags = []
            due_date = None
            created_at = datetime.now()
            completed_at = None
            
            for line in lines[1:]:
                if line.startswith('- Priority: '):
                    priority = line.replace('- Priority: ', '').strip()
                elif line.startswith('- Tags: '):
                    tags = [t.strip() for t in line.replace('- Tags: ', '').split(',')]
                elif line.startswith('- Due: '):
                    due_str = line.replace('- Due: ', '').strip()
                    due_date = datetime.strptime(due_str, '%Y-%m-%d').date()
                elif line.startswith('- Created: '):
                    created_str = line.replace('- Created: ', '').strip()
                    created_at = datetime.strptime(created_str, '%Y-%m-%d %H:%M:%S')
                elif line.startswith('- Completed: '):
                    completed_str = line.replace('- Completed: ', '').strip()
                    completed_at = datetime.strptime(completed_str, '%Y-%m-%d %H:%M:%S')
                    
            todo = TodoItem(
                id=int(id_str),
                task=task,
                priority=priority,
                tags=tags,
                due_date=due_date,
                created_at=created_at,
                completed_at=completed_at
            )
            self.todos.append(todo)
            
    def _save_todos(self):
        # Group todos by date
        todos_by_date: Dict[str, List[TodoItem]] = {}
        
        for todo in sorted(self.todos, key=lambda t: t.created_at, reverse=True):
            date_key = todo.created_at.strftime('%Y-%m-%d')
            if date_key not in todos_by_date:
                todos_by_date[date_key] = []
            todos_by_date[date_key].append(todo)
            
        # Build markdown content
        lines = ["# TODOs\n"]
        
        for date_key in sorted(todos_by_date.keys(), reverse=True):
            lines.append(f"## {date_key}\n")
            for todo in todos_by_date[date_key]:
                lines.append(todo.to_markdown())
                lines.append("")
                
        self.todo_file.write_text('\n'.join(lines))
        
    def add_todo(self, task: str, priority: str = 'medium', 
                 tags: List[str] = None, due_date: Optional[date] = None) -> TodoItem:
        todo = TodoItem(
            id=self._get_next_id(),
            task=task,
            priority=priority,
            tags=tags,
            due_date=due_date
        )
        self.todos.append(todo)
        self._save_todos()
        return todo
        
    def list_todos(self, show_completed: bool = False, filter_tag: Optional[str] = None) -> List[TodoItem]:
        todos = self.todos
        
        if not show_completed:
            todos = [t for t in todos if not t.is_completed]
            
        if filter_tag:
            todos = [t for t in todos if filter_tag in t.tags]
            
        return sorted(todos, key=lambda t: (t.is_completed, t.priority == 'low', 
                                           t.priority == 'medium', t.created_at))
        
    def complete_todo(self, todo_id: int) -> bool:
        for todo in self.todos:
            if todo.id == todo_id and not todo.is_completed:
                todo.complete()
                self._save_todos()
                return True
        return False
        
    def delete_todo(self, todo_id: int) -> bool:
        original_len = len(self.todos)
        self.todos = [t for t in self.todos if t.id != todo_id]
        if len(self.todos) < original_len:
            self._save_todos()
            return True
        return False
        
    def edit_todo(self, todo_id: int, new_task: str) -> bool:
        for todo in self.todos:
            if todo.id == todo_id:
                todo.task = new_task
                self._save_todos()
                return True
        return False


def parse_date(date_str: str) -> Optional[date]:
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None


def format_todo_line(todo: TodoItem, include_id: bool = True) -> str:
    status = "✓" if todo.is_completed else "○"
    priority_symbol = {"high": "!", "medium": "·", "low": " "}[todo.priority]
    
    if include_id:
        line = f"{status} [{todo.id:3d}] {priority_symbol} {todo.task}"
    else:
        line = f"{status} {priority_symbol} {todo.task}"
    
    if todo.tags:
        line += f" [{', '.join(todo.tags)}]"
        
    if todo.due_date:
        days_until = (todo.due_date - date.today()).days
        if days_until < 0:
            line += f" (OVERDUE by {-days_until} days)"
        elif days_until == 0:
            line += " (DUE TODAY)"
        elif days_until <= 3:
            line += f" (Due in {days_until} days)"
        else:
            line += f" (Due: {todo.due_date})"
            
    return line


def format_todo_display(todo: TodoItem) -> str:
    """Format todo for display - compact single line"""
    # Status
    if todo.is_completed:
        status = "✓"
    else:
        status = " "
    
    # Color codes (disabled if NO_COLOR)
    if NO_COLOR:
        priority_colors = {"high": "", "medium": "", "low": ""}
        reset_color = ""
        cyan_color = ""
        gray_color = ""
        red_color = ""
        yellow_color = ""
    else:
        priority_colors = {
            "high": "\033[91m",    # Red
            "medium": "\033[93m",  # Yellow  
            "low": "\033[90m"      # Gray
        }
        reset_color = "\033[0m"
        cyan_color = "\033[96m"
        gray_color = "\033[90m"
        red_color = "\033[91m"
        yellow_color = "\033[93m"
    
    # Priority prefix
    priority_prefix = {"high": "! ", "medium": "  ", "low": "  "}[todo.priority]
    priority_color = priority_colors[todo.priority]
    
    # Task name with priority color
    task_display = f"{priority_color}{todo.task}{reset_color}"
    
    # Tags (compact)
    tag_display = ""
    if todo.tags:
        tag_display = f" {gray_color}[{','.join(todo.tags)}]{reset_color}"
    
    # Date display (only most important)
    date_display = ""
    if todo.due_date:
        days_until = (todo.due_date - date.today()).days
        if days_until < 0:
            date_display = f" {red_color}!{-days_until}d{reset_color}"
        elif days_until == 0:
            date_display = f" {red_color}!today{reset_color}"
        elif days_until == 1:
            date_display = f" {yellow_color}→1d{reset_color}"
        elif days_until <= 7:
            date_display = f" {yellow_color}→{days_until}d{reset_color}"
        else:
            date_display = f" {gray_color}{todo.due_date.strftime('%-m/%-d')}{reset_color}"
    elif not todo.is_completed:
        # Show age for tasks without due date
        created_days = (date.today() - todo.created_at.date()).days
        if created_days > 7:
            date_display = f" {gray_color}{created_days}d{reset_color}"
    
    # Combine all parts
    line = f"{status} {priority_prefix}{task_display}{tag_display}{date_display}"
    
    return line


def print_todo(todo: TodoItem):
    print(format_todo_display(todo))


def print_todos_simple(todos: List[TodoItem]):
    """Print todos in simple list format"""
    if not todos:
        print("No todos found.")
        return
    
    # Simple list - just print in order they were loaded
    for todo in todos:
        print(format_todo_display(todo))


def print_todos_sorted(todos: List[TodoItem], sort_by: str = None, group: bool = False):
    """Print todos with sorting and optional grouping"""
    if not todos:
        print("No todos found.")
        return
    
    # Apply sorting
    if sort_by == 'due':
        # Sort by due date (tasks without due date at the end)
        sorted_todos = sorted(todos, key=lambda t: (
            t.is_completed,
            t.due_date is None,
            t.due_date or date.max
        ))
    elif sort_by == 'priority':
        # Sort by priority
        sorted_todos = sorted(todos, key=lambda t: (
            t.is_completed,
            0 if t.priority == "high" else (1 if t.priority == "medium" else 2),
            t.created_at
        ))
    elif sort_by == 'created':
        # Sort by creation date (newest first)
        sorted_todos = sorted(todos, key=lambda t: (
            t.is_completed,
            -t.created_at.timestamp()
        ))
    elif sort_by == 'age':
        # Sort by age (oldest first)
        sorted_todos = sorted(todos, key=lambda t: (
            t.is_completed,
            t.created_at
        ))
    else:
        # Default: no special sorting
        sorted_todos = todos
    
    # Print with optional grouping
    if group:
        # Separate by completion status and priority
        active = [t for t in sorted_todos if not t.is_completed]
        completed = [t for t in sorted_todos if t.is_completed]
        
        # Group active by priority
        high = [t for t in active if t.priority == "high"]
        medium = [t for t in active if t.priority == "medium"]
        low = [t for t in active if t.priority == "low"]
        
        # Colors
        if NO_COLOR:
            red_color = yellow_color = gray_color = reset_color = ""
        else:
            red_color = "\033[91m"
            yellow_color = "\033[93m"
            gray_color = "\033[90m"
            reset_color = "\033[0m"
        
        # Print grouped
        if high:
            print(f"\n{red_color}HIGH PRIORITY{reset_color}")
            for todo in high:
                print(format_todo_display(todo))
        
        if medium:
            print(f"\n{yellow_color}MEDIUM PRIORITY{reset_color}")
            for todo in medium:
                print(format_todo_display(todo))
        
        if low:
            print(f"\n{gray_color}LOW PRIORITY{reset_color}")
            for todo in low:
                print(format_todo_display(todo))
        
        if completed:
            print(f"\n{gray_color}COMPLETED{reset_color}")
            for todo in completed:
                print(format_todo_display(todo))
    else:
        # Simple sorted list
        for todo in sorted_todos:
            print(format_todo_display(todo))


class InteractiveSelector:
    def __init__(self, todos: List[TodoItem], action: str = "select"):
        self.todos = todos
        self.action = action
        self.selected = 0
        self.start_line = 0  # Track where we started displaying
        
    def get_key(self):
        fd = sys.stdin.fileno()
        try:
            old_settings = termios.tcgetattr(fd)
        except termios.error:
            # Fallback to simple input if terminal doesn't support raw mode
            return None
            
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
            if key == '\x1b':  # ESC sequence
                key += sys.stdin.read(2)
            return key
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
    def display_inline(self, initial=False):
        """Display inline selection without clearing screen"""
        # If not initial display, move cursor up to overwrite previous display
        if not initial:
            # Move cursor up by the number of todos + header lines
            print(f'\033[{len(self.todos) + 2}A', end='')
        
        # Header
        action_text = {
            "done": "Mark as completed",
            "delete": "Delete", 
            "edit": "Edit",
            "select": "Select"
        }.get(self.action, self.action)
        
        # Colors
        if NO_COLOR:
            highlight_color = ""
            reset_color = ""
        else:
            highlight_color = "\033[7m"  # Reverse video
            reset_color = "\033[0m"
        
        print(f"\n{action_text}: (use ↑/↓ or j/k to select, Enter to confirm, q to cancel)")
        
        # Show todos
        for i, todo in enumerate(self.todos):
            if i == self.selected:
                # Highlight selected item
                print(f"{highlight_color} ▶ {format_todo_display(todo)} {reset_color}")
            else:
                print(f"   {format_todo_display(todo)}")
        
        # Clear any remaining lines from previous display
        print('\033[K', end='')  # Clear to end of line
                
    def run_fallback(self) -> Optional[TodoItem]:
        # Fallback mode for environments that don't support raw terminal input
        action_text = {
            "done": "Mark as completed",
            "delete": "Delete",
            "edit": "Edit",
            "select": "Select"
        }.get(self.action, self.action)
        
        print(f"\n{action_text}:")
        
        for i, todo in enumerate(self.todos):
            print(f"{i+1}. {format_todo_display(todo)}")
            
        print(f"\nEnter number (1-{len(self.todos)}) or 'q' to quit: ", end='')
        
        try:
            choice = input().strip()
            if choice.lower() == 'q':
                return None
            num = int(choice)
            if 1 <= num <= len(self.todos):
                return self.todos[num - 1]
            else:
                print("Invalid number")
                return None
        except (ValueError, KeyboardInterrupt):
            return None
            
    def run(self) -> Optional[TodoItem]:
        if not self.todos:
            print("No todos available.")
            return None
            
        # Check if we can use interactive mode
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            use_interactive = True
        except:
            use_interactive = False
            
        if not use_interactive:
            # Fallback to number selection
            return self.run_fallback()
            
        # Interactive mode with inline display
        first_display = True
        while True:
            self.display_inline(initial=first_display)
            first_display = False
            key = self.get_key()
            
            if key == '\x1b[A' or key == 'k':  # Up arrow or k
                self.selected = max(0, self.selected - 1)
            elif key == '\x1b[B' or key == 'j':  # Down arrow or j
                self.selected = min(len(self.todos) - 1, self.selected + 1)
            elif key == '\r' or key == '\n':  # Enter
                # Move cursor down to after the list
                print(f'\n', end='')
                return self.todos[self.selected]
            elif key == 'q' or key == '\x03':  # q or Ctrl+C
                # Move cursor down to after the list
                print(f'\n', end='')
                return None


def main():
    parser = argparse.ArgumentParser(description='Simple CLI Todo Manager', prog='todo')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', aliases=['a'], help='Add a new todo')
    add_parser.add_argument('task', help='Task description')
    add_parser.add_argument('-p', '--priority', choices=['high', 'medium', 'low'], 
                          default='medium', help='Task priority')
    add_parser.add_argument('-t', '--tags', help='Comma-separated tags')
    add_parser.add_argument('-d', '--due', help='Due date (YYYY-MM-DD)')
    
    # List command
    list_parser = subparsers.add_parser('list', aliases=['l', 'ls'], help='List todos')
    list_parser.add_argument('--show-completed', action='store_true', 
                           help='Show completed todos')
    list_parser.add_argument('--filter-tag', help='Filter by tag')
    list_parser.add_argument('-s', '--sort', choices=['due', 'priority', 'created', 'age'],
                           help='Sort by: due (due date), priority, created (newest first), age (oldest first)')
    list_parser.add_argument('-g', '--group', action='store_true',
                           help='Group by priority')
    
    # Done command
    done_parser = subparsers.add_parser('done', aliases=['d'], help='Mark todo as done')
    done_parser.add_argument('id', type=int, nargs='?', help='Todo ID (optional - use interactive mode if not provided)')
    done_parser.add_argument('-i', '--interactive', action='store_true', help='Interactive selection mode')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', aliases=['del', 'rm'], help='Delete a todo')
    delete_parser.add_argument('id', type=int, nargs='?', help='Todo ID (optional - use interactive mode if not provided)')
    delete_parser.add_argument('-i', '--interactive', action='store_true', help='Interactive selection mode')
    
    # Edit command
    edit_parser = subparsers.add_parser('edit', aliases=['e'], help='Edit a todo')
    edit_parser.add_argument('id', type=int, nargs='?', help='Todo ID (optional - use interactive mode if not provided)')
    edit_parser.add_argument('task', nargs='?', help='New task description')
    edit_parser.add_argument('-i', '--interactive', action='store_true', help='Interactive selection mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    manager = TodoManager()
    
    if args.command in ['add', 'a']:
        tags = [t.strip() for t in args.tags.split(',')] if args.tags else []
        due_date = parse_date(args.due) if args.due else None
        
        if args.due and not due_date:
            print(f"Error: Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
            
        todo = manager.add_todo(args.task, args.priority, tags, due_date)
        print(f"Added todo #{todo.id}: {todo.task}")
        
    elif args.command in ['list', 'l', 'ls']:
        todos = manager.list_todos(args.show_completed, args.filter_tag)
        
        if args.sort or args.group:
            print_todos_sorted(todos, args.sort, args.group)
        else:
            print_todos_simple(todos)
                
    elif args.command in ['done', 'd']:
        if args.interactive or args.id is None:
            todos = manager.list_todos(show_completed=False)
            selector = InteractiveSelector(todos, action="done")
            selected = selector.run()
            if selected:
                if manager.complete_todo(selected.id):
                    print(f"Marked todo #{selected.id} as completed: {selected.task}")
        else:
            if manager.complete_todo(args.id):
                print(f"Marked todo #{args.id} as completed")
            else:
                print(f"Todo #{args.id} not found or already completed")
            
    elif args.command in ['delete', 'del', 'rm']:
        if args.interactive or args.id is None:
            todos = manager.list_todos(show_completed=True)
            selector = InteractiveSelector(todos, action="delete")
            selected = selector.run()
            if selected:
                confirm = input(f"Delete todo '{selected.task}'? (y/N): ")
                if confirm.lower() == 'y':
                    if manager.delete_todo(selected.id):
                        print(f"Deleted todo #{selected.id}: {selected.task}")
                else:
                    print("Deletion cancelled")
        else:
            if manager.delete_todo(args.id):
                print(f"Deleted todo #{args.id}")
            else:
                print(f"Todo #{args.id} not found")
            
    elif args.command in ['edit', 'e']:
        if args.interactive or (args.id is None and args.task is None):
            todos = manager.list_todos(show_completed=True)
            selector = InteractiveSelector(todos, action="edit")
            selected = selector.run()
            if selected:
                new_task = input(f"Current: {selected.task}\nNew task: ")
                if new_task.strip():
                    if manager.edit_todo(selected.id, new_task):
                        print(f"Updated todo #{selected.id}")
                else:
                    print("Edit cancelled")
        elif args.id and args.task:
            if manager.edit_todo(args.id, args.task):
                print(f"Updated todo #{args.id}")
            else:
                print(f"Todo #{args.id} not found")
        else:
            print("Error: Please provide both ID and new task, or use -i for interactive mode")


if __name__ == '__main__':
    main()