import copy
import os
import re
from typing_extensions import Any, Union, Optional
from pathlib import Path

import yaml
from loguru import logger
from xlin import ls, load_text, xmap_async, load_text
from agentlin.core.types import *



class CodeInterpreterConfig(BaseModel):
    jupyter_host: str  # Jupyter host URL
    jupyter_port: str  # Jupyter port
    jupyter_token: str  # Jupyter token
    jupyter_timeout: int  # Jupyter timeout
    jupyter_username: str  # Jupyter username


class SubAgentConfig(BaseModel):
    """
    Configuration for a sub-agent.
    """

    id: str
    name: str
    description: str
    model: Optional[str] = None  # Optional model name
    developer_prompt: str
    code_for_agent: str
    code_for_interpreter: str
    allowed_tools: list[str] = ["*"]


BUILTIN_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "CodeInterpreter",
            "description": "在受限、安全的沙盒环境中执行 Python 3 代码的解释器，可用于数据处理、科学计算、自动化脚本、可视化等任务，支持大多数标准库及常见第三方科学计算库。",
            "parameters": {
                "type": "object",
                "required": ["code"],
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "要执行的 Python 代码",
                    }
                },
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Task",
            "description": """\
Launch a new task to handle complex, multi-step tasks autonomously.

## Available Agent Types
Available agent types and the tools they have access to:
{{subagents}}

## Alert
When using the Task tool, you must specify a 'name' parameter to select which agent to use.

When to use the Task tool:
- For complex, multi-step tasks that require autonomous handling.

Usage notes:
1. Launch multiple agents concurrently whenever possible to maximize performance.
2. The agent will return a single message back to you.
3. Each agent invocation is stateless.
4. Your prompt should contain a highly detailed task description.
5. Clearly tell the agent whether you expect it to write code or do research.""",
            "parameters": {
                "type": "object",
                "required": ["name", "description", "prompt"],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The type of specialized agent to use for this task",
                    },
                    "description": {
                        "type": "string",
                        "description": "A short (3-5 word) description of the task",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "The task for the agent to perform",
                    },
                },
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
]

def _extract_developer_prompt(markdown_content: str) -> str:
    """Extract the main content before any code sections."""
    # Split by code section headers
    code_section_pattern = r"\n## Code for (Agent|Interpreter)"
    parts = re.split(code_section_pattern, markdown_content)

    if parts:
        # Return the first part (before any code sections)
        return parts[0].strip()

    return markdown_content.strip()


def _extract_code_section(markdown_content: str, section_name: str) -> Optional[str]:
    """Extract code from a specific section."""
    # Pattern to match: ## Section Name followed by code block
    pattern = rf"## {re.escape(section_name)}\s*\n```(?:python)?\s*\n(.*?)\n```"
    match = re.search(pattern, markdown_content, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return None


def parse_config_from_markdown(text: str) -> tuple[dict, str, Optional[str], Optional[str]]:
    """
    Load a agent configuration from a markdown file.

    Expected format:
    ---
    name: agent-name
    description: Agent description
    model: model-name (optional)
    allowed_tools: ["tool1", "tool2"] (optional, defaults to ["*"])
    ---

    Agent prompt content here...

    ## Code for Agent (optional)
    ```python
    # Code specific for agent
    ```

    ## Code for Interpreter (optional)
    ```python
    # Code specific for interpreter
    ```
    """
    # Parse YAML front matter
    front_matter_pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(front_matter_pattern, text, re.DOTALL)

    if not match:
        raise ValueError("No valid front matter found")

    yaml_content, markdown_content = match.groups()

    try:
        config = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML: {e}")

    # Extract developer prompt (everything before code sections)
    developer_prompt = _extract_developer_prompt(markdown_content)

    # Extract code sections
    code_for_agent = _extract_code_section(markdown_content, "Code for Agent")
    code_for_interpreter = _extract_code_section(markdown_content, "Code for Interpreter")

    return config, developer_prompt, code_for_agent, code_for_interpreter


async def load_subagent(path: str) -> Optional[SubAgentConfig]:
    """
    Load a sub-agent configuration from a markdown file.

    Expected format:
    ---
    name: agent-name
    description: Agent description
    model: model-name (optional)
    allowed_tools: ["tool1", "tool2"] (optional, defaults to ["*"])
    ---

    Agent prompt content here...

    ## Code for Agent (optional)
    ```python
    # Code specific for agent
    ```

    ## Code for Interpreter (optional)
    ```python
    # Code specific for interpreter
    ```
    """
    try:
        text = load_text(path)
        if not text:
            return None

        config, developer_prompt, code_for_agent, code_for_interpreter = parse_config_from_markdown(text)

        # Extract required fields
        name = config.get("name")
        description = config.get("description")
        model = config.get("model")  # Optional model name

        if not name or not description:
            print(f"Missing required fields (name, description) in {path}")
            return None

        # Generate ID from file path
        file_path = Path(path)
        agent_id = file_path.stem

        return SubAgentConfig(
            id=agent_id,
            name=name,
            description=description,
            model=model,
            developer_prompt=developer_prompt,
            code_for_agent=code_for_agent or "",
            code_for_interpreter=code_for_interpreter or "",
            allowed_tools=config.get("allowed_tools", ["*"]),
        )

    except ValueError as e:
        print(f"Error parsing config from {path}: {e}")
        return None
    except Exception as e:
        print(f"Error loading subagent from {path}: {e}")
        return None


async def load_subagents(dir_path: Union[str, list[str]], env: dict[str, Union[str, dict]]={}) -> list[SubAgentConfig]:
    paths = ls(dir_path, filter=lambda f: f.name.endswith(".md"))
    if not paths:
        return []
    results = await xmap_async(paths, load_subagent, is_async_work_func=True)
    subagents: list[SubAgentConfig] = []
    for subagent in results:
        if subagent and isinstance(subagent, SubAgentConfig):
            if env:
                for key, value in env.items():
                    value = os.getenv(key, value)
                    subagent.developer_prompt = subagent.developer_prompt.replace("{{" + key + "}}", str(value))
                    if subagent.code_for_agent:
                        subagent.code_for_agent = subagent.code_for_agent.replace("{{" + key + "}}", str(value))
                    if subagent.code_for_interpreter:
                            subagent.code_for_interpreter = subagent.code_for_interpreter.replace("{{" + key + "}}", str(value))
            subagents.append(subagent)
        else:
            logger.warning(f"Invalid subagent: {subagent}")
    return subagents


class AgentConfig(BaseModel):
    name: str
    description: str
    developer_prompt: str
    code_for_agent: str
    code_for_interpreter: str
    allowed_tools: list[str] = ["*"]

    model: str

    tool_mcp_config: dict[str, Any] = {
        "mcpServers": {
            "aime_sse_server": {"url": "http://localhost:7778/tool_mcp"},
        }
    }
    code_mcp_config: dict[str, Any] = {
        "mcpServers": {
            "aime_sse_server": {"url": "http://localhost:7778/code_mcp"},
        }
    }

    code_interpreter_config: CodeInterpreterConfig
    inference_args: dict[str, Any] = {}

    # 内置工具列表
    builtin_tools: list[dict[str, Any]] = copy.deepcopy(BUILTIN_TOOLS)
    builtin_subagents: list[SubAgentConfig] = []

    def get_builtin_tools(self, allowed_subagents: Optional[list[str]] = None) -> list[dict[str, Any]]:
        """获取内置工具列表"""
        for tool in self.builtin_tools:
            if tool["function"]["name"] == "Task":
                # 如果内置工具中已经有 Task 工具，则更新 description
                subagents_texts = []
                subagent_names = []
                for subagent in self.builtin_subagents:
                    if allowed_subagents is not None and subagent.name not in allowed_subagents:
                        continue
                    # 只添加允许的子代理
                    subagent_names.append(subagent.name)
                    subagents_texts.append(f"### {subagent.name}\nTools: {', '.join(subagent.allowed_tools)}\nDescription: {subagent.description}\n")
                subagents_text = "\n".join(subagents_texts)
                tool["function"]["description"] = tool["function"]["description"].replace("{{subagents}}", subagents_text)
                # print(tool)
                tool["function"]["parameters"]["properties"]["name"]["enum"] = subagent_names
                # "enum": ["A", "B"]
        return self.builtin_tools


async def load_agent_config(agent_dir: Union[str, Path], env: Optional[dict[str, str]] = None) -> AgentConfig:
    """Load agent configuration from the specified directory.

    agent dir:
    - [agent_dir]
      - subagents/
      - main.md

    Args:
        agent_dir (Union[str, Path]): The directory containing the agent configuration files.

    Raises:
        FileNotFoundError: If the main agent config file is not found.

    Returns:
        AgentConfig: The loaded agent configuration.
    """
    agent_dir = Path(agent_dir)
    main_agent_config = agent_dir / "main.md"
    if not main_agent_config.exists():
        raise FileNotFoundError(f"Main agent config not found: {main_agent_config}")

    text = load_text(main_agent_config)
    config, developer_prompt, code_for_agent, code_for_interpreter = parse_config_from_markdown(text)
    env: dict[str, Union[str, dict]] = config.get("env", {}) | (env if env else {})
    if env:
        for key, value in env.items():
            value = os.getenv(key, value)
            if code_for_agent:
                code_for_agent = code_for_agent.replace("{{" + key + "}}", str(value))
            if code_for_interpreter:
                code_for_interpreter = code_for_interpreter.replace("{{" + key + "}}", str(value))

    builtin_subagents = []
    builtin_subagents_dir = config.get("builtin_subagents", ["agents"])
    builtin_subagents_dirpath = []
    if builtin_subagents_dir:
        if isinstance(builtin_subagents_dir, list):
            for subagent_dir in builtin_subagents_dir:
                subagent_path = Path(subagent_dir)
                if subagent_path.exists():
                    builtin_subagents_dirpath.append(subagent_path)
                elif (agent_dir / subagent_path).exists():
                    builtin_subagents_dirpath.append(agent_dir / subagent_path)
        elif isinstance(builtin_subagents_dir, str):
            subagent_path = Path(builtin_subagents_dir)
            if subagent_path.exists():
                builtin_subagents_dirpath.append(subagent_path)
            elif (agent_dir / subagent_path).exists():
                builtin_subagents_dirpath.append(agent_dir / subagent_path)
    builtin_subagents = await load_subagents(builtin_subagents_dirpath, env)
    builtin_tool_names = config.get("builtin_tools", ["CodeInterpreter", "Task"])
    if "*" in builtin_tool_names:
        builtin_tools = BUILTIN_TOOLS
    else:
        builtin_tools = [tool for tool in BUILTIN_TOOLS if tool["function"]["name"] in builtin_tool_names]

    return AgentConfig(
        name=config.get("name"),
        description=config.get("description"),
        developer_prompt=developer_prompt,
        code_for_agent=code_for_agent or "",
        code_for_interpreter=code_for_interpreter or "",
        allowed_tools=config.get("allowed_tools", ["*"]),
        model=config.get("model"),
        tool_mcp_config=config.get("tool_mcp_config", {}),
        code_mcp_config=config.get("code_mcp_config", {}),
        code_interpreter_config=CodeInterpreterConfig.model_validate(config.get("code_interpreter_config", {})),
        inference_args=config.get("inference_args", {}),
        builtin_tools=builtin_tools,
        builtin_subagents=builtin_subagents,
    )


async def get_agent_id(host_frontend_id: str) -> str:
    frontend_to_agent_map = {
        "AInvest": "aime",
        "iWencai": "wencai",
        "ARC-AGI": "agi",
    }
    return frontend_to_agent_map.get(host_frontend_id, "aime")


async def get_agent_config(
    agent_id: str,
    env: Optional[dict[str, str]] = None,
) -> AgentConfig:
    """获取指定agent的配置"""
    home_path = Path(__file__).parent.parent.parent
    # 映射agent_id到对应的配置路径
    agent_paths = {
        "aime": "aime",
        "agi": "agi",
        # "wencai": "wencai",  # 未实现
    }

    agent_dir = agent_paths.get(agent_id, "agi")  # 默认使用agi
    path = home_path / "assets" / agent_dir
    return await load_agent_config(path, env)


# "todo": {
#     "command": "/Users/lxy/anaconda3/envs/agent/bin/python",
#     "args": ["-m", "agentlin", "launch", "--mcp-server", "todo", "--host", "localhost", "--port", "7780", "--path", "/todo_mcp", "--debug"],
#     "env": {
#         "PYTHONPATH": home_path.resolve().as_posix(),
#         "TODO_FILE_PATH": (home_path / "todos.json").resolve().as_posix(),
#     },
#     "cwd": home_path.resolve().as_posix(),
# },
# "todo": {
#     "command": "/Users/lxy/anaconda3/envs/agent/bin/python",
#     "args": ["agentlin/tools/server/todo_mcp_server.py", "--host", "localhost", "--port", "7780", "--debug"],
#     "env": {
#         "PYTHONPATH": home_path.resolve().as_posix(),
#         "TODO_FILE_PATH": (home_path / "todos.json").resolve().as_posix(),
#     },
#     "cwd": home_path.resolve().as_posix(),
# },


