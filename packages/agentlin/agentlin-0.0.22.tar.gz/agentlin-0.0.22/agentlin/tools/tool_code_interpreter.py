from typing_extensions import Any, Literal, TypedDict, Optional, Union
import base64
import json
import pickle
import random
import time
import re
import io
from plotly import graph_objects as go
from plotly import io as pio
from PIL import Image
from loguru import logger
from pathlib import Path

from agentlin.code_interpreter.jupyter_parse import iopub_msg_to_tool_response, parse_msg_list_to_tool_response
from agentlin.code_interpreter.types import Block
from agentlin.core.agent_schema import content_to_text, ContentData


class CodeInterpreter:
    def __init__(self, work_dir, debug=False):
        import jupyter_client

        self.debug = debug
        self.kernel_manager, self.kernel_client = jupyter_client.manager.start_new_kernel(kernel_name="python3")
        self.work_dir = work_dir
        self.interrupt_signal = False
        self._create_work_dir()

    def _create_work_dir(self):
        # set work dir in jupyter environment
        if self.debug:
            logger.debug(f"Setting work directory to: {self.work_dir}")
        init_code = f"""
import os
if not os.path.exists('{self.work_dir}'):
    os.mkdir('{self.work_dir}')
os.chdir('{self.work_dir}')
del os
""".strip()
        self._execute_code(init_code)

    def _execute_code(self, code: str):
        msg_id = self.kernel_client.execute(code)

        # Get the output of the code
        msg_list = []
        while True:
            try:
                iopub_msg = self.kernel_client.get_iopub_msg(timeout=1)
                msg_list.append(iopub_msg)
                if iopub_msg["msg_type"] == "status" and iopub_msg["content"].get("execution_state") == "idle":
                    break
            except Exception as e:
                # logger.debug(f"error: {e}\niopub_msg: {iopub_msg}")
                # logger.error(e.with_traceback(e.__traceback__))
                if self.interrupt_signal:
                    self.kernel_manager.interrupt_kernel()
                    self.interrupt_signal = False
                continue

        return msg_id, msg_list

    def inject_variable(self, name: str, obj):
        encoded = base64.b64encode(pickle.dumps(obj)).decode("utf-8")
        code = f"""
import pickle, base64
{name} = pickle.loads(base64.b64decode("{encoded}"))
print("Variable '{name}' injected successfully.")
"""
        return self.execute_code(code)

    def execute_code(self, code: str):
        start_time = time.time()
        msg_id, msg_list = self._execute_code(code)
        process_time = time.time() - start_time
        logger.info(f"代码运行时间: {process_time:.4f}秒")

        response = parse_msg_list_to_tool_response(msg_list, "full")
        content_to_gpt: list[ContentData] = response["message_content"]
        content_to_display: list[Block] = response["block_list"]

        if self.debug:
            lines = []
            lines.append(10 * "=")
            lines.append(content_to_text(content_to_gpt))
            lines.append(10 * "=")
            logger.debug("\n".join(lines))
        return content_to_gpt, content_to_display

    def _stream_execute_code(self, code: str):
        """
        Execute code in the Jupyter kernel and return a generator that yields output messages.
        This is useful for streaming output in real-time.
        """
        msg_id = self.kernel_client.execute(code)

        # Get the output of the code
        while True:
            try:
                iopub_msg = self.kernel_client.get_iopub_msg(timeout=1)
                if iopub_msg["msg_type"] == "status" and iopub_msg["content"].get("execution_state") == "idle":
                    break
                yield iopub_msg
            except Exception as e:
                if self.interrupt_signal:
                    self.kernel_manager.interrupt_kernel()
                    self.interrupt_signal = False
                continue

    def stream_execute_code(self, code: str):
        for iopub_msg in self._stream_execute_code(code):
            if self.debug:
                logger.debug(iopub_msg)
            msg = iopub_msg_to_tool_response(iopub_msg)
            content_to_gpt = msg["message_content"]
            content_to_display = msg["block_list"]
            yield content_to_gpt, content_to_display

    def send_interrupt_signal(self):
        self.interrupt_signal = True

    def restart_jupyter_kernel(self):
        import jupyter_client

        self.kernel_client.shutdown()
        self.kernel_manager, self.kernel_client = jupyter_client.manager.start_new_kernel(kernel_name="python3")
        self.interrupt_signal = False
        self._create_work_dir()

    def shutdown(self):
        if self.debug:
            logger.debug("Shutting down Jupyter kernel")
        self.kernel_client.shutdown()
        self.kernel_manager.shutdown_kernel(now=True)
        self.kernel_manager.cleanup_resources()
        self.kernel_manager = None
        self.kernel_client = None
        self.interrupt_signal = False
        if self.debug:
            logger.debug("Jupyter kernel shutdown complete")


if __name__ == "__main__":
    from pathlib import Path
    import datetime
    import sys
    import os

    work_dir = Path(__file__).parent.parent.parent
    sys.path.append(str(work_dir))

    code_interpreter = CodeInterpreter(str(work_dir), debug=True)
    code = """
print("Hello World!")
import requests
import json
import uuid
import base64

tool_server_url = "http://127.0.0.1:8989/aime"


def generate_short_uuid(length=8):
    # 生成标准 UUID
    uuid_value = uuid.uuid4().bytes

    # 使用 Base64 编码并转换为 URL 安全格式
    encoded = base64.urlsafe_b64encode(uuid_value).decode("ascii")

    # 移除可能的填充字符 '='
    encoded = encoded.rstrip("=")

    # 截取指定长度的字符串
    return encoded[:length]
def run_Search(query):
    req = requests.post(
        tool_server_url,
        json={
            "chain_name": "Search",
            "req_type": "nostream",
            "human_message": query,
            "debug": "false",
            "source": "ths_mobile_yuyinzhushou",
        },
    )
    resp = req.json()
    raw_data = []
    try:
        resp_result = resp["response"]["result"][0]
        raw_data: list[dict[str, str]] = resp_result["raw_data"]
    except Exception as e:
        logger.error(f"请求失败: {e}")
        logger.error(f"响应内容: {json.dumps(resp, indent=2, ensure_ascii=False)}")

    obs = []
    for i, x in enumerate(raw_data):
        texts = []
        if "title" in x and x["title"]:
            if "url" in x and x["url"]:
                texts.append(f"[{x['title']}]({x['url']})")
            else:
                texts.append(f"Title: {x['title']}")
        texts.append(f"ID: {generate_short_uuid()}")
        if "publish_time" in x and x["publish_time"]:
            texts.append(f"Publish Time: {x['publish_time']}")
        if "summary" in x and x["summary"]:
            texts.append(f"Summary: {x['summary']}")
        if "full_summary" in x and x["full_summary"]:
            texts.append(f"Content: {x['full_summary']}")
        obs.append("\\n".join(texts))
    return "\\n\\n".join(obs)
print("Running Search query...")
print(run_Search("国际美股 top 3"))
"""
    code = """
from time import sleep
print("Hello World!")
sleep(3)
print("This is a test for Code Interpreter.")
sleep(3)
print("Let's see how it works with streaming output.")
"""

    for content_to_gpt, content_to_display in code_interpreter.stream_execute_code(code):
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{time_str} - Content to GPT:")
        print(content_to_text(content_to_gpt))
        print(f"{time_str} - Content to Display:")
        print(content_to_display)
        print()
        print()
    # result, _ = code_interpreter.execute_code(code)
    # print(result)
#     code = """
# import pandas as pd
# from typing_extensions import Optional


# def dataframe_to_markdown(df: pd.DataFrame, columns: Optional[list[str]] = None):
#     if not columns:
#         columns = list(df.columns)
#     df = df[columns]
#     markdown = ""

#     # Write column headers
#     markdown += "|" + "index" + "|" + "|".join(columns) + "|" + "\\n"
#     markdown += "|" + "---" + "|" + "|".join(["----"] * len(columns)) + "|" + "\\n"

#     # Write data rows
#     for i, row in df.iterrows():
#         values = []
#         for col in columns:
#             value = row[col]
#             if isinstance(value, str):
#                 values.append(value)
#             elif isinstance(value, float):
#                 values.append(f"{value:.4f}")
#             else:
#                 values.append(str(value))
#         values_str = "|".join(values)
#         markdown += "|" + str(i) + "|" + values_str + "|\\n"

#     markdown = markdown.strip()
#     return markdown


# def _custom_md_repr(self):
#     df = self.head(10)
#     if df.empty:
#         return "DataFrame is empty"
#     text = dataframe_to_markdown(df)
#     return text


# pd.DataFrame._repr_markdown_ = _custom_md_repr

# import pandas as pd
# data = [{'国际美股@stock code': 'BKNG.O',
#   '国际美股@stock name': 'Booking Holdings',
#   '国际美股@last-price': '5475.26',
#   '国际美股@last-change': '0.4314218946611621',
#   '国际美股@Interval Closing Price[20250521-20250528]': 5475.26,
#   '国际美股@Boll(Mid Value)[20250528]': '5250.1760',
#   '{(}国际美股@Interval Closing Price[20250521-20250528]{-}国际美股@Boll(Mid Value)[20250528]{)}': 225.08399999999983,
#   '国际美股@Closing Price[20250528]': 5475.26,
#   '国际美股@Closing Price ranking[20250528]': '1/3122',
#   '国际美股@Closing Price ranking position[20250528]': 1.0,
#   '国际美股@Closing Price ranking base[20250528]': 3122.0},
#  {'国际美股@stock code': 'SEB.A',
#   '国际美股@stock name': 'Seaboard',
#   '国际美股@last-price': '2660.86',
#   '国际美股@last-change': '0.6281554315968659',
#   '国际美股@Interval Closing Price[20250521-20250528]': 2660.86,
#   '国际美股@Boll(Mid Value)[20250528]': '2541.4055',
#   '{(}国际美股@Interval Closing Price[20250521-20250528]{-}国际美股@Boll(Mid Value)[20250528]{)}': 119.45450000000028,
#   '国际美股@Closing Price[20250528]': 2660.86,
#   '国际美股@Closing Price ranking[20250528]': '2/3122',
#   '国际美股@Closing Price ranking position[20250528]': 2.0,
#   '国际美股@Closing Price ranking base[20250528]': 3122.0},
#  {'国际美股@stock code': 'MELI.O',
#   '国际美股@stock name': 'Mercadolibre',
#   '国际美股@last-price': '2550.71',
#   '国际美股@last-change': '-0.1745480731223377',
#   '国际美股@Interval Closing Price[20250521-20250528]': 2550.71,
#   '国际美股@Boll(Mid Value)[20250528]': '2461.9040',
#   '{(}国际美股@Interval Closing Price[20250521-20250528]{-}国际美股@Boll(Mid Value)[20250528]{)}': 88.80600000000004,
#   '国际美股@Closing Price[20250528]': 2550.71,
#   '国际美股@Closing Price ranking[20250528]': '3/3122',
#   '国际美股@Closing Price ranking position[20250528]': 3.0,
#   '国际美股@Closing Price ranking base[20250528]': 3122.0},]
# df = pd.DataFrame(data)
# df
# """
#     result, _ = code_interpreter.execute_code(code)
#     print(result)

#     code = """
# import plotly.graph_objects as go
# x = df['国际美股@stock code']
# y = df['国际美股@last-price']
# fig = go.Figure(data=[go.Bar(x=x, y=y)])
# fig.update_layout(title='国际美股@last-price', xaxis_title='Stock Code', yaxis_title='Last Price')
# fig
# """
#     result, _ = code_interpreter.execute_code(code)
#     print(result)
#     code_interpreter.send_interrupt_signal()
