from typing_extensions import Any, Literal, TypedDict, Optional, Union

MIME_MARKDOWN = "text/markdown"
MIME_TEXT = "text/plain"

class TextBlock(TypedDict, total=False):
    type: Literal["text"]
    text: str
    id: Optional[int]


MIME_IMAGE_PNG = "image/png"
MIME_IMAGE_JPEG = "image/jpeg"

class ImageUrl(TypedDict, total=False):
    url: str  # base64, http, or file path


class ImageBlock(TypedDict):
    type: Literal["image_url"]
    image_url: ImageUrl
    id: int


MIME_PLOTLY = "application/vnd.plotly.v1+json"


class PlotlyBlock(TypedDict):
    type: Literal["plotly-json"]
    data: dict[Literal["application/vnd.plotly.v1+json"], dict]
    id: int


MIME_TABLE_V1 = "application/vnd.aime.table.v1+json"


class TableDataV1(TypedDict):
    # v1 是通用 dataframe 的渲染
    columns: list[dict[str, Any]]
    datas: list[dict[str, Any]]


MIME_TABLE_V2 = "application/vnd.aime.table.v2+json"


class TableDataV2(TypedDict):
    # v2 是带 text2sql 的 dataframe 渲染
    columns: list[dict[str, Any]]
    datas: list[dict[str, Any]]
    condition: str
    model_sql: str
    model_condition: str
    chunks_info: str
    meta: str
    row_count: str
    code_count: str
    token: str
    status_code: str
    status_msg: str


class TableBlock(TypedDict):
    type: Literal["table-json"]
    data: Union[
        dict[Literal["application/vnd.aime.table.v1+json"], TableDataV1],
        dict[Literal["application/vnd.aime.table.v2+json"], TableDataV2],
    ]
    id: int


MIME_HTML = "text/html"


class HtmlBlock(TypedDict):
    type: Literal["html"]
    data: dict[Literal["text/html"], str]  # HTML content
    id: int


MIME_JSON = "application/json"


class JsonBlock(TypedDict):
    type: Literal["json"]
    data: dict[Literal["application/json"], dict]
    id: int


Block = Union[
    TextBlock,
    ImageBlock,
    PlotlyBlock,
    TableBlock,
    HtmlBlock,
    JsonBlock,
]


MIME_TOOL_CALL = "application/vnd.aime.tool.call+json"
MIME_TOOL_RESPONSE = "application/vnd.aime.tool.response+json"

class ToolCall(TypedDict):
    type: Literal["tool_call"]
    tool_name: str
    tool_args: dict[str, Any]
    call_id: str

class ToolResponse(TypedDict):
    message_content: list[dict[str, Any]]
    block_list: list[Block]
    data: dict[str, Any]
