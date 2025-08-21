import json
from enum import Enum
from typing import Any, Optional, Type, Union, Dict, List
import json
import os

import requests
from requests import Response
from loguru import logger
from pydantic import BaseModel, Field, computed_field, field_validator
from PIL import Image, ImageDraw, ImageFont


MAX_REASONING_BYTES = 16 * 1024  # 16KB Max


class GameState(str, Enum):
    NOT_PLAYED = "NOT_PLAYED"
    NOT_FINISHED = "NOT_FINISHED"
    WIN = "WIN"
    GAME_OVER = "GAME_OVER"


class Card(BaseModel):
    """
    A single scorecard for a single game. A game can be played more than
    once, we track each play with lists of card properties (scores, states, actions)
    """

    game_id: str
    total_plays: int = 0

    guids: list[str] = Field(default_factory=list, exclude=True)
    scores: list[int] = Field(default_factory=list)
    states: list[GameState] = Field(default_factory=list)
    actions: list[int] = Field(default_factory=list)
    resets: list[int] = Field(default_factory=list)

    @property
    def idx(self) -> int:
        # lists are zero indexed by play_count starts at 1
        return self.total_plays - 1

    @property
    def started(self) -> bool:
        return self.total_plays > 0

    @property
    def score(self) -> Optional[int]:
        return self.scores[self.idx] if self.started else None

    @property
    def high_score(self) -> int:
        return max(self.scores) if self.started else 0

    @property
    def state(self) -> str:
        return self.states[self.idx] if self.started else GameState.NOT_PLAYED

    @property
    def action_count(self) -> Optional[int]:
        return self.actions[self.idx] if self.started else None

    @property
    def total_actions(self) -> int:
        return sum(self.actions)


class Scorecard(BaseModel):
    """
    Tracks and holds the scorecard for all games
    """

    games: list[str] = Field(default_factory=list, exclude=True)
    cards: dict[str, Card] = Field(default_factory=dict)
    source_url: Optional[str] = None
    tags: Optional[list[str]] = None
    opaque: Optional[Any] = Field(default=None)
    card_id: str = ""
    api_key: str = ""

    def model_post_init(self, __context: Any) -> None:
        if not self.cards:
            self.cards = {}

    @computed_field(return_type=int)
    def won(self) -> int:
        return sum(GameState.WIN in g.states for g in self.cards.values())

    @computed_field(return_type=int)
    def played(self) -> int:
        return sum(bool(g.states) for g in self.cards.values())

    @computed_field(return_type=int)
    def total_actions(self) -> int:
        return sum(g.total_actions for g in self.cards.values())

    @computed_field(return_type=int)
    def score(self) -> int:
        return sum(g.high_score for g in self.cards.values())

    def get(self, game_id: Optional[str] = None) -> dict[str, Any]:
        if game_id is not None:
            card = self.cards.get(game_id)
            return {game_id: card.model_dump()} if card else {}
        return {k: v.model_dump() for k, v in self.cards.items()}

    def get_json_for(self, game_id: str) -> dict[str, Any]:
        card = self.cards.get(game_id)
        return {
            "won": self.won,
            "played": self.played,
            "total_actions": self.total_actions,
            "score": self.score,
            "cards": {game_id: card.model_dump()} if card else {},
        }


class SimpleAction(BaseModel):
    game_id: str = ""


class ComplexAction(BaseModel):
    game_id: str = ""
    x: int = Field(default=0, ge=0, le=63)
    y: int = Field(default=0, ge=0, le=63)


class GameAction(Enum):
    RESET = (0, SimpleAction)
    ACTION1 = (1, SimpleAction)
    ACTION2 = (2, SimpleAction)
    ACTION3 = (3, SimpleAction)
    ACTION4 = (4, SimpleAction)
    ACTION5 = (5, SimpleAction)
    ACTION6 = (6, ComplexAction)

    action_type: Union[Type[SimpleAction], Type[ComplexAction]]
    action_data: Union[SimpleAction, ComplexAction]
    reasoning: Optional[Any]

    def __init__(
        self,
        action_id: int,
        action_type: Union[Type[SimpleAction], Type[ComplexAction]],
    ) -> None:
        self._value_ = action_id
        self.action_type = action_type
        self.action_data = action_type()
        self.reasoning = None

    def is_simple(self) -> bool:
        return self.action_type is SimpleAction

    def is_complex(self) -> bool:
        return self.action_type is ComplexAction

    def validate_data(self, data: dict[str, Any]) -> bool:
        """Raise exception on invalid parse of incoming JSON data."""
        self.action_type.model_validate(data)
        return True

    def set_data(self, data: dict[str, Any]) -> Union[SimpleAction, ComplexAction]:
        self.action_data = self.action_type(**data)
        return self.action_data

    @classmethod
    def from_id(cls, action_id: int) -> "GameAction":
        for action in cls:
            if action.value == action_id:
                return action
        raise ValueError(f"No GameAction with id {action_id}")

    @classmethod
    def from_name(cls, name: str) -> "GameAction":
        try:
            return cls[name.upper()]
        except KeyError:
            raise ValueError(f"No GameAction with name '{name}'")

    @classmethod
    def all_simple(cls) -> list["GameAction"]:
        return [a for a in cls if a.is_simple()]

    @classmethod
    def all_complex(cls) -> list["GameAction"]:
        return [a for a in cls if a.is_complex()]


class ActionInput(BaseModel):
    id: GameAction = GameAction.RESET
    data: dict[str, Any] = {}
    reasoning: Optional[Any] = Field(
        default=None,
        description="Opaque client-supplied blob; stored & echoed back verbatim.",
    )

    # Optional size / serialisability guard
    @field_validator("reasoning")
    @classmethod
    def _check_reasoning(cls, v: Any) -> Any:
        if v is None:
            return v  # field omitted → fine
        try:
            raw = json.dumps(v, separators=(",", ":")).encode("utf-8")
        except (TypeError, ValueError):
            raise ValueError("reasoning must be JSON-serialisable")
        if len(raw) > MAX_REASONING_BYTES:
            raise ValueError(f"reasoning exceeds {MAX_REASONING_BYTES} bytes")
        return v


class FrameData(BaseModel):
    game_id: str = ""
    frame: list[list[list[int]]] = []
    state: GameState = GameState.NOT_PLAYED
    score: int = Field(0, ge=0, le=254)
    action_input: ActionInput = Field(default_factory=lambda: ActionInput())
    guid: Optional[str] = None
    full_reset: bool = False

    def is_empty(self) -> bool:
        return len(self.frame) == 0


class ARC_AGI_Client:
    """Client for ARC-AGI-3 agents."""

    def __init__(self, root_url: str, api_key: Optional[str] = None):
        """
        Initialize the ARC-AGI-3 client.

        Args:
            root_url: Base URL for the ARC-AGI-3 API
            api_key: API key for authentication (defaults to ARC_API_KEY env var)
        """
        self.root_url = root_url.rstrip('/')
        self.api_key = api_key or os.getenv("ARC_API_KEY", "")

        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "Accept": "application/json",
        }

        self._session = requests.Session()
        self._session.headers.update(self.headers)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the session."""
        if hasattr(self, '_session'):
            self._session.close()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 10
    ) -> Response:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without leading slash)
            data: Request payload for POST requests
            timeout: Request timeout in seconds

        Returns:
            Response object

        Raises:
            requests.RequestException: On network errors
            ValueError: On invalid JSON response
        """
        url = f"{self.root_url}/api/{endpoint}"

        try:
            if method.upper() == 'GET':
                response = self._session.get(url, timeout=timeout)
            elif method.upper() == 'POST':
                response = self._session.post(
                    url,
                    json=data,
                    timeout=timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            logger.debug(f"{method} {url} -> {response.status_code}")
            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {method} {url} - {e}")
            raise

    def get_games(self) -> List[str]:
        """
        Get the list of available games.

        Returns:
            List of game IDs

        Raises:
            requests.RequestException: On network errors
            ValueError: On invalid response format
        """
        response = self._make_request('GET', 'games')

        if response.status_code == 200:
            try:
                games_data = response.json()
                return [game["game_id"] for game in games_data]
            except (ValueError, KeyError) as e:
                logger.error(f"Failed to parse games response: {e}")
                logger.error(f"Response content: {response.text[:200]}")
                raise ValueError(f"Invalid games response format: {e}")
        else:
            error_msg = f"Failed to get games: {response.status_code} - {response.text[:200]}"
            logger.error(error_msg)
            raise requests.RequestException(error_msg)

    def execute_action(
        self,
        action: GameAction,
        game_id: str,
        card_id: Optional[str] = None,
        guid: Optional[str] = None,
        reasoning: Optional[Any] = None
    ) -> FrameData:
        """
        Execute a game action.

        Args:
            action: The game action to execute
            game_id: ID of the game being played
            card_id: Scorecard ID (for RESET actions)
            guid: Game instance GUID
            reasoning: Optional reasoning data

        Returns:
            FrameData with the result of the action

        Raises:
            requests.RequestException: On network errors
            ValueError: On invalid response format
        """
        # Prepare action data
        data = action.action_data.model_dump()
        data["game_id"] = game_id

        if action == GameAction.RESET and card_id:
            data["card_id"] = card_id

        if guid:
            data["guid"] = guid

        if reasoning is not None:
            data["reasoning"] = reasoning

        # Execute the action
        response = self._make_request('POST', f'cmd/{action.name}', data)

        if not response.ok:
            error_msg = f"Action {action.name} failed: {response.status_code} - {response.text[:200]}"
            logger.error(error_msg)
            raise requests.RequestException(error_msg)

        try:
            frame_data = response.json()

            # Check for API error in response
            if "error" in frame_data:
                logger.warning(f"API error in action response: {frame_data}")

            return FrameData.model_validate(frame_data)

        except (ValueError, Exception) as e:
            logger.error(f"Failed to parse action response: {e}")
            logger.error(f"Response content: {response.text[:200] if hasattr(response, 'text') else 'No response text'}")
            raise ValueError(f"Invalid action response format: {e}")

    def open_scorecard(self, tags: Optional[List[str]] = None) -> str:
        """
        Open a new scorecard.

        Args:
            tags: Optional list of tags for the scorecard

        Returns:
            Scorecard ID

        Raises:
            requests.RequestException: On network errors or API errors
        """
        data = {"tags": tags or []}
        response = self._make_request('POST', 'scorecard/open', data)

        if not response.ok:
            error_msg = f"Failed to open scorecard: {response.status_code} - {response.text[:200]}"
            logger.error(error_msg)
            raise requests.RequestException(error_msg)

        try:
            response_data = response.json()

            if "error" in response_data:
                error_msg = f"API error opening scorecard: {response_data}"
                logger.error(error_msg)
                raise requests.RequestException(error_msg)

            return response_data["card_id"]

        except (ValueError, KeyError) as e:
            logger.error(f"Failed to parse open scorecard response: {e}")
            raise ValueError(f"Invalid open scorecard response: {e}")

    def close_scorecard(self, card_id: str) -> Optional[Scorecard]:
        """
        Close a scorecard and get the final results.

        Args:
            card_id: ID of the scorecard to close

        Returns:
            Scorecard object with final results, or None if failed
        """
        data = {"card_id": card_id}
        response = self._make_request('POST', 'scorecard/close', data)

        if not response.ok:
            logger.warning(f"Failed to close scorecard: {response.status_code} - {response.text[:200]}")
            return None

        try:
            response_data = response.json()

            if "error" in response_data:
                logger.warning(f"API error closing scorecard: {response_data}")
                return None

            return Scorecard.model_validate(response_data)

        except (ValueError, Exception) as e:
            logger.warning(f"Failed to parse close scorecard response: {e}")
            return None

    def get_scorecard(self, card_id: str, game_id: str) -> Scorecard:
        """
        Get scorecard for a specific game.

        Args:
            card_id: Scorecard ID
            game_id: Game ID

        Returns:
            Scorecard object

        Raises:
            requests.RequestException: On network errors or API errors
        """
        response = self._make_request('GET', f'scorecard/{card_id}/{game_id}')

        if not response.ok:
            error_msg = f"Failed to get scorecard: {response.status_code} - {response.text[:200]}"
            logger.error(error_msg)
            raise requests.RequestException(error_msg)

        try:
            response_data = response.json()

            if "error" in response_data:
                error_msg = f"API error getting scorecard: {response_data}"
                logger.error(error_msg)
                raise requests.RequestException(error_msg)

            return Scorecard.model_validate(response_data)

        except (ValueError, Exception) as e:
            logger.error(f"Failed to parse scorecard response: {e}")
            raise ValueError(f"Invalid scorecard response: {e}")

    def set_api_key(self, api_key: str) -> None:
        """
        Update the API key for authentication.

        Args:
            api_key: New API key
        """
        self.api_key = api_key
        self.headers["X-API-Key"] = api_key
        self._session.headers.update({"X-API-Key": api_key})


def generate_grid_image_with_zone(grid: List[List[int]], ZONE_SIZE: int=16, cell_size: int = 5) -> Image.Image:
    """Generate PIL image of the grid with colored cells and zone coordinates."""
    if not grid or not grid[0]:
        # Create empty image
        img = Image.new("RGB", (200, 200), color="black")
        return img

    height = len(grid)
    width = len(grid[0])

    # Create image
    img = Image.new("RGB", (width * cell_size, height * cell_size), color="white")
    draw = ImageDraw.Draw(img)

    # Color mapping for grid cells
    key_colors = {
        0: "#FFFFFF",
        1: "#CCCCCC",
        2: "#999999",
        3: "#666666",
        4: "#333333",
        5: "#000000",
        6: "#E53AA3",
        7: "#FF7BCC",
        8: "#F93C31",
        9: "#1E93FF",
        10: "#88D8F1",
        11: "#FFDC00",
        12: "#FF851B",
        13: "#921231",
        14: "#4FCC30",
        15: "#A356D6",
    }

    # Draw grid cells
    for y in range(height):
        for x in range(width):
            color = key_colors.get(grid[y][x], "#888888")  # default: floor

            # Draw cell
            draw.rectangle(
                [
                    x * cell_size,
                    y * cell_size,
                    (x + 1) * cell_size,
                    (y + 1) * cell_size,
                ],
                fill=color,
                outline="#000000",
                width=1,
            )

    # Draw zone coordinates and borders
    for y in range(0, height, ZONE_SIZE):
        for x in range(0, width, ZONE_SIZE):
            # Draw zone coordinate label
            try:
                font = ImageFont.load_default()
                zone_text = f"({x},{y})"
                draw.text(
                    (x * cell_size + 2, y * cell_size + 2),
                    zone_text,
                    fill="#FFFFFF",
                    font=font,
                )
            except (ImportError, OSError) as e:
                logger.debug(f"Could not load font for zone labels: {e}")
            except Exception as e:
                logger.error(f"Failed to draw zone label at ({x},{y}): {e}")

            # Draw zone boundary
            zone_width = min(ZONE_SIZE, width - x) * cell_size
            zone_height = min(ZONE_SIZE, height - y) * cell_size
            draw.rectangle(
                [
                    x * cell_size,
                    y * cell_size,
                    x * cell_size + zone_width,
                    y * cell_size + zone_height,
                ],
                fill=None,
                outline="#FFD700",  # gold border for zone
                width=2,
            )

    return img


def generate_grid_text(grid: List[List[int]], ZONE_SIZE: int = 16, use_colors: bool = True) -> str:
    """Generate text representation of the grid with ASCII characters, colors, and zone coordinates."""
    if not grid or not grid[0]:
        return "Empty grid"

    height = len(grid)
    width = len(grid[0])

    # Check if colors are supported in terminal
    import sys
    terminal_supports_color = (
        hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and
        os.getenv('TERM', '').lower() not in ('dumb', '') and
        os.getenv('NO_COLOR', '') == ''
    )
    use_colors = use_colors and terminal_supports_color

    # Character mapping for different cell values
    char_map = {
        0: '██',  # double block for better visibility
        1: '██',  # light gray
        2: '██',  # medium gray
        3: '██',  # dark gray
        4: '██',  # darker gray
        5: '██',  # black
        6: '██',  # magenta
        7: '██',  # light magenta
        8: '██',  # red
        9: '██',  # blue
        10: '██', # light blue
        11: '██', # yellow
        12: '██', # orange
        13: '██', # dark red
        14: '██', # green
        15: '██', # purple
    }

    # Improved ANSI color codes with 256-color support fallback
    color_codes = {
        0: '\033[48;5;231m',   # white background (color 231)
        1: '\033[48;5;250m',   # light gray background (color 250)
        2: '\033[48;5;244m',   # medium gray background (color 244)
        3: '\033[48;5;238m',   # dark gray background (color 238)
        4: '\033[48;5;235m',   # darker gray background (color 235)
        5: '\033[48;5;16m',    # black background (color 16)
        6: '\033[48;5;198m',   # magenta background (color 198)
        7: '\033[48;5;213m',   # light magenta background (color 213)
        8: '\033[48;5;196m',   # red background (color 196)
        9: '\033[48;5;21m',    # blue background (color 21)
        10: '\033[48;5;81m',   # light blue/cyan background (color 81)
        11: '\033[48;5;226m',  # yellow background (color 226)
        12: '\033[48;5;208m',  # orange background (color 208)
        13: '\033[48;5;124m',  # dark red background (color 124)
        14: '\033[48;5;46m',   # green background (color 46)
        15: '\033[48;5;129m',  # purple background (color 129)
    }

    # Fallback for basic 16 color terminals
    basic_color_codes = {
        0: '\033[47m',   # white background
        1: '\033[47m',   # white background (approximation)
        2: '\033[100m',  # bright black (dark gray) background
        3: '\033[100m',  # bright black (dark gray) background
        4: '\033[40m',   # black background
        5: '\033[40m',   # black background
        6: '\033[105m',  # bright magenta background
        7: '\033[105m',  # bright magenta background
        8: '\033[101m',  # bright red background
        9: '\033[104m',  # bright blue background
        10: '\033[106m', # bright cyan background
        11: '\033[103m', # bright yellow background
        12: '\033[103m', # bright yellow background (orange approximation)
        13: '\033[41m',  # red background
        14: '\033[102m', # bright green background
        15: '\033[45m',  # magenta background
    }

    # Use 256-color if available, otherwise fallback to basic colors
    colors_to_use = color_codes if os.getenv('COLORTERM', '').lower() in ('truecolor', '24bit') or '256' in os.getenv('TERM', '') else basic_color_codes

    # Reset color code
    reset_color = '\033[0m' if use_colors else ''

    lines = []

    # Add top border with column numbers
    header = "     "  # space for row numbers (adjusted for wider chars)
    for x in range(width):
        if x % 10 == 0:
            header += (str(x // 10) if x >= 10 else " ") + " "
        else:
            header += "  "
    lines.append(header)

    header2 = "     "
    for x in range(width):
        header2 += str(x % 10) + " "
    lines.append(header2)

    lines.append("     " + "--" * width)

    # Generate grid rows
    for y in range(height):
        # Row number
        row_str = f"{y:3d}| "

        # Grid cells with colors
        for x in range(width):
            value = grid[y][x]
            char = char_map.get(value, '??')  # default: unknown

            if use_colors:
                color_code = colors_to_use.get(value, '')
                row_str += f"{color_code}{char}{reset_color}"
            else:
                # Use different characters without colors
                simple_chars = {
                    0: '··', 1: '░░', 2: '▒▒', 3: '▓▓', 4: '██', 5: '■■',
                    6: 'AA', 7: 'BB', 8: 'CC', 9: 'DD', 10: 'EE', 11: 'FF',
                    12: 'GG', 13: 'HH', 14: 'II', 15: 'JJ'
                }
                row_str += simple_chars.get(value, '??')

        lines.append(row_str)

        # Add zone boundary markers every ZONE_SIZE rows
        if (y + 1) % ZONE_SIZE == 0 and y + 1 < height:
            zone_marker = "    +" + "==" * width
            lines.append(zone_marker)

    # # Add zone coordinate labels
    # zone_info = []
    # for y in range(0, height, ZONE_SIZE):
    #     for x in range(0, width, ZONE_SIZE):
    #         zone_info.append(f"Zone ({x},{y})")

    # if zone_info:
    #     lines.append("")
    #     lines.append("Zones: " + " | ".join(zone_info))

    # Add color legend
    lines.append("")
    lines.append("Legend:")
    legend_items = []
    for value in range(16):
        if any(value in row for row in grid):  # only show used values
            char = char_map.get(value, '??')
            if use_colors:
                color_code = colors_to_use.get(value, '')
                colored_char = f"{color_code}{char}{reset_color}"
                legend_items.append(f"{value}: {colored_char}")
            else:
                simple_chars = {
                    0: '··', 1: '░░', 2: '▒▒', 3: '▓▓', 4: '██', 5: '■■',
                    6: 'AA', 7: 'BB', 8: 'CC', 9: 'DD', 10: 'EE', 11: 'FF',
                    12: 'GG', 13: 'HH', 14: 'II', 15: 'JJ'
                }
                legend_items.append(f"{value}: {simple_chars.get(value, '??')}")

    # Group legend items in lines of 8
    for i in range(0, len(legend_items), 8):
        lines.append("  " + " ".join(legend_items[i:i+8]))

    return "\n".join(lines)


def generate_llm_friendly_text(grid: List[List[int]], ZONE_SIZE: int = 16, max_width=64, include_coordinates: bool = True) -> str:
    """
    Generate LLM-friendly text representation of the grid.

    This function creates a clean, structured text format that is easy for LLMs to parse
    and understand, focusing on clarity and logical structure rather than visual appeal.

    Args:
        grid: 2D list representing the game grid
        ZONE_SIZE: Size of zones for coordinate references (default: 16)
        include_coordinates: Whether to include coordinate information

    Returns:
        String with LLM-friendly formatted grid representation
    """
    if not grid or not grid[0]:
        return "Grid Status: Empty\nDimensions: 0x0\nContent: No data available"

    height = len(grid)
    width = len(grid[0])

    lines = []

    # Header with basic information
    lines.append(f"Grid Analysis Report")
    lines.append(f"==================")
    lines.append(f"Dimensions: {width}x{height} (width x height)")
    lines.append(f"Total cells: {width * height}")
    lines.append("")

    # Collect statistics about the grid
    cell_counts = {}
    unique_values = set()
    for row in grid:
        for cell in row:
            unique_values.add(cell)
            cell_counts[cell] = cell_counts.get(cell, 0) + 1

    # Value distribution
    lines.append("Value Distribution:")
    lines.append("-" * 18)
    for value in sorted(unique_values):
        count = cell_counts[value]
        percentage = (count / (width * height)) * 100
        lines.append(f"Value {value:2d}: {count:4d} cells ({percentage:5.1f}%)")
    lines.append("")

    # # Grid representation with clear structure
    # lines.append("Grid Structure:")
    # lines.append("-" * 14)

    # if include_coordinates:
    #     # Add column headers for reference
    #     header_line = "Row |"
    #     for x in range(min(width, max_width)):  # Limit width for readability
    #         if x < 10:
    #             header_line += f" {x}"
    #         else:
    #             header_line += f"{x:2d}"
    #     if width > max_width:
    #         header_line += " ..."
    #     lines.append(header_line)
    #     lines.append("----+" + "--" * min(width, max_width) + ("---" if width > max_width else ""))

    # # Grid data with row numbers
    # for y in range(height):
    #     if include_coordinates:
    #         row_str = f"{y:3d} |"
    #     else:
    #         row_str = ""

    #     # Add cells (limit width for very wide grids)
    #     for x in range(min(width, max_width)):
    #         value = grid[y][x]
    #         if include_coordinates:
    #             row_str += f" {value}" if value < 10 else f"{value:2d}"
    #         else:
    #             row_str += f"{value:2d} " if value < 10 else f"{value:3d}"

    #     if width > max_width:
    #         row_str += " ..."

    #     lines.append(row_str)

    #     # Add zone separators for better readability
    #     if ZONE_SIZE > 0 and (y + 1) % ZONE_SIZE == 0 and y + 1 < height:
    #         if include_coordinates:
    #             lines.append("    " + "  " * min(width, max_width) + ("   " if width > max_width else ""))
    #         else:
    #             lines.append("")

    # lines.append("")

    # Zone information if coordinates are included
    # if include_coordinates and ZONE_SIZE > 0:
    #     lines.append("Zone Information:")
    #     lines.append("-" * 16)
    #     zones_x = (width + ZONE_SIZE - 1) // ZONE_SIZE
    #     zones_y = (height + ZONE_SIZE - 1) // ZONE_SIZE
    #     lines.append(f"Zone size: {ZONE_SIZE}x{ZONE_SIZE}")
    #     lines.append(f"Total zones: {zones_x}x{zones_y} = {zones_x * zones_y}")
    #     lines.append("")

    #     # List zones with their coordinates
    #     zone_list = []
    #     for zy in range(zones_y):
    #         for zx in range(zones_x):
    #             start_x = zx * ZONE_SIZE
    #             start_y = zy * ZONE_SIZE
    #             end_x = min(start_x + ZONE_SIZE - 1, width - 1)
    #             end_y = min(start_y + ZONE_SIZE - 1, height - 1)
    #             zone_list.append(f"Zone ({zx},{zy}): cells ({start_x},{start_y}) to ({end_x},{end_y})")

    #     for zone_info in zone_list[:10]:  # Limit to first 10 zones for readability
    #         lines.append(zone_info)
    #     if len(zone_list) > 10:
    #         lines.append(f"... and {len(zone_list) - 10} more zones")
    #     lines.append("")

    # Pattern analysis
    lines.append("Pattern Analysis:")
    lines.append("-" * 16)

    # Check for common patterns
    patterns = []

    # Check if grid is mostly one value
    if cell_counts:
        most_common_value = max(cell_counts.keys(), key=lambda k: cell_counts[k])
        most_common_count = cell_counts[most_common_value]
        if most_common_count > (width * height * 0.8):
            patterns.append(f"Dominant value: {most_common_value} ({most_common_count} cells)")

    # Check for empty (value 0) regions
    if 0 in cell_counts:
        empty_percentage = (cell_counts[0] / (width * height)) * 100
        patterns.append(f"Empty cells (value 0): {empty_percentage:.1f}%")

    # Check for diversity
    unique_count = len(unique_values)
    if unique_count == 1:
        patterns.append("Uniform grid: all cells have the same value")
    elif unique_count == 2:
        patterns.append("Binary grid: only two different values")
    elif unique_count > 10:
        patterns.append(f"High diversity: {unique_count} different values")

    if patterns:
        for pattern in patterns:
            lines.append(f"- {pattern}")
    else:
        lines.append("- No obvious patterns detected")

    lines.append("")

    # Summary for LLM understanding
    lines.append("Summary for Analysis:")
    lines.append("-" * 20)
    lines.append(f"This is a {width}x{height} grid containing {len(unique_values)} unique values.")
    if cell_counts:
        most_common = max(cell_counts.keys(), key=lambda k: cell_counts[k])
        lines.append(f"Most frequent value: {most_common} (appears {cell_counts[most_common]} times)")
        least_common = min(cell_counts.keys(), key=lambda k: cell_counts[k])
        lines.append(f"Least frequent value: {least_common} (appears {cell_counts[least_common]} times)")
    lines.append(f"Value range: {min(unique_values)} to {max(unique_values)}")

    return "\n".join(lines)


def test_color_support() -> str:
    """Test function to check color support in the terminal."""
    import sys

    result = []
    result.append("Terminal Color Support Test:")
    result.append(f"- stdout.isatty(): {hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()}")
    result.append(f"- TERM: {os.getenv('TERM', 'not set')}")
    result.append(f"- COLORTERM: {os.getenv('COLORTERM', 'not set')}")
    result.append(f"- NO_COLOR: {os.getenv('NO_COLOR', 'not set')}")

    # Test basic colors
    result.append("\nBasic ANSI colors test:")
    basic_line = ""
    for i in range(8):
        basic_line += f"\033[4{i}m  \033[0m {i} "
    result.append(basic_line)

    # Test 256 colors sample
    result.append("\n256-color support test (sample):")
    color_line = ""
    for color in [196, 21, 46, 226, 198, 81, 208, 129]:
        color_line += f"\033[48;5;{color}m  \033[0m "
    result.append(color_line)

    return "\n".join(result)
