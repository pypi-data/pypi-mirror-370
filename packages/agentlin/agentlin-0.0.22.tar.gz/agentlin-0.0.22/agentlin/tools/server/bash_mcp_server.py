#!/usr/bin/env python3
import asyncio
import datetime
from typing import Any, Dict, Optional
from typing_extensions import Annotated
from loguru import logger

from fastmcp import FastMCP, Context

from agentlin.tools.tool_bash import execute_command


mcp = FastMCP(
    "Bash Command Tool Server",
    version="0.1.0",
)


@mcp.tool(
    name="Bash",
    title="Bash",
    description="""Executes a given bash command in a persistent shell session with optional timeout, ensuring proper handling and security measures.

Before executing the command, please follow these steps:

1. Directory Verification:
    - If the command will create new directories or files, first use the LS tool to verify the parent directory exists and is the correct location
    - For example, before running "mkdir foo/bar", first use LS to check that "foo" exists and is the intended parent directory

2. Command Execution:
    - Always quote file paths that contain spaces with double quotes (e.g., cd "path with spaces/file.txt")
    - Examples of proper quoting:
    - cd "/Users/name/My Documents" (correct)
    - cd /Users/name/My Documents (incorrect - will fail)
    - python "/path/with spaces/script.py" (correct)
    - python /path/with spaces/script.py (incorrect - will fail)
    - After ensuring proper quoting, execute the command.
    - Capture the output of the command.

Usage notes:
- The command argument is required.
- You can specify an optional timeout in milliseconds (up to 600000ms / 10 minutes). If not specified, commands will timeout after 120000ms (2 minutes).
- It is very helpful if you write a clear, concise description of what this command does in 5-10 words.
- If the output exceeds 30000 characters, output will be truncated before being returned to you.
- VERY IMPORTANT: You MUST avoid using search commands like `find` and `grep`. Instead use Grep, Glob, or Task to search. You MUST avoid read tools like `cat`, `head`, `tail`, and `ls`, and use Read and LS to read files.
- If you _still_ need to run `grep`, STOP. ALWAYS USE ripgrep at `rg` first, which all ${PRODUCT_NAME} users have pre-installed.
- When issuing multiple commands, use the ';' or '&&' operator to separate them. DO NOT use newlines (newlines are ok in quoted strings).
- Try to maintain your current working directory throughout the session by using absolute paths and avoiding usage of `cd`. You may use `cd` if the User explicitly requests it.
    <good-example>
    pytest /foo/bar/tests
    </good-example>
    <bad-example>
    cd /foo/bar && pytest tests
    </bad-example>
""",
    exclude_args=["cwd"],
)
async def execute_command_tool(
    ctx: Context,
    command: Annotated[str, "The bash command to execute. Ensure it is properly quoted if it contains spaces."],
    timeout: Annotated[int, "Optional timeout in milliseconds (max 600000)"] = 120000,
    description: Annotated[Optional[str], """Clear, concise description of what this command does in 5-10 words. Examples:

Input: ls
Output: Lists files in current directory

Input: git status
Output: Shows working tree status

Input: npm install
Output: Installs package dependencies

Input: mkdir foo
Output: Creates directory 'foo'"""] = None,
    cwd: Optional[str] = None,
):
    """执行bash命令并返回结果"""
    # roots = await ctx.list_roots()
    # for root_path in roots:
    #     root_path.uri
    result = await ctx.elicit(
        f"""
```bash
{command}
```
""".strip(),
        None,
    )
    if result.action == "accept":
        result = await execute_command(command, cwd, timeout)
    else:
        result = {
            "success": False,
            "error": "Command not accepted or canceled",
            "stdout": "",
            "stderr": "",
            "code": -1,
            "command": command,
            "executedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7779, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    logger.info("Starting Bash Command MCP Server...")
    logger.info("Available tools: execute_command")

    mcp.run("http", host=args.host, port=args.port, log_level="debug" if args.debug else "info")
