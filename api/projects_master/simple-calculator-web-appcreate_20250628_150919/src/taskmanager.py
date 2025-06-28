#!/usr/bin/env python3
"""
Task Management CLI Tool
A simple command-line task manager with priorities, JSON persistence, and colorful output.
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
import argparse
from enum import Enum
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import print as rprint
from rich.panel import Panel
from rich.text import Text

console = Console()

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    
    @classmethod
    def from_string(cls, priority_str: str) -> 'Priority':
        priority_map = {
            'low': cls.LOW,
            'medium': cls.MEDIUM,
            'high': cls.HIGH
        }
        return priority_map.get(priority_str.lower(), cls.MEDIUM)
    
    def to_color(self) -> str:
        color_map = {
            Priority.LOW: "green",
            Priority.MEDIUM: "yellow",
            Priority.HIGH: "red"
        }
        return color_map.get(self, "white")

class Task:
    def __init__(self, title: str, priority: Priority, created_at: Optional[str] = None, completed: bool = False):
        self.title = title
        self.priority = priority
        self.created_at = created_at or datetime.now().isoformat()
        self.completed = completed
    
    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'priority': self.priority.name,
            'created_at': self.created_at,
            'completed': self.completed
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        return cls(
            title=data['title'],
            priority=Priority[data['priority']],
            created_at=data['created_at'],
            completed=data.get('completed', False)
        )

class TaskManager:
    def __init__(self, filename: str = "tasks.json"):
        self.filename = filename
        self.tasks: List[Task] = []
        self.load_tasks()
    
    def load_tasks(self) -> None:
        """Load tasks from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(task_data) for task_data in data]
            except (json.JSONDecodeError, KeyError) as e:
                console.print(f"[red]Error loading tasks: {e}[/red]")
                self.tasks = []
    
    def save_tasks(self) -> None:
        """Save tasks to JSON file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump([task.to_dict() for task in self.tasks], f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving tasks: {e}[/red]")
    
    def add_task(self, title: str, priority: str) -> None:
        """Add a new task"""
        task = Task(title, Priority.from_string(priority))
        self.tasks.append(task)
        self.save_tasks()
        console.print(f"[green]✓ Task added successfully![/green]")
    
    def list_tasks(self, show_completed: bool = False) -> None:
        """List all tasks sorted by priority"""
        if not self.tasks:
            console.print("[yellow]No tasks found. Add your first task![/yellow]")
            return
        
        # Filter tasks
        tasks_to_show = self.tasks if show_completed else [t for t in self.tasks if not t.completed]
        
        if not tasks_to_show:
            console.print("[yellow]No pending tasks. Great job![/yellow]")
            return
        
        # Sort by priority (high to low) and completion status
        sorted_tasks = sorted(tasks_to_show, 
                            key=lambda t: (-t.priority.value, t.completed, t.created_at))
        
        # Create table
        table = Table(title="Task List", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Task", style="white")
        table.add_column("Priority", justify="center", width=10)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Created", width=20)
        
        for idx, task in enumerate(sorted_tasks, 1):
            priority_color = task.priority.to_color()
            status = "[green]✓ Done[/green]" if task.completed else "[yellow]⏳ Pending[/yellow]"
            created_date = datetime.fromisoformat(task.created_at).strftime("%Y-%m-%d %H:%M")
            
            table.add_row(
                str(idx),
                Text(task.title, style="dim" if task.completed else "normal"),
                f"[{priority_color}]{task.priority.name}[/{priority_color}]",
                status,
                created_date
            )
        
        console.print(table)
    
    def mark_complete(self, task_id: int) -> None:
        """Mark a task as complete"""
        pending_tasks = [t for t in self.tasks if not t.completed]
        
        if not pending_tasks:
            console.print("[yellow]No pending tasks to complete![/yellow]")
            return
        
        if 1 <= task_id <= len(pending_tasks):
            task = pending_tasks[task_id - 1]
            task.completed = True
            self.save_tasks()
            console.print(f"[green]✓ Task '{task.title}' marked as complete![/green]")
        else:
            console.print(f"[red]Invalid task ID. Please choose between 1 and {len(pending_tasks)}[/red]")
    
    def delete_task(self, task_id: int) -> None:
        """Delete a task"""
        if not self.tasks:
            console.print("[yellow]No tasks to delete![/yellow]")
            return
        
        if 1 <= task_id <= len(self.tasks):
            task = self.tasks.pop(task_id - 1)
            self.save_tasks()
            console.print(f"[green]✓ Task '{task.title}' deleted![/green]")
        else:
            console.print(f"[red]Invalid task ID. Please choose between 1 and {len(self.tasks)}[/red]")
    
    def clear_completed(self) -> None:
        """Remove all completed tasks"""
        completed_count = len([t for t in self.tasks if t.completed])
        
        if completed_count == 0:
            console.print("[yellow]No completed tasks to clear![/yellow]")
            return
        
        if Confirm.ask(f"Are you sure you want to delete {completed_count} completed task(s)?"):
            self.tasks = [t for t in self.tasks if not t.completed]
            self.save_tasks()
            console.print(f"[green]✓ Cleared {completed_count} completed task(s)![/green]")

def main():
    parser = argparse.ArgumentParser(description="Task Management CLI Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('title', help='Task title')
    add_parser.add_argument('-p', '--priority', choices=['low', 'medium', 'high'], 
                          default='medium', help='Task priority (default: medium)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all tasks')
    list_parser.add_argument('-a', '--all', action='store_true', 
                           help='Show all tasks including completed ones')
    
    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Mark a task as complete')
    complete_parser.add_argument('id', type=int, help='Task ID to mark as complete')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('id', type=int, help='Task ID to delete')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear all completed tasks')
    
    # Interactive mode
    interactive_parser = subparsers.add_parser('interactive', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # Create task manager instance
    manager = TaskManager()
    
    if args.command == 'add':
        manager.add_task(args.title, args.priority)
    elif args.command == 'list':
        manager.list_tasks(show_completed=args.all)
    elif args.command == 'complete':
        manager.mark_complete(args.id)
    elif args.command == 'delete':
        manager.delete_task(args.id)
    elif args.command == 'clear':
        manager.clear_completed()
    elif args.command == 'interactive':
        run_interactive_mode(manager)
    else:
        # Show help if no command provided
        parser.print_help()
        console.print("\n[cyan]Quick start:[/cyan]")
        console.print("  taskmanager add 'My first task' -p high")
        console.print("  taskmanager list")
        console.print("  taskmanager complete 1")

def run_interactive_mode(manager: TaskManager):
    """Run the task manager in interactive mode"""
    console.print(Panel.fit(
        "[bold cyan]Task Manager - Interactive Mode[/bold cyan]\n"
        "Type 'help' for available commands or 'quit' to exit",
        border_style="cyan"
    ))
    
    while True:
        try:
            command = Prompt.ask("\n[cyan]taskmanager>[/cyan]").strip().lower()
            
            if command in ['quit', 'exit', 'q']:
                console.print("[yellow]Goodbye![/yellow]")
                break
            elif command == 'help':
                console.print(Panel(
                    "[bold]Available commands:[/bold]\n"
                    "  add         - Add a new task\n"
                    "  list        - List pending tasks\n"
                    "  list all    - List all tasks (including completed)\n"
                    "  complete    - Mark a task as complete\n"
                    "  delete      - Delete a task\n"
                    "  clear       - Clear completed tasks\n"
                    "  help        - Show this help message\n"
                    "  quit        - Exit the program",
                    title="Help",
                    border_style="green"
                ))
            elif command == 'add':
                title = Prompt.ask("Task title")
                priority = Prompt.ask("Priority", choices=['low', 'medium', 'high'], default='medium')
                manager.add_task(title, priority)
            elif command == 'list':
                manager.list_tasks(show_completed=False)
            elif command == 'list all':
                manager.list_tasks(show_completed=True)
            elif command == 'complete':
                manager.list_tasks(show_completed=False)
                try:
                    task_id = int(Prompt.ask("Task ID to complete"))
                    manager.mark_complete(task_id)
                except ValueError:
                    console.print("[red]Please enter a valid number[/red]")
            elif command == 'delete':
                manager.list_tasks(show_completed=True)
                try:
                    task_id = int(Prompt.ask("Task ID to delete"))
                    manager.delete_task(task_id)
                except ValueError:
                    console.print("[red]Please enter a valid number[/red]")
            elif command == 'clear':
                manager.clear_completed()
            elif command:
                console.print(f"[red]Unknown command: '{command}'. Type 'help' for available commands.[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'quit' to exit[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()