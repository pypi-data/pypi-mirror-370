import os
from loguru import logger
from typing import List, Optional, Annotated

from fastmcp import FastMCP
from mcp.types import TextContent, ImageContent

from agentlin.tools.tool_file_system import (
    list_directory as fs_list_directory,
    read_file as fs_read_file,
    write_file as fs_write_file,
    glob as fs_glob,
    search_file_content as fs_search_file_content,
    replace_in_file as fs_replace_in_file,
)
from agentlin.tools.tool_read_many_files import read_many_files as fs_read_many_files


mcp = FastMCP(
    "File System Tool Server",
    version="0.1.0",
)


@mcp.tool(
    name="list_directory",
    title="LS",
    description="Lists files and directories in a given path. The path parameter must be an absolute path, not a relative path. You can optionally provide an array of glob patterns to ignore with the ignore parameter. You should generally prefer the Glob and Grep tools, if you know which directories to search.",
)
def list_directory(
    path: Annotated[Optional[str], "The absolute path to the directory to list (must be absolute, not relative)"] = None,
    ignore: Annotated[Optional[List[str]], "List of glob patterns to ignore"] = None,
    respect_git_ignore: Annotated[bool, "Whether to respect .gitignore file rules"] = True,
) -> str:
    """列出指定目录中的文件和子目录"""
    if not path:
        path = os.getenv("HOME_DIR", os.path.expanduser("~"))  # Default to home directory if not specified
        path = os.path.abspath(path)  # Ensure it's absolute
    return fs_list_directory(path, ignore, respect_git_ignore)


@mcp.tool(
    name="read_file",
    title="Read",
    description="""Reads a file from the local filesystem. You can access any file directly by using this tool.

Assume this tool is able to read all files on the machine. If the User \
provides a path to a file assume that path is valid. It is okay to read a file \
that does not exist; an error will be returned.


Usage:

- The file_path parameter must be an absolute path, not a relative path

- By default, it reads up to 2000 lines starting from the beginning of the \
file

- You can optionally specify a line offset and limit (especially handy for \
long files), but it's recommended to read the whole file by not providing \
these parameters

- Any lines longer than 2000 characters will be truncated

- Results are returned using cat -n format, with line numbers starting at 1

- This tool allows Claude Code to read images (eg PNG, JPG, etc). When reading \
an image file the contents are presented visually as Claude Code is a \
multimodal LLM.

- This tool can read PDF files (.pdf). PDFs are processed page by page, \
extracting both text and visual content for analysis.

- For Jupyter notebooks (.ipynb files), use the NotebookRead instead

- You have the capability to call multiple tools in a single response. It is \
always better to speculatively read multiple files as a batch that are \
potentially useful.

- You will regularly be asked to read screenshots. If the user provides a path \
to a screenshot ALWAYS use this tool to view the file at the path. This tool \
will work with all temporary file paths like \
/var/folders/123/abc/T/TemporaryItems/NSIRD_screencaptureui_ZfB1tD/Screenshot.png

- If you read a file that exists but has empty contents you will receive a \
system reminder warning in place of file contents.""",
)
def read_file(
    path: Annotated[str, "The absolute path to the file to read"],
    offset: Annotated[Optional[int], "The line number to start reading from. Only provide if the file is too large to read at once"] = None,
    limit: Annotated[Optional[int], "The number of lines to read. Only provide if the file is too large to read at once"] = None,
):
    """读取并返回指定文件的内容"""
    result = fs_read_file(path, offset, limit)

    # 如果返回的是字典（图像或PDF），需要转换为适当的MCP内容类型
    if isinstance(result, dict) and "inlineData" in result:
        inline_data = result["inlineData"]
        if inline_data["mimeType"].startswith("image/"):
            return [
                ImageContent(
                    type="image",
                    data=inline_data["data"],
                    mimeType=inline_data["mimeType"],
                )
            ]
        else:  # PDF或其他二进制文件
            return [
                TextContent(
                    type="text",
                    text=f"Binary file content (MIME: {inline_data['mimeType']}): {inline_data['data'][:20]}...",
                )
            ]

    # 文本文件直接返回字符串
    return result


@mcp.tool(
    name="write_file",
    title="Write",
    description="""Writes a file to the local filesystem.

Usage:
- This tool will overwrite the existing file if there is one at the provided path
- If this is an existing file, you MUST use the Read tool first to read the file's contents. This tool will fail if you did not read the file first
- ALWAYS prefer editing existing files in the codebase. NEVER write new files unless explicitly required
- NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User
- Only use emojis if the user explicitly requests it. Avoid writing emojis to files unless asked""",
)
def write_file(
    file_path: Annotated[str, "The absolute path to the file to write (must be absolute, not relative)"],
    content: Annotated[str, "The content to write to the file"],
) -> str:
    """将内容写入指定文件"""
    return fs_write_file(file_path, content)


@mcp.tool(
    name="glob",
    title="Glob",
    description="""- Fast file pattern matching tool that works with any codebase size
- Supports glob patterns like "**/*.js" or "src/**/*.ts"
- Returns matching file paths sorted by modification time
- Use this tool when you need to find files by name patterns
- When you are doing an open ended search that may require multiple rounds of globbing and grepping, use the Agent tool instead
- You have the capability to call multiple tools in a single response. It is always better to speculatively perform multiple searches as a batch that are potentially useful""",
)
def glob(
    pattern: Annotated[str, "The glob pattern to match against (e.g., '**/*.py', 'docs/*.md')"],
    path: Annotated[Optional[str], "The directory to search in. If not specified, the current working directory will be used. IMPORTANT: Omit this field to use the default directory. DO NOT enter 'undefined' or 'null' - simply omit it for the default behavior. Must be a valid directory path if provided"] = None,
    case_sensitive: Annotated[bool, "Whether to be case sensitive"] = False,
    respect_git_ignore: Annotated[bool, "Whether to respect .gitignore"] = True,
) -> str:
    """查找匹配特定glob模式的文件"""
    if not path:
        path = os.getenv("HOME_DIR", os.path.expanduser("~"))  # Default to home directory if not specified
        path = os.path.abspath(path)  # Ensure it's absolute
    return fs_glob(pattern, path, case_sensitive, respect_git_ignore)


@mcp.tool(
    name="search_file_content",
    title="Grep",
    description="""A powerful search tool built on ripgrep

Usage:
- ALWAYS use Grep for search tasks. NEVER invoke `grep` or `rg` as a Bash command. The Grep tool has been optimized for correct permissions and access
- Supports full regex syntax (e.g., "log.*Error", "function\s+\w+")
- Filter files with glob parameter (e.g., "*.js", "**/*.tsx") or type parameter (e.g., "js", "py", "rust")
- Output modes: "content" shows matching lines, "files_with_matches" shows only file paths (default), "count" shows match counts
- Use Task tool for open-ended searches requiring multiple rounds
- Pattern syntax: Uses ripgrep (not grep) - literal braces need escaping (use `interface\{\}` to find `interface{}` in Go code)""",
)
def search_file_content(
    pattern: Annotated[str, "The regular expression pattern to search for in file contents"],
    path: Annotated[Optional[str], "File or directory to search in. Defaults to current working directory"] = None,
    include: Annotated[Optional[str], "Glob pattern to filter files (e.g. \"*.js\", \"*.{ts,tsx}\")"] = None,
) -> str:
    """在指定目录内的文件内容中搜索正则表达式模式"""
    if not path:
        path = os.getenv("HOME_DIR", os.path.expanduser("~"))  # Default to home directory if not specified
        path = os.path.abspath(path)  # Ensure it's absolute
    return fs_search_file_content(pattern, path, include)


@mcp.tool(
    name="replace_in_file",
    title="Edit",
    description="""Performs exact string replacements in files.

Usage:
- You must use your `Read` tool at least once in the conversation before editing. This tool will error if you attempt an edit without reading the file
- When editing text from Read tool output, ensure you preserve the exact indentation (tabs/spaces) as it appears AFTER the line number prefix. The line number prefix format is: spaces + line number + tab. Everything after that tab is the actual file content to match. Never include any part of the line number prefix in the old_string or new_string
- ALWAYS prefer editing existing files in the codebase. NEVER write new files unless explicitly required
- Only use emojis if the user explicitly requests it. Avoid adding emojis to files unless asked
- The edit will FAIL if `old_string` is not unique in the file. Either provide a larger string with more surrounding context to make it unique or use `expected_replacements` to change every instance of `old_string`
- Use `expected_replacements` for replacing and renaming strings across the file. This parameter is useful if you want to rename a variable for instance""",
)
def replace_in_file(
    file_path: Annotated[str, "The absolute path to the file to modify"],
    old_string: Annotated[str, "The text to replace. If empty, will create new file"],
    new_string: Annotated[str, "The text to replace it with (must be different from old_string)"],
    expected_replacements: Annotated[int, "Expected number of replacements"] = 1,
) -> str:
    """用于替换文件中的文本"""
    return fs_replace_in_file(file_path, old_string, new_string, expected_replacements)


@mcp.tool(
    name="read_many_files",
    title="ReadManyFiles",
    description="""Reads content from multiple files specified by paths or glob patterns. For text files, concatenates their contents into a single string.
Primarily designed for text-based files. However, it can also handle images (like .png, .jpg) and PDF (.pdf) files if their filenames or extensions are explicitly included in the 'paths' parameter. For these explicitly requested non-text files, their data is read and included in a format suitable for model consumption (like base64 encoding).

This tool is useful when you need to understand or analyze a collection of files, such as:
- Getting an overview of a codebase or part of it (like all TypeScript files in the 'src' directory)
- Finding where specific functionality is implemented if the user asks broad questions about code
- Reviewing documentation files (like all Markdown files in the 'docs' directory)
- Gathering context from multiple configuration files
- When the user requests "read all files in X directory" or "show me the contents of all Y files"

Use this tool when the user's query implies a need to get content from multiple files simultaneously for contextual analysis or summarization.
For text files, uses default UTF-8 encoding and '--- {filePath} ---' separators between file contents.
Ensure paths are relative to the target directory. Supports glob patterns like 'src/**/*.js'.
Usually skips other binary files unless explicitly requested as images/PDFs.
Excludes by default patterns applicable to common non-text files and large dependency directories unless 'use_default_excludes' is false.""",
)
async def read_many_files(
    paths: Annotated[List[str], "Required. Array of glob patterns or paths relative to the tool's target directory. Examples: ['src/**/*.ts'], ['README.md', 'docs/']"],
    include: Annotated[Optional[List[str]], "Optional. Additional glob patterns to include. These are merged with `paths`. Example: ['*.test.ts'] to specifically add test files"] = None,
    exclude: Annotated[Optional[List[str]], "Optional. Glob patterns to exclude. These are merged with `paths`. Example: ['*.spec.ts'] to specifically exclude test files"] = None,
    recursive: Annotated[bool, "Optional. Whether to search recursively (primarily controlled by `**` in glob patterns). Default is true"] = True,
    use_default_excludes: Annotated[bool, "Optional. Whether to apply a default list of exclude patterns (like node_modules, .git, binary files). Default is true"] = True,
    respect_git_ignore: Annotated[bool, "Optional. Whether to respect .gitignore file rules. Default is true"] = True,
):
    """从多个文件中读取内容"""
    path = os.getenv("HOME_DIR", os.path.expanduser("~"))  # Default to home directory if not specified
    path = os.path.abspath(path)  # Ensure it's absolute
    result = await fs_read_many_files(
        paths,
        include,
        exclude,
        recursive,
        path,
        use_default_excludes,
        respect_git_ignore,
    )
    return {
        "message_content": result.message_content,
        "block_list": result.block_list,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7779, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    logger.info("Starting File System MCP Server...")
    logger.info("Available tools: list_directory, read_file, write_file, glob, search_file_content, replace")

    mcp.run("http", host=args.host, port=args.port, log_level="debug" if args.debug else "info")
