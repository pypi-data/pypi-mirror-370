"""
支持通过路径或 glob 模式读取多个文件的内容。
对于文本文件，将内容连接成单个字符串；对于图像、PDF、音频和视频文件，返回 base64 编码的数据。
"""

import os
import glob
import mimetypes
import base64
import traceback
from typing import List, Optional, Dict, Any, Set
import fnmatch

from xlin import xmap_async
from agentlin.core.types import ToolResult


# 默认排除模式（与 TypeScript 版本保持一致）
DEFAULT_EXCLUDES = [
    '**/node_modules/**',
    '**/.git/**',
    '**/.vscode/**',
    '**/.idea/**',
    '**/dist/**',
    '**/build/**',
    '**/coverage/**',
    '**/__pycache__/**',
    '**/*.pyc',
    '**/*.pyo',
    '**/*.bin',
    '**/*.exe',
    '**/*.dll',
    '**/*.so',
    '**/*.dylib',
    '**/*.class',
    '**/*.jar',
    '**/*.war',
    '**/*.zip',
    '**/*.tar',
    '**/*.gz',
    '**/*.bz2',
    '**/*.rar',
    '**/*.7z',
    '**/*.doc',
    '**/*.docx',
    '**/*.xls',
    '**/*.xlsx',
    '**/*.ppt',
    '**/*.pptx',
    '**/*.odt',
    '**/*.ods',
    '**/*.odp',
    '**/.DS_Store',
    '**/.env',
]

# 文件类型常量
DEFAULT_ENCODING = 'utf-8'
DEFAULT_MAX_LINES_TEXT_FILE = 2000
MAX_LINE_LENGTH_TEXT_FILE = 2000
DEFAULT_OUTPUT_SEPARATOR_FORMAT = '--- {filePath} ---'
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB
SVG_MAX_SIZE_BYTES = 1 * 1024 * 1024  # 1MB for SVG files


def _safe_relative_path(file_path: str, target_directory: str) -> str:
    """安全地计算相对路径，处理文件在目标目录外的情况"""
    try:
        if _is_within_root(file_path, target_directory):
            return os.path.relpath(file_path, target_directory).replace('\\', '/')
        else:
            # 如果文件不在目标目录内，返回文件名或简化的路径
            return os.path.basename(file_path)
    except ValueError:
        # 在某些情况下 os.path.relpath 可能失败
        return os.path.basename(file_path)


def _is_within_root(path_to_check: str, root_directory: str) -> bool:
    """检查路径是否在给定的根目录内"""
    normalized_path = os.path.abspath(path_to_check)
    normalized_root = os.path.abspath(root_directory)

    # 确保根目录路径以分隔符结尾以进行正确的 startswith 比较
    if not normalized_root.endswith(os.sep):
        normalized_root += os.sep

    return (
        normalized_path == normalized_root.rstrip(os.sep) or
        normalized_path.startswith(normalized_root)
    )

def _is_binary_file(file_path: str) -> bool:
    """基于内容采样确定文件是否可能是二进制文件"""
    try:
        with open(file_path, 'rb') as f:
            # 读取最多 4KB 或文件大小，取较小者
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return False  # 空文件不被视为二进制

            buffer_size = min(4096, file_size)
            buffer = f.read(buffer_size)

            if len(buffer) == 0:
                return False

            # 空字节是强指示符
            if b'\x00' in buffer:
                return True

            # 如果 >30% 的非可打印字符，则视为二进制
            non_printable_count = 0
            for byte in buffer:
                if byte < 9 or (byte > 13 and byte < 32):
                    non_printable_count += 1

            return non_printable_count / len(buffer) > 0.3

    except Exception as e:
        # 如果发生任何错误，在这里视为非二进制文件
        return False

def _detect_file_type(file_path: str) -> str:
    """检测文件类型：'text', 'image', 'pdf', 'audio', 'video', 'binary', 'svg'"""
    ext = os.path.splitext(file_path)[1].lower()

    # TypeScript 文件的特殊处理
    if ext == '.ts':
        return 'text'

    if ext == '.svg':
        return 'svg'

    # 使用 mimetypes 模块
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        if mime_type.startswith('image/'):
            return 'image'
        if mime_type.startswith('audio/'):
            return 'audio'
        if mime_type.startswith('video/'):
            return 'video'
        if mime_type == 'application/pdf':
            return 'pdf'

    # 严格的二进制检查，用于常见的非文本扩展名
    binary_extensions = {
        '.zip', '.tar', '.gz', '.exe', '.dll', '.so', '.class', '.jar',
        '.war', '.7z', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.odt', '.ods', '.odp', '.bin', '.dat', '.obj', '.o', '.a',
        '.lib', '.wasm', '.pyc', '.pyo'
    }

    if ext in binary_extensions:
        return 'binary'

    # 基于内容的回退检查
    if _is_binary_file(file_path):
        return 'binary'

    return 'text'


async def _process_file_wrapper(args):
    """包装函数用于 xmap_async，接受参数元组"""
    file_path, target_directory = args
    return _process_single_file_content(target_directory, file_path)


def _process_single_file_content(
    target_directory: str,
    file_path: str,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """处理单个文件，返回包含内容和元数据的字典"""
    try:
        if not os.path.exists(file_path):
            return {
                'content': None,
                'display': 'File not found.',
                'error': f'File not found: {file_path}',
                'type': 'error'
            }

        if os.path.isdir(file_path):
            return {
                'content': None,
                'display': 'Path is a directory.',
                'error': f'Path is a directory, not a file: {file_path}',
                'type': 'error'
            }

        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE_BYTES:
            return {
                'content': None,
                'display': f'File too large: {file_size / (1024*1024):.2f}MB',
                'error': f'File size exceeds 20MB limit: {file_path}',
                'type': 'error'
            }

        file_type = _detect_file_type(file_path)
        relative_path = _safe_relative_path(file_path, target_directory)

        if file_type == 'binary':
            return {
                'content': f'Cannot display content of binary file: {relative_path}',
                'display': f'Skipped binary file: {relative_path}',
                'type': 'binary',
                'relative_path': relative_path
            }

        elif file_type == 'svg':
            if file_size > SVG_MAX_SIZE_BYTES:
                return {
                    'content': None,
                    'display': f'SVG file too large: {file_size / 1024:.1f}KB',
                    'error': f'SVG file exceeds 1MB limit: {file_path}',
                    'type': 'error'
                }

            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # SVG 文件应该是 UTF-8，如果不是则可能有问题
                return {
                    'content': f'Cannot decode SVG file: {relative_path}',
                    'display': f'Skipped SVG file with encoding issues: {relative_path}',
                    'type': 'binary',
                    'relative_path': relative_path
                }

            return {
                'content': content,
                'display': f'Read SVG as text: {relative_path}',
                'type': 'text',
                'relative_path': relative_path
            }

        elif file_type == 'text':
            try:
                with open(file_path, 'r', encoding=DEFAULT_ENCODING, errors='replace') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # 如果 UTF-8 解码失败，尝试其他常见编码
                encodings_to_try = ['latin1', 'cp1252', 'iso-8859-1']
                content = None
                for encoding in encodings_to_try:
                    try:
                        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                            content = f.read()
                        break
                    except (UnicodeDecodeError, LookupError):
                        continue

                if content is None:
                    # 如果所有编码都失败，作为二进制文件处理
                    return {
                        'content': f'Cannot decode text file: {relative_path}',
                        'display': f'Skipped file with encoding issues: {relative_path}',
                        'type': 'binary',
                        'relative_path': relative_path
                    }

            lines = content.split('\n')
            original_line_count = len(lines)

            start_line = offset or 0
            effective_limit = limit if limit is not None else DEFAULT_MAX_LINES_TEXT_FILE
            end_line = min(start_line + effective_limit, original_line_count)
            actual_start_line = min(start_line, original_line_count)

            selected_lines = lines[actual_start_line:end_line]

            # 处理行长度截断
            lines_were_truncated_in_length = False
            formatted_lines = []
            for line in selected_lines:
                if len(line) > MAX_LINE_LENGTH_TEXT_FILE:
                    formatted_lines.append(line[:MAX_LINE_LENGTH_TEXT_FILE] + '...[line truncated]')
                    lines_were_truncated_in_length = True
                else:
                    formatted_lines.append(line)

            content_range_truncated = end_line < original_line_count
            is_truncated = content_range_truncated or lines_were_truncated_in_length

            text_content = ''
            if content_range_truncated:
                text_content += f'[Content truncated: showing lines {actual_start_line + 1}-{end_line} of {original_line_count} total lines]\n'
            elif lines_were_truncated_in_length:
                text_content += f'[Some lines truncated at {MAX_LINE_LENGTH_TEXT_FILE} characters]\n'

            text_content += '\n'.join(formatted_lines)

            return {
                'content': text_content,
                'display': '(truncated)' if is_truncated else '',
                'type': 'text',
                'is_truncated': is_truncated,
                'original_line_count': original_line_count,
                'lines_shown': [actual_start_line + 1, end_line],
                'relative_path': relative_path
            }

        elif file_type in ['image', 'pdf', 'audio', 'video']:
            with open(file_path, 'rb') as f:
                content_buffer = f.read()

            base64_data = base64.b64encode(content_buffer).decode('utf-8')

            # 确定 MIME 类型
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                ext = os.path.splitext(file_path)[1].lower()
                if file_type == 'image':
                    mime_type = f'image/{ext[1:]}' if ext else 'image/png'
                elif file_type == 'pdf':
                    mime_type = 'application/pdf'
                elif file_type == 'audio':
                    mime_type = f'audio/{ext[1:]}' if ext else 'audio/mpeg'
                elif file_type == 'video':
                    mime_type = f'video/{ext[1:]}' if ext else 'video/mp4'

            # 返回字典格式的文件内容
            file_content = {
                'type': 'file',
                'inlineData': {
                    'mimeType': mime_type,
                    'data': base64_data
                }
            }

            return {
                'content': file_content,
                'display': f'Read {file_type} file: {relative_path}',
                'type': file_type,
                'relative_path': relative_path
            }

        else:
            return {
                'content': f'Unhandled file type: {file_type}',
                'display': f'Skipped unhandled file type: {relative_path}',
                'error': f'Unhandled file type for {file_path}',
                'type': 'error'
            }

    except Exception as e:
        error_message = str(e)
        display_path = _safe_relative_path(file_path, target_directory)
        return {
            'content': f'Error reading file {display_path}: {error_message}',
            'display': f'Error reading file {display_path}: {error_message}',
            'error': f'Error reading file {file_path}: {error_message}',
            'type': 'error'
        }



def _find_files_by_patterns(
    target_directory: str,
    patterns: List[str],
    exclude_patterns: List[str],
    respect_git_ignore: bool = True,
) -> Set[str]:
    """使用 glob 模式查找文件，应用排除规则"""
    files_to_consider = set()

    # 读取 .gitignore 模式
    gitignore_patterns = []
    if respect_git_ignore:
        gitignore_path = os.path.join(target_directory, '.gitignore')
        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    gitignore_patterns = [
                        line.strip() for line in f.readlines()
                        if line.strip() and not line.startswith('#')
                    ]
            except Exception:
                pass  # 忽略读取错误

    # 应用搜索模式
    for pattern in patterns:
        # 处理绝对路径和相对路径
        if os.path.isabs(pattern):
            # 对于绝对路径，检查是否在 target_directory 内
            abs_pattern = os.path.abspath(pattern)
            abs_target = os.path.abspath(target_directory)

            # 如果绝对路径在目标目录内，转换为相对路径
            if abs_pattern.startswith(abs_target + os.sep) or abs_pattern == abs_target:
                pattern = os.path.relpath(abs_pattern, abs_target)
                full_pattern = os.path.join(target_directory, pattern)
            else:
                # 如果绝对路径不在目标目录内，直接使用绝对路径
                full_pattern = abs_pattern
        else:
            # 相对路径，相对于目标目录
            full_pattern = os.path.join(target_directory, pattern)

        # 使用 glob 查找文件
        try:
            matches = glob.glob(full_pattern, recursive=True)
            for match in matches:
                if os.path.isfile(match):
                    # 如果使用绝对路径搜索，不要求文件在 target_directory 内
                    if os.path.isabs(pattern) and not _is_within_root(match, target_directory):
                        # 对于目标目录外的文件，仍然添加到结果中
                        files_to_consider.add(os.path.abspath(match))
                    elif _is_within_root(match, target_directory):
                        files_to_consider.add(os.path.abspath(match))
        except Exception:
            continue  # 忽略无效模式

    # 应用排除模式
    filtered_files = set()
    all_exclude_patterns = exclude_patterns + gitignore_patterns

    for file_path in files_to_consider:
        # 检查文件是否在 target_directory 内
        if _is_within_root(file_path, target_directory):
            # 文件在目标目录内，使用相对路径进行排除匹配
            relative_path = os.path.relpath(file_path, target_directory).replace('\\', '/')
        else:
            # 文件在目标目录外，使用文件的绝对路径进行排除匹配
            # 但是，对于外部文件，我们应该使用更宽松的排除策略
            # 这里我们主要关注文件名和直接父目录的排除
            relative_path = os.path.basename(file_path)

        should_exclude = False

        for exclude_pattern in all_exclude_patterns:
            # 标准化模式以进行匹配
            if exclude_pattern.startswith('/'):
                exclude_pattern = exclude_pattern[1:]

            # 标准化模式路径分隔符
            exclude_pattern = exclude_pattern.replace('\\', '/')

            # 使用 fnmatch 进行模式匹配
            # 1. 完整路径匹配
            if fnmatch.fnmatch(relative_path, exclude_pattern):
                should_exclude = True
                break

            # 2. 如果模式以 **/ 开头，则匹配任何深度的路径
            if exclude_pattern.startswith('**/'):
                pattern_without_prefix = exclude_pattern[3:]  # 移除 **/
                # 检查文件名是否匹配
                if fnmatch.fnmatch(os.path.basename(file_path), pattern_without_prefix):
                    should_exclude = True
                    break
                # 检查路径的任何部分是否匹配完整模式
                path_parts = relative_path.split('/')
                for i in range(len(path_parts)):
                    sub_path = '/'.join(path_parts[i:])
                    if fnmatch.fnmatch(sub_path, pattern_without_prefix):
                        should_exclude = True
                        break
                if should_exclude:
                    break

            # 3. 简单的文件名匹配
            if fnmatch.fnmatch(os.path.basename(file_path), exclude_pattern):
                should_exclude = True
                break

        if not should_exclude:
            filtered_files.add(file_path)

    return filtered_files


async def read_many_files(
    paths: List[str],
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    recursive: bool = True,
    target_directory: Optional[str] = None,
    use_default_excludes: bool = True,
    respect_git_ignore: bool = True,
) -> ToolResult:
    """
    读取多个文件的便利函数

    Args:
        paths: 文件路径或 glob 模式列表
        include: 要包含的额外模式
        exclude: 要排除的模式
        recursive: 是否递归搜索
        target_directory: 目标目录
        use_default_excludes: 是否使用默认排除列表
        respect_git_ignore: 是否遵循 .gitignore

    Returns:
        包含处理结果的字典
    """
    try:
        if not paths:
            return ToolResult(
                message_content=[{"type": "text", "text": "Error: No paths provided"}],
                block_list=[{"type": "text", "text": "Error: No paths provided"}],
            )
        if not include:
            include = []
        if not exclude:
            exclude = []

        # 确保 target_directory 不为 None
        if target_directory is None:
            target_directory = os.getcwd()

        # 准备排除模式
        effective_excludes = []
        if use_default_excludes:
            effective_excludes.extend(DEFAULT_EXCLUDES)
        if exclude:
            effective_excludes.extend(exclude)

        # 合并搜索模式
        search_patterns = paths + include

        # 查找文件
        files_to_consider = _find_files_by_patterns(
            target_directory,
            search_patterns,
            effective_excludes,
            respect_git_ignore,
        )

        if not files_to_consider:
            return ToolResult(
                message_content=[{"type": "text", "text": f"No files found matching patterns: {search_patterns}"}],
                block_list=[{"type": "text", "text": f"No files found matching patterns: {search_patterns}"}],
            )

        # 处理文件 - 智能选择串行或并行处理
        sorted_files = sorted(files_to_consider)
        file_count = len(sorted_files)

        # 根据文件数量决定是否使用并行处理
        # 对于少量文件（<= 20个），使用串行处理避免并行开销
        # 对于大量文件（> 20个），使用并行处理提高效率
        use_parallel = file_count > 20

        if use_parallel:
            # 并行处理大量文件
            file_args = [(file_path, target_directory) for file_path in sorted_files]
            results = await xmap_async(file_args, _process_file_wrapper, is_async_work_func=True, max_workers=4)
        else:
            # 串行处理少量文件
            results = []
            for file_path in sorted_files:
                result = _process_single_file_content(target_directory, file_path)
                results.append(result)

        processed_files = []
        skipped_files = []
        content_parts = []
        reference_number = 0

        for file_path, result in zip(sorted_files, results):
            reference_number += 1

            if result['type'] == 'error' or result['type'] == 'binary':
                skipped_files.append({
                    'path': result.get('relative_path', _safe_relative_path(file_path, target_directory)),
                    'reason': result.get('display', 'Unknown error')
                })
            else:
                processed_files.append(result['relative_path'])

                if result['type'] == 'text':
                    # 为文本文件添加分隔符和内容
                    separator = DEFAULT_OUTPUT_SEPARATOR_FORMAT.format(
                        filePath=result['relative_path'],
                    )
                    content_parts.append({"type": "text", "text": f"\n{separator}\n", "id": reference_number})
                    content_parts.append({"type": "text", "text": result['content'], "id": reference_number})
                else:
                    # 对于图像/PDF/音频/视频文件，添加文件内容
                    if isinstance(result['content'], dict) and 'type' in result['content']:
                        result['content']["id"] = reference_number
                        content_parts.append(result['content'])
                    else:
                        # 处理其他类型的内容
                        content_parts.append({
                            "type": "text",
                            "text": f"File: {result['relative_path']}\nContent: {result['content']}",
                            "id": reference_number
                        })

        # 构建显示消息
        display_message = f"### ReadManyFiles Result (Target Dir: `{target_directory}`)\n\n"

        if processed_files:
            display_message += f"**Processed {len(processed_files)} files:**\n"
            for file_path in processed_files:
                display_message += f"- `{file_path}`\n"
            display_message += "\n"

        if skipped_files:
            display_message += f"**Skipped {len(skipped_files)} files:**\n"
            for skipped in skipped_files:
                display_message += f"- `{skipped['path']}`: {skipped['reason']}\n"
            display_message += "\n"

        if not processed_files and not skipped_files:
            display_message += "No files were found or processed.\n"

        # 如果没有内容，添加错误消息
        if not content_parts:
            content_parts.append({"type": "text", "text": "No file content was successfully read."})

        return ToolResult(
            message_content=content_parts,
            block_list=content_parts,
        )

    except Exception as e:
        error_message = f"Error executing multi-file read: {str(e)}\n{traceback.format_exc()}"
        return ToolResult(
            message_content=[{"type": "text", "text": error_message}],
            block_list=[{"type": "text", "text": error_message}],
        )
