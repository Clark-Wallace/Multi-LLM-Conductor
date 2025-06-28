#!/usr/bin/env python3

import json
import os
import sys
import csv
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
import argparse
from colorama import init, Fore, Style, Back
import logging

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('task_manager.log'),
        logging.StreamHandler()
    ]
)


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    
    def __str__(self):
        return self.name


class Task:
    def __init__(self, title: str, description: str = "", priority: Priority = Priority.MEDIUM,
                 due_date: Optional[datetime] = None, tags: Optional[Set[str]] = None):
        self.id = datetime.now().timestamp()
        self.title = self._validate_title(title)
        self.description = description
        self.priority = priority
        self.completed = False
        self.created_at = datetime.now().isoformat()
        self.completed_at = None
        self.due_date = due_date.isoformat() if due_date else None
        self.tags = tags or set()
        self.updated_at = datetime.now().isoformat()
    
    def _validate_title(self, title: str) -> str:
        """Validate task title"""
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        if len(title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")
        return title.strip()
    
    def mark_complete(self):
        self.completed = True
        self.completed_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "completed": self.completed,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "due_date": self.due_date,
            "tags": list(self.tags),
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        due_date = None
        if data.get("due_date"):
            due_date = datetime.fromisoformat(data["due_date"])
        
        task = cls(
            title=data["title"],
            description=data.get("description", ""),
            priority=Priority(data["priority"]),
            due_date=due_date,
            tags=set(data.get("tags", []))
        )
        task.id = data["id"]
        task.completed = data["completed"]
        task.created_at = data["created_at"]
        task.completed_at = data.get("completed_at")
        task.updated_at = data.get("updated_at", task.created_at)
        return task
    
    def update(self, title: Optional[str] = None, description: Optional[str] = None,
               priority: Optional[Priority] = None, due_date: Optional[datetime] = None,
               tags: Optional[Set[str]] = None):
        """Update task properties"""
        if title is not None:
            self.title = self._validate_title(title)
        if description is not None:
            self.description = description
        if priority is not None:
            self.priority = priority
        if due_date is not None:
            self.due_date = due_date.isoformat() if due_date else None
        if tags is not None:
            self.tags = tags
        self.updated_at = datetime.now().isoformat()
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if self.due_date and not self.completed:
            return datetime.fromisoformat(self.due_date) < datetime.now()
        return False
    
    def days_until_due(self) -> Optional[int]:
        """Get days until due date"""
        if self.due_date:
            delta = datetime.fromisoformat(self.due_date) - datetime.now()
            return delta.days
        return None


class TaskManager:
    def __init__(self, data_file: str = "tasks.json"):
        self.data_file = data_file
        self.tasks: List[Task] = []
        self.backup_dir = "backups"
        self._ensure_backup_dir()
        self.load_tasks()
    
    def _ensure_backup_dir(self):
        """Ensure backup directory exists"""
        if not os.path.exists(self.backup_dir):
            try:
                os.makedirs(self.backup_dir)
            except OSError as e:
                logging.error(f"Failed to create backup directory: {e}")
    
    def add_task(self, title: str, description: str = "", priority: Priority = Priority.MEDIUM,
                 due_date: Optional[datetime] = None, tags: Optional[Set[str]] = None) -> Task:
        """Add a new task with validation"""
        try:
            task = Task(title, description, priority, due_date, tags)
            self.tasks.append(task)
            self.save_tasks()
            logging.info(f"Added task: {title}")
            return task
        except ValueError as e:
            logging.error(f"Failed to add task: {e}")
            raise
    
    def list_tasks(self, show_completed: bool = False, filter_text: Optional[str] = None,
                   filter_tags: Optional[Set[str]] = None, filter_priority: Optional[Priority] = None,
                   show_overdue_only: bool = False) -> List[Task]:
        """List tasks with various filters"""
        # Start with all tasks
        filtered_tasks = self.tasks
        
        # Filter by completion status
        if not show_completed:
            filtered_tasks = [t for t in filtered_tasks if not t.completed]
        
        # Filter by search text
        if filter_text:
            pattern = re.compile(re.escape(filter_text), re.IGNORECASE)
            filtered_tasks = [t for t in filtered_tasks 
                            if pattern.search(t.title) or pattern.search(t.description)]
        
        # Filter by tags
        if filter_tags:
            filtered_tasks = [t for t in filtered_tasks if filter_tags.intersection(t.tags)]
        
        # Filter by priority
        if filter_priority:
            filtered_tasks = [t for t in filtered_tasks if t.priority == filter_priority]
        
        # Filter overdue only
        if show_overdue_only:
            filtered_tasks = [t for t in filtered_tasks if t.is_overdue()]
        
        # Sort by: overdue first, then priority (highest first), then due date, then creation time
        def sort_key(task: Task) -> Tuple:
            overdue = 0 if task.is_overdue() else 1
            due_date = task.due_date or "9999-12-31"  # Tasks without due date go last
            return (overdue, -task.priority.value, due_date, task.created_at)
        
        return sorted(filtered_tasks, key=sort_key)
    
    def mark_task_complete(self, task_id: float) -> bool:
        for task in self.tasks:
            if task.id == task_id:
                task.mark_complete()
                self.save_tasks()
                return True
        return False
    
    def delete_task(self, task_id: float) -> bool:
        """Delete a task by ID"""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                deleted_task = self.tasks.pop(i)
                self.save_tasks()
                logging.info(f"Deleted task: {deleted_task.title}")
                return True
        return False
    
    def edit_task(self, task_id: float, **kwargs) -> bool:
        """Edit a task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                try:
                    task.update(**kwargs)
                    self.save_tasks()
                    logging.info(f"Updated task: {task.title}")
                    return True
                except ValueError as e:
                    logging.error(f"Failed to update task: {e}")
                    raise
        return False
    
    def get_task_by_id(self, task_id: float) -> Optional[Task]:
        """Get a task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def export_to_csv(self, filename: str):
        """Export tasks to CSV file"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'title', 'description', 'priority', 'status', 'created_at', 
                    'due_date', 'tags', 'completed_at'
                ])
                writer.writeheader()
                for task in self.tasks:
                    writer.writerow({
                        'title': task.title,
                        'description': task.description,
                        'priority': str(task.priority),
                        'status': 'Completed' if task.completed else 'Pending',
                        'created_at': task.created_at,
                        'due_date': task.due_date or '',
                        'tags': ', '.join(task.tags),
                        'completed_at': task.completed_at or ''
                    })
            logging.info(f"Exported tasks to {filename}")
        except IOError as e:
            logging.error(f"Failed to export to CSV: {e}")
            raise
    
    def export_to_json(self, filename: str):
        """Export tasks to JSON file"""
        try:
            data = {
                "exported_at": datetime.now().isoformat(),
                "task_count": len(self.tasks),
                "tasks": [task.to_dict() for task in self.tasks]
            }
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            logging.info(f"Exported tasks to {filename}")
        except IOError as e:
            logging.error(f"Failed to export to JSON: {e}")
            raise
    
    def get_statistics(self) -> Dict:
        """Get task statistics"""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.completed)
        pending = total - completed
        overdue = sum(1 for t in self.tasks if t.is_overdue())
        
        priority_stats = {}
        for priority in Priority:
            priority_stats[str(priority)] = sum(1 for t in self.tasks if t.priority == priority)
        
        # Tasks due in next 7 days
        upcoming = 0
        for task in self.tasks:
            if not task.completed and task.days_until_due() is not None:
                if 0 <= task.days_until_due() <= 7:
                    upcoming += 1
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "overdue": overdue,
            "upcoming": upcoming,
            "completion_rate": f"{(completed/total*100 if total > 0 else 0):.1f}%",
            "by_priority": priority_stats
        }
    
    def save_tasks(self):
        """Save tasks with error handling and backup"""
        try:
            # Create backup before saving
            if os.path.exists(self.data_file):
                backup_file = os.path.join(self.backup_dir, 
                                         f"tasks_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                try:
                    with open(self.data_file, 'r') as src, open(backup_file, 'w') as dst:
                        dst.write(src.read())
                except IOError as e:
                    logging.warning(f"Failed to create backup: {e}")
            
            # Save tasks
            data = {
                "version": "2.0",
                "last_updated": datetime.now().isoformat(),
                "tasks": [task.to_dict() for task in self.tasks]
            }
            
            # Write to temporary file first
            temp_file = f"{self.data_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Atomic rename
            os.replace(temp_file, self.data_file)
            logging.info("Tasks saved successfully")
            
        except Exception as e:
            logging.error(f"Failed to save tasks: {e}")
            raise
    
    def load_tasks(self):
        """Load tasks with error handling"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
                logging.info(f"Loaded {len(self.tasks)} tasks")
            except (json.JSONDecodeError, KeyError) as e:
                logging.error(f"Failed to load tasks: {e}")
                self.tasks = []
                # Try to restore from backup
                self._restore_from_backup()
            except Exception as e:
                logging.error(f"Unexpected error loading tasks: {e}")
                self.tasks = []
        else:
            self.tasks = []
            logging.info("No existing task file found, starting fresh")
    
    def _restore_from_backup(self):
        """Try to restore from the most recent backup"""
        try:
            backups = sorted([f for f in os.listdir(self.backup_dir) if f.endswith('.json')], reverse=True)
            if backups:
                backup_file = os.path.join(self.backup_dir, backups[0])
                with open(backup_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
                logging.info(f"Restored {len(self.tasks)} tasks from backup")
        except Exception as e:
            logging.error(f"Failed to restore from backup: {e}")


def get_priority_color(priority: Priority) -> str:
    colors = {
        Priority.LOW: Fore.BLUE,
        Priority.MEDIUM: Fore.YELLOW,
        Priority.HIGH: Fore.RED,
        Priority.URGENT: Fore.WHITE + Back.RED
    }
    return colors.get(priority, Fore.WHITE)


def format_date(date_str: Optional[str]) -> str:
    """Format ISO date string to readable format"""
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return date_str


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime object"""
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%m/%d/%Y",
        "%m-%d-%Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Try relative dates
    date_str_lower = date_str.lower()
    if date_str_lower == "today":
        return datetime.now().replace(hour=23, minute=59, second=59)
    elif date_str_lower == "tomorrow":
        return (datetime.now() + timedelta(days=1)).replace(hour=23, minute=59, second=59)
    elif date_str_lower.startswith("in "):
        parts = date_str_lower.split()
        if len(parts) >= 3 and parts[2] in ["days", "day"]:
            try:
                days = int(parts[1])
                return (datetime.now() + timedelta(days=days)).replace(hour=23, minute=59, second=59)
            except ValueError:
                pass
    
    raise ValueError(f"Cannot parse date: {date_str}")


def parse_tags(tag_string: str) -> Set[str]:
    """Parse comma-separated tags"""
    if not tag_string:
        return set()
    return {tag.strip() for tag in tag_string.split(",") if tag.strip()}


def print_task(task: Task, index: int):
    priority_color = get_priority_color(task.priority)
    status_icon = "✓" if task.completed else "○"
    status_color = Fore.GREEN if task.completed else Fore.WHITE
    
    # Check if overdue
    overdue_marker = ""
    if task.is_overdue():
        overdue_marker = f" {Back.RED}{Fore.WHITE}OVERDUE{Style.RESET_ALL}"
    
    print(f"{Fore.CYAN}{index}. {status_color}{status_icon} "
          f"{Fore.WHITE}{task.title} "
          f"{priority_color}[{task.priority}]{Style.RESET_ALL}"
          f"{overdue_marker}")
    
    if task.description:
        print(f"   {Fore.LIGHTBLACK_EX}{task.description}{Style.RESET_ALL}")
    
    # Tags
    if task.tags:
        tags_str = ", ".join(sorted(task.tags))
        print(f"   {Fore.MAGENTA}Tags: {tags_str}{Style.RESET_ALL}")
    
    # Dates
    created = format_date(task.created_at)
    print(f"   {Fore.LIGHTBLACK_EX}Created: {created}{Style.RESET_ALL}")
    
    if task.due_date:
        due = format_date(task.due_date)
        days_until = task.days_until_due()
        if days_until is not None:
            if days_until < 0:
                due_info = f"{due} ({-days_until} days overdue)"
            elif days_until == 0:
                due_info = f"{due} (Due today!)"
            elif days_until == 1:
                due_info = f"{due} (Due tomorrow)"
            else:
                due_info = f"{due} ({days_until} days remaining)"
        else:
            due_info = due
        
        due_color = Fore.RED if task.is_overdue() else Fore.YELLOW
        print(f"   {due_color}Due: {due_info}{Style.RESET_ALL}")
    
    if task.completed and task.completed_at:
        completed = format_date(task.completed_at)
        print(f"   {Fore.GREEN}Completed: {completed}{Style.RESET_ALL}")
    
    print()


def print_statistics(stats: Dict):
    """Print task statistics"""
    print(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}TASK STATISTICS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}\n")
    
    print(f"Total Tasks: {Fore.WHITE}{stats['total']}{Style.RESET_ALL}")
    print(f"Completed: {Fore.GREEN}{stats['completed']}{Style.RESET_ALL}")
    print(f"Pending: {Fore.YELLOW}{stats['pending']}{Style.RESET_ALL}")
    print(f"Overdue: {Fore.RED}{stats['overdue']}{Style.RESET_ALL}")
    print(f"Due in next 7 days: {Fore.MAGENTA}{stats['upcoming']}{Style.RESET_ALL}")
    print(f"Completion Rate: {Fore.CYAN}{stats['completion_rate']}{Style.RESET_ALL}")
    
    print(f"\n{Fore.WHITE}Tasks by Priority:{Style.RESET_ALL}")
    for priority, count in stats['by_priority'].items():
        color = get_priority_color(Priority[priority])
        print(f"  {color}{priority}: {count}{Style.RESET_ALL}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Task Management CLI Tool - A robust task manager with advanced features",
        epilog="Examples:\n"
               "  %(prog)s add 'Write report' -d 'Quarterly sales report' -p high --due tomorrow\n"
               "  %(prog)s list --filter 'report' --priority high\n"
               "  %(prog)s edit 1 --title 'Updated title' --due 'in 3 days'\n"
               "  %(prog)s stats\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add task command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument("-d", "--description", default="", help="Task description")
    add_parser.add_argument("-p", "--priority", 
                           choices=["low", "medium", "high", "urgent"],
                           default="medium", 
                           help="Task priority (default: medium)")
    add_parser.add_argument("--due", help="Due date (e.g., 'tomorrow', '2024-12-31', 'in 7 days')")
    add_parser.add_argument("-t", "--tags", help="Comma-separated tags")
    
    # List tasks command
    list_parser = subparsers.add_parser("list", help="List tasks with filters")
    list_parser.add_argument("-a", "--all", action="store_true", 
                            help="Show completed tasks as well")
    list_parser.add_argument("-f", "--filter", help="Filter tasks by text search")
    list_parser.add_argument("-t", "--tags", help="Filter by tags (comma-separated)")
    list_parser.add_argument("-p", "--priority", 
                           choices=["low", "medium", "high", "urgent"],
                           help="Filter by priority")
    list_parser.add_argument("--overdue", action="store_true", help="Show only overdue tasks")
    
    # Complete task command
    complete_parser = subparsers.add_parser("complete", help="Mark task as complete")
    complete_parser.add_argument("index", type=int, help="Task index from list")
    
    # Delete task command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("index", type=int, help="Task index from list")
    
    # Edit task command
    edit_parser = subparsers.add_parser("edit", help="Edit an existing task")
    edit_parser.add_argument("index", type=int, help="Task index from list")
    edit_parser.add_argument("--title", help="New task title")
    edit_parser.add_argument("-d", "--description", help="New task description")
    edit_parser.add_argument("-p", "--priority", 
                           choices=["low", "medium", "high", "urgent"],
                           help="New task priority")
    edit_parser.add_argument("--due", help="New due date")
    edit_parser.add_argument("-t", "--tags", help="New tags (comma-separated)")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export tasks to file")
    export_parser.add_argument("filename", help="Output filename")
    export_parser.add_argument("-f", "--format", choices=["csv", "json"], 
                              default="csv", help="Export format (default: csv)")
    
    # Statistics command
    stats_parser = subparsers.add_parser("stats", help="Show task statistics")
    
    # Search command (alias for list with filter)
    search_parser = subparsers.add_parser("search", help="Search tasks by text")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("-a", "--all", action="store_true", 
                              help="Search in completed tasks as well")
    
    args = parser.parse_args()
    
    # Initialize task manager
    try:
        manager = TaskManager()
    except Exception as e:
        print(f"{Fore.RED}✗ Failed to initialize task manager: {e}{Style.RESET_ALL}")
        sys.exit(1)
    
    try:
        if args.command == "add":
            priority_map = {
                "low": Priority.LOW,
                "medium": Priority.MEDIUM,
                "high": Priority.HIGH,
                "urgent": Priority.URGENT
            }
            priority = priority_map[args.priority.lower()]
            
            # Parse due date if provided
            due_date = None
            if args.due:
                try:
                    due_date = parse_date(args.due)
                except ValueError as e:
                    print(f"{Fore.RED}✗ Invalid due date: {e}{Style.RESET_ALL}")
                    sys.exit(1)
            
            # Parse tags
            tags = parse_tags(args.tags) if args.tags else None
            
            task = manager.add_task(args.title, args.description, priority, due_date, tags)
            print(f"{Fore.GREEN}✓ Task added successfully!{Style.RESET_ALL}")
            print_task(task, 1)
        
        elif args.command == "list" or args.command == "search":
            # Handle search as an alias for list with filter
            if args.command == "search":
                filter_text = args.query
                show_all = args.all
            else:
                filter_text = args.filter
                show_all = args.all
            
            # Parse filters
            filter_tags = parse_tags(args.tags) if hasattr(args, 'tags') and args.tags else None
            filter_priority = None
            if hasattr(args, 'priority') and args.priority:
                priority_map = {
                    "low": Priority.LOW,
                    "medium": Priority.MEDIUM,
                    "high": Priority.HIGH,
                    "urgent": Priority.URGENT
                }
                filter_priority = priority_map[args.priority.lower()]
            
            show_overdue = hasattr(args, 'overdue') and args.overdue
            
            tasks = manager.list_tasks(
                show_completed=show_all,
                filter_text=filter_text,
                filter_tags=filter_tags,
                filter_priority=filter_priority,
                show_overdue_only=show_overdue
            )
            
            if not tasks:
                print(f"{Fore.YELLOW}No tasks found matching your criteria.{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
                if filter_text or filter_tags or filter_priority or show_overdue:
                    print(f"{Fore.WHITE}FILTERED TASK LIST{Style.RESET_ALL}")
                else:
                    print(f"{Fore.WHITE}TASK LIST{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}\n")
                
                for i, task in enumerate(tasks, 1):
                    print_task(task, i)
        
        elif args.command == "complete":
            tasks = manager.list_tasks(show_completed=False)
            
            if 0 < args.index <= len(tasks):
                task = tasks[args.index - 1]
                if manager.mark_task_complete(task.id):
                    print(f"{Fore.GREEN}✓ Task marked as complete!{Style.RESET_ALL}")
                    print_task(task, args.index)
                else:
                    print(f"{Fore.RED}✗ Failed to mark task as complete.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✗ Invalid task index. Please run 'list' to see available tasks.{Style.RESET_ALL}")
        
        elif args.command == "delete":
            tasks = manager.list_tasks(show_completed=True)
            
            if 0 < args.index <= len(tasks):
                task = tasks[args.index - 1]
                # Confirm deletion
                confirm = input(f"Are you sure you want to delete '{task.title}'? (y/N): ")
                if confirm.lower() == 'y':
                    if manager.delete_task(task.id):
                        print(f"{Fore.GREEN}✓ Task deleted successfully!{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}✗ Failed to delete task.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Deletion cancelled.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✗ Invalid task index. Please run 'list --all' to see all tasks.{Style.RESET_ALL}")
        
        elif args.command == "edit":
            tasks = manager.list_tasks(show_completed=True)
            
            if 0 < args.index <= len(tasks):
                task = tasks[args.index - 1]
                
                # Prepare update kwargs
                update_kwargs = {}
                
                if args.title:
                    update_kwargs['title'] = args.title
                
                if args.description is not None:
                    update_kwargs['description'] = args.description
                
                if args.priority:
                    priority_map = {
                        "low": Priority.LOW,
                        "medium": Priority.MEDIUM,
                        "high": Priority.HIGH,
                        "urgent": Priority.URGENT
                    }
                    update_kwargs['priority'] = priority_map[args.priority.lower()]
                
                if args.due is not None:
                    if args.due.lower() == 'none' or args.due.lower() == 'clear':
                        update_kwargs['due_date'] = None
                    else:
                        try:
                            update_kwargs['due_date'] = parse_date(args.due)
                        except ValueError as e:
                            print(f"{Fore.RED}✗ Invalid due date: {e}{Style.RESET_ALL}")
                            sys.exit(1)
                
                if args.tags is not None:
                    update_kwargs['tags'] = parse_tags(args.tags)
                
                if update_kwargs:
                    if manager.edit_task(task.id, **update_kwargs):
                        print(f"{Fore.GREEN}✓ Task updated successfully!{Style.RESET_ALL}")
                        # Get updated task and display it
                        updated_task = manager.get_task_by_id(task.id)
                        if updated_task:
                            print_task(updated_task, args.index)
                    else:
                        print(f"{Fore.RED}✗ Failed to update task.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}No changes specified.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✗ Invalid task index. Please run 'list --all' to see all tasks.{Style.RESET_ALL}")
        
        elif args.command == "export":
            if args.format == "csv":
                manager.export_to_csv(args.filename)
                print(f"{Fore.GREEN}✓ Tasks exported to {args.filename}{Style.RESET_ALL}")
            else:
                manager.export_to_json(args.filename)
                print(f"{Fore.GREEN}✓ Tasks exported to {args.filename}{Style.RESET_ALL}")
        
        elif args.command == "stats":
            stats = manager.get_statistics()
            print_statistics(stats)
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}✗ An error occurred: {e}{Style.RESET_ALL}")
        logging.error(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()