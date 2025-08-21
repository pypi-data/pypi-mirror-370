#!/usr/bin/env python3
import os
from typing import Any, Dict, List
from typing_extensions import Annotated
from loguru import logger

from fastmcp import FastMCP, Context

from agentlin.tools.tool_todo import TodoItem, todo_write, todo_read


mcp = FastMCP(
    "Todo Management Tool Server",
    version="0.1.0",
)


@mcp.tool(
    name="todo_write",
    title="TodoWrite",
    description="""Use this tool to create and manage a structured task list for your current coding session. This helps you track progress, organize complex tasks, and demonstrate thoroughness to the user.
It also helps the user understand the progress of the task and overall progress of their requests.

## When to Use This Tool
Use this tool proactively in these scenarios:

1. Complex multi-step tasks - When a task requires 3 or more distinct steps or actions
2. Non-trivial and complex tasks - Tasks that require careful planning or multiple operations
3. User explicitly requests todo list - When the user directly asks you to use the todo list
4. User provides multiple tasks - When users provide a list of things to be done (numbered or comma-separated)
5. After receiving new instructions - Immediately capture user requirements as todos
6. When you start working on a task - Mark it as in_progress BEFORE beginning work. Ideally you should only have one todo as in_progress at a time
7. After completing a task - Mark it as completed and add any new follow-up tasks discovered during implementation

## When NOT to Use This Tool

Skip using this tool when:
1. There is only a single, straightforward task
2. The task is trivial and tracking it provides no organizational benefit
3. The task can be completed in less than 3 trivial steps
4. The task is purely conversational or informational

NOTE that you should not use this tool if there is only one trivial task to do. In this case you are better off just doing the task directly.

## Task States and Management

1. **Task States**: Use these states to track progress:
   - pending: Task not yet started
   - in_progress: Currently working on (limit to ONE task at a time)
   - completed: Task finished successfully

2. **Task Management**:
   - Update task status in real-time as you work
   - Mark tasks complete IMMEDIATELY after finishing (don't batch completions)
   - Only have ONE task in_progress at any time
   - Complete current tasks before starting new ones
   - Remove tasks that are no longer relevant from the list entirely

3. **Task Completion Requirements**:
   - ONLY mark a task as completed when you have FULLY accomplished it
   - If you encounter errors, blockers, or cannot finish, keep the task as in_progress
   - When blocked, create a new task describing what needs to be resolved
   - Never mark a task as completed if:
     - Tests are failing
     - Implementation is partial
     - You encountered unresolved errors
     - You couldn't find necessary files or dependencies

4. **Task Breakdown**:
   - Create specific, actionable items
   - Break complex tasks into smaller, manageable steps
   - Use clear, descriptive task names

When in doubt, use this tool. Being proactive with task management demonstrates attentiveness and ensures you complete all requirements successfully.""",
)
async def todo_write_tool(
    ctx: Context,
    todos: Annotated[List[TodoItem], """List of todo items with the following structure:
    - content (string, required): The task description
    - status (string, required): One of 'pending', 'in_progress', 'completed'
    - priority (string, required): One of 'high', 'medium', 'low'
    - id (string, required): Unique identifier for the task

    Example:
    [
        {
            "content": "Implement user authentication",
            "status": "pending",
            "priority": "high",
            "id": "task-1"
        },
        {
            "content": "Add error handling to API endpoints",
            "status": "in_progress",
            "priority": "medium",
            "id": "task-2"
        }
    ]"""],
):
    """创建和管理结构化任务列表"""
    file_path = os.getenv("TODO_FILE_PATH", "todos.json")
    result = await todo_write(file_path, todos)
    return result


@mcp.tool(
    name="todo_read",
    title="TodoRead",
    description="""View the current todo list and task progress from a specific file.

This tool displays:
- Current task status and completion progress
- Tasks organized by status (In Progress, Pending, Completed)
- Priority indicators for each task
- Summary statistics

Use this tool to:
1. Check current progress on tasks
2. Review what work remains to be done
3. See completed tasks for reference
4. Get an overview of task priorities

The display is formatted in markdown with clear visual indicators:
- 🔄 for in-progress tasks
- ⏳ for pending tasks
- ✅ for completed tasks
- 🔥 for high priority
- ⚡ for medium priority
- 💡 for low priority""",
)
async def todo_read_tool(
    ctx: Context,
):
    """查看todo列表和任务进度"""
    file_path = os.getenv("TODO_FILE_PATH", "todos.json")
    result = await todo_read(file_path)
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Todo Management MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7780, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    logger.info("Starting Todo Management MCP Server...")
    logger.info("Available tools: todo_write, todo_read")

    mcp.run("http", host=args.host, port=args.port, log_level="debug" if args.debug else "info")
