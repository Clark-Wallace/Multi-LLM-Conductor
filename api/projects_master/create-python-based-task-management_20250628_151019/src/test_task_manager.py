#!/usr/bin/env python3

import unittest
import tempfile
import os
import json
import csv
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from task_manager import Task, TaskManager, Priority, parse_date, parse_tags


class TestTask(unittest.TestCase):
    def test_task_creation(self):
        """Test basic task creation"""
        task = Task("Test task", "Description", Priority.HIGH)
        self.assertEqual(task.title, "Test task")
        self.assertEqual(task.description, "Description")
        self.assertEqual(task.priority, Priority.HIGH)
        self.assertFalse(task.completed)
        self.assertIsNotNone(task.id)
        self.assertIsNotNone(task.created_at)
        self.assertIsNone(task.completed_at)
        self.assertEqual(task.tags, set())
    
    def test_task_with_due_date_and_tags(self):
        """Test task creation with due date and tags"""
        due_date = datetime.now() + timedelta(days=7)
        tags = {"work", "urgent"}
        task = Task("Test task", due_date=due_date, tags=tags)
        
        self.assertIsNotNone(task.due_date)
        self.assertEqual(task.tags, tags)
    
    def test_task_validation(self):
        """Test task title validation"""
        # Empty title
        with self.assertRaises(ValueError):
            Task("")
        
        # Whitespace only title
        with self.assertRaises(ValueError):
            Task("   ")
        
        # Too long title
        with self.assertRaises(ValueError):
            Task("x" * 201)
    
    def test_mark_complete(self):
        """Test marking task as complete"""
        task = Task("Test task")
        self.assertFalse(task.completed)
        self.assertIsNone(task.completed_at)
        
        task.mark_complete()
        self.assertTrue(task.completed)
        self.assertIsNotNone(task.completed_at)
    
    def test_is_overdue(self):
        """Test overdue detection"""
        # Task without due date
        task1 = Task("No due date")
        self.assertFalse(task1.is_overdue())
        
        # Task with future due date
        future_date = datetime.now() + timedelta(days=1)
        task2 = Task("Future task", due_date=future_date)
        self.assertFalse(task2.is_overdue())
        
        # Task with past due date
        past_date = datetime.now() - timedelta(days=1)
        task3 = Task("Past task", due_date=past_date)
        self.assertTrue(task3.is_overdue())
        
        # Completed task with past due date
        task4 = Task("Completed past task", due_date=past_date)
        task4.mark_complete()
        self.assertFalse(task4.is_overdue())
    
    def test_days_until_due(self):
        """Test days until due calculation"""
        # No due date
        task1 = Task("No due date")
        self.assertIsNone(task1.days_until_due())
        
        # Due in 7 days
        future_date = datetime.now() + timedelta(days=7)
        task2 = Task("Future task", due_date=future_date)
        days_until = task2.days_until_due()
        self.assertIn(days_until, [6, 7])  # Allow for timing differences
        
        # Overdue by 3 days
        past_date = datetime.now() - timedelta(days=3)
        task3 = Task("Past task", due_date=past_date)
        days_overdue = task3.days_until_due()
        self.assertIn(days_overdue, [-4, -3])  # Allow for timing differences
    
    def test_update_task(self):
        """Test updating task properties"""
        task = Task("Original title", "Original desc", Priority.LOW)
        
        # Update all properties
        new_due_date = datetime.now() + timedelta(days=5)
        new_tags = {"updated", "test"}
        
        task.update(
            title="Updated title",
            description="Updated desc",
            priority=Priority.HIGH,
            due_date=new_due_date,
            tags=new_tags
        )
        
        self.assertEqual(task.title, "Updated title")
        self.assertEqual(task.description, "Updated desc")
        self.assertEqual(task.priority, Priority.HIGH)
        self.assertIsNotNone(task.due_date)
        self.assertEqual(task.tags, new_tags)
        self.assertNotEqual(task.updated_at, task.created_at)
    
    def test_to_dict_from_dict(self):
        """Test serialization and deserialization"""
        due_date = datetime.now() + timedelta(days=5)
        tags = {"tag1", "tag2"}
        task1 = Task("Test task", "Description", Priority.HIGH, due_date, tags)
        
        # Convert to dict
        task_dict = task1.to_dict()
        
        # Create new task from dict
        task2 = Task.from_dict(task_dict)
        
        self.assertEqual(task1.id, task2.id)
        self.assertEqual(task1.title, task2.title)
        self.assertEqual(task1.description, task2.description)
        self.assertEqual(task1.priority, task2.priority)
        self.assertEqual(task1.due_date, task2.due_date)
        self.assertEqual(task1.tags, task2.tags)


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.manager = TaskManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures"""
        try:
            os.unlink(self.temp_file.name)
        except:
            pass
        # Clean up backup directory
        if os.path.exists(self.manager.backup_dir):
            for file in os.listdir(self.manager.backup_dir):
                try:
                    os.unlink(os.path.join(self.manager.backup_dir, file))
                except:
                    pass
            try:
                os.rmdir(self.manager.backup_dir)
            except:
                pass
    
    def test_add_task(self):
        """Test adding tasks"""
        task = self.manager.add_task("Test task", "Description", Priority.HIGH)
        
        self.assertEqual(len(self.manager.tasks), 1)
        self.assertEqual(task.title, "Test task")
        self.assertEqual(task.description, "Description")
        self.assertEqual(task.priority, Priority.HIGH)
        
        # Test validation
        with self.assertRaises(ValueError):
            self.manager.add_task("")
    
    def test_list_tasks_basic(self):
        """Test basic task listing"""
        # Add tasks
        task1 = self.manager.add_task("Task 1", priority=Priority.LOW)
        task2 = self.manager.add_task("Task 2", priority=Priority.HIGH)
        task3 = self.manager.add_task("Task 3", priority=Priority.MEDIUM)
        
        # Mark one as complete
        self.manager.mark_task_complete(task2.id)
        
        # List pending tasks
        pending_tasks = self.manager.list_tasks(show_completed=False)
        self.assertEqual(len(pending_tasks), 2)
        
        # List all tasks
        all_tasks = self.manager.list_tasks(show_completed=True)
        self.assertEqual(len(all_tasks), 3)
    
    def test_list_tasks_with_filters(self):
        """Test task listing with filters"""
        # Add tasks with various properties
        due_date = datetime.now() + timedelta(days=2)
        overdue_date = datetime.now() - timedelta(days=1)
        
        task1 = self.manager.add_task("Report task", "Write report", Priority.HIGH, 
                                     tags={"work", "report"})
        task2 = self.manager.add_task("Meeting task", "Team meeting", Priority.MEDIUM,
                                     due_date=due_date, tags={"work", "meeting"})
        task3 = self.manager.add_task("Overdue task", "Past deadline", Priority.URGENT,
                                     due_date=overdue_date, tags={"urgent"})
        task4 = self.manager.add_task("Personal task", "Buy groceries", Priority.LOW,
                                     tags={"personal"})
        
        # Test text filter
        filtered = self.manager.list_tasks(filter_text="report")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].title, "Report task")
        
        # Test tag filter
        filtered = self.manager.list_tasks(filter_tags={"work"})
        self.assertEqual(len(filtered), 2)
        
        # Test priority filter
        filtered = self.manager.list_tasks(filter_priority=Priority.HIGH)
        self.assertEqual(len(filtered), 1)
        
        # Test overdue filter
        filtered = self.manager.list_tasks(show_overdue_only=True)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].title, "Overdue task")
    
    def test_mark_task_complete(self):
        """Test marking tasks as complete"""
        task = self.manager.add_task("Test task")
        
        # Mark as complete
        result = self.manager.mark_task_complete(task.id)
        self.assertTrue(result)
        self.assertTrue(task.completed)
        self.assertIsNotNone(task.completed_at)
        
        # Try to mark non-existent task
        result = self.manager.mark_task_complete(999999)
        self.assertFalse(result)
    
    def test_delete_task(self):
        """Test deleting tasks"""
        task = self.manager.add_task("Test task")
        task_id = task.id
        
        # Delete task
        result = self.manager.delete_task(task_id)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.tasks), 0)
        
        # Try to delete non-existent task
        result = self.manager.delete_task(task_id)
        self.assertFalse(result)
    
    def test_edit_task(self):
        """Test editing tasks"""
        task = self.manager.add_task("Original title", "Original desc", Priority.LOW)
        
        # Edit task
        result = self.manager.edit_task(
            task.id,
            title="Updated title",
            priority=Priority.HIGH
        )
        self.assertTrue(result)
        
        # Verify changes
        updated_task = self.manager.get_task_by_id(task.id)
        self.assertEqual(updated_task.title, "Updated title")
        self.assertEqual(updated_task.priority, Priority.HIGH)
        self.assertEqual(updated_task.description, "Original desc")  # Unchanged
        
        # Try to edit non-existent task
        result = self.manager.edit_task(999999, title="New title")
        self.assertFalse(result)
    
    def test_save_and_load_tasks(self):
        """Test saving and loading tasks"""
        # Add tasks
        due_date = datetime.now() + timedelta(days=3)
        task1 = self.manager.add_task("Task 1", "Description 1", Priority.HIGH,
                                     due_date=due_date, tags={"tag1", "tag2"})
        task2 = self.manager.add_task("Task 2", "Description 2", Priority.LOW)
        self.manager.mark_task_complete(task2.id)
        
        # Create new manager instance to test loading
        manager2 = TaskManager(self.temp_file.name)
        
        # Verify loaded tasks
        self.assertEqual(len(manager2.tasks), 2)
        
        loaded_task1 = manager2.get_task_by_id(task1.id)
        self.assertEqual(loaded_task1.title, "Task 1")
        self.assertEqual(loaded_task1.priority, Priority.HIGH)
        self.assertEqual(loaded_task1.tags, {"tag1", "tag2"})
        self.assertIsNotNone(loaded_task1.due_date)
        
        loaded_task2 = manager2.get_task_by_id(task2.id)
        self.assertTrue(loaded_task2.completed)
    
    def test_export_to_csv(self):
        """Test CSV export"""
        # Add tasks
        self.manager.add_task("Task 1", "Description 1", Priority.HIGH, tags={"work"})
        self.manager.add_task("Task 2", "Description 2", Priority.LOW)
        
        # Export to CSV
        csv_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        csv_file.close()
        
        try:
            self.manager.export_to_csv(csv_file.name)
            
            # Verify CSV content
            with open(csv_file.name, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[0]['title'], 'Task 1')
                self.assertEqual(rows[0]['priority'], 'HIGH')
                self.assertEqual(rows[0]['tags'], 'work')
        finally:
            os.unlink(csv_file.name)
    
    def test_export_to_json(self):
        """Test JSON export"""
        # Add tasks
        self.manager.add_task("Task 1", "Description 1", Priority.HIGH)
        self.manager.add_task("Task 2", "Description 2", Priority.LOW)
        
        # Export to JSON
        json_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json_file.close()
        
        try:
            self.manager.export_to_json(json_file.name)
            
            # Verify JSON content
            with open(json_file.name, 'r') as f:
                data = json.load(f)
                
                self.assertEqual(data['task_count'], 2)
                self.assertEqual(len(data['tasks']), 2)
                self.assertIn('exported_at', data)
        finally:
            os.unlink(json_file.name)
    
    def test_get_statistics(self):
        """Test statistics generation"""
        # Add various tasks
        overdue_date = datetime.now() - timedelta(days=2)
        upcoming_date = datetime.now() + timedelta(days=3)
        
        task1 = self.manager.add_task("Task 1", priority=Priority.HIGH)
        task2 = self.manager.add_task("Task 2", priority=Priority.LOW, due_date=upcoming_date)
        task3 = self.manager.add_task("Task 3", priority=Priority.URGENT, due_date=overdue_date)
        task4 = self.manager.add_task("Task 4", priority=Priority.MEDIUM)
        
        # Mark one as complete
        self.manager.mark_task_complete(task1.id)
        
        stats = self.manager.get_statistics()
        
        self.assertEqual(stats['total'], 4)
        self.assertEqual(stats['completed'], 1)
        self.assertEqual(stats['pending'], 3)
        self.assertEqual(stats['overdue'], 1)
        self.assertEqual(stats['upcoming'], 1)
        self.assertEqual(stats['by_priority']['HIGH'], 1)
        self.assertEqual(stats['by_priority']['URGENT'], 1)
        self.assertIn('completion_rate', stats)


class TestUtilityFunctions(unittest.TestCase):
    def test_parse_date(self):
        """Test date parsing functionality"""
        # Test various date formats
        formats_to_test = [
            ("2024-12-31", datetime(2024, 12, 31, 0, 0)),
            ("2024-12-31 14:30", datetime(2024, 12, 31, 14, 30)),
            ("31/12/2024", datetime(2024, 12, 31, 0, 0)),
            ("31-12-2024", datetime(2024, 12, 31, 0, 0)),
            ("12/31/2024", datetime(2024, 12, 31, 0, 0)),
            ("12-31-2024", datetime(2024, 12, 31, 0, 0))
        ]
        
        for date_str, expected in formats_to_test:
            with self.subTest(date_str=date_str):
                result = parse_date(date_str)
                self.assertEqual(result.date(), expected.date())
        
        # Test relative dates
        today = datetime.now().date()
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        
        self.assertEqual(parse_date("today").date(), today)
        self.assertEqual(parse_date("tomorrow").date(), tomorrow)
        self.assertEqual(parse_date("in 7 days").date(), 
                        (datetime.now() + timedelta(days=7)).date())
        
        # Test invalid dates
        with self.assertRaises(ValueError):
            parse_date("invalid date")
    
    def test_parse_tags(self):
        """Test tag parsing"""
        # Test various tag formats
        self.assertEqual(parse_tags("tag1, tag2, tag3"), {"tag1", "tag2", "tag3"})
        self.assertEqual(parse_tags("tag1,tag2,tag3"), {"tag1", "tag2", "tag3"})
        self.assertEqual(parse_tags("  tag1  ,  tag2  "), {"tag1", "tag2"})
        self.assertEqual(parse_tags(""), set())
        self.assertEqual(parse_tags("single"), {"single"})


if __name__ == '__main__':
    unittest.main()