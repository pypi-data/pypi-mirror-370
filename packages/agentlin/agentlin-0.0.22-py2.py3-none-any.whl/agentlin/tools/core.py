import json
import subprocess
import traceback
from typing import Any, Dict, List, Optional, Union, Set

from fastmcp import Client as McpClient
from fastmcp.tools.tool import Tool as McpTool
from mcp.types import ContentBlock, TextContent, ImageContent, AudioContent, ResourceLink, EmbeddedResource
from loguru import logger

from agentlin.core.types import (
    ContentData,
    BaseTool,
    FunctionDefinition,
    FunctionParameters,
    ToolParams,
    ToolResult,
    sanitize_parameters,
)


class DiscoveredMcpTool(BaseTool):
    def __init__(self, client: McpClient, tool: McpTool):
        self.client = client
        self.tool = tool
        super().__init__(
            name=tool.name,
            title=tool.title,
            description=tool.description,
            parameters=tool.parameters,
            strict=True,
        )

    async def execute(self, params: ToolParams) -> ToolResult:
        async with self.client:
            result = await self.client.call_tool(
                name=self.tool.name,
                arguments=params,
            )
        content = result.content
        structured_content = result.structured_content

        message_content: list[ContentData] = []
        for c in content:
            if isinstance(c, TextContent):
                message_content.append({"type": "text", "text": c.text})
            elif isinstance(c, ImageContent):
                message_content.append({"type": "image_url", "image_url": {"url": f"data:{c.mimeType};base64,{c.data}"}})
            elif isinstance(c, AudioContent):
                message_content.append({"type": "input_audio", "input_audio": {"data": f"data:{c.mimeType};base64,{c.data}"}})
            # TODO 暂不支持
            # elif isinstance(c, ResourceLink):
            #     message_content.append({"type": "link", "url": c.url, "title": c.title})
            # elif isinstance(c, EmbeddedResource):
            #     message_content.append({"type": "embed", "url": c.url, "title": c.title})

        block_list = []
        if structured_content:
            if "message_content" in structured_content:
                message_content = structured_content.pop("message_content", [])
            block_list = structured_content.pop("block_list", [])
        if not block_list:
            block_list = message_content
        return ToolResult(
            message_content=message_content,
            block_list=block_list,
        )


class DiscoveredCmdTool(BaseTool):
    def __init__(
        self,
        discovery_cmd: str,
        call_cmd: str,
        name: str,
        description: str,
        parameters: FunctionParameters,
    ):
        self.discovery_cmd = discovery_cmd
        self.call_cmd = call_cmd
        description += f"""

This tool was discovered by executing `{discovery_cmd}` on project root.
When called, this tool will execute `{call_cmd} {name}`.

Tool discovery and call commands can be configured in project/user settings.
"""
        super().__init__(name, name, description, parameters)

    async def execute(self, params: ToolParams) -> ToolResult:
        process = subprocess.Popen(
            [self.call_cmd, self.name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate(input=json.dumps(params).encode())
        code = process.returncode

        stdout_str = stdout.decode()
        stderr_str = stderr.decode()

        if code != 0 or stderr_str:
            text = f"""Stdout: {stdout_str or '(empty)'}
Stderr: {stderr_str or '(empty)'}
Error: (none)
Exit Code: {code}
Signal: (none)"""
            message_content = [{"type": "text", "text": text}]
            block_list = [{"type": "text", "text": text}]
            return ToolResult(message_content, block_list)

        message_content = [{"type": "text", "text": stdout_str}]
        block_list = [{"type": "text", "text": stdout_str}]
        return ToolResult(message_content, block_list)


async def discover_tools_from_command(discovery_cmd: str, call_cmd: str) -> List[DiscoveredCmdTool]:
    """
    Discover tools from command and return a list of DiscoveredCmdTool instances.

    Args:
        discovery_cmd: Command to discover available tools
        call_cmd: Command prefix used to call the tools

    Returns:
        List of DiscoveredCmdTool instances

    Raises:
        RuntimeError: If discovery command fails
        ValueError: If discovery output is not a valid JSON array
    """
    if not discovery_cmd:
        return []

    try:
        proc = subprocess.Popen(discovery_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"Discovery command failed: {stderr.decode()}")

        tools = json.loads(stdout.decode())
        if not isinstance(tools, list):
            raise ValueError("Expected discovery output to be a JSON array")

        functions: List[FunctionDefinition] = []
        for item in tools:
            if isinstance(item, dict):
                if "function_declarations" in item:
                    functions.extend(FunctionDefinition(**f) for f in item["function_declarations"])
                elif "functionDeclarations" in item:
                    functions.extend(FunctionDefinition(**f) for f in item["functionDeclarations"])
                elif "name" in item:
                    functions.append(FunctionDefinition(**item))

        for func in functions:
            sanitize_parameters(func["parameters"])

        # 创建 DiscoveredCmdTool 实例列表
        discovered_tools = []
        for func in functions:
            discovered_tools.append(
                DiscoveredCmdTool(
                    discovery_cmd,
                    call_cmd,
                    func["name"],
                    func.get("description", ""),
                    func["parameters"],
                )
            )

        return discovered_tools
    except Exception as e:
        logger.error(f"Error discovering tools: {e}\n{traceback.format_exc()}")
        return []


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

    def get_function_declarations(self) -> List[FunctionDefinition]:
        return [tool.schema for tool in self.tools.values()]

    def get_all_tools(self) -> List[BaseTool]:
        return list(self.tools.values())

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self.tools.get(name)

    def register_tool(self, tool: BaseTool) -> None:
        if tool.name in self.tools:
            logger.warning(f'Warning: Tool "{tool.name}" already registered. Overwriting.')
        self.tools[tool.name] = tool

    async def discover_tools(self):
        # 清除已发现的工具（根据类型判定）
        self.tools = {k: v for k, v in self.tools.items() if not isinstance(v, DiscoveredCmdTool)}
        # MCP 相关略过，需另实现 discover_mcp_tools
        discovery_cmd = "agentlin discover"
        call_cmd = "agentlin call"

        discovered_tools = await discover_tools_from_command(discovery_cmd, call_cmd)
        for tool in discovered_tools:
            self.register_tool(tool)
