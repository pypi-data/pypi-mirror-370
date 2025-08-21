from typing_extensions import Literal, Optional, Union
import json
import re
import io
from plotly import graph_objects as go
from plotly import io as pio
from PIL import Image
from loguru import logger

from agentlin.core.multimodal import image_content
from agentlin.core.agent_schema import content_to_text, generate_short_uuid
from agentlin.code_interpreter.types import (
    MIME_MARKDOWN,
    MIME_TEXT,
    MIME_IMAGE_PNG,
    MIME_IMAGE_JPEG,
    MIME_PLOTLY,
    MIME_TABLE_V1,
    MIME_TABLE_V2,
    MIME_HTML,
    MIME_TOOL_CALL,
    ToolCall,
    MIME_TOOL_RESPONSE,
    ToolResponse,
)


def delete_color_control_char(string: str) -> str:
    ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
    return ansi_escape.sub("", string)


def text_response(iopub_msg: dict, text: str) -> ToolResponse:
    return {
        "message_content": [{"type": "text", "text": text}],
        "block_list": [{"type": "text", "text": text}],
        "iopub_messages": [iopub_msg],
    }

def image_response(iopub_msg: dict, image_url: str, **kwargs) -> ToolResponse:
    image_id: int = kwargs.get("image_id", None)
    if not image_id:
        # image_id = generate_hash_id(image_url)
        image_id = generate_short_uuid()
    return {
        "message_content": image_content(image_url, image_id),
        "block_list": [{"type": "image_url", "image_url": {"url": image_url}, "id": image_id}],
        "iopub_messages": [iopub_msg],
    }

def html_response(iopub_msg: dict, text: Union[list[str], str], **kwargs) -> ToolResponse:
    if isinstance(text, list):
        text = "".join(text)
    uuid = kwargs.get("uuid", None)
    if not uuid:
        # uuid = generate_hash_id(image_url)
        uuid = generate_short_uuid()
    return {
        "message_content": [{"type": "text", "text": f"```html\n{text}\n```", "id": uuid}],
        "block_list": [{"type": "html", "data": {MIME_HTML: text}, "id": uuid}],
        "iopub_messages": [iopub_msg],
    }

def plotly_response(iopub_msg: dict, fig_json: dict, **kwargs) -> ToolResponse:
    image_id: int = kwargs.get("image_id", None)
    if not image_id:
        # image_id = generate_hash_id(json.dumps(fig_json, ensure_ascii=False))
        image_id = generate_short_uuid()
    if isinstance(fig_json, dict):
        fig = go.Figure(fig_json)
    else:
        fig = pio.from_json(fig_json)

    # Convert to image bytes using plotly
    img_bytes = pio.to_image(fig, format="png")
    image = Image.open(io.BytesIO(img_bytes))
    return {
        "message_content": image_content(image, image_id),
        "block_list": [
            {
                "type": "plotly-json",
                "data": {MIME_PLOTLY: fig_json},
                "id": image_id,
            }
        ],
        "iopub_messages": [iopub_msg],
    }

def table_response(iopub_msg: dict, data: dict, **kwargs) -> ToolResponse:
    text = data.get("text/plain", "")
    block = {
        "type": "table-json",
        "data": {},
    }
    if MIME_TABLE_V1 in data:
        table_data = data[MIME_TABLE_V1]
        block["data"][MIME_TABLE_V1] = table_data
    elif MIME_TABLE_V2 in data:
        table_data = data[MIME_TABLE_V2]
        block["data"][MIME_TABLE_V2] = table_data
    else:
        table_data = {"columns": [], "datas": []}
        block["data"][MIME_TABLE_V2] = table_data
    query_id = table_data.get("query_id", None)
    if not query_id:
        # query_id = generate_hash_id(json.dumps(table_data, ensure_ascii=False))
        query_id = generate_short_uuid()
    block["id"] = query_id
    if not text:
        text = table_data.get("text", "")

    return {
        "message_content": [{"type": "text", "text": text, "id": query_id}],
        "block_list": [block],
        "iopub_messages": [iopub_msg],
    }


def iopub_msg_to_tool_response(iopub_msg: Optional[dict], mode: Literal["simple", "full", "debug"]) -> Optional[ToolResponse]:
    """
    Convert iopub message to a ToolResponse format.
    """
    if not iopub_msg:
        return None
    if iopub_msg["msg_type"] == "stream":
        if iopub_msg["content"].get("name") == "stdout":
            output = iopub_msg["content"]["text"]
            return text_response(iopub_msg, text=delete_color_control_char(output))
    elif iopub_msg["msg_type"] == "execute_result":
        if "data" in iopub_msg["content"]:
            data = iopub_msg["content"]["data"]
            output = None
            if MIME_TOOL_RESPONSE in data:
                tool_response = data[MIME_TOOL_RESPONSE]
                return {
                    **tool_response,
                    "iopub_messages": [iopub_msg],
                }
            elif MIME_TOOL_CALL in data:
                return {
                    "message_content": [],
                    "block_list": [{
                        "type": "tool_call",
                        "data": data,
                    }],
                    "iopub_messages": [iopub_msg],
                }
            elif MIME_PLOTLY in data:
                fig_json = data[MIME_PLOTLY]
                return plotly_response(iopub_msg, fig_json=fig_json)
            elif MIME_TABLE_V1 in data or MIME_TABLE_V2 in data:
                return table_response(iopub_msg, data=data)
            elif MIME_MARKDOWN in data:
                output = data[MIME_MARKDOWN]
                return text_response(iopub_msg, text=delete_color_control_char(output))
            elif MIME_IMAGE_PNG in data:
                output = data[MIME_IMAGE_PNG]
                output = "data:image/png;base64," + output
                return image_response(iopub_msg, image_url=output)
            elif MIME_IMAGE_JPEG in data:
                output = data[MIME_IMAGE_JPEG]
                output = "data:image/jpeg;base64," + output
                return image_response(iopub_msg, image_url=output)
            elif MIME_HTML in data:
                output = data[MIME_HTML]
                return html_response(iopub_msg, text=output)
            elif MIME_TEXT in data:
                output = data[MIME_TEXT]
                return text_response(iopub_msg, text=delete_color_control_char(output))
            else:
                logger.warning("content type not supported in execute_result")
                logger.warning(data)
    elif iopub_msg["msg_type"] == "display_data":
        if "data" in iopub_msg["content"]:
            data = iopub_msg["content"]["data"]
            output = None
            if MIME_TOOL_RESPONSE in data:
                tool_response = data[MIME_TOOL_RESPONSE]
                return {
                    **tool_response,
                    "iopub_messages": [iopub_msg],
                }
            elif MIME_TOOL_CALL in data:
                return {
                    "message_content": [],
                    "block_list": [{
                        "type": "tool_call",
                        "data": data,
                    }],
                    "iopub_messages": [iopub_msg],
                }
            elif MIME_PLOTLY in data:
                fig_json = data[MIME_PLOTLY]
                return plotly_response(iopub_msg, fig_json=fig_json)
            elif MIME_TABLE_V1 in data or MIME_TABLE_V2 in data:
                return table_response(iopub_msg, data=data)
            elif MIME_MARKDOWN in data:
                output = data[MIME_MARKDOWN]
                return text_response(iopub_msg, text=delete_color_control_char(output))
            elif MIME_IMAGE_PNG in data:
                output = data[MIME_IMAGE_PNG]
                output = "data:image/png;base64," + output
                return image_response(iopub_msg, image_url=output)
            elif MIME_IMAGE_JPEG in data:
                output = data[MIME_IMAGE_JPEG]
                output = "data:image/jpeg;base64," + output
                return image_response(iopub_msg, image_url=output)
            elif MIME_HTML in data:
                output = data[MIME_HTML]
                return html_response(iopub_msg, text=output)
            elif MIME_TEXT in data:
                output = data[MIME_TEXT]
                return text_response(iopub_msg, text=delete_color_control_char(output))
            else:
                logger.warning("content type not supported in display_data")
                logger.warning(data)
    elif iopub_msg["msg_type"] == "error":
        if "traceback" in iopub_msg["content"]:
            output = "\n".join(iopub_msg["content"]["traceback"])
            text = delete_color_control_char(output)
            if mode == "debug":
                return text_response(iopub_msg, text=text)
            else:
                return {
                    "message_content": [{"type": "text", "text": text}],
                    "block_list": [],  # No block for error messages
                    "iopub_messages": [iopub_msg],
                }
    return None

def parse_msg_list_to_tool_response(msg_list: list[Optional[dict]], mode: Literal["simple", "full", "debug"]) -> ToolResponse:
    tool_response = {
        "message_content": [],
        "block_list": [],
        "iopub_messages": [],
    }
    for i, msg in enumerate(msg_list):
        logger.debug(f"Processing message {i+1}/{len(msg_list)}: {msg['msg_type'] if msg else 'None'}")
        response = iopub_msg_to_tool_response(msg, mode)
        if response:
            tool_response["message_content"].extend(response.get("message_content", []))
            tool_response["block_list"].extend(response.get("block_list", []))
            tool_response["iopub_messages"].extend(response.get("iopub_messages", []))
            logger.debug(f"\n{content_to_text(response.get('message_content', []))}")
    return tool_response
