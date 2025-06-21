#!/usr/bin/env python3
import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime, date
import sys
import os

# Add parent directory to path to import todo module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from todo import TodoItem, TodoManager


class TestTodoItem(unittest.TestCase):
    def test_todo_creation(self):
        """Test TodoItem creation with various parameters"""
        todo = TodoItem(
            id=1,
            task="Test task",
            priority="high",
            tags=["work", "urgent"],
            due_date=date(2024, 12, 31)
        )
        
        self.assertEqual(todo.id, 1)
        self.assertEqual(todo.task, "Test task")
        self.assertEqual(todo.priority, "high")
        self.assertEqual(todo.tags, ["work", "urgent"])
        self.assertEqual(todo.due_date, date(2024, 12, 31))
        self.assertFalse(todo.is_completed)
        
    def test_todo_completion(self):
        """Test todo completion functionality"""
        todo = TodoItem(1, "Test task")
        self.assertFalse(todo.is_completed)
        self.assertIsNone(todo.completed_at)
        
        todo.complete()
        self.assertTrue(todo.is_completed)
        self.assertIsNotNone(todo.completed_at)
        
    def test_todo_to_dict(self):
        """Test JSON serialization"""
        created_time = datetime(2024, 1, 1, 10, 0, 0)
        due_date = date(2024, 12, 31)
        
        todo = TodoItem(
            id=1,
            task="Test task",
            priority="high",
            tags=["work"],
            due_date=due_date,
            created_at=created_time
        )
        
        data = todo.to_dict()
        expected = {
            'id': 1,
            'task': 'Test task',
            'priority': 'high',
            'tags': ['work'],
            'due_date': '2024-12-31',
            'created_at': '2024-01-01T10:00:00',
            'completed_at': None
        }
        
        self.assertEqual(data, expected)
        
    def test_todo_from_dict(self):
        """Test JSON deserialization"""
        data = {
            'id': 1,
            'task': 'Test task',
            'priority': 'high',
            'tags': ['work'],
            'due_date': '2024-12-31',
            'created_at': '2024-01-01T10:00:00',
            'completed_at': None
        }
        
        todo = TodoItem.from_dict(data)
        
        self.assertEqual(todo.id, 1)
        self.assertEqual(todo.task, 'Test task')
        self.assertEqual(todo.priority, 'high')
        self.assertEqual(todo.tags, ['work'])
        self.assertEqual(todo.due_date, date(2024, 12, 31))
        self.assertEqual(todo.created_at, datetime(2024, 1, 1, 10, 0, 0))
        self.assertIsNone(todo.completed_at)


class TestTodoManager(unittest.TestCase):
    def setUp(self):
        """Set up temporary directory for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.todo_dir = Path(self.temp_dir) / '.todo'
        self.manager = TodoManager(self.todo_dir)
        
    def tearDown(self):
        """Clean up temporary directory"""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_manager_initialization(self):
        """Test TodoManager initialization"""
        self.assertTrue(self.todo_dir.exists())
        self.assertTrue((self.todo_dir / 'todos.json').exists())
        self.assertEqual(len(self.manager.todos), 0)
        
    def test_add_todo(self):
        """Test adding todos"""
        todo = self.manager.add_todo("Test task", "high", ["work"], date(2024, 12, 31))
        
        self.assertEqual(todo.id, 1)
        self.assertEqual(todo.task, "Test task")
        self.assertEqual(len(self.manager.todos), 1)
        
        # Test JSON file was created
        with open(self.todo_dir / 'todos.json', 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['task'], "Test task")
            
    def test_list_todos(self):
        """Test listing todos with filters"""
        # Add test todos
        self.manager.add_todo("Task 1", "high", ["work"])
        self.manager.add_todo("Task 2", "medium", ["personal"])
        self.manager.add_todo("Task 3", "low", ["work", "urgent"])
        
        # Test basic listing
        todos = self.manager.list_todos()
        self.assertEqual(len(todos), 3)
        
        # Test tag filtering
        work_todos = self.manager.list_todos(filter_tag="work")
        self.assertEqual(len(work_todos), 2)
        
        # Test completed filter
        self.manager.complete_todo(1)
        active_todos = self.manager.list_todos(show_completed=False)
        self.assertEqual(len(active_todos), 2)
        
        all_todos = self.manager.list_todos(show_completed=True)
        self.assertEqual(len(all_todos), 3)
        
    def test_complete_todo(self):
        """Test completing todos"""
        todo = self.manager.add_todo("Test task")
        self.assertFalse(todo.is_completed)
        
        result = self.manager.complete_todo(todo.id)
        self.assertTrue(result)
        self.assertTrue(todo.is_completed)
        
        # Test completing non-existent todo
        result = self.manager.complete_todo(999)
        self.assertFalse(result)
        
    def test_delete_todo(self):
        """Test deleting todos"""
        todo = self.manager.add_todo("Test task")
        self.assertEqual(len(self.manager.todos), 1)
        
        result = self.manager.delete_todo(todo.id)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.todos), 0)
        
        # Test deleting non-existent todo
        result = self.manager.delete_todo(999)
        self.assertFalse(result)
        
    def test_edit_todo(self):
        """Test editing todos"""
        todo = self.manager.add_todo("Original task")
        self.assertEqual(todo.task, "Original task")
        
        result = self.manager.edit_todo(todo.id, "Updated task")
        self.assertTrue(result)
        self.assertEqual(todo.task, "Updated task")
        
        # Test editing non-existent todo
        result = self.manager.edit_todo(999, "New task")
        self.assertFalse(result)
        
    def test_persistence(self):
        """Test data persistence across manager instances"""
        # Add todos with first manager
        self.manager.add_todo("Task 1", "high", ["work"])
        self.manager.add_todo("Task 2", "medium", ["personal"])
        
        # Create new manager instance with same directory
        new_manager = TodoManager(self.todo_dir)
        
        # Check that todos were loaded
        self.assertEqual(len(new_manager.todos), 2)
        self.assertEqual(new_manager.todos[0].task, "Task 1")
        self.assertEqual(new_manager.todos[1].task, "Task 2")
        
    def test_next_id_generation(self):
        """Test ID generation"""
        todo1 = self.manager.add_todo("Task 1")
        todo2 = self.manager.add_todo("Task 2")
        
        self.assertEqual(todo1.id, 1)
        self.assertEqual(todo2.id, 2)
        
        # Delete first todo and add new one
        self.manager.delete_todo(1)
        todo3 = self.manager.add_todo("Task 3")
        
        self.assertEqual(todo3.id, 3)  # Should continue incrementing
        
    def test_json_file_corruption(self):
        """Test handling of corrupted JSON file"""
        # Write invalid JSON to file
        json_file = self.todo_dir / 'todos.json'
        json_file.write_text('invalid json content')
        
        # Create new manager - should handle corruption gracefully
        new_manager = TodoManager(self.todo_dir)
        self.assertEqual(len(new_manager.todos), 0)
        
        # Should be able to add todos after corruption
        todo = new_manager.add_todo("Recovery test")
        self.assertEqual(todo.id, 1)


class TestDateParsing(unittest.TestCase):
    def test_parse_date_valid(self):
        """Test valid date parsing"""
        from todo import parse_date
        
        result = parse_date('2024-12-31')
        self.assertEqual(result, date(2024, 12, 31))
        
    def test_parse_date_invalid(self):
        """Test invalid date parsing"""
        from todo import parse_date
        
        result = parse_date('invalid-date')
        self.assertIsNone(result)
        
        result = parse_date('2024-13-01')  # Invalid month
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()