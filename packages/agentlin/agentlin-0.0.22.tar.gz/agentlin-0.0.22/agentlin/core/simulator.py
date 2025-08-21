
from typing_extensions import Optional

from xlin import load_text
from agentlin.core.agent_schema import AgentCore
from agentlin.tools.tool_code_interpreter import CodeInterpreter
from deeplin.inference_engine import InferenceEngine


class AgentWithSimulator(AgentCore):
    def __init__(self, engine: InferenceEngine):
        super().__init__(engine)
        self.simulator: Optional["Simulator"] = None

    def bind_simulator(self, simulator: "Simulator"):
        self.simulator = simulator


class Simulator:
    def __init__(
        self,
        work_dir: str,
        tool_context_for_agent: Optional[str] = None,
        tool_context_for_interpreter: Optional[str] = None,
        debug=False,
    ):
        self.work_dir = work_dir
        self.debug = debug
        self.agent: AgentCore = None
        self._text_tool_context_for_agent = tool_context_for_agent
        self._text_tool_context_for_interpreter = tool_context_for_interpreter
        self.initialize_code_interpreter(work_dir, debug, self._tool_context_for_interpreter())

    def initialize_code_interpreter(self, work_dir: str, debug: bool, initial_code_context: str):
        self.code_interpreter = CodeInterpreter(work_dir, debug)
        self.code_interpreter.execute_code(initial_code_context)

    def execute(self, code: str):
        return self.code_interpreter.execute_code(code)

    def reset(self):
        self.code_interpreter.restart_jupyter_kernel()

    def set_tool_context(self, for_agent: str, for_interpreter: str):
        """
        设置工具的上下文信息。
        Args:
            for_agent (str): 用于 LLM 的提示
            for_interpreter (str): 用于代码解释器实际执行
        """
        self._text_tool_context_for_agent = for_agent
        self._text_tool_context_for_interpreter = for_interpreter
        self.initialize_code_interpreter(self.work_dir, self.debug, self._tool_context_for_interpreter())

    def tool_context_for_agent(self):
        """
        获取工具的上下文信息，用于 LLM 的提示。
        【拼进 prompt 里的】
        Returns:
            str: 工具的上下文信息
        """
        if not self._text_tool_context_for_agent:
            self._text_tool_context_for_agent = load_text("tool_context_for_agent.py")
        return self._text_tool_context_for_agent

    def _tool_context_for_interpreter(self):
        """
        获取工具的上下文信息，用于代码解释器实际执行。
        【实际执行的】
        Returns:
            str: 工具的上下文信息
        """
        if not self._text_tool_context_for_interpreter:
            self._text_tool_context_for_interpreter = load_text("tool_context_for_interpreter.py")
        return self._text_tool_context_for_interpreter

    def bind_agent(self, agent: AgentCore):
        self.agent = agent
