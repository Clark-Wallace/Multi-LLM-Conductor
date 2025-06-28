#!/usr/bin/env python3
"""
Example usage script for the Task Management CLI Tool.
This demonstrates various features of the task manager.
"""

import subprocess
import sys
import time


def run_command(cmd):
    """Run a command and print its output"""
    print(f"\n{'='*60}")
    print(f"Running: {cmd}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("Error:", result.stderr, file=sys.stderr)
    
    time.sleep(1)  # Small delay for readability
    return result.returncode == 0


def main():
    print("Task Management CLI Tool - Example Usage")
    print("="*60)
    
    # 1. Add some tasks
    print("\n1. Adding various tasks...")
    
    commands = [
        # Basic task
        'python task_manager.py add "Write project documentation"',
        
        # Task with description and priority
        'python task_manager.py add "Fix critical bug in login system" -d "Users cannot login with special characters in password" -p urgent',
        
        # Task with due date
        'python task_manager.py add "Prepare presentation" --due tomorrow -p high',
        
        # Task with tags
        'python task_manager.py add "Review pull requests" -t "development,code-review" --due "in 2 days"',
        
        # Personal task
        'python task_manager.py add "Buy groceries" -t "personal,shopping" -p low --due today',
        
        # Task with everything
        'python task_manager.py add "Deploy to production" -d "Deploy version 2.0 after testing" -p high --due "in 5 days" -t "deployment,release"',
        
        # Overdue task (for demonstration)
        'python task_manager.py add "Submit tax forms" -p urgent --due "2024-01-01" -t "personal,finance"'
    ]
    
    for cmd in commands:
        if not run_command(cmd):
            print("Failed to add task!")
            return
    
    # 2. List tasks
    print("\n2. Listing tasks...")
    run_command('python task_manager.py list')
    
    # 3. Search and filter
    print("\n3. Searching and filtering tasks...")
    
    filter_commands = [
        'python task_manager.py search "project"',
        'python task_manager.py list --priority urgent',
        'python task_manager.py list --tags "personal"',
        'python task_manager.py list --overdue'
    ]
    
    for cmd in filter_commands:
        run_command(cmd)
    
    # 4. Complete some tasks
    print("\n4. Completing tasks...")
    run_command('python task_manager.py complete 5')  # Complete "Buy groceries"
    
    # 5. Edit a task
    print("\n5. Editing a task...")
    run_command('python task_manager.py edit 1 --title "Write comprehensive project documentation" --due "in 3 days"')
    
    # 6. Show statistics
    print("\n6. Viewing statistics...")
    run_command('python task_manager.py stats')
    
    # 7. List all tasks including completed
    print("\n7. Showing all tasks (including completed)...")
    run_command('python task_manager.py list --all')
    
    # 8. Export tasks
    print("\n8. Exporting tasks...")
    run_command('python task_manager.py export example_tasks.csv')
    run_command('python task_manager.py export example_tasks.json --format json')
    
    print("\n" + "="*60)
    print("Example usage completed!")
    print("Files created: example_tasks.csv, example_tasks.json")
    print("Task data stored in: tasks.json")
    print("="*60)


if __name__ == "__main__":
    main()