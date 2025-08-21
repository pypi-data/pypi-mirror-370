import copy
import re
import uuid
import datetime
import hashlib

import pandas as pd
import numpy as np
from loguru import logger
from loguru._logger import Logger, Core
from pydantic import BaseModel

from xlin import *
from deeplin.inference_engine import InferenceEngine
from deeplin.inference_engine.hexin_engine import retry_request
from agentlin.core.types import ContentData, DialogData, ResponsesContentData, ResponsesDialogData, ToolData, ResponsesToolData
from openai.types.chat.chat_completion_message_tool_call_param import ChatCompletionMessageToolCallParam
from agentlin.core.multimodal import *


def temporal_dataframe_to_jsonlist(df: pd.DataFrame):
    """
    Args:
        df (pd.DataFrame): df

    Returns:
        List[Dict[str, str]]: json list: [{"col1": "xxx", "col2": "xxx", ...}, ...]
    """
    json_list = []
    if "date" not in df.columns:
        df = df.reset_index().rename(columns={"index": "date"})
    for i, line in df.iterrows():
        data = dict(line)
        for k in data:
            v = data[k]
            if isinstance(v, np.float64):
                data[k] = float(v)
            elif isinstance(v, np.int64):
                data[k] = int(v)
            elif isinstance(v, np.bool_):
                data[k] = bool(v)
            elif isinstance(v, np.ndarray):
                data[k] = v.tolist()
            elif isinstance(v, (datetime.datetime, pd.Timestamp)):
                data[k] = v.isoformat()
            elif isinstance(v, np.datetime64):
                data[k] = v.astype(str)
            elif isinstance(v, pd.Series):
                data[k] = v.tolist()
            elif isinstance(v, pd.DataFrame):
                data[k] = temporal_dataframe_to_jsonlist(v)
            elif v == np.nan:
                data[k] = None
        json_list.append(data)
    return json_list


def jsonlist_to_temporal_dataframe(json_list: list[dict]):
    """
    Args:
        json_list (list[dict]): [{"col1": "xxx", "col2": "xxx", ...}, ...]

    Returns:
        pd.DataFrame: df
    """
    df = pd.DataFrame(json_list)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df


def dataframe_to_markdown(df: pd.DataFrame, columns: Optional[List[str]] = None):
    if not columns:
        columns = list(df.columns)
    df = df[columns]
    markdown = ""

    # Write column headers
    markdown += "|" + "index" + "|" + "|".join(columns) + "|" + "\n"
    markdown += "|" + "---" + "|" + "|".join(["----"] * len(columns)) + "|" + "\n"

    # Write data rows
    for i, row in df.iterrows():
        values = []
        for col in columns:
            value = row[col]
            if col == "date":
                if isinstance(value, str):
                    value = pd.to_datetime(value)
                if value.hour == 0 and value.minute == 0 and value.second == 0:
                    value = value.strftime("%Y-%m-%d")
                else:
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
            elif col == "code":
                continue
            elif col == "pct_change":
                if not isinstance(value, str):
                    value = f"{value:.2%}"
            if isinstance(value, str):
                values.append(value)
            elif isinstance(value, float):
                values.append(f"{value:.4f}")
            else:
                values.append(str(value))
        values_str = "|".join(values)
        markdown += "|" + str(i) + "|" + values_str + "|\n"

    markdown = markdown.strip()
    return markdown


def dataframe_to_json_str(code: str, df: pd.DataFrame, columns: Optional[List[str]] = None):
    if not columns:
        columns = list(df.columns)
    obj = {
        "code": code,
    }
    for col in columns:
        if col == "date":
            if isinstance(df.iloc[0][col], str):
                obj[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d").tolist()
            elif isinstance(df.iloc[0][col], pd.Timestamp):
                obj[col] = df[col].dt.strftime("%Y-%m-%d").tolist()
            else:
                obj[col] = df[col].tolist()
        elif col == "code":
            continue
        elif col == "pct_change":
            values = df[col].tolist()
            # 百分数格式化
            values = [f"{value:.2%}" for value in values]
            obj[col] = values
        else:
            values = df[col].tolist()
            if isinstance(values[0], float):
                values = [round(value, 4) for value in values]
            elif isinstance(values[0], int):
                values = [int(value) for value in values]
            else:
                values = [str(value) for value in values]
            obj[col] = values
    json_str_list = []
    for key, value in obj.items():
        if isinstance(value, list):
            json_str_list.append(f'  "{key}": {value},')
        elif isinstance(value, str):
            json_str_list.append(f'  "{key}": "{value}",')
        else:
            json_str_list.append(f'  "{key}": {value},')
    json_str = "{\n" + "\n".join(json_str_list) + "\n}"
    return json_str


def parse_config_from_ipynb(ipynb_path: str):
    json_data = load_json(ipynb_path)
    if not json_data:
        raise ValueError(f"Failed to load JSON data from {ipynb_path}")
    return parse_config_from_json(json_data)


def parse_config_from_json(json_data: dict):
    cells = json_data["cells"]
    id2cell = {cell["id"]: cell for cell in cells}
    code_for_interpreter = "".join(id2cell.get("code_for_interpreter", {}).get("source", []))
    code_for_agent = "".join(id2cell.get("code_for_agent", {}).get("source", []))
    developer_prompt = "".join(id2cell.get("developer_prompt", {}).get("source", []))
    return code_for_interpreter, code_for_agent, developer_prompt


def parse_actions(input_string: str, action_names: List[str]):
    """
    >>> input_string = \"\"\"我将使用Search工具来搜索杭州的实时天气情况。
    ActionList:
    Search: 杭州实时天气1
    Search:杭州实时天气2
    Search：杭州实时天气3\tSearch：杭州实时天气4
    Clarify: 多行澄清
    这一行也属于澄清
    可以用 : 进行选择5
    Search: 下一个动作6\"\"\"

    >>> action_names = ["Search", "Clarify"]
    >>> actionlist = parse_actions(input_string, action_names)
    >>> print(actionlist)
    [('Search', '杭州实时天气1'), ('Search', '杭州实时天气2'), ('Search', '杭州实时天气3'), ('Search', '杭州实时天气4'), ('Clarify', '多行澄清\\n这一行也属于澄清\\n可以用 : 进行选择5'), ('Search', '下一个动作6')]
    """
    # 构建正则表达式：| 作为分隔符，将所有的action名称连接在一起，形成一个正则表达式模式。
    action_pattern = "|".join(map(re.escape, action_names))

    # 正则表达式说明：
    # ({action_pattern}):         匹配action名称及其后面的冒号。
    # ([\s\S]*?)                  匹配action内容，[\s\S]*? 非贪婪匹配所有字符（包括换行符）。
    # (?=({action_pattern}):|$)   使用正向预查，确保匹配到下一个action名称或字符串结尾。
    regex = re.compile(rf"({action_pattern})\s*[:：]*([\s\S]*?)(?=({action_pattern})[:：]|$)")

    # 进行匹配
    matches = regex.findall(input_string)

    # 将匹配结果存入动作列表
    actionlist: list[tuple[str, str]] = []
    for match in matches:
        action_name = match[0]
        action_content = match[1].strip().strip("-").strip("*").strip()
        actionlist.append((action_name, action_content))
    return actionlist


def extract_action_block(text: str) -> str:
    m = re.search(r"(<action>.*?</action>)", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""


def extract_action(text: str) -> str:
    m = re.search(r"<action>(.*?)</action>", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""


def parse_text_with_apply(text):
    """
    解析文本，提取 <apply> 标签中的内容

    Example:
    ```python
    test_text = \"\"\"
    xxx
    <apply>
    yyy
    </apply>
    zzz
    \"\"\"
    parsed = parse_text(test_text)
    print(parsed)
    ```
    Output:
    ```python
    [{'type': 'text', 'text': 'xxx'}, {'type': 'apply', 'apply': 'yyy'}, {'type': 'text', 'text': 'zzz'}]
    ```
    """

    # 定义正则表达式模式
    pattern = r"(.*?)(?:<apply>(.*?)</apply>|$)"

    # 使用正则表达式查找所有匹配项
    matches = re.finditer(pattern, text, re.DOTALL)

    result = []

    for match in matches:
        # 提取文本部分
        text_part = match.group(1).strip()
        if text_part:
            result.append({"type": "text", "text": text_part})

        # 提取 apply 部分
        apply_part = match.group(2)
        if apply_part is not None:
            apply_content = apply_part.strip()
            if apply_content:
                result.append({"type": "apply", "apply": apply_content})

    return result


def extract_apply_block(text: str) -> str:
    """
    提取 <apply> 标签中的内容
    """
    m = re.search(r"(<apply>.*?</apply>)", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""


def extract_apply(text: str) -> str:
    m = re.search(r"<apply>(.*?)</apply>", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""


def exist_apply(text: str) -> bool:
    """
    检查文本中是否存在 <apply> 标签
    """
    return re.search(r"<apply>.*?</apply>", text, re.DOTALL) is not None


def extract_tool_calls(content: str) -> list[dict]:
    # 提取 <tool_call> 标签中的内容
    tool_calls = []
    start = 0
    while True:
        start = content.find("<tool_call>", start)
        if start == -1:
            break
        end = content.find("</tool_call>", start)
        if end == -1:
            break
        tool_call = content[start + len("<tool_call>") : end]
        try:
            tool_calls.append(json.loads(tool_call))
        except json.JSONDecodeError:
            logger.error(f"无法解析的工具调用: \n{tool_call}")
        except Exception as e:
            logger.error(f"未知错误: {e}")
        start = end + len("</tool_call>")
    return tool_calls


def extract_code(content: str) -> Optional[str]:
    # 提取 <code-interpreter> 标签中的内容
    m = re.search(r"<code-interpreter>(.*?)</code-interpreter>", content, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def extract_code_block(content: str) -> Optional[str]:
    # 提取 <code-interpreter> 标签中的内容
    m = re.search(r"(<code-interpreter>.*?</code-interpreter>)", content, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def extract_thought(text):
    # 提取 <think> 标签中的内容
    m = re.search(r"<think>(.*?)</think>", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def extract_execution_result(content: str) -> str:
    # 提取 <execution-result> 标签中的内容
    m = re.search(r"<execution-result>(.*?)</execution-result>", content, re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""


def extract_answer(content: str) -> str:
    # 提取 <answer> 标签中的内容
    m = re.search(r"<answer>(.*?)</answer>", content, re.DOTALL)
    if m:
        return m.group(1).strip()
    return content


def parse_function_call_response(response: dict):
    """
    解析函数调用响应，提取函数名和参数。
    """
    if isinstance(response, BaseModel):
        response = response.model_dump()  # 将 Pydantic 模型转换为字典
    call_id: str = response.get("id", f"call_{uuid.uuid4().hex}")
    call_name: str = response.get("function").get("name", "unknown_function")
    call_args: str = response.get("function").get("arguments", "{}")
    if isinstance(call_args, str) and len(call_args) == 0:
        call_args = "{}"
    call_args: dict = json.loads(call_args) if isinstance(call_args, str) else call_args
    return call_id, call_name, call_args


def remove_thoughts(resposne: str):
    # 移除 <think> 标签中的内容
    m = re.sub(r"<think>.*?</think>", "", resposne, flags=re.DOTALL)
    return m


def remove_answer(resposne: str):
    # 移除 <answer> 标签中的内容
    m = re.sub(r"<answer>.*?</answer>", "", resposne, flags=re.DOTALL)
    return m


def remove_thoughts_in_messages(messages: list[DialogData]) -> list[DialogData]:
    new_messages = []
    for msg in messages:
        if msg["role"] == "assistant":
            content = msg["content"]
            if isinstance(content, list):
                new_content = []
                for part in content:
                    if part["type"] == "text":
                        text = part["text"]
                        text = remove_thoughts(text)
                        new_content.append({"type": "text", "text": text})
                    else:
                        new_content.append(part)
                msg["content"] = new_content
            else:
                msg["content"] = remove_thoughts(content)
        new_messages.append(msg)
    return new_messages


def add_scale_bar_in_messages(messages: list[DialogData]) -> list[DialogData]:
    for msg in messages:
        if msg["role"] == "user":
            content = msg["content"]
            if isinstance(content, list):
                for part in content:
                    if part["type"] == "image_url":
                        base64_str = part["image_url"]["url"]
                        image = base64_to_image(base64_str)
                        image = scale_to_fit_and_add_scale_bar(image)  # 缩放图片到目标大小，并添加比例尺
                        base64_str = image_to_base64(image)
                        part["image_url"]["url"] = base64_str
    return messages


def autofix(response: str):
    if not response:
        return "<think>response 为空</think><answer>结束</answer>"
    if response.endswith("</code-interpreter"):
        return response + ">"
    return response


def synthesize_response(
    thought: str,
    motivation: str,
    code: str,
    response_type: Literal["info", "decision"] = "decision",
):
    if response_type == "decision":
        return f"""\
<think>
{thought}
</think>
{motivation}
<action>
{code}
</action>
""".strip()
    elif response_type == "info":
        return f"""\
<think>
{thought}
</think>
{motivation}
<code-interpreter>
{code}
</code-interpreter>
""".strip()
    else:
        raise ValueError(f"Unknown response_type: {response_type}")


def daily_return_to_cumulative_return(time_return, initial_cash=10000):
    returns = []
    cumulative_return = 0
    dates = []
    value = initial_cash
    for date, daily_return in time_return.items():
        cumulative_return += daily_return
        value *= 1 + daily_return
        returns.append((value / initial_cash - 1) * 100)  # 转换为百分比
        dates.append(pd.to_datetime(date))  # 转换为 pandas 时间戳
    return dates, returns


def select_sub_df(
    df: pd.DataFrame,
    start_date: str,
    end_date: str,
    lookback_window: int = 0,
    lookforward_window: int = 0,
    include_end_date: bool = False,
) -> pd.DataFrame:
    """
    从DataFrame中选择指定日期范围内的子DataFrame。

    Args:
        df (pd.DataFrame): 带有日期索引的DataFrame，index是日期。
        start_date (str): 起始日期，格式'YYYY-MM-DD'。
        end_date (str): 结束日期，格式'YYYY-MM-DD'。
        lookback_window (int): 向后查看的天数，默认为0。
        lookforward_window (int): 向前查看的天数，默认为0。

    Returns:
        pd.DataFrame: 指定日期范围内的子DataFrame。
    """
    # 确保索引是DatetimeIndex类型
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    # 确保索引是有序的
    if not df.index.is_monotonic_increasing:
        df = df.sort_index()

    # 获取索引的时区信息
    tz = df.index.tz

    # 创建带时区的切片日期
    start = pd.Timestamp(start_date, tz=tz)
    end = pd.Timestamp(end_date, tz=tz)

    # 选择子DataFrame
    try:
        if lookback_window > 0:
            start = start - pd.Timedelta(days=lookback_window)
        if lookforward_window > 0:
            end = end + pd.Timedelta(days=lookforward_window)
        if include_end_date:
            end = end + pd.Timedelta(days=1)
        sub_df = df[start:end]
    except KeyError:
        print(f"日期 {start_date} 或 {end_date} 不在索引范围内。")
        sub_df = pd.DataFrame()

    return sub_df


def generate_short_uuid(length=8):
    num_low = 10 ** (length - 1)
    num_high = 10**length - 1
    return random.randint(num_low, num_high)


def generate_hash_id(text: str, length: int = 6) -> int:
    """
    生成指定位数的数字哈希ID

    参数:
    - text: 要生成哈希ID的文本
    - length: 哈希ID的位数，默认为6

    返回:
    - 指定长度的数字哈希ID字符串
    """
    # 使用SHA-256生成哈希值
    hash_obj = hashlib.sha256(text.encode("utf-8"))
    hash_hex = hash_obj.hexdigest()

    # 将哈希值转换为整数
    hash_int = int(hash_hex, 16)

    # 生成指定位数的数字哈希ID
    # 使用模运算确保生成的数字在指定位数的范围内
    max_value = 10**length
    digit_id = hash_int % max_value

    return digit_id


def content_to_text(content: list[ContentData] | ContentData | str):
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        type_str = content["type"]
        if type_str == "text":
            return content["text"]
        elif type_str == "image":
            return f"[image]"
        elif type_str == "image_url":
            return f"[image]"
        elif type_str == "function":
            if content["function"]["name"] == "CodeInterpreter":
                args = content['function']['arguments']
                if isinstance(args, str):
                    args = json.loads(args)
                code = args.get("code")
                return f"{content['function']['name']} | {content['id']}\n{code}"
            if content["function"]["name"] == "Task":
                args = content['function']['arguments']
                if isinstance(args, str):
                    args = json.loads(args)
                prompt = args.get("prompt")
                return f"{content['function']['name']} | {content['id']}\n{prompt}"
            return f"{content['function']['name']} | {content['id']}\n{json.dumps(content['function']['arguments'], ensure_ascii=False, indent=2)}"
        return str(content)
    elif isinstance(content, list):
        return "\n".join([content_to_text(c) for c in content])
    return ""


def messages_to_text(messages: list[DialogData]):
    lines = []
    for msg in messages:
        if msg["role"] == "system":
            icon = "⚙️"
        elif msg["role"] == "user":
            icon = "👤"
        elif msg["role"] == "assistant":
            icon = "🤖"
        elif msg["role"] == "tool":
            icon = "🛠️"
        else:
            icon = "❓"
        if msg["role"] == "assistant" and "tool_calls" in msg and len(msg["tool_calls"]) > 0:
            content = ""
            if "content" in msg and len(msg["content"]) > 0:
                content += content_to_text(msg["content"])
                content += "\n"
            content += content_to_text(msg["tool_calls"])
        else:
            content = content_to_text(msg["content"])
        lines.append(f"{icon}【{msg['role']}】: {content}")
    return "\n".join(lines)


def completion_content_to_responses_content(content: ContentData) -> ResponsesContentData:
    """
    将 ContentData 格式的内容转换为 ResponsesContentData 格式。

    主要转换逻辑：
    1. text
         - 转换为 {"type": "input_text", "text": content}
    2. image_url
         - 转换为 {"type": "input_image", "image_url": content["image_url"]["url"]}
    3. file
         - 转换为 {"type": "input_file", **content["file"]}
    4. function
         - 转换为 {"type": "function_call", **content["function"]}

    如果 content 的类型不支持，则抛出 ValueError。
    """
    if isinstance(content, str):
        return {"type": "input_text", "text": content}

    if isinstance(content, dict):
        if content["type"] == "text":
            return {"type": "input_text", "text": content["text"]}
        elif content["type"] == "image_url":
            return {"type": "input_image", "image_url": content["image_url"]["url"]}
        elif content["type"] == "file":
            data = content.get("file", {})
            return {"type": "input_file", **data}
        elif content["type"] == "function":
            data = content.get("function", {})
            return {
                "type": "function_call",
                "id": content.get("id", str(uuid.uuid4())),
                "call_id": content.get("call_id", str(uuid.uuid4())),
                "name": data.get("name", ""),
                "arguments": data.get("arguments", "{}"),
            }

    raise ValueError(f"Unsupported content type: {content}")


def completion_messages_to_responses_messages(messages: list[DialogData], remove_thoughts=False) -> list[ResponsesDialogData]:
    """
    将 ChatCompletionMessageParam 格式的消息列表转换为 ResponseInputMessageItem 格式的消息列表。
    """
    from openai.types.responses import (
        EasyInputMessage,
        ResponseOutputMessage,
        ResponseFunctionToolCall,
        ResponseReasoningItem,
        ResponseFunctionToolCallOutputItem,
    )
    responses_messages: list[ResponsesDialogData] = []
    for msg in messages:
        if msg["role"] in ["system"]:
            response_msg = {}
            response_msg["type"] = "message"
            # response_msg["role"] = "developer"
            response_msg["role"] = "system"
            # response_msg["id"] = f"msg_{str(uuid.uuid4())}"
            if isinstance(msg["content"], str):
                if len(msg["content"]) == 0:
                    continue
                response_msg["content"] = [{"type": "input_text", "text": msg["content"]}]
            elif isinstance(msg["content"], list):
                response_msg["content"] = [completion_content_to_responses_content(c) for c in msg["content"]]
            else:
                raise ValueError(f"Unsupported content type: {type(msg['content'])}")
            # response_msg = EasyInputMessage.model_validate(response_msg)
            responses_messages.append(response_msg)
        elif msg["role"] in ["user"]:
            response_msg = {}
            response_msg["type"] = "message"
            response_msg["role"] = "user"
            # response_msg["id"] = f"msg_{str(uuid.uuid4())}"
            if isinstance(msg["content"], str):
                if len(msg["content"]) == 0:
                    continue
                response_msg["content"] = [{"type": "input_text", "text": msg["content"]}]
            elif isinstance(msg["content"], list):
                response_msg["content"] = [completion_content_to_responses_content(c) for c in msg["content"]]
            else:
                raise ValueError(f"Unsupported content type: {type(msg['content'])}")
            # response_msg = EasyInputMessage.model_validate(response_msg)
            responses_messages.append(response_msg)
        elif msg["role"] in ["assistant"]:
            if "tool_calls" in msg and len(msg["tool_calls"]) > 0:
                # 存在工具调用的情况下，content 为 reasoning
                # 处理 reasoning 内容
                content = msg["content"]
                if isinstance(content, str):
                    from openai.types.responses import ResponseReasoningItemParam
                    response_msg: ResponseReasoningItemParam = {
                        "id": f"rs_{str(uuid.uuid4())}",
                        "type": "reasoning",
                        "summary": [{
                            "type": "summary_text",
                            "text": content
                        }],
                        # "content": [{"type": "reasoning_text", "text": content}],
                    }
                    if not remove_thoughts:
                        # response_msg = ResponseReasoningItem.model_validate(response_msg)
                        responses_messages.append(response_msg)
                elif isinstance(content, list):
                    response_msg: ResponseReasoningItemParam = {
                        "id": f"rs_{str(uuid.uuid4())}",
                        "type": "reasoning",
                        "summary": [{
                            "type": "summary_text",
                            "text": c["text"],
                        } for c in content],
                        # "content": [{"type": "reasoning_text", "text": c["text"]}],
                    }
                    if not remove_thoughts:
                        # response_msg = ResponseReasoningItem.model_validate(response_msg)
                        responses_messages.append(response_msg)
                else:
                    raise ValueError(f"Unsupported content type: {type(content)}")

                # 处理工具调用
                tool_calls: list[ChatCompletionMessageToolCallParam] = msg["tool_calls"]
                for tool_call in tool_calls:
                    # print(tool_call)
                    assert tool_call.get("id") is not None, "Tool call must have a call_id"
                    assert tool_call.get("function", {}).get("name") is not None, "Tool call must have a name"
                    assert tool_call.get("function", {}).get("arguments") is not None, "Tool call must have arguments"
                    tool_call_message = {
                        "type": "function_call",
                        "call_id": tool_call.get("id"),
                        "name": tool_call.get("function", {}).get("name", ""),
                        "arguments": tool_call.get("function", {}).get("arguments", "{}"),
                        "id": f"fc_{str(uuid.uuid4())}",
                    }
                    # tool_call_message = ResponseFunctionToolCall.model_validate(tool_call_message)
                    responses_messages.append(tool_call_message)
            else:
                # 不存在工具调用的情况下，content 为回答
                response_msg = {}
                response_msg["type"] = "message"
                response_msg["role"] = "assistant"
                response_msg["id"] = f"msg_{str(uuid.uuid4())}"
                if isinstance(msg["content"], str):
                    if len(msg["content"]) == 0:
                        continue
                    response_msg["content"] = [{"type": "output_text", "text": msg["content"]}]
                elif isinstance(msg["content"], list):
                    response_msg["content"] = [completion_content_to_responses_content(c) for c in msg["content"]]
                    for c in response_msg["content"]:
                        if c["type"] == "input_text":
                            c["type"] = "output_text"
                else:
                    raise ValueError(f"Unsupported content type: {type(msg['content'])}")
                # response_msg = ResponseOutputMessage.model_validate(response_msg)
                responses_messages.append(response_msg)
        elif msg["role"] in ["tool"]:
            # assert isinstance(msg, )
            from openai.types.responses.response_input_item_param import FunctionCallOutput
            content = msg["content"]
            if is_multimodal_content(content):
                # 如果是多模态内容，转换为 user 模式的消息
                response_msg: FunctionCallOutput = {
                    "type": "function_call_output",
                    "id": f"fco_{str(uuid.uuid4())}",
                    "call_id": msg["tool_call_id"],
                    "output": "the output will be in the next message",
                }
                # response_msg = ResponseFunctionToolCallOutputItem.model_validate(response_msg)
                responses_messages.append(response_msg)
                response_msg = {
                    "type": "message",
                    "role": "user",
                    # "id": f"msg_{str(uuid.uuid4())}",
                    "content": [completion_content_to_responses_content(c) for c in content],
                }
                # response_msg = EasyInputMessage.model_validate(response_msg)
                responses_messages.append(response_msg)
            else:
                if isinstance(content, list):
                    texts = []
                    for c in content:
                        texts.append(c["text"])
                response_msg: FunctionCallOutput = {
                    "type": "function_call_output",
                    "id": f"fco_{str(uuid.uuid4())}",
                    "call_id": msg["tool_call_id"],
                    "output": "".join(texts),
                }
                # response_msg = ResponseFunctionToolCallOutputItem.model_validate(response_msg)
                responses_messages.append(response_msg)
        else:
            raise ValueError(f"Unsupported role: {msg['role']} in message: {msg}")
    return responses_messages


def completion_tools_to_responses_tools(tools: list[ToolData]) -> list[ResponsesToolData]:
    responses_tools = []
    for tool in tools:
        response_tool: ResponsesToolData = {
            "type": "function",
            "id": str(uuid.uuid4()),
            "name": tool["function"]["name"],
            "description": tool["function"].get("description", ""),
            "parameters": tool["function"].get("parameters", {}),
            "strict": tool.get("strict", False),
        }
        responses_tools.append(response_tool)
    return responses_tools


def create_logger(log_dir: str, name: str) -> Logger:
    # 创建独立的logger实例
    new_logger = Logger(
        core=Core(),
        exception=None,
        depth=0,
        record=False,
        lazy=False,
        colors=False,
        raw=False,
        capture=True,
        patchers=[],
        extra={"name": name},
    )

    # 创建日志文件路径
    log_file = os.path.join(log_dir, f"{name}.log")

    # 确保目录存在
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    formats = [
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | ",
        "<cyan>{extra[name]: <8}</cyan> | ",
        "<level>{level: <8}</level> | ",
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    ]
    # 添加控制台输出处理器
    new_logger.add(
        sink=sys.stdout,
        format="".join(formats),
        level="INFO",
        filter=lambda record: record["extra"].get("name") == name,
        colorize=True,
    )

    # 添加文件输出处理器
    new_logger.add(
        sink=log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {extra[name]: <8} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )

    return new_logger


class AgentState:
    def __init__(
        self,
        history_messages: list[DialogData] = [],
        decision_messages_list: list[list[DialogData]] = [],
        thought_messages_list: list[list[DialogData]] = [],
    ):
        self.history_messages = history_messages
        self.decision_messages_list = decision_messages_list
        self.thought_messages_list = thought_messages_list

    def append_history_message(self, message: DialogData):
        self.history_messages.append(message)

    def append_decision_messages(self, messages: list[DialogData]):
        self.decision_messages_list.append(messages)

    def append_thought_messages(self, messages: list[DialogData]):
        self.thought_messages_list.append(messages)


class AgentCore:
    def __init__(self, engine: InferenceEngine):
        self.engine = engine

    def inference(self, messages: list[DialogData], **inference_args):
        # 调用推理引擎获取回复
        inference_args.setdefault("max_tokens", 10 * 1024)
        inference_args.setdefault("debug", True)
        inference_args.setdefault("multi_modal", True)
        inference_args.setdefault("max_retry", 3)
        messages = copy.deepcopy(messages)
        messages = remove_thoughts_in_messages(messages)
        messages = add_scale_bar_in_messages(messages)

        @retry_request
        def retry_inference(**inference_args):
            response = self.engine.inference_one(messages, **inference_args)[0]
            if response is not None:
                response = self.autofix(response)
            if response is None:
                logger.debug("response is not valid and unable to fix, retrying sampling...")
            return response

        response = retry_inference(**inference_args)
        if not response:
            # response is None 的时候，inference 内部已经尽力还是失败了，此时我们自动修复
            return "<think>response 为空</think><answer>抱歉，请刷新页面重试</answer>"
        return response

    def autofix(self, response: str | dict):
        if not isinstance(response, str):
            logger.warning(f"Response is not a string (type: {type(response)}): \n{response}")
            return response
        # return None 表示需要重新推理，采样新的response
        # 以下情况，inference 成功了，需要自动修复 response
        if response.endswith("</code-interpreter"):
            return response + ">"
        case1 = re.match(r"^\s*<think>(.*?)</think>\s*<answer>(.*?)</answer>\s*$", response, re.DOTALL)
        case2 = re.match(r"^\s*<think>(.*?)</think>\s*<code-interpreter>(.*?)</code-interpreter>\s*$", response, re.DOTALL)
        if not case1 and not case2:
            # 如果没有 <think> 和 <answer> 或 <code-interpreter> 标签，先考虑think缺失情况
            case3 = re.match(r"^\s*<think>(.*?)</think>\s*$", response, re.DOTALL)
            if case3:
                # think 没有缺失，可能是<answer>或<code-interpreter>缺失
                # 我们建议 retry inference，通过 return None 来触发
                return None
            else:
                # 没有 <think> 标签，可能存在 <answer> 或 <code-interpreter> 标签
                case4 = re.match(r"^\s*<answer>(.*?)</answer>\s*$", response, re.DOTALL)
                case5 = re.match(r"^\s*<code-interpreter>(.*?)</code-interpreter>\s*$", response, re.DOTALL)
                # if case4:
                #     # 只有 <answer> 标签，直接添加 <think> 标签
                #     response = f"<think>无思考</think><answer>{case4.group(1)}</answer>"
                # elif case5:
                #     # 只有 <code-interpreter> 标签，直接添加 <think> 标签
                #     response = f"<think>无思考</think><code-interpreter>{case5.group(1)}</code-interpreter>"
                if case4 or case5:
                    # 跳过思考，直接出现 <answer> 或 <code-interpreter> 标签
                    # 这是允许的
                    pass
                else:
                    # 既没有 <think> 标签，也没有 <answer> 或 <code-interpreter> 标签
                    # 此时 response 里什么也没有，建议 retry inference
                    return None
        return response

    def think_and_answer(
        self,
        history_messages: list[DialogData],
        thought_messages: list[DialogData] = [],
        **inference_args,
    ):
        # history_messages 里定义了任务以及足够的上下文
        # 本函数是在 history_messages 的基础上进行深度推理，继续获取更多信息，做出最后的决策
        # thought_messages 是额外的信息，可能是从外部数据源获取的. 可以注入 thought_messages 来提供更多上下文信息。
        # history_messages 和 thought_messages 都是对话消息列表，每个消息是一个字典，包含 "role" 和 "content" 字段。
        # history_messages + thought_messages 生成 response，如果response 不是 decision，将 response 拼回 thought_messages 中，继续推理。
        # 直到 response 是决策性消息，才将其拼回 history_messages 中。此时 thought_messages 是 history_messages 最后一轮对话的中间结果。
        # inference_args 是推理引擎的参数
        debug = inference_args.get("debug", False)
        current_step = 0
        if len(thought_messages) > 0:
            current_step = sum([1 for m in thought_messages if m["role"] == "assistant"])
        while True:
            current_step += 1
            if debug:
                logger.debug(f"当前推理深度: {current_step}, 历史消息数量: {len(history_messages)}")
            # 调用推理引擎获取回复
            messages = history_messages + thought_messages
            response = self.inference(messages, **inference_args)
            if debug:
                logger.debug(f"🤖【assistant】: {response}")

            # 判断是否有代码解释器标记
            code = extract_code(remove_thoughts(response))
            if code:
                # 如果有代码解释器标记，为规划阶段，执行代码
                content_to_gpt, content_to_display = self.simulator.execute(code)
                # logger.info(json.dumps(content_to_gpt, ensure_ascii=False, indent=2))
                thought_messages.append({"role": "assistant", "content": [{"type": "text", "text": response}]})
                thought_messages.append({"role": "user", "content": content_to_gpt})
            else:
                # 没有代码解释器标记时，为回答阶段，添加到历史记录并返回
                history_messages.append({"role": "assistant", "content": [{"type": "text", "text": response}]})
                break
        return response
