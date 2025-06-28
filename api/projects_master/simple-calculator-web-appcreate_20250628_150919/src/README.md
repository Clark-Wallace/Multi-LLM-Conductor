# Task Manager CLI

A colorful command-line task management tool with priorities and JSON persistence.

## Features

- ✅ Add tasks with priorities (low, medium, high)
- 📋 List tasks sorted by priority
- ✓ Mark tasks as complete
- 💾 Automatic save to JSON file
- 🎨 Colorful terminal output using Rich library
- 🗑️ Delete tasks
- 🧹 Clear completed tasks
- 💬 Interactive mode

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Mode

```bash
# Add a new task
python taskmanager.py add "Buy groceries" -p high
python taskmanager.py add "Read a book" -p low

# List pending tasks
python taskmanager.py list

# List all tasks (including completed)
python taskmanager.py list --all

# Mark task as complete (by ID)
python taskmanager.py complete 1

# Delete a task
python taskmanager.py delete 2

# Clear all completed tasks
python taskmanager.py clear
```

### Interactive Mode

```bash
python taskmanager.py interactive
```

In interactive mode, you can use commands like:
- `add` - Add a new task
- `list` - Show pending tasks
- `list all` - Show all tasks
- `complete` - Mark task as done
- `delete` - Remove a task
- `clear` - Remove completed tasks
- `help` - Show available commands
- `quit` - Exit the program

## Task Priorities

Tasks are color-coded by priority:
- 🔴 **HIGH** - Red (most urgent)
- 🟡 **MEDIUM** - Yellow (moderate priority)
- 🟢 **LOW** - Green (least urgent)

## Data Storage

Tasks are automatically saved to `tasks.json` in the same directory as the script.

## Examples

```bash
# Quick task management workflow
python taskmanager.py add "Finish project report" -p high
python taskmanager.py add "Call dentist" -p medium
python taskmanager.py add "Water plants" -p low
python taskmanager.py list
python taskmanager.py complete 1
python taskmanager.py list --all
```