"""
Todo Management System for AgentLin

This module implements a comprehensive todo management system inspired by Claude Code's
intelligent task planning approach. It provides functionality to create, manage, and
track todo items with priorities and status tracking.

Features:
- Create and manage todo items with status and priority
- Smart sorting using YJ1 algorithm (status > priority > time)
- File-based storage with JSON persistence
- Rich markdown formatting for displays
- Progress analysis and suggestions
- Integration with AgentLin's tool system

Usage:
    from agentlin.tools.tool_todo import todo_write, todo_read

    # Write todos to a specific file
    result = await todo_write(
        file_path="my_todos.json",
        todos=[{'content': 'Complete documentation', 'priority': 'high', 'status': 'pending'}]
    )

    # Read todos from a specific file
    result = await todo_read(file_path="my_todos.json")

    # Analyze progress from a file
    analysis = analyze_progress_from_file("my_todos.json")
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from functools import reduce
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from agentlin.core.types import ToolResult


class TodoStatus(str, Enum):
    """Todo item status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TodoPriority(str, Enum):
    """Todo item priority enumeration."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TodoItem(BaseModel):
    """Todo item data model."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    status: TodoStatus = TodoStatus.PENDING
    priority: TodoPriority = TodoPriority.MEDIUM
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def update_timestamp(self):
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.now(timezone.utc).isoformat()


# Module-level storage - more Pythonic than singleton class
# _current_todos: List[TodoItem] = []  # Removed global storage


# Constants for sorting priorities
STATUS_PRIORITY = {
    TodoStatus.IN_PROGRESS: 0,
    TodoStatus.PENDING: 1,
    TodoStatus.COMPLETED: 2,
}

IMPORTANCE_PRIORITY = {
    TodoPriority.HIGH: 0,
    TodoPriority.MEDIUM: 1,
    TodoPriority.LOW: 2,
}

PRIORITY_ICONS = {
    TodoPriority.HIGH: "🔥",
    TodoPriority.MEDIUM: "⚡",
    TodoPriority.LOW: "💡",
}

STATUS_ICONS = {
    TodoStatus.IN_PROGRESS: "🔄",
    TodoStatus.PENDING: "⏳",
    TodoStatus.COMPLETED: "✅",
}


# File-based storage functions - functional approach
def load_todos_from_file(file_path: str) -> List[TodoItem]:
    """Load todos from a JSON file."""
    try:
        path = Path(file_path)
        if not path.exists():
            return []

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return [TodoItem.model_validate(item) for item in data]
    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        # If file doesn't exist or is corrupted, return empty list
        return []


def save_todos_to_file(file_path: str, todos: List[TodoItem]) -> None:
    """Save todos to a JSON file."""
    try:
        path = Path(file_path)
        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert todos to dict format for JSON serialization
        data = [todo.model_dump() for todo in todos]

        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise Exception(f"Failed to save todos to file {file_path}: {str(e)}")


def get_todos_from_file(file_path: str) -> List[TodoItem]:
    """Get todos from file."""
    return load_todos_from_file(file_path)


def set_todos_to_file(file_path: str, todos: List[TodoItem]) -> None:
    """Set todos to file."""
    save_todos_to_file(file_path, todos)


def clear_todos_from_file(file_path: str) -> None:
    """Clear all todos from file."""
    save_todos_to_file(file_path, [])


# Sorting functions - functional approach
def _get_sort_key(todo: TodoItem) -> tuple:
    """
    Generate sort key for a todo item using YJ1 algorithm:
    1. By status priority (in_progress > pending > completed)
    2. By importance (high > medium > low)
    3. By creation time (newer first for pending/in_progress)
    """
    status_priority = STATUS_PRIORITY[todo.status]
    importance_priority = IMPORTANCE_PRIORITY[todo.priority]

    # Parse creation time
    try:
        created_time = datetime.fromisoformat(todo.created_at.replace("Z", "+00:00"))
        time_timestamp = created_time.timestamp()
    except (ValueError, AttributeError):
        time_timestamp = 0

    # For completed tasks, older first; for active tasks, newer first
    time_sort = time_timestamp if todo.status == TodoStatus.COMPLETED else -time_timestamp

    return (status_priority, importance_priority, time_sort)


def sort_todos(todos: List[TodoItem]) -> List[TodoItem]:
    """Sort todos using Claude Code's YJ1 algorithm."""
    return sorted(todos, key=_get_sort_key)


# Statistics functions - functional approach
def calculate_stats(todos: List[TodoItem]) -> Dict[str, int]:
    """Calculate various statistics for a list of todos using functional approach."""
    # Count by status using list comprehensions
    status_counts = {
        "total": len(todos),
        "completed": len([t for t in todos if t.status == TodoStatus.COMPLETED]),
        "in_progress": len([t for t in todos if t.status == TodoStatus.IN_PROGRESS]),
        "pending": len([t for t in todos if t.status == TodoStatus.PENDING]),
    }

    # Count by priority
    priority_counts = {
        "high": len([t for t in todos if t.priority == TodoPriority.HIGH]),
        "medium": len([t for t in todos if t.priority == TodoPriority.MEDIUM]),
        "low": len([t for t in todos if t.priority == TodoPriority.LOW]),
    }

    return {**status_counts, **priority_counts}


# Alternative functional approach using reduce
def calculate_stats_functional(todos: List[TodoItem]) -> Dict[str, int]:
    """Calculate stats using reduce - more functional but less readable."""

    def count_reducer(acc: Dict[str, int], todo: TodoItem) -> Dict[str, int]:
        acc["total"] += 1
        acc[todo.status.value] = acc.get(todo.status.value, 0) + 1
        acc[todo.priority.value] = acc.get(todo.priority.value, 0) + 1
        return acc

    initial_stats = {
        "total": 0,
        "completed": 0,
        "in_progress": 0,
        "pending": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    return reduce(count_reducer, todos, initial_stats)


# Formatting functions - functional approach
def _group_todos_by_status(todos: List[TodoItem]) -> Dict[TodoStatus, List[TodoItem]]:
    """Group todos by status using functional approach."""
    return {status: [t for t in todos if t.status == status] for status in TodoStatus}


def format_todo_display(todos: List[TodoItem]) -> str:
    """Format todos for display in markdown using functional approach."""
    if not todos:
        return """# 📝 Todo List

No tasks currently tracked.

💡 **Tip**: Use the `todo_write` tool to create a task list and track your progress!"""

    stats = calculate_stats(todos)
    grouped_todos = _group_todos_by_status(todos)

    # Build display using string concatenation and comprehensions
    header = f"""# 📝 Todo List

**Progress**: {stats['completed']}/{stats['total']} completed
**Priorities**: {stats['high']} high, {stats['medium']} medium, {stats['low']} low

"""

    # Format sections using list comprehensions and joins
    sections = []

    if grouped_todos[TodoStatus.IN_PROGRESS]:
        in_progress_items = [f"- {PRIORITY_ICONS[todo.priority]} **{todo.content}**" for todo in grouped_todos[TodoStatus.IN_PROGRESS]]
        sections.append("## 🔄 In Progress\n\n" + "\n".join(in_progress_items) + "\n")

    if grouped_todos[TodoStatus.PENDING]:
        pending_items = [f"- {PRIORITY_ICONS[todo.priority]} {todo.content}" for todo in grouped_todos[TodoStatus.PENDING]]
        sections.append("## ⏳ Pending\n\n" + "\n".join(pending_items) + "\n")

    if grouped_todos[TodoStatus.COMPLETED]:
        completed_items = [f"- ~~{todo.content}~~" for todo in grouped_todos[TodoStatus.COMPLETED]]
        sections.append("## ✅ Completed\n\n" + "\n".join(completed_items) + "\n")

    footer = f"\n*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"

    return header + "\n".join(sections) + footer


def generate_summary(todos: List[TodoItem]) -> str:
    """Generate a brief summary of todos using functional approach."""
    if not todos:
        return "No tasks currently tracked"

    stats = calculate_stats(todos)
    return f"{stats['completed']}/{stats['total']} tasks completed ({stats['in_progress']} in progress, {stats['pending']} pending)"


async def todo_write(file_path: str, todos: List[Dict[str, Any]]) -> ToolResult:
    """
    Create and manage a structured task list for a specific file.

    Args:
        file_path: Path to the JSON file where todos will be stored
        todos: List of todo items with id, content, status, and priority

    Returns:
        ToolResult with updated todo list and summary
    """
    try:
        # Validate and convert todos
        todo_items = []
        for todo_data in todos:
            # Create TodoItem
            todo_item = TodoItem.model_validate(todo_data)
            todo_item.update_timestamp()
            todo_items.append(todo_item)

        # Sort todos using YJ1 algorithm
        sorted_todos = sort_todos(todo_items)

        # Store todos to file
        set_todos_to_file(file_path, sorted_todos)

        # Generate display and summary
        display = format_todo_display(sorted_todos)
        summary = generate_summary(sorted_todos)

        # Create result
        result = ToolResult(
            message_content=[
                {
                    "type": "text",
                    "text": f"Todo list updated successfully in {file_path}. Current status:\n{summary}",
                    "id": 1,
                },
            ],
            block_list=[
                {
                    "type": "text",
                    "text": display,
                    "id": 1,
                },
            ],
        )

        return result

    except Exception as e:
        error_result = ToolResult(
            message_content=[
                {"type": "text", "text": f"Error updating todo list: {str(e)}"},
            ],
            block_list=[
                {
                    "type": "text",
                    "text": "Failed to update todo list. Please check the input format and try again.",
                },
            ],
        )
        return error_result


async def todo_read(file_path: str) -> ToolResult:
    """
    View the todo list and task progress from a specific file.

    Args:
        file_path: Path to the JSON file containing todos

    Returns:
        ToolResult with current todo list and summary
    """
    try:
        todos = get_todos_from_file(file_path)

        # Generate display and summary
        display = format_todo_display(todos)
        summary = generate_summary(todos)

        # Create result
        result = ToolResult(
            message_content=[
                {"type": "text", "text": f"Todo list from {file_path}:\n{summary}", "id": 1},
            ],
            block_list=[
                {
                    "type": "text",
                    "text": display,
                    "id": 1,
                },
            ],
        )

        return result

    except Exception as e:
        error_result = ToolResult(
            message_content=[{"type": "text", "text": f"Error reading todo list from {file_path}: {str(e)}"}],
            block_list=[],
        )
        return error_result


# Management functions - functional approach
REMINDER_MESSAGES = [
    "Consider using the todo_write tool to plan your tasks before starting.",
    "Breaking down complex tasks into smaller todos can help track progress.",
    "Don't forget to update your todo list as you complete tasks!",
    "Planning with todos helps ensure nothing important is missed.",
]


def should_remind_about_todos(file_path: Optional[str] = None) -> bool:
    """Check if user should be reminded to use todo system."""
    if file_path:
        todos = get_todos_from_file(file_path)
        return len(todos) == 0
    # If no file path provided, assume user has no todos
    return True


def get_random_reminder() -> str:
    """Get a random reminder message."""
    import random

    return random.choice(REMINDER_MESSAGES)


def analyze_progress_from_file(file_path: str) -> Dict[str, Any]:
    """Analyze todo progress from a specific file using functional approach."""
    todos = get_todos_from_file(file_path)

    if not todos:
        return {
            "has_active_tasks": False,
            "completion_rate": 0,
            "needs_attention": [],
            "suggestions": ["Create a todo list to track your tasks"],
        }

    stats = calculate_stats(todos)
    completion_rate = stats["completed"] / stats["total"] if stats["total"] > 0 else 0
    has_active_tasks = any(t.status != TodoStatus.COMPLETED for t in todos)

    # Filter high-priority in-progress tasks using functional approach
    needs_attention = [t for t in todos if t.status == TodoStatus.IN_PROGRESS and t.priority == TodoPriority.HIGH]

    # Generate suggestions using conditional logic
    suggestions = []
    if needs_attention:
        suggestions.append(f"Focus on {len(needs_attention)} high-priority in-progress tasks")

    if completion_rate < 0.3:
        suggestions.append("Consider breaking down large tasks into smaller ones")

    if stats["pending"] > 5:
        suggestions.append("Many pending tasks - prioritize the most important ones")

    return {
        "has_active_tasks": has_active_tasks,
        "completion_rate": completion_rate,
        "needs_attention": [t.model_dump() for t in needs_attention],
        "suggestions": suggestions,
    }


def generate_system_reminder_for_file(file_path: str) -> Optional[str]:
    """Generate system reminder about todo usage for a specific file."""
    analysis = analyze_progress_from_file(file_path)

    if not analysis["has_active_tasks"] and not Path(file_path).exists():
        return (
            "This is a reminder that your todo list is currently empty. "
            "DO NOT mention this to the user explicitly because they are already aware. "
            "If you are working on tasks that would benefit from a todo list please use "
            "the todo_write tool to create one. If not, please feel free to ignore. "
            "Again do not mention this message to the user."
        )

    if analysis["needs_attention"]:
        task_list = ", ".join([t["content"] for t in analysis["needs_attention"]])
        return f"Your todo list has {len(analysis['needs_attention'])} high-priority tasks in progress: {task_list}. Continue with the current tasks if applicable."

    return None
