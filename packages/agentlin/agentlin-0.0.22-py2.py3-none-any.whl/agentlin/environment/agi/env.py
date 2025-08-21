import os
from typing import Optional, TypedDict
from typing_extensions import Literal

from loguru import logger
from pydantic import BaseModel, Field
from agentlin.core.types import ContentData, ToolData, BaseTool, ToolParams, ToolResult
from agentlin.environment.agi.client import ARC_AGI_Client, FrameData, GameAction, generate_grid_text, generate_llm_friendly_text


class Experience(BaseModel):
    reason: dict = {}
    action: GameAction
    frame: FrameData


class EnvState(BaseModel):
    game_id: str
    card_id: str
    guid: Optional[str] = None

    experiences: list[Experience] = []


class EnvToolParams(TypedDict):
    action: GameAction
    state: EnvState


class ReasoningActionResponse(BaseModel):
    """Action response structure for reasoning agent."""

    name: Literal["ACTION1", "ACTION2", "ACTION3", "ACTION4", "RESET"] = Field(
        description="The action to take. ACTION1 (Move Up), ACTION2 (Move Down), ACTION3 (Move Left), ACTION4 (Move Right), RESET (Reset Game)",
    )
    reason: str = Field(
        description="Detailed reasoning for choosing this action",
        min_length=0,
        max_length=2000,
    )
    short_description: str = Field(
        description="Brief description of the action",
        min_length=5,
        max_length=500,
    )
    hypothesis: str = Field(
        description="Current hypothesis about game mechanics",
        min_length=0,
        max_length=2000,
    )
    aggregated_findings: str = Field(
        description="Summary of discoveries and learnings so far",
        min_length=0,
        max_length=2000,
    )
    util_code: str = Field(
        description="Code snippets or examples that may help in understanding or solving the problem.",
        min_length=0,
        max_length=10 * 1000,
    )


def screen_content(grid: list[list[int]]) -> list[ContentData]:
    text = generate_llm_friendly_text(grid)
    return [{"type": "text", "text": text}]


class EnvTool(BaseTool):
    def __init__(self, client: ARC_AGI_Client):
        schema = ReasoningActionResponse.model_json_schema()
        schema["additionalProperties"] = False
        super().__init__(
            name="TakeAction",
            title="Take Action",
            description="Take an action in the environment.",
            parameters=schema,
        )
        self.client = client

    async def execute(self, params: EnvToolParams) -> ToolResult:
        action: GameAction = params.get("action")
        assert action is not None, "Action is required"
        state: EnvState = params.get("state")
        assert state is not None, "State is required"
        reason: dict = params.get("reason", {})

        frame = await self.take_action(action, state)
        state.experiences.append(Experience(reason=reason, action=action, frame=frame))
        tool_result = ToolResult(
            message_content=screen_content(frame.frame),
            block_list=[{"type": "frame", "data": frame.model_dump()}],
        )
        return tool_result

    async def take_action(self, action: GameAction, state: EnvState) -> FrameData:
        """
        Take an action in the environment.
        Args:
            action: The action to take.
            state: The current state of the environment.
        Returns:
            The next state of the environment.
        """
        frame = self.client.execute_action(action=action, game_id=state.game_id, card_id=state.card_id, guid=state.guid)
        state.guid = frame.guid  # 更新guid以便后续使用
        grid = frame.frame[-1] if frame.frame else []
        frame.frame = grid
        return frame


class ArcAgi3:
    def __init__(self, debug=False):
        self.debug = debug
        # 从环境变量获取配置
        api_key = os.getenv("ARC_API_KEY")
        # 构建根URL
        scheme = os.getenv("SCHEME", "http")
        host = os.getenv("HOST", "localhost")
        port = os.getenv("PORT", "8001")

        if (scheme == "http" and str(port) == "80") or (scheme == "https" and str(port) == "443"):
            root_url = f"{scheme}://{host}"
        else:
            root_url = f"{scheme}://{host}:{port}"

        logger.info(f"连接到ARC-AGI-3 API: {root_url}")

        self.client = ARC_AGI_Client(root_url, api_key)
        self.id2state: dict[str, EnvState] = {}
        self.tools = [
            EnvTool(client=self.client),
        ]
        self.name2tool: dict[str, BaseTool] = {t.name: t for t in self.tools}

    def list_tools(self) -> list[ToolData]:
        """
        List the actions available in the ArcAgi3 environment.
        This method is a placeholder for the actual implementation.
        Returns:
            A list of ToolData objects representing the available actions.
        """
        return [self.name2tool[name].function_tool_schema for name in self.name2tool]

    def create_state(self, tags=["demo", "example"]):
        # 1. 打开计分卡
        logger.info("打开新的计分卡...")

        card_id = self.client.open_scorecard(tags=tags)
        logger.info(f"计分卡已创建: {card_id}")

        # 2. 获取可用游戏列表
        logger.info("获取可用游戏列表...")
        games = self.client.get_games()
        logger.info(f"找到 {len(games)} 个可用游戏: {games[:5]}...")  # 只显示前5个

        # 3. 选择第一个游戏进行演示
        game_id = games[0]
        game_id = "ls20-f340c8e5138e"
        logger.info(f"使用游戏: {game_id}")
        state = EnvState(
            game_id=game_id,
            card_id=card_id,
        )
        self.id2state[card_id] = state
        return state

    async def step(self, card_id: str, action: GameAction, reason: Optional[dict] = None) -> ToolResult:
        """
        Take a step in the ArcAgi3 environment based on the given action.
        Args:
            action: The action to take in the environment.
        Returns:
            A tuple containing the next state, reward, done flag, and additional info.
        """
        state = self.id2state.get(card_id)
        if not state:
            if self.debug:
                logger.debug("State not found, creating a new one.")
            state = self.create_state()

        tool = self.name2tool.get("TakeAction")
        if not tool:
            if self.debug:
                logger.warning("Tool not found.")
            return ToolResult(
                message_content=[{"type": "text", "text": "action not executed. tool not found"}],
                block_list=[{"type": "text", "text": "action not executed. tool not found"}],
            )
        result = await tool.execute(EnvToolParams(action=action, state=state, reason=reason))
        return result

    def close(self, card_id: str):
        """
        Close the ArcAgi3 environment.
        This method is a placeholder for the actual implementation.
        """
        if card_id in self.id2state:
            state = self.id2state[card_id]
            result = self.client.close_scorecard(card_id=state.card_id)
            if result:
                del self.id2state[card_id]
            else:
                logger.warning(f"Failed to close scorecard: {card_id}")
        else:
            logger.warning(f"Card ID not found: {card_id}")

    def render(self, frame: FrameData):
        """
        Render one frame.
        """
        if self.debug:
            logger.debug(f"Rendering frame:")
        screen_as_text = generate_grid_text(frame.frame, use_colors=False)
        print(screen_as_text)

