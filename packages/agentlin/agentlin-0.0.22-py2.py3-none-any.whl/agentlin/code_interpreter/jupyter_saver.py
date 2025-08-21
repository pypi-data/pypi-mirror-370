from agentlin.core.agent_schema import (
    content_to_text,
    extract_action,
    extract_action_block,
    extract_answer,
    extract_code,
    extract_code_block,
    extract_thought,
    messages_to_text,
    remove_thoughts,
)
from agentlin.core.multimodal import (
    base64_to_image,
    image_to_base64,
    scale_to_fit_and_add_scale_bar,
)
from agentlin.core.types import DialogData
from xlin import save_json


class JupyterSaver:
    """
    A class to handle saving Jupyter notebook outputs.
    """

    def __init__(self, filename: str):
        self.filename = filename
        self.cells = []

    def _append_cell(self, cell_type: str, source: list, metadata=None, outputs=None):
        if not source and cell_type != "code":
            return
        if isinstance(source, str):
            source = [source]

        cell = {
            "cell_type": cell_type,
            "metadata": metadata or {},
            "source": source,
        }
        if outputs is not None:
            cell["outputs"] = outputs
        else:
            cell["outputs"] = []

        self.cells.append(cell)

    def _append_raw(self, text: str):
        if text and text.strip():
            self._append_cell("raw", text)

    def _append_markdown(self, text: str):
        if text and text.strip():
            self._append_cell("markdown", text)

    def _append_code(self, code: str, outputs=None):
        if code and code.strip():
            self._append_cell("code", code, outputs=outputs)

    def _process_text_part(self, part: dict, msg: DialogData, i: int, history_len: int, thoughts_len: int):
        text = part["text"]
        if "code-interpreter" in part and not part["code-interpreter"]:
            self._append_markdown(text)
            return

        thought = extract_thought(text)
        if thought and len(thought.strip()) > 10:
            self._append_raw("<think>")
            self._append_markdown(thought)
            self._append_raw("</think>")
            text = remove_thoughts(text)

        cleaned_text = remove_thoughts(text)
        code_block = extract_code_block(cleaned_text)
        if code_block:
            code = extract_code(code_block)
            for i, split in enumerate(text.split(code_block)):
                self._append_markdown(split)
                if i < len(text.split(code_block)) - 1:
                    self._append_raw("<code-interpreter>")
                    self._append_code(code)
                    self._append_raw("</code-interpreter>")
        elif "code-interpreter" in part and part["code-interpreter"]:
            self._append_code(text)
        else:
            action_block = extract_action_block(cleaned_text)
            if action_block:
                action = extract_action(action_block)
                for i, split in enumerate(text.split(action_block)):
                    self._append_markdown(split)
                    if i < len(text.split(action_block)) - 1:
                        self._append_raw("<action>")
                        self._append_code(action)
                        self._append_raw("</action>")
            else:
                code = extract_code(text)
                if code:
                    self._append_code(code)
                else:
                    answer = extract_answer(text)
                    if answer:
                        self._append_markdown(answer)
                    else:
                        is_env_message = (
                            history_len - 1 < i < history_len - 1 + thoughts_len
                            and msg["role"] == "user"
                        )
                        if is_env_message:
                            self._append_raw(text)
                        else:
                            self._append_markdown(text)

    def _process_image_part(self, part: dict):
        image_url = part["image_url"]
        if isinstance(image_url, dict):
            image_url = image_url["url"]

        image = base64_to_image(image_url)
        origin_image = image
        scaled_image = scale_to_fit_and_add_scale_bar(image)

        md_text = (
            f"| 模型看到的图片尺寸: {scaled_image.width}x{scaled_image.height} | 原始图片 {origin_image.width}x{origin_image.height} |\n"
            f"| --- | --- |\n"
            f"| ![模型看到的图片]({image_to_base64(scaled_image)}) | ![原始图片]({image_to_base64(origin_image)}) |"
        )
        self._append_markdown(md_text)

        if "plotly_json" in part:
            fig_json = part["plotly_json"]
            outputs = [
                {
                    "output_type": "display_data",
                    "data": {"application/vnd.plotly.v1+json": fig_json},
                    "metadata": {},
                }
            ]
            self._append_code("", outputs=outputs)

    def _process_message(self, msg: DialogData, i: int, history_len: int, thoughts_len: int):
        icon = "🤖" if msg["role"] == "assistant" else "👤"
        self._append_markdown(f"# {icon}")

        if isinstance(msg["content"], list):
            for part in msg["content"]:
                if part["type"] == "text":
                    self._process_text_part(part, msg, i, history_len, thoughts_len)
                elif part["type"] == "image_url":
                    self._process_image_part(part)
        else:
            self._append_markdown(msg["content"])

    def save(self, history: list[DialogData], thoughts: list[DialogData]):
        self.cells = []

        all_messages = history[:-1] + thoughts + [history[-1]]
        history_len = len(history)
        thoughts_len = len(thoughts)

        for i, msg in enumerate(all_messages):
            self._process_message(msg, i, history_len, thoughts_len)

        notebook = {
            "cells": self.cells,
            "metadata": {
                "kernelspec": {
                    "display_name": "rft",
                    "language": "python",
                    "name": "python3",
                },
                "language_info": {
                    "codemirror_mode": {"name": "ipython", "version": 3},
                    "file_extension": ".py",
                    "mimetype": "text/x-python",
                    "name": "python",
                    "nbconvert_exporter": "python",
                    "pygments_lexer": "ipython3",
                    "version": "3.10.14",
                },
            },
            "nbformat": 4,
            "nbformat_minor": 2,
        }
        save_json(notebook, self.filename)


def save_jupyter_notebook(history: list[DialogData], thoughts: list[DialogData], path: str):
    cells = []

    def append_raw(text: str):
        if not text or len(text.strip()) == 0:
            return
        cells.append(
            {
                "cell_type": "raw",
                "metadata": {},
                "source": [text],
                "outputs": [],
            }
        )

    def append_markdown(text: str):
        if not text or len(text.strip()) == 0:
            return
        cells.append(
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [text],
                "outputs": [],
            }
        )

    def append_code(code: str):
        if not code or len(code.strip()) == 0:
            return
        cells.append(
            {
                "cell_type": "code",
                "metadata": {},
                "source": [code],
                "outputs": [],
            }
        )

    for i, msg in enumerate(history[:-1] + thoughts + [history[-1]]):
        icon = "🤖" if msg["role"] == "assistant" else "👤"
        append_markdown(f"# {icon}")
        if "content" not in msg:
            if "tool_calls" in msg:
                append_raw(messages_to_text([msg]))
            continue
        elif isinstance(msg["content"], list):
            for part in msg["content"]:
                if part["type"] == "text":
                    text = part["text"]
                    if "code-interpreter" in part and not part["code-interpreter"]:
                        append_markdown(text)
                    else:
                        thought = extract_thought(text)
                        if thought and len(thought.strip()) > 10:
                            append_raw("<think>")
                            append_markdown(thought)
                            append_raw("</think>")
                            text = remove_thoughts(text)
                        code_block = extract_code_block(remove_thoughts(text))
                        if code_block:
                            code = extract_code(code_block)
                            for i, split in enumerate(text.split(code_block)):
                                append_markdown(split)
                                if i < len(text.split(code_block)) - 1:
                                    append_raw("<code-interpreter>")
                                    append_code(code)
                                    append_raw("</code-interpreter>")
                        elif "code-interpreter" in part and part["code-interpreter"]:
                            code = text
                            append_code(code)
                        else:
                            code_block = extract_action_block(remove_thoughts(text))
                            if code_block:
                                code = extract_action(code_block)
                                for i, split in enumerate(text.split(code_block)):
                                    append_markdown(split)
                                    if i < len(text.split(code_block)) - 1:
                                        append_raw("<action>")
                                        append_code(code)
                                        append_raw("</action>")
                            else:
                                code = extract_code(text)
                                if code:
                                    append_code(code)
                                else:
                                    answer = extract_answer(text)
                                    if answer:
                                        append_markdown(answer)
                                    else:
                                        if len(history) - 1 < i < len(history) - 1 + len(thoughts) and msg["role"] == "user":
                                            # planning 阶段的 user 为环境
                                            append_raw(text)
                                        else:
                                            append_markdown(text)
                elif part["type"] == "image_url":
                    image_url = part["image_url"]
                    if isinstance(image_url, dict):
                        image_url = image_url["url"]
                    image = base64_to_image(image_url)
                    origin_image = image
                    image = scale_to_fit_and_add_scale_bar(image)  # 缩放图片到目标大小，并添加比例尺
                    md_text = "| {left_img} | {right_image} |\n| --- | --- |\n| ![模型看到的图片]({image_url}) | ![原始图片]({origin_image_url}) |".format(
                        left_img=f"模型看到的图片尺寸: {image.width}x{image.height}",
                        right_image=f"原始图片 {origin_image.width}x{origin_image.height}",
                        image_url=image_to_base64(image),
                        origin_image_url=image_to_base64(origin_image),
                    )
                    append_markdown(md_text)
                    if "plotly_json" in part:
                        fig_json = part["plotly_json"]
                        cells.append(
                            {
                                "cell_type": "code",
                                "metadata": {},
                                "source": [],
                                "outputs": [
                                    {
                                        "output_type": "display_data",
                                        "data": {
                                            "application/vnd.plotly.v1+json": fig_json,
                                        },
                                        "metadata": {},
                                    }
                                ],
                            }
                        )
        else:
            append_markdown(msg["content"])
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "rft",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3,
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.10.14",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 2,
    }
    save_json(notebook, path)
