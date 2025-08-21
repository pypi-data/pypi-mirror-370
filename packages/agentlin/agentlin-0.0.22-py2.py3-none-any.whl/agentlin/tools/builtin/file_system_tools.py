import json
import os
from pathlib import Path
import subprocess
from typing import Any, Dict, List, Optional, Union, Set

from loguru import logger

from xlin import save_text
from agentlin.core.types import (
    BaseTool,
    FunctionDefinition,
    FunctionParameters,
    ToolParams,
    ToolResult,
    sanitize_parameters,
)
from agentlin.tools.tool_read_many_files import read_many_files
from agentlin.tools.tool_bash import execute_command
from agentlin.tools.tool_file_system import list_directory, read_file, write_file, glob, search_file_content_advanced, replace_in_file
from agentlin.tools.tool_todo import todo_write, todo_read, TodoItem


class ReadManyFilesTool(BaseTool):
    """
    用于读取多个文件内容的工具。

    支持通过路径或 glob 模式指定文件，对文本文件连接内容，
    对图像、PDF、音频和视频文件返回 base64 编码数据。
    """

    def __init__(self, target_directory: str = None):
        """
        初始化多文件读取工具

        Args:
            target_directory: 目标目录，如果为 None 则使用当前工作目录
        """
        self.target_directory = target_directory or os.getenv("TARGET_DIRECTORY", os.getcwd())

        parameters = {
            "type": "object",
            "properties": {
                "paths": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "minLength": 1,
                    },
                    "minItems": 1,
                    "description": "必需。相对于工具目标目录的 glob 模式或路径数组。例如：['src/**/*.ts'], ['README.md', 'docs/']",
                },
                "include": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "minLength": 1,
                    },
                    "description": "可选。要包含的额外 glob 模式。这些与 `paths` 合并。例如：['*.test.ts'] 来专门添加测试文件",
                    "default": [],
                },
                "exclude": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "minLength": 1,
                    },
                    "description": "可选。要排除的文件/目录的 glob 模式。如果 useDefaultExcludes 为 true，则添加到默认排除列表。例如：['**/*.log', 'temp/']",
                    "default": [],
                },
                "recursive": {
                    "type": "boolean",
                    "description": "可选。是否递归搜索（主要由 glob 模式中的 `**` 控制）。默认为 true",
                    "default": True,
                },
                "useDefaultExcludes": {
                    "type": "boolean",
                    "description": "可选。是否应用默认排除模式列表（如 node_modules、.git、二进制文件）。默认为 true",
                    "default": True,
                },
                "respect_git_ignore": {
                    "type": "boolean",
                    "description": "可选。是否遵循 .gitignore 模式。默认为 true",
                    "default": True,
                },
            },
            "required": ["paths"],
            "additionalProperties": False,
        }
        super().__init__(
            name="read_many_files",
            title="读取多个文件",
            description="""
从由路径或 glob 模式指定的多个文件中读取内容。对于文本文件，将其内容连接到单个字符串中。
主要设计用于基于文本的文件。但是，如果在 'paths' 参数中明确包含文件名或扩展名，
它也可以处理图像（如 .png、.jpg）和 PDF (.pdf) 文件。对于这些明确请求的非文本文件，
其数据以适合模型使用的格式（如 base64 编码）读取和包含。

此工具在需要理解或分析文件集合时很有用，例如：
- 获取代码库或其部分的概览（如 'src' 目录中的所有 TypeScript 文件）
- 如果用户询问关于代码的广泛问题，找到特定功能的实现位置
- 审查文档文件（如 'docs' 目录中的所有 Markdown 文件）
- 从多个配置文件收集上下文
- 当用户要求"读取 X 目录中的所有文件"或"显示所有 Y 文件的内容"时

当用户的查询暗示需要同时获取多个文件的内容以进行上下文分析或总结时，请使用此工具。
对于文本文件，使用默认的 UTF-8 编码和文件内容之间的 '--- {filePath} ---' 分隔符。
确保路径相对于目标目录。支持 'src/**/*.js' 等 glob 模式。
除非明确请求为图像/PDF，否则通常跳过其他二进制文件。
除非 'useDefaultExcludes' 为 false，否则默认排除适用于常见非文本文件和大型依赖目录。
        """.strip(),
            parameters=parameters,
        )

    async def execute(self, params: ToolParams) -> ToolResult:
        """执行多文件读取操作

        Args:
            params: 包含读取文件所需参数的字典

        Returns:
            ToolResult 对象，包含处理结果
        """
        paths = params.get('paths', [])
        include = params.get('include', [])
        exclude = params.get('exclude', [])
        recursive = params.get('recursive', True)
        use_default_excludes = params.get('useDefaultExcludes', True)
        respect_git_ignore = params.get('respect_git_ignore', True)

        return await read_many_files(
            paths=paths,
            include=include,
            exclude=exclude,
            recursive=recursive,
            target_directory=self.target_directory,
            use_default_excludes=use_default_excludes,
            respect_git_ignore=respect_git_ignore,
        )

class ListDirectoryTool(BaseTool):
    """
    列出指定目录中的文件和子目录的工具。
    """

    def __init__(self, target_directory: Optional[str] = None):
        """
        初始化目录列表工具

        Args:
            target_directory: 目标目录，如果为 None 则使用当前工作目录
        """
        self.target_directory = target_directory or os.getenv("TARGET_DIRECTORY", os.getcwd())

        parameters = {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "要列出的目录的绝对路径（必须是绝对路径，不是相对路径）",
                    "default": self.target_directory
                },
                "ignore": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "可选的要忽略的 glob 模式数组",
                    "default": []
                },
                "respect_git_ignore": {
                    "type": "boolean",
                    "description": "是否遵循 .gitignore 文件规则",
                    "default": True
                },
            },
            "required": ["path", "ignore", "respect_git_ignore"],
            "additionalProperties": False,
        }

        super().__init__(
            name="LS",
            title="LS",
            description="列出指定目录中的文件和子目录。path 参数必须是绝对路径，不是相对路径。您可以选择性地提供一个要忽略的 glob 模式数组。如果您知道要搜索的目录，通常应优先使用 Glob 和 Grep 工具。",
            parameters=parameters,
        )

    async def execute(self, params: ToolParams) -> ToolResult:
        """执行目录列表操作

        Args:
            params: 包含列表操作所需参数的字典

        Returns:
            ToolResult 对象，包含目录内容
        """
        path = params.get('path', self.target_directory)
        ignore = params.get('ignore', [])
        respect_git_ignore = params.get('respect_git_ignore', True)

        result_text = list_directory(path, ignore, respect_git_ignore)

        result = ToolResult(
            message_content=[{"type": "text", "text": result_text}],
            block_list=[{"type": "text", "text": result_text}],
        )
        return result


class ReadFileTool(BaseTool):
    """
    从本地文件系统读取文件的工具。
    """

    def __init__(self, target_directory: Optional[str] = None):
        """
        初始化文件读取工具

        Args:
            target_directory: 目标目录，如果为 None 则使用当前工作目录
        """
        self.target_directory = target_directory or os.getenv("TARGET_DIRECTORY", os.getcwd())

        parameters = {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "要读取的文件的绝对路径"
                },
                "offset": {
                    "type": "integer",
                    "description": "开始读取的行号。仅在文件太大无法一次性读取时提供",
                    "minimum": 1
                },
                "limit": {
                    "type": "integer",
                    "description": "要读取的行数。仅在文件太大无法一次性读取时提供",
                    "minimum": 1
                },
            },
            "required": ["path", "offset", "limit"],
            "additionalProperties": False,
        }

        super().__init__(
            name="Read",
            title="Read",
            description="""从本地文件系统读取文件。您可以使用此工具直接访问任何文件。

假设此工具能够读取机器上的所有文件。如果用户提供文件路径，请假设该路径有效。读取不存在的文件是可以的；将返回错误。

用法：

- file_path 参数必须是绝对路径，不是相对路径
- 默认情况下，从文件开头读取最多 2000 行
- 您可以选择指定行偏移量和限制（特别适用于长文件），但建议通过不提供这些参数来读取整个文件
- 任何超过 2000 个字符的行都将被截断
- 结果使用 cat -n 格式返回，行号从 1 开始
- 此工具允许读取图像（例如 PNG、JPG 等）。读取图像文件时，内容以视觉方式呈现。
- 此工具可以读取 PDF 文件 (.pdf)。PDF 逐页处理，提取文本和视觉内容进行分析。
- 您有能力在单个响应中调用多个工具。批量推测性地读取可能有用的多个文件总是更好的。
""",
            parameters=parameters,
        )

    async def execute(self, params: ToolParams) -> ToolResult:
        """执行文件读取操作

        Args:
            params: 包含读取文件所需参数的字典

        Returns:
            ToolResult 对象，包含文件内容
        """
        path = params.get('path')
        offset = params.get('offset')
        limit = params.get('limit')

        file_content = read_file(path, offset, limit)

        result = ToolResult()

        # 如果返回的是字典（图像或PDF），需要转换为适当的内容类型
        if isinstance(file_content, dict) and "inlineData" in file_content:
            inline_data = file_content["inlineData"]
            if inline_data["mimeType"].startswith("image/"):
                result.append_content({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{inline_data['mimeType']};base64,{inline_data['data']}"
                    }
                })
            else:  # PDF或其他二进制文件
                result.append_content({
                    "type": "text",
                    "text": f"Binary file content (MIME: {inline_data['mimeType']}): {inline_data['data'][:20]}..."
                })
        else:
            # 文本文件直接返回字符串
            result.append_content({
                "type": "text",
                "text": str(file_content)
            })

        return result


class WriteFileTool(BaseTool):
    """
    向本地文件系统写入文件的工具。
    """

    def __init__(self, target_directory: Optional[str] = None):
        """
        初始化文件写入工具

        Args:
            target_directory: 目标目录，如果为 None 则使用当前工作目录
        """
        self.target_directory = target_directory or os.getenv("TARGET_DIRECTORY", os.getcwd())

        parameters = {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要写入的文件的绝对路径（必须是绝对路径，不是相对路径）"
                },
                "content": {
                    "type": "string",
                    "description": "要写入文件的内容"
                },
            },
            "required": ["file_path", "content"],
            "additionalProperties": False,
        }

        super().__init__(
            name="Write",
            title="Write",
            description="""向本地文件系统写入文件。

用法：
- 如果提供的路径处有现有文件，此工具将覆盖该文件
- 如果这是现有文件，您必须首先使用 Read 工具读取文件的内容。如果您没有首先读取文件，此工具将失败
- 始终优先编辑代码库中的现有文件。除非明确需要，否则永远不要写入新文件
- 永远不要主动创建文档文件 (*.md) 或 README 文件。只有在用户明确请求时才创建文档文件
- 除非用户明确请求，否则只使用表情符号。除非被询问，否则避免向文件写入表情符号
""",
            parameters=parameters,
        )

    async def execute(self, params: ToolParams) -> ToolResult:
        """执行文件写入操作

        Args:
            params: 包含写入文件所需参数的字典

        Returns:
            ToolResult 对象，包含写入结果
        """
        file_path = params.get('file_path')
        content = params.get('content')
        path = Path(file_path)
        if not path.is_absolute():
            # 如果路径不是绝对路径，则将其转换为绝对路径
            file_path = os.path.join(self.target_directory, file_path)
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        result_text = write_file(file_path, content)

        result = ToolResult(
            message_content=[{"type": "text", "text": result_text}],
            block_list=[{"type": "text", "text": result_text}],
        )

        return result


class GlobTool(BaseTool):
    """
    快速文件模式匹配工具。
    """

    def __init__(self, target_directory: Optional[str] = None):
        """
        初始化 Glob 工具

        Args:
            target_directory: 目标目录，如果为 None 则使用当前工作目录
        """
        self.target_directory = target_directory or os.getenv("TARGET_DIRECTORY", os.getcwd())

        parameters = {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "要匹配的 glob 模式（例如，'**/*.py'，'docs/*.md'）"
                },
                "path": {
                    "type": "string",
                    "description": "要搜索的目录。如果未指定，将使用当前工作目录。重要：省略此字段以使用默认目录。不要输入 'undefined' 或 'null' - 对于默认行为，只需省略它。如果提供，必须是有效的目录路径",
                    "default": ""
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "是否区分大小写",
                    "default": False
                },
                "respect_git_ignore": {
                    "type": "boolean",
                    "description": "是否遵循 .gitignore",
                    "default": True
                },
            },
            "required": ["pattern", "path", "case_sensitive", "respect_git_ignore"],
            "additionalProperties": False,
        }

        super().__init__(
            name="Glob",
            title="Glob",
            description="""- 适用于任何代码库大小的快速文件模式匹配工具
- 支持像 "**/*.js" 或 "src/**/*.ts" 这样的 glob 模式
- 返回按修改时间排序的匹配文件路径
- 当您需要按名称模式查找文件时使用此工具
- 当您进行可能需要多轮全局搜索和搜索的开放性搜索时，请改用 Agent 工具
- 您有能力在单个响应中调用多个工具。批量推测性地执行可能有用的多个搜索总是更好的""",
            parameters=parameters,
        )

    async def execute(self, params: ToolParams) -> ToolResult:
        """执行 Glob 搜索操作

        Args:
            params: 包含搜索所需参数的字典

        Returns:
            ToolResult 对象，包含匹配的文件路径
        """

        pattern = params.get('pattern')
        path = params.get('path', self.target_directory)
        case_sensitive = params.get('case_sensitive', False)
        respect_git_ignore = params.get('respect_git_ignore', True)

        result_text = glob(pattern, path, case_sensitive, respect_git_ignore)

        result = ToolResult(
            message_content=[{"type": "text", "text": result_text}],
            block_list=[{"type": "text", "text": result_text}],
        )

        return result


class GrepTool(BaseTool):
    """
    基于 ripgrep-python 的强大搜索工具。
    """

    def __init__(self, target_directory: Optional[str] = None):
        """
        初始化文件内容搜索工具

        Args:
            target_directory: 目标目录，如果为 None 则使用当前工作目录
        """
        self.target_directory = target_directory or os.getenv("TARGET_DIRECTORY", os.getcwd())

        parameters = {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "要在文件内容中搜索的正则表达式模式",
                },
                "path": {
                    "type": "string",
                    "description": "要搜索的文件或目录。默认为当前工作目录",
                    "default": "",
                },
                "include": {
                    "type": "string",
                    "description": "用于过滤文件的 Glob 模式（例如 \"*.js\"，\"*.{ts,tsx}\"）",
                },
                "case_insensitive": {
                    "type": "boolean",
                    "description": "是否进行大小写不敏感搜索",
                    "default": False,
                },
                "context_lines": {
                    "type": "integer",
                    "description": "匹配行前后显示的上下文行数（类似 ripgrep 的 -C 选项）",
                    "minimum": 0,
                    "default": 0,
                },
                "max_results": {
                    "type": "integer",
                    "description": "限制返回的最大结果数量",
                    "minimum": 1,
                    "default": 100,
                },
            },
            "required": ["pattern", "path", "include", "case_insensitive", "context_lines", "max_results"],
            "additionalProperties": False,
        }

        super().__init__(
            name="Grep",
            title="Grep",
            description=r"""A powerful search tool built on ripgrep

Usage:

- ALWAYS use Grep for search tasks. NEVER invoke `grep` or `rg` as a Bash command. The Grep tool has been optimized for correct permissions and access.
- Supports full regex syntax (e.g., "log.*Error", "function\s+\w+")
- Filter files with glob parameter (e.g., "*.js", "**/*.tsx") or type parameter (e.g., "js", "py", "rust")
- Output modes: "content" shows matching lines, "files_with_matches" shows only file paths (default), "count" shows match counts
- Use Task tool for open-ended searches requiring multiple rounds
- Pattern syntax: Uses ripgrep (not grep) - literal braces need escaping (use `interface\{\}` to find `interface{}` in Go code)
- Multiline matching: By default patterns match within single lines only. For cross-line patterns like `struct \{[\s\S]*?field`, use `multiline: true`""",
            parameters=parameters,
        )

    async def execute(self, params: ToolParams) -> ToolResult:
        """执行文件内容搜索操作

        Args:
            params: 包含搜索所需参数的字典

        Returns:
            ToolResult 对象，包含搜索结果
        """
        pattern = params.get('pattern')
        path = params.get('path', self.target_directory)
        include = params.get('include')
        case_insensitive = params.get('case_insensitive', False)
        context_lines = params.get('context_lines', 0)
        max_results = params.get('max_results', 100)

        # 使用新的搜索函数，它支持 ripgrep-python 和额外参数
        result_text = search_file_content_advanced(
            pattern=pattern,
            path=path,
            include=include,
            case_insensitive=case_insensitive,
            context_lines=context_lines,
            max_results=max_results
        )

        result = ToolResult(
            message_content=[{"type": "text", "text": result_text}],
            block_list=[{"type": "text", "text": result_text}],
        )
        return result


class ReplaceInFileTool(BaseTool):
    """
    在文件中执行精确字符串替换的工具。
    """

    def __init__(self, target_directory: Optional[str] = None):
        """
        初始化文件替换工具

        Args:
            target_directory: 目标目录，如果为 None 则使用当前工作目录
        """
        self.target_directory = target_directory or os.getenv("TARGET_DIRECTORY", os.getcwd())

        parameters = {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要修改的文件的绝对路径"
                },
                "old_string": {
                    "type": "string",
                    "description": "要替换的文本。如果为空，将创建新文件"
                },
                "new_string": {
                    "type": "string",
                    "description": "替换的文本（必须与 old_string 不同）"
                },
                "expected_replacements": {
                    "type": "integer",
                    "description": "预期的替换次数",
                    "default": 1,
                    "minimum": 1
                },
            },
            "required": ["file_path", "old_string", "new_string", "expected_replacements"],
            "additionalProperties": False,
        }

        super().__init__(
            name="Edit",
            title="Edit",
            description="""在文件中执行精确的字符串替换。

用法：
- 在编辑之前，您必须在对话中至少使用一次 `Read` 工具。如果您尝试在不读取文件的情况下进行编辑，此工具会出错
- 从 Read 工具输出编辑文本时，确保您保留行号前缀之后出现的精确缩进（制表符/空格）。行号前缀格式为：空格 + 行号 + 制表符。该制表符之后的所有内容都是要匹配的实际文件内容。永远不要在 old_string 或 new_string 中包含行号前缀的任何部分
- 始终优先编辑代码库中的现有文件。除非明确需要，否则永远不要写入新文件
- 除非用户明确请求，否则只使用表情符号。除非被询问，否则避免向文件添加表情符号
- 如果 `old_string` 在文件中不唯一，编辑将失败。要么提供一个具有更多周围上下文的较大字符串以使其唯一，要么使用 `expected_replacements` 来更改 `old_string` 的每个实例
- 使用 `expected_replacements` 来替换和重命名整个文件中的字符串。如果您想重命名变量，此参数很有用
""",
            parameters=parameters,
        )

    async def execute(self, params: ToolParams) -> ToolResult:
        """执行文件内容替换操作

        Args:
            params: 包含替换操作所需参数的字典

        Returns:
            ToolResult 对象，包含替换结果
        """
        file_path = params.get('file_path')
        old_string = params.get('old_string')
        new_string = params.get('new_string')
        expected_replacements = params.get('expected_replacements', 1)

        result_text = replace_in_file(file_path, old_string, new_string, expected_replacements)

        result = ToolResult(
            message_content=[{"type": "text", "text": result_text}],
            block_list=[{"type": "text", "text": result_text}],
        )

        return result


class BashTool(BaseTool):
    """
    执行 bash 命令的工具。
    """

    def __init__(self, target_directory: Optional[str] = None):
        """
        初始化 Bash 工具

        Args:
            target_directory: 目标目录，如果为 None 则使用当前工作目录
        """
        self.target_directory = target_directory or os.getenv("TARGET_DIRECTORY", os.getcwd())

        parameters = {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "要执行的 bash 命令。确保如果包含空格则正确引用。"
                },
                "timeout": {
                    "type": "integer",
                    "description": "可选的超时时间（毫秒）（最大 600000）",
                    "default": 120000,
                    "minimum": 1000,
                    "maximum": 600000
                },
                "description": {
                    "type": "string",
                    "description": "对此命令作用的清晰、简洁的描述，5-10 个词"
                },
            },
            "required": ["command", "timeout", "description"],
            "additionalProperties": False,
        }

        super().__init__(
            name="Bash",
            title="Bash",
            description="""在持久shell会话中执行给定的bash命令，可选超时，确保适当的处理和安全措施。

执行命令之前，请按照以下步骤：

1. 目录验证：
    - 如果命令将创建新目录或文件，首先使用 LS 工具验证父目录存在且是正确的位置
    - 例如，运行 "mkdir foo/bar" 之前，首先使用 LS 检查 "foo" 存在且是预期的父目录

2. 命令执行：
    - 始终用双引号引用包含空格的文件路径（例如，cd "path with spaces/file.txt"）
    - 正确引用的示例：
    - cd "/Users/name/My Documents"（正确）
    - cd /Users/name/My Documents（不正确 - 将失败）
    - python "/path/with spaces/script.py"（正确）
    - python /path/with spaces/script.py（不正确 - 将失败）
    - 确保正确引用后，执行命令。
    - 捕获命令的输出。

用法注意事项：
- command 参数是必需的。
- 您可以指定可选的超时时间（毫秒）（最多 600000ms / 10 分钟）。如果未指定，命令将在 120000ms（2 分钟）后超时。
- 如果您能用 5-10 个词清晰、简洁地描述此命令的作用，这将很有帮助。
- 如果输出超过 30000 个字符，输出将在返回给您之前被截断。
- 非常重要：您必须避免使用像 `find` 和 `grep` 这样的搜索命令。请改用 Grep、Glob 或 Task 进行搜索。您必须避免使用像 `cat`、`head`、`tail` 和 `ls` 这样的读取工具，并使用 Read 和 LS 来读取文件。
- 如果您仍然需要运行 `grep`，请停止。始终首先使用 `rg`（ripgrep），所有用户都已预安装。
- 发出多个命令时，使用 ';' 或 '&&' 运算符分隔它们。不要使用换行符（引用字符串中的换行符是可以的）。
- 尽量通过使用绝对路径和避免使用 `cd` 来在整个会话中保持当前工作目录。如果用户明确要求，您可以使用 `cd`。
""",
            parameters=parameters,
        )

    async def execute(self, params: ToolParams) -> ToolResult:
        """执行 bash 命令

        Args:
            params: 包含命令执行所需参数的字典

        Returns:
            ToolResult 对象，包含命令执行结果
        """
        command = params.get('command')
        timeout = params.get('timeout', 120000)
        description = params.get('description')

        result_dict = await execute_command(command, self.target_directory, timeout)


        # 格式化命令执行结果
        output_text = f"Command: {command}\n"
        if description:
            output_text += f"Description: {description}\n"
        output_text += f"Exit Code: {result_dict['code']}\n"
        output_text += f"Executed At: {result_dict['executedAt']}\n\n"

        if result_dict['success']:
            if result_dict['stdout']:
                output_text += f"stdout:\n{result_dict['stdout']}\n"
            if result_dict['stderr']:
                output_text += f"stderr:\n{result_dict['stderr']}\n"
        else:
            output_text += f"Error: {result_dict.get('error', 'Unknown error')}\n"
            if result_dict['stderr']:
                output_text += f"stderr:\n{result_dict['stderr']}\n"

        result = ToolResult(
            message_content=[{"type": "text", "text": output_text}],
            block_list=[{"type": "text", "text": output_text}],
        )

        return result


class TodoWriteTool(BaseTool):
    """
    创建和管理结构化任务列表的工具。
    """

    def __init__(self, target_directory: Optional[str] = None):
        """
        初始化 Todo 写入工具

        Args:
            target_directory: 目标目录，如果为 None 则使用当前工作目录
        """
        self.target_directory = target_directory or os.getenv("TARGET_DIRECTORY", os.getcwd())

        parameters = {
            "type": "object",
            "properties": {
                "todos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "任务的唯一标识符",
                            },
                            "content": {
                                "type": "string",
                                "description": "任务描述",
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed"],
                                "description": "任务状态：'pending'、'in_progress' 或 'completed'",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                                "description": "任务优先级：'high'、'medium' 或 'low'",
                            },
                        },
                        "required": ["id", "content", "status", "priority"],
                        "additionalProperties": False,
                    },
                    "description": "todo 项目列表，包含任务内容、状态和优先级",
                },
            },
            "required": ["todos"],
            "additionalProperties": False,
        }

        super().__init__(
            name="TodoWrite",
            title="TodoWrite",
            description="""使用此工具为当前编码会话创建和管理结构化任务列表。这有助于您跟踪进度、组织复杂任务，并向用户展示彻底性。
它还帮助用户了解任务进度和其请求的总体进度。

## 何时使用此工具
在以下场景中主动使用此工具：

1. 复杂的多步骤任务 - 当任务需要 3 个或更多不同的步骤或操作时
2. 非平凡和复杂的任务 - 需要仔细规划或多种操作的任务
3. 用户明确请求 todo 列表 - 当用户直接要求您使用 todo 列表时
4. 用户提供多个任务 - 当用户提供要完成的事项列表（编号或逗号分隔）时
5. 收到新指令后 - 立即将用户要求作为 todo 捕获
6. 当您开始处理任务时 - 在开始工作前将其标记为 in_progress。理想情况下，您应该一次只有一个 todo 为 in_progress
7. 完成任务后 - 将其标记为已完成，并添加在实施过程中发现的任何新后续任务

## 何时不使用此工具

在以下情况下跳过使用此工具：
1. 只有一个简单直接的任务
2. 任务很简单，跟踪它不会带来组织上的好处
3. 任务可以在少于 3 个简单步骤中完成
4. 任务纯粹是对话或信息性的

注意：如果只有一个简单任务要做，您不应该使用此工具。在这种情况下，最好直接执行任务。

## 任务状态和管理

1. **任务状态**：使用这些状态跟踪进度：
   - pending：任务尚未开始
   - in_progress：当前正在处理（一次限制为一个任务）
   - completed：任务成功完成

2. **任务管理**：
   - 在工作时实时更新任务状态
   - 完成后立即将任务标记为完成（不要批量完成）
   - 在任何时间只有一个任务为 in_progress
   - 在开始新任务之前完成当前任务
   - 从列表中完全删除不再相关的任务

3. **任务完成要求**：
   - 只有在您完全完成任务时才将其标记为已完成
   - 如果遇到错误、阻塞或无法完成，请保持任务为 in_progress
   - 当被阻塞时，创建一个新任务描述需要解决的问题
   - 如果出现以下情况，永远不要将任务标记为已完成：
     - 测试失败
     - 实施不完整
     - 遇到未解决的错误
     - 无法找到必要的文件或依赖项

4. **任务分解**：
   - 创建具体、可操作的项目
   - 将复杂任务分解为更小、可管理的步骤
   - 使用清晰、描述性的任务名称

有疑问时，使用此工具。主动进行任务管理展示了专注性，并确保您成功完成所有要求。""",
            parameters=parameters,
        )

    async def execute(self, params: ToolParams) -> ToolResult:
        """执行 todo 写入操作

        Args:
            params: 包含写入 todo 所需参数的字典

        Returns:
            ToolResult 对象，包含更新的 todo 列表
        """
        todos = params.get('todos', [])

        # 使用默认的 todos.json 文件路径
        file_path = os.path.join(self.target_directory, "todos.json")

        result = await todo_write(file_path, todos)
        return result


class TodoReadTool(BaseTool):
    """
    查看当前 todo 列表和任务进度的工具。
    """

    def __init__(self, target_directory: Optional[str] = None):
        """
        初始化 Todo 读取工具

        Args:
            target_directory: 目标目录，如果为 None 则使用当前工作目录
        """
        self.target_directory = target_directory or os.getenv("TARGET_DIRECTORY", os.getcwd())

        parameters = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

        super().__init__(
            name="TodoRead",
            title="TodoRead",
            description="""查看当前 todo 列表和任务进度。""",
            parameters=parameters,
        )

    async def execute(self, params: ToolParams) -> ToolResult:
        """执行 todo 读取操作

        Args:
            params: 包含读取 todo 所需参数的字典

        Returns:
            ToolResult 对象，包含 todo 列表内容
        """
        # 使用默认的 todos.json 文件路径
        file_path = os.path.join(self.target_directory, "todos.json")

        result = await todo_read(file_path)
        return result


class MemoryTool(BaseTool):
    """
    用于访问和管理 Agent 的记忆的工具。
    """

    def __init__(self, target_directory: Optional[str] = None):
        """
        初始化 Memory 工具

        Args:
            target_directory: 目标目录，如果为 None 则使用当前工作目录
        """
        self.target_directory = target_directory or os.getenv("TARGET_DIRECTORY", os.getcwd())

        parameters = {
            "type": "object",
            "properties": {
                "memory": {
                    "type": "string",
                    "description": "要存储的记忆内容。",
                },
            },
            "required": ["memory"],
            "additionalProperties": False,
        }

        super().__init__(
            name="SaveMemory",
            title="SaveMemory",
            description="""保存特定信息或事实到长期记忆。使用结构化的 markdown 格式，越详细越好。""",
            parameters=parameters,
        )
        self.write_tool = WriteFileTool(target_directory=self.target_directory)

    async def execute(self, params: ToolParams) -> ToolResult:
        """执行记忆操作

        Args:
            params: 包含写入记忆所需参数的字典

        Returns:
            ToolResult 对象，包含写入结果
        """
        memory_filepath = Path(self.target_directory) / "memory.md"
        if not memory_filepath.exists():
            memory_filepath.parent.mkdir(parents=True, exist_ok=True)
            save_text("", memory_filepath)
        return await self.write_tool.execute({
            "file_path": memory_filepath,
            "content": params.get("memory", "")
        })


# target_directory = os.getcwd()
# tools = [
#   ReadManyFilesTool(target_directory=target_directory),
#   ListDirectoryTool(target_directory=target_directory),
#   ReadFileTool(target_directory=target_directory),
#   WriteFileTool(target_directory=target_directory),
#   GlobTool(target_directory=target_directory),
#   GrepTool(target_directory=target_directory),
#   ReplaceInFileTool(target_directory=target_directory),
#   BashTool(target_directory=target_directory),
#   TodoWriteTool(target_directory=target_directory),
#   TodoReadTool(target_directory=target_directory),
#   MemoryTool(target_directory=target_directory),
# ]