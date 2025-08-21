import os
import re
from pathlib import Path
from typing import Optional
from datetime import datetime

from agentlin.core.types import ToolResult

# 配置常量
AGENTLIN_CONFIG_DIR = '.agentlin'
DEFAULT_MEMORY_FILENAME = 'MEMORY.md'
MEMORY_SECTION_HEADER = '## Memory Bank'


def get_global_memory_file_path() -> str:
    """获取全局记忆文件路径"""
    home_dir = Path.home()
    config_dir = home_dir / AGENTLIN_CONFIG_DIR
    return str(config_dir / DEFAULT_MEMORY_FILENAME)


def ensure_newline_separation(current_content: str) -> str:
    """确保正确的换行分隔"""
    if len(current_content) == 0:
        return ''
    if current_content.endswith('\n\n'):
        return ''
    if current_content.endswith('\n'):
        return '\n'
    return '\n\n'


def perform_add_memory_entry(text: str, memory_file_path: str) -> None:
    """添加记忆条目到文件"""
    # 处理文本
    processed_text = text.strip()
    # 移除可能被误解为 markdown 列表项的前导连字符和空格
    processed_text = processed_text.lstrip('- ').strip()

    # 添加时间戳和分类
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_memory_item = f"- [{timestamp}] {processed_text}"

    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(memory_file_path), exist_ok=True)

        content = ''
        try:
            with open(memory_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            # 文件不存在，将创建包含标题和条目的新文件
            pass

        header_index = content.find(MEMORY_SECTION_HEADER)

        if header_index == -1:
            # 未找到标题，追加标题然后是条目
            separator = ensure_newline_separation(content)
            content += f"{separator}{MEMORY_SECTION_HEADER}\n{new_memory_item}\n"
        else:
            # 找到标题，找到插入新记忆条目的位置
            start_of_section_content = header_index + len(MEMORY_SECTION_HEADER)
            end_of_section_index = content.find('\n## ', start_of_section_content)
            if end_of_section_index == -1:
                end_of_section_index = len(content)  # 文件末尾

            before_section_marker = content[:start_of_section_content].rstrip()
            section_content = content[start_of_section_content:end_of_section_index].rstrip()
            after_section_marker = content[end_of_section_index:]

            section_content += f"\n{new_memory_item}"
            content = f"{before_section_marker}\n{section_content.lstrip()}\n{after_section_marker}".rstrip() + '\n'

        with open(memory_file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    except Exception as error:
        raise Exception(f"添加记忆条目失败: {str(error)}")


def save_memory(fact: str, memory_file_path: Optional[str]=None) -> ToolResult:
    """执行保存记忆操作"""
    if not fact or not isinstance(fact, str) or not fact.strip():
        error_message = '参数 "fact" 必须是非空字符串。'
        return ToolResult(
            message_content=[{"type": "text", "text": f"错误: {error_message}"}],
            block_list=[{"type": "text", "text": f"错误: {error_message}"}],
        )

    try:
        # 保存到文件
        if not memory_file_path:
            memory_file_path = get_global_memory_file_path()
        perform_add_memory_entry(fact, memory_file_path)

        success_message = f'好的，我已经记住了："{fact}"'
        return ToolResult(
            message_content=[{"type": "text", "text": success_message}],
            block_list=[{"type": "text", "text": success_message}],
        )

    except Exception as error:
        error_message = f"保存记忆失败: {str(error)}"
        return ToolResult(
            message_content=[{"type": "text", "text": f"错误: {error_message}"}],
            block_list=[{"type": "text", "text": f"错误: {error_message}"}],
        )


def read_memory_file(file_path: Optional[str] = None) -> ToolResult:
    """读取记忆文件内容"""
    if file_path is None:
        home_dir = Path.home()
        config_dir = home_dir / AGENTLIN_CONFIG_DIR
        file_path = str(config_dir / DEFAULT_MEMORY_FILENAME)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            message = "记忆文件为空。"
        else:
            message = f"记忆文件内容：\n{content}"

        return ToolResult(
            message_content=[{"type": "text", "text": message}],
            block_list=[{"type": "text", "text": message}],
        )

    except FileNotFoundError:
        message = f"记忆文件不存在：{file_path}"
        return ToolResult(
            message_content=[{"type": "text", "text": message}],
            block_list=[{"type": "text", "text": message}],
        )
    except Exception as error:
        error_message = f"读取记忆文件失败: {str(error)}"
        return ToolResult(
            message_content=[{"type": "text", "text": error_message}],
            block_list=[{"type": "text", "text": error_message}],
        )


def parse_preferences(preference_string: str) -> list[tuple[str, str, str]]:
    """
    解析偏好设置字符串，提取日期时间、ID和内容。

    >>> preference_string = \"\"\"
    ... - [2025-02-05 22:11] [123456] fact
    ... - [2025-02-05 22:12] [123457] fact2
    ... \"\"\"
    >>> preferences = parse_preferences(preference_string)
    >>> print(preferences)
    [('2025-02-05 22:11', '123456', 'fact'), ('2025-02-05 22:12', '123457', 'fact2')]
    """
    # 定义正则表达式模式，使用负向前瞻断言允许内容跨越多行
    pattern = re.compile(r"""
        ^\s*-\s*\[            # 匹配开头的 "- ["
        (\d{4}-\d{2}-\d{2}\s\d{2}:\d{2})\]  # 提取日期时间
        \s*\[\s*(\d+)\]\s*    # 提取ID
        (.*?)(?=\Z|^\s*-\s*\[\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}\])  # 提取内容，非贪婪模式，直到字符串结尾或下一个偏好设置开头
    """, re.MULTILINE | re.VERBOSE | re.DOTALL)

    # 查找所有匹配项
    matches = pattern.finditer(preference_string)

    # 构建结果列表
    preferences = []
    for match in matches:
        datetime_str = match.group(1)
        id_str = match.group(2)
        content = match.group(3).strip()
        preferences.append((datetime_str, id_str, content))

    return preferences

if __name__ == '__main__':
    import unittest
    class TestParsePreferences(unittest.TestCase):
        def test_empty_input(self):
            self.assertEqual(parse_preferences(""), [])

        def test_single_todo_with_spaces(self):
            input_str = "  - [2025-02-05 22:11] [123456]   fact with spaces  "
            expected = [('2025-02-05 22:11', '123456', 'fact with spaces')]
            self.assertEqual(parse_preferences(input_str), expected)

        def test_multiple_todos(self):
            input_str = """
            - [2025-02-05 22:11] [123456] fact1
            - [2025-02-06 10:30] [789012] fact2 with colon: and dash-
            """
            expected = [
                ('2025-02-05 22:11', '123456', 'fact1'),
                ('2025-02-06 10:30', '789012', 'fact2 with colon: and dash-')
            ]
            self.assertEqual(parse_preferences(input_str), expected)

        def test_edge_dates_and_ids(self):
            input_str = """
            - [0001-01-01 00:00] [0] min values
            - [9999-12-31 23:59] [999999999999] max values
            - [2025-02-29 00:00] [123456] leap day (invalid date but valid format)
            """
            expected = [
                ('0001-01-01 00:00', '0', 'min values'),
                ('9999-12-31 23:59', '999999999999', 'max values'),
                ('2025-02-29 00:00', '123456', 'leap day (invalid date but valid format)')
            ]
            self.assertEqual(parse_preferences(input_str), expected)

        def test_special_characters_in_content(self):
            input_str = """
            - [2025-02-05 22:11] [123456] !@#$%^&*()_+{}|:\"<>?
            - [2025-02-05 22:12] [123457] 中文内容 Chinese Content
            - [2025-02-05 22:13] [123458] Line1\nLine2\nLine3
            """
            expected = [
                ('2025-02-05 22:11', '123456', '!@#$%^&*()_+{}|:\"<>?'),
                ('2025-02-05 22:12', '123457', '中文内容 Chinese Content'),
                ('2025-02-05 22:13', '123458', 'Line1\nLine2\nLine3')
            ]
            self.assertEqual(parse_preferences(input_str), expected)

        def test_malformed_entries(self):
            input_str = """
            - [2025-02-05 22:11 [123456] missing closing bracket
            - 2025-02-05 22:12] [123457] missing opening bracket
            - [2025-02-05 22:13] [abcdef] non-numeric ID
            [2025-02-05 22:14] [123458] missing dash prefix
            """
            self.assertEqual(parse_preferences(input_str), [])
    # 执行测试
    unittest.main(argv=[''], verbosity=2, exit=False)

    # 运行原始测试示例
    print("\n原始测试示例结果:")
    preference_string = """
    - [2025-02-05 22:11] [123456] fact
    - [2025-02-05 22:12] [123457] fact2
    """
    preferences = parse_preferences(preference_string)
    print(preferences)