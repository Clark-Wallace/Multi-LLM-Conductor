# Task Management CLI Tool

A robust, feature-rich command-line task management application written in Python. This tool helps you organize your tasks with priorities, due dates, tags, and advanced filtering capabilities.

## Features

### Core Features
- **Add Tasks**: Create tasks with title, description, priority level, due dates, and tags
- **List Tasks**: View all pending or completed tasks with various sorting options
- **Complete Tasks**: Mark tasks as done
- **Delete Tasks**: Remove tasks with confirmation prompt
- **Edit Tasks**: Modify existing tasks

### Advanced Features
- **Search & Filter**: Find tasks by text, tags, priority, or overdue status
- **Due Dates**: Set deadlines and get visual indicators for overdue tasks
- **Tags**: Organize tasks with multiple tags
- **Export**: Save your tasks to CSV or JSON format
- **Statistics**: View task completion rates and distribution
- **Automatic Backups**: Tasks are backed up before each save
- **Comprehensive Error Handling**: Graceful handling of invalid inputs
- **Colorful Output**: Visual indicators for priorities and task status

## Installation

1. Clone or download the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Commands

#### Add a Task
```bash
# Simple task
python task_manager.py add "Write report"

# With description and priority
python task_manager.py add "Write report" -d "Quarterly sales report" -p high

# With due date and tags
python task_manager.py add "Write report" --due tomorrow -t "work,urgent"

# Various due date formats
python task_manager.py add "Task" --due "2024-12-31"
python task_manager.py add "Task" --due "in 7 days"
python task_manager.py add "Task" --due today
```

#### List Tasks
```bash
# Show pending tasks
python task_manager.py list

# Show all tasks including completed
python task_manager.py list --all

# Filter by text
python task_manager.py list --filter "report"

# Filter by priority
python task_manager.py list --priority high

# Filter by tags
python task_manager.py list --tags "work,urgent"

# Show only overdue tasks
python task_manager.py list --overdue
```

#### Complete a Task
```bash
# Mark task #1 as complete
python task_manager.py complete 1
```

#### Delete a Task
```bash
# Delete task #2 (with confirmation)
python task_manager.py delete 2
```

#### Edit a Task
```bash
# Change title
python task_manager.py edit 1 --title "Updated title"

# Change multiple properties
python task_manager.py edit 1 --title "New title" -p urgent --due "in 3 days"

# Clear due date
python task_manager.py edit 1 --due none

# Update tags
python task_manager.py edit 1 --tags "work,revised"
```

### Advanced Commands

#### Search Tasks
```bash
# Quick search (alias for list --filter)
python task_manager.py search "report"
python task_manager.py search "meeting" --all
```

#### Export Tasks
```bash
# Export to CSV
python task_manager.py export tasks.csv

# Export to JSON
python task_manager.py export tasks.json --format json
```

#### View Statistics
```bash
python task_manager.py stats
```

## Priority Levels

Tasks can have four priority levels:
- **LOW** (Blue)
- **MEDIUM** (Yellow) - Default
- **HIGH** (Red)
- **URGENT** (White on Red background)

## Due Dates

Due dates can be specified in multiple formats:
- Absolute: `2024-12-31`, `31/12/2024`, `12-31-2024`
- With time: `2024-12-31 14:30`
- Relative: `today`, `tomorrow`, `in 7 days`

Tasks that are overdue will be marked with a red "OVERDUE" indicator.

## Tags

Tags help categorize tasks. You can:
- Add multiple tags to a task (comma-separated)
- Filter tasks by tags
- Update tags when editing tasks

## Data Storage

- Tasks are stored in `tasks.json` in the current directory
- Automatic backups are created in the `backups/` directory
- The tool will attempt to restore from backup if the main file is corrupted

## Error Handling

The tool includes comprehensive error handling for:
- Invalid task titles (empty or too long)
- Invalid date formats
- File I/O errors
- Corrupted data files
- Invalid command arguments

## Testing

Run the test suite:
```bash
python -m pytest test_task_manager.py -v

# With coverage
python -m pytest test_task_manager.py --cov=task_manager --cov-report=html
```

## Examples

### Daily Workflow
```bash
# Start your day by checking tasks
python task_manager.py list

# Add a new urgent task
python task_manager.py add "Fix critical bug" -p urgent --due today -t "work,bug"

# Check overdue tasks
python task_manager.py list --overdue

# Complete a task
python task_manager.py complete 3

# View your progress
python task_manager.py stats
```

### Project Management
```bash
# Add project tasks with tags
python task_manager.py add "Design UI mockups" -t "project-x,design" --due "in 3 days"
python task_manager.py add "Implement API" -t "project-x,backend" --due "in 7 days"
python task_manager.py add "Write tests" -t "project-x,testing" --due "in 10 days"

# View all project tasks
python task_manager.py list --tags "project-x"

# Export project tasks
python task_manager.py export project-x-tasks.csv
```

## Tips

1. Use tags consistently for better organization
2. Set realistic due dates to avoid too many overdue tasks
3. Use the search feature to quickly find tasks
4. Export your tasks regularly for backup
5. Check statistics to monitor your productivity

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.