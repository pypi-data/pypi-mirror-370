import json
import os
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict

from loguru import logger

from agentlin.core.types import (
    BaseTool,
    FunctionDefinition,
    FunctionParameters,
    ToolParams,
    ToolResult,
)


@dataclass
class ThoughtData:
    """思维数据的结构化表示"""
    thought: str
    thought_number: int
    total_thoughts: int
    next_thought_needed: bool
    is_revision: Optional[bool] = None
    revises_thought: Optional[int] = None
    branch_from_thought: Optional[int] = None
    branch_id: Optional[str] = None
    needs_more_thoughts: Optional[bool] = None


class SequentialThinkingProcessor:
    """处理序列化思维过程的核心类"""

    def __init__(self):
        self.thought_history: List[ThoughtData] = []
        self.branches: Dict[str, List[ThoughtData]] = {}
        self.disable_thought_logging: bool = os.getenv("DISABLE_THOUGHT_LOGGING", "").lower() == "true"

    def validate_thought_data(self, input_data: Dict[str, Any]) -> ThoughtData:
        """验证并转换输入数据为 ThoughtData"""
        # 处理参数名映射（驼峰命名法转下划线命名法）
        param_mapping = {
            'thoughtNumber': 'thought_number',
            'totalThoughts': 'total_thoughts',
            'nextThoughtNeeded': 'next_thought_needed',
            'isRevision': 'is_revision',
            'revisesThought': 'revises_thought',
            'branchFromThought': 'branch_from_thought',
            'branchId': 'branch_id',
            'needsMoreThoughts': 'needs_more_thoughts',
        }

        # 转换参数名
        converted_data = {}
        for key, value in input_data.items():
            if key in param_mapping:
                converted_data[param_mapping[key]] = value
            else:
                converted_data[key] = value

        required_fields = ['thought', 'thought_number', 'total_thoughts', 'next_thought_needed']

        for field in required_fields:
            if field not in converted_data:
                raise ValueError(f"Missing required field: {field}")

        if not isinstance(converted_data['thought'], str):
            raise ValueError('Invalid thought: must be a string')
        if not isinstance(converted_data['thought_number'], int):
            raise ValueError('Invalid thought_number: must be an integer')
        if not isinstance(converted_data['total_thoughts'], int):
            raise ValueError('Invalid total_thoughts: must be an integer')
        if not isinstance(converted_data['next_thought_needed'], bool):
            raise ValueError('Invalid next_thought_needed: must be a boolean')

        return ThoughtData(
            thought=converted_data['thought'],
            thought_number=converted_data['thought_number'],
            total_thoughts=converted_data['total_thoughts'],
            next_thought_needed=converted_data['next_thought_needed'],
            is_revision=converted_data.get('is_revision'),
            revises_thought=converted_data.get('revises_thought'),
            branch_from_thought=converted_data.get('branch_from_thought'),
            branch_id=converted_data.get('branch_id'),
            needs_more_thoughts=converted_data.get('needs_more_thoughts'),
        )

    def format_thought(self, thought_data: ThoughtData) -> str:
        """格式化思维内容为可视化输出"""
        thought_number = thought_data.thought_number
        total_thoughts = thought_data.total_thoughts
        thought = thought_data.thought
        is_revision = thought_data.is_revision
        revises_thought = thought_data.revises_thought
        branch_from_thought = thought_data.branch_from_thought
        branch_id = thought_data.branch_id

        prefix = ''
        context = ''

        if is_revision:
            prefix = '🔄 Revision'
            context = f' (revising thought {revises_thought})'
        elif branch_from_thought:
            prefix = '🌿 Branch'
            context = f' (from thought {branch_from_thought}, ID: {branch_id})'
        else:
            prefix = '💭 Thought'
            context = ''

        header = f"{prefix} {thought_number}/{total_thoughts}{context}"
        border_length = max(len(header), len(thought)) + 4
        border = '─' * border_length

        return f"""
┌{border}┐
│ {header} │
├{border}┤
│ {thought.ljust(border_length - 2)} │
└{border}┘"""

    def process_thought(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理思维输入并返回结果"""
        try:
            validated_input = self.validate_thought_data(input_data)

            # 如果当前思维数量超过总估计，调整总数
            if validated_input.thought_number > validated_input.total_thoughts:
                validated_input.total_thoughts = validated_input.thought_number

            # 添加到历史记录
            self.thought_history.append(validated_input)

            # 处理分支
            if validated_input.branch_from_thought and validated_input.branch_id:
                if validated_input.branch_id not in self.branches:
                    self.branches[validated_input.branch_id] = []
                self.branches[validated_input.branch_id].append(validated_input)

            # 记录思维过程（如果启用）
            if not self.disable_thought_logging:
                formatted_thought = self.format_thought(validated_input)
                logger.info(formatted_thought)

            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "thought_number": validated_input.thought_number,
                        "total_thoughts": validated_input.total_thoughts,
                        "next_thought_needed": validated_input.next_thought_needed,
                        "branches": list(self.branches.keys()),
                        "thought_history_length": len(self.thought_history)
                    }, indent=2, ensure_ascii=False)
                }]
            }

        except Exception as error:
            return {
                "content": [{
                    "type": "text",
                    "text": f"error: {error}",
                }],
                "is_error": True
            }


class SequentialThinkingTool(BaseTool):
    """
    用于动态和反思性问题解决的详细思维工具。

    这个工具帮助通过灵活的思维过程分析问题，该过程可以适应和演化。
    每个思维都可以建立、质疑或修正之前的洞察，随着理解的深入。
    """

    def __init__(self):
        self.processor = SequentialThinkingProcessor()

        parameters = {
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "您当前的思维步骤",
                },
                "nextThoughtNeeded": {
                    "type": "boolean",
                    "description": "是否需要另一个思维步骤",
                },
                "thoughtNumber": {
                    "type": "integer",
                    "description": "当前思维编号",
                    "minimum": 1,
                },
                "totalThoughts": {
                    "type": "integer",
                    "description": "估计需要的总思维数",
                    "minimum": 1,
                },
                "isRevision": {
                    "type": "boolean",
                    "description": "这是否修正了之前的思维",
                },
                "revisesThought": {
                    "type": "integer",
                    "description": "正在重新考虑的思维编号",
                    "minimum": 1,
                },
                "branchFromThought": {
                    "type": "integer",
                    "description": "分支点思维编号",
                    "minimum": 1,
                },
                "branchId": {
                    "type": "string",
                    "description": "分支标识符",
                },
                "needsMoreThoughts": {
                    "type": "boolean",
                    "description": "如果需要更多思维",
                }
            },
            "required": ["thought", "nextThoughtNeeded", "thoughtNumber", "totalThoughts"],
            "additionalProperties": False,
        }

        super().__init__(
            name="SequentialThinking",
            title="SequentialThinking",
            description="""一个用于通过思维进行动态和反思性问题解决的详细工具。
这个工具帮助通过可以适应和演化的灵活思维过程来分析问题。
每个思维都可以建立、质疑或修正之前的洞察，随着理解的深入。

何时使用此工具：
- 将复杂问题分解为步骤
- 带有修正空间的规划和设计
- 可能需要纠正方向的分析
- 全面范围可能不清楚的问题
- 需要多步骤解决方案的问题
- 需要在多个步骤中保持上下文的任务
- 需要过滤无关信息的情况

关键特性：
- 您可以随着进展调整 total_thoughts 的数量
- 您可以质疑或修正之前的思维
- 即使在似乎结束后也可以添加更多思维
- 您可以表达不确定性并探索替代方法
- 不是每个思维都需要线性构建 - 您可以分支或回溯
- 生成解决方案假设
- 基于思维链步骤验证假设
- 重复过程直到满意
- 提供正确答案

您应该：
1. 开始时估计需要的思维数，但准备好调整
2. 随时质疑或修正之前的思维
3. 不要犹豫添加更多思维，即使在"结尾"
4. 在存在时表达不确定性
5. 标记修正之前思维或分支到新路径的思维
6. 忽略与当前步骤无关的信息
7. 在适当时生成解决方案假设
8. 基于思维链步骤验证假设
9. 重复过程直到对解决方案满意
10. 提供单一的、理想的正确答案作为最终输出
11. 只有在真正完成并达到满意答案时才将 next_thought_needed 设置为 false""",
            parameters=parameters,
        )

    async def execute(self, params: ToolParams) -> ToolResult:
        """执行序列化思维处理

        Args:
            params: 包含思维处理所需参数的字典

        Returns:
            ToolResult 对象，包含处理结果
        """
        # 处理思维输入
        result_data = self.processor.process_thought(params)

        # 构建返回结果
        result = ToolResult(
            message_content=result_data["content"],
            block_list=result_data["content"],  # 同时作为块内容
        )

        return result
