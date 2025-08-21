import fnmatch
import re
import base64
import mimetypes
from pathlib import Path
from typing import List, Optional, TypedDict
import glob as glob_module

try:
    import pyripgrep
    HAS_PYRIPGREP = True
except ImportError:
    HAS_PYRIPGREP = False


def list_directory(path: str, ignore: Optional[List[str]] = None, respect_git_ignore: bool = True) -> str:
    """
    列出指定目录中的文件和子目录。

    Args:
        path (str): 要列出的目录路径。
        ignore (List[str], optional): 要忽略的文件或目录列表。默认为 None。
        respect_git_ignore (bool, optional): 是否遵循 .gitignore 文件规则。默认为 True。

    Returns:
        str: 目录内容的字符串表示。
    """
    path_obj = Path(path)
    if not path_obj.exists():
        return f"Error: Directory '{path}' does not exist."

    if not path_obj.is_dir():
        return f"Error: '{path}' is not a directory."

    try:
        entries = []
        ignored_patterns = ignore or []
        gitignore_patterns = []

        # 读取 .gitignore 文件
        if respect_git_ignore:
            gitignore_path = path_obj / '.gitignore'
            if gitignore_path.exists():
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    gitignore_patterns = [
                        line.strip() for line in f.readlines()
                        if line.strip() and not line.startswith('#')
                    ]

        # 获取目录内容
        for item in path_obj.iterdir():
            item_name = item.name

            # 检查是否应该忽略
            should_ignore = False

            # 检查用户指定的忽略模式
            for pattern in ignored_patterns:
                if fnmatch.fnmatch(item_name, pattern):
                    should_ignore = True
                    break

            # 检查 .gitignore 模式
            if not should_ignore and respect_git_ignore:
                for pattern in gitignore_patterns:
                    if fnmatch.fnmatch(item_name, pattern):
                        should_ignore = True
                        break

            if not should_ignore:
                is_dir = item.is_dir()
                entries.append((item_name, is_dir))

        # 排序：目录优先，然后按字母顺序
        entries.sort(key=lambda x: (not x[1], x[0].lower()))

        # 格式化输出
        result = f"Directory listing for {path}:\n"
        for name, is_dir in entries:
            prefix = "[DIR] " if is_dir else ""
            result += f"{prefix}{name}\n"

        return result

    except PermissionError:
        return f"Error: Permission denied to access directory '{path}'."
    except Exception as e:
        return f"Error listing directory '{path}': {str(e)}"


def read_file(path: str, offset: Optional[int] = None, limit: Optional[int] = None):
    """
    读取并返回指定文件的内容。支持文本、图像和PDF文件。

    Args:
        path (str): 要读取的文件的绝对路径。
        offset (Optional[int]): 文本文件中开始读取的起始行号（从0开始）。
        limit (Optional[int]): 最大读取行数。

    Returns:
        Union[str, dict]: 文本文件返回字符串内容，图像/PDF返回包含base64数据的字典。
    """
    path_obj = Path(path)
    if not path_obj.exists():
        return f"Error: File '{path}' does not exist."

    if not path_obj.is_file():
        return f"Error: '{path}' is not a file."

    try:
        # 获取文件扩展名和MIME类型
        ext = path_obj.suffix.lower()
        mime_type, _ = mimetypes.guess_type(path)

        # 图像文件处理
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp']:
            with open(path, 'rb') as f:
                content = f.read()
                encoded_content = base64.b64encode(content).decode('utf-8')
                return {
                    'inlineData': {
                        'mimeType': mime_type or f'image/{ext[1:]}',
                        'data': encoded_content
                    }
                }

        # PDF文件处理
        elif ext == '.pdf':
            with open(path, 'rb') as f:
                content = f.read()
                encoded_content = base64.b64encode(content).decode('utf-8')
                return {
                    'inlineData': {
                        'mimeType': 'application/pdf',
                        'data': encoded_content
                    }
                }

        # 二进制文件检测
        elif _is_binary_file(path):
            return f"Cannot display content of binary file: {path}"

        # 文本文件处理
        else:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                total_lines = len(lines)

                # 处理offset和limit
                if offset is not None and limit is not None:
                    start = max(0, offset)
                    end = min(total_lines, start + limit)
                    selected_lines = lines[start:end]
                    content = ''.join(selected_lines)

                    if start > 0 or end < total_lines:
                        prefix = f"[File content truncated: showing lines {start+1}-{end} of {total_lines} total lines...]\n"
                        content = prefix + content
                elif limit is not None:
                    # 只设置limit，从头开始读取
                    selected_lines = lines[:limit]
                    content = ''.join(selected_lines)

                    if limit < total_lines:
                        prefix = f"[File content truncated: showing first {limit} lines of {total_lines} total lines...]\n"
                        content = prefix + content
                else:
                    # 读取整个文件，但有默认限制
                    max_lines = 2000
                    if total_lines > max_lines:
                        selected_lines = lines[:max_lines]
                        content = ''.join(selected_lines)
                        prefix = f"[File content truncated: showing first {max_lines} lines of {total_lines} total lines...]\n"
                        content = prefix + content
                    else:
                        content = ''.join(lines)

                return content

    except UnicodeDecodeError:
        return f"Cannot display content of binary file: {path}"
    except PermissionError:
        return f"Error: Permission denied to read file '{path}'."
    except Exception as e:
        return f"Error reading file '{path}': {str(e)}"


def _is_binary_file(file_path: str) -> bool:
    """检测文件是否为二进制文件"""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:
                return True
            # 检查非文本字符的比例
            text_chars = sum(1 for c in chunk if c in range(32, 127) or c in [9, 10, 13])
            return len(chunk) > 0 and text_chars / len(chunk) < 0.85
    except:
        return True


def write_file(file_path: str, content: str) -> str:
    """
    将内容写入指定文件。如果文件存在将被覆盖，如果不存在将创建新文件。

    Args:
        file_path (str): 要写入的文件的绝对路径。
        content (str): 要写入文件的内容。

    Returns:
        str: 操作结果信息。
    """
    try:
        # 检查父目录是否存在，不存在则创建
        file_path_obj = Path(file_path)
        parent_dir = file_path_obj.parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)

        file_existed = file_path_obj.exists()

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        if file_existed:
            return f"Successfully overwrote file: {file_path}"
        else:
            return f"Successfully created and wrote to new file: {file_path}"

    except PermissionError:
        return f"Error: Permission denied to write file '{file_path}'."
    except Exception as e:
        return f"Error writing file '{file_path}': {str(e)}"


def glob(pattern: str, path: Optional[str] = None, case_sensitive: bool = False,
         respect_git_ignore: bool = True) -> str:
    """
    查找匹配特定glob模式的文件，返回按修改时间排序的绝对路径列表。

    Args:
        pattern (str): 用于匹配的glob模式。
        path (Optional[str]): 要搜索的目录的绝对路径，若未指定则在当前目录搜索。
        case_sensitive (bool): 是否区分大小写，默认False。
        respect_git_ignore (bool): 是否遵循.gitignore，默认True。

    Returns:
        str: 匹配文件的路径列表，按修改时间排序。
    """
    search_path_obj = Path(path) if path else Path.cwd()
    search_path = str(search_path_obj)

    if not search_path_obj.exists():
        return f"Error: Search path '{search_path}' does not exist."

    try:
        gitignore_patterns = []

        # 读取.gitignore文件
        if respect_git_ignore:
            gitignore_path = search_path_obj / '.gitignore'
            if gitignore_path.exists():
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    gitignore_patterns = [
                        line.strip() for line in f.readlines()
                        if line.strip() and not line.startswith('#')
                    ]

        # 默认忽略的目录
        default_ignore = {'.git', 'node_modules', '__pycache__', '.vscode', '.idea', 'venv', 'env'}

        # 搜索匹配的文件
        matches = []
        search_pattern = search_path_obj / pattern

        # 使用glob模块查找文件
        found_files = glob_module.glob(str(search_pattern), recursive=True)

        for file_path in found_files:
            file_path_obj = Path(file_path)
            if not file_path_obj.is_file():
                continue

            # 获取相对路径用于匹配
            rel_path = file_path_obj.relative_to(search_path_obj)
            file_name = file_path_obj.name

            # 检查是否应该忽略
            should_ignore = False

            # 检查路径中是否包含默认忽略的目录
            path_parts = rel_path.parts
            if any(part in default_ignore for part in path_parts):
                should_ignore = True

            # 检查.gitignore模式
            if not should_ignore and respect_git_ignore:
                for ignore_pattern in gitignore_patterns:
                    if fnmatch.fnmatch(str(rel_path), ignore_pattern) or fnmatch.fnmatch(file_name, ignore_pattern):
                        should_ignore = True
                        break

            if not should_ignore:
                # 大小写敏感性处理
                if not case_sensitive:
                    pattern_lower = pattern.lower()
                    if fnmatch.fnmatch(str(rel_path).lower(), pattern_lower):
                        matches.append(file_path)
                else:
                    matches.append(file_path)

        # 按修改时间排序（最新的在前）
        matches.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)

        # 格式化输出
        count = len(matches)
        if count == 0:
            return f"Found 0 files matching \"{pattern}\" within {search_path}"

        result = f"Found {count} file(s) matching \"{pattern}\" within {search_path}, sorted by modification time (newest first):\n"
        for match in matches:
            result += f"{match}\n"

        return result

    except Exception as e:
        return f"Error searching for pattern '{pattern}' in '{search_path}': {str(e)}"


def search_file_content(pattern: str, path: Optional[str] = None, include: Optional[str] = None) -> str:
    """
    在指定目录内的文件内容中搜索正则表达式模式。

    Args:
        pattern (str): 要搜索的正则表达式。
        path (Optional[str]): 要搜索的目录的绝对路径，默认为当前工作目录。
        include (Optional[str]): 过滤要搜索的文件的glob模式。

    Returns:
        str: 匹配内容的行、文件路径和行号。
    """
    search_path_obj = Path(path) if path else Path.cwd()
    search_path = str(search_path_obj)

    if not search_path_obj.exists():
        return f"Error: Search path '{search_path}' does not exist."

    try:
        # 如果有 ripgrep-python，使用它进行搜索
        if HAS_PYRIPGREP:
            return _search_with_pyripgrep(pattern, search_path, include)
        else:
            # 回退到原始实现
            return _search_with_regex(pattern, search_path_obj, include)

    except Exception as e:
        return f"Error searching for pattern '{pattern}' in '{search_path}': {str(e)}"


def _search_with_pyripgrep(pattern: str, search_path: str, include: Optional[str] = None) -> str:
    """使用 ripgrep-python 进行搜索"""
    try:
        grep = pyripgrep.Grep()

        # 使用 content 模式获取匹配的行和行号
        results = grep.search(
            pattern,
            path=search_path,
            output_mode="content",
            n=True,  # 显示行号
            glob=include,  # 使用 glob 过滤文件
        )

        if not results:
            filter_info = f" (filter: \"{include}\")" if include else ""
            return f"Found 0 matches for pattern \"{pattern}\" in path \"{search_path}\"{filter_info}"

        # 解析结果并格式化输出
        total_matches = len(results)
        filter_info = f" (filter: \"{include}\")" if include else ""
        result = f"Found {total_matches} matches for pattern \"{pattern}\" in path \"{search_path}\"{filter_info}:\n"

        # 按文件分组结果
        files_matches = {}
        for line in results:
            # 格式: "path:line_number:content"
            try:
                parts = line.split(':', 2)
                if len(parts) >= 3:
                    file_path, line_num, content = parts[0], parts[1], parts[2]
                    rel_path = Path(file_path).relative_to(Path(search_path)) if Path(file_path).is_absolute() else Path(file_path)

                    if str(rel_path) not in files_matches:
                        files_matches[str(rel_path)] = []
                    files_matches[str(rel_path)].append((line_num, content))
                else:
                    # 如果格式不正确，直接使用原始行
                    if "unknown" not in files_matches:
                        files_matches["unknown"] = []
                    files_matches["unknown"].append(("?", line))
            except Exception:
                # 解析失败，使用原始行
                if "unknown" not in files_matches:
                    files_matches["unknown"] = []
                files_matches["unknown"].append(("?", line))

        # 格式化输出
        for file_path, file_matches in files_matches.items():
            result += "---\n"
            result += f"File: {file_path}\n"
            for line_num, line_content in file_matches:
                result += f"L{line_num}: {line_content}\n"
        result += "---\n"

        return result

    except Exception as e:
        # 如果 pyripgrep 出错，回退到原始实现
        search_path_obj = Path(search_path)
        return _search_with_regex(pattern, search_path_obj, include)


def _search_with_regex(pattern: str, search_path_obj: Path, include: Optional[str] = None) -> str:
    """使用原始正则表达式搜索的回退实现"""
    try:
        # 编译正则表达式
        regex = re.compile(pattern, re.MULTILINE)

        matches = []
        file_count = 0

        # 确定要搜索的文件
        if include:
            # 使用指定的glob模式
            search_pattern = search_path_obj / include
            search_files = glob_module.glob(str(search_pattern), recursive=True)
        else:
            # 搜索大多数文本文件
            search_files = []
            for item in search_path_obj.rglob('*'):
                if item.is_file():
                    # 跳过常见的忽略目录
                    if any(part in {'.git', 'node_modules', '__pycache__', '.vscode', '.idea', 'venv', 'env'}
                           for part in item.parts):
                        continue

                    # 只搜索可能的文本文件
                    if _is_likely_text_file(str(item)):
                        search_files.append(str(item))

        # 在每个文件中搜索模式
        for file_path in search_files:
            file_path_obj = Path(file_path)
            if not file_path_obj.is_file():
                continue

            try:
                with open(file_path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                file_matches = []
                for line_num, line in enumerate(lines, 1):
                    if regex.search(line):
                        file_matches.append((line_num, line.rstrip('\n\r')))

                if file_matches:
                    rel_path = file_path_obj.relative_to(search_path_obj)
                    matches.append((str(rel_path), file_matches))
                    file_count += 1

            except (UnicodeDecodeError, PermissionError):
                # 跳过二进制文件或无权限文件
                continue

        # 格式化输出
        if not matches:
            filter_info = f" (filter: \"{include}\")" if include else ""
            return f"Found 0 matches for pattern \"{pattern}\" in path \"{str(search_path_obj)}\"{filter_info}"

        total_matches = sum(len(file_matches) for _, file_matches in matches)
        filter_info = f" (filter: \"{include}\")" if include else ""
        result = f"Found {total_matches} matches for pattern \"{pattern}\" in path \"{str(search_path_obj)}\"{filter_info}:\n"

        for file_path, file_matches in matches:
            result += "---\n"
            result += f"File: {file_path}\n"
            for line_num, line_content in file_matches:
                result += f"L{line_num}: {line_content}\n"
        result += "---\n"

        return result

    except re.error as e:
        return f"Error: Invalid regular expression '{pattern}': {str(e)}"


def search_file_content_advanced(
    pattern: str,
    path: Optional[str] = None,
    include: Optional[str] = None,
    case_insensitive: bool = False,
    context_lines: int = 0,
    max_results: int = 100
) -> str:
    """
    高级文件内容搜索函数，支持 ripgrep-python 的扩展功能。

    Args:
        pattern (str): 要搜索的正则表达式。
        path (Optional[str]): 要搜索的目录的绝对路径，默认为当前工作目录。
        include (Optional[str]): 过滤要搜索的文件的glob模式。
        case_insensitive (bool): 是否进行大小写不敏感搜索。
        context_lines (int): 匹配行前后显示的上下文行数。
        max_results (int): 限制返回的最大结果数量。

    Returns:
        str: 匹配内容的行、文件路径和行号。
    """
    search_path_obj = Path(path) if path else Path.cwd()
    search_path = str(search_path_obj)

    if not search_path_obj.exists():
        return f"Error: Search path '{search_path}' does not exist."

    try:
        # 如果有 ripgrep-python，使用它进行搜索
        if HAS_PYRIPGREP:
            return _search_with_pyripgrep_advanced(
                pattern, search_path, include, case_insensitive, context_lines, max_results
            )
        else:
            # 回退到原始实现
            return _search_with_regex_advanced(
                pattern, search_path_obj, include, case_insensitive, context_lines, max_results
            )

    except Exception as e:
        return f"Error searching for pattern '{pattern}' in '{search_path}': {str(e)}"


def _search_with_pyripgrep_advanced(
    pattern: str,
    search_path: str,
    include: Optional[str] = None,
    case_insensitive: bool = False,
    context_lines: int = 0,
    max_results: int = 100
) -> str:
    """使用 ripgrep-python 进行高级搜索"""
    try:
        grep = pyripgrep.Grep()

        # 使用 content 模式获取匹配的行和行号
        results = grep.search(
            pattern,
            path=search_path,
            output_mode="content",
            n=True,  # 显示行号
            glob=include,  # 使用 glob 过滤文件
            i=case_insensitive,  # 大小写不敏感搜索
            C=context_lines if context_lines > 0 else None,  # 上下文行数
            head_limit=max_results  # 限制结果数量
        )

        if not results:
            filter_info = f" (filter: \"{include}\")" if include else ""
            case_info = " (case insensitive)" if case_insensitive else ""
            context_info = f" (context: {context_lines})" if context_lines > 0 else ""
            return f"Found 0 matches for pattern \"{pattern}\" in path \"{search_path}\"{filter_info}{case_info}{context_info}"

        # 解析结果并格式化输出
        total_matches = len(results)
        filter_info = f" (filter: \"{include}\")" if include else ""
        case_info = " (case insensitive)" if case_insensitive else ""
        context_info = f" (context: {context_lines})" if context_lines > 0 else ""
        limit_info = f" (limited to {max_results})" if total_matches >= max_results else ""

        result = f"Found {total_matches} matches for pattern \"{pattern}\" in path \"{search_path}\"{filter_info}{case_info}{context_info}{limit_info}:\n"

        # 按文件分组结果
        files_matches = {}
        for line in results:
            # 格式: "path:line_number:content"
            try:
                parts = line.split(':', 2)
                if len(parts) >= 3:
                    file_path, line_num, content = parts[0], parts[1], parts[2]
                    rel_path = Path(file_path).relative_to(Path(search_path)) if Path(file_path).is_absolute() else Path(file_path)

                    if str(rel_path) not in files_matches:
                        files_matches[str(rel_path)] = []
                    files_matches[str(rel_path)].append((line_num, content))
                else:
                    # 如果格式不正确，直接使用原始行
                    if "unknown" not in files_matches:
                        files_matches["unknown"] = []
                    files_matches["unknown"].append(("?", line))
            except Exception:
                # 解析失败，使用原始行
                if "unknown" not in files_matches:
                    files_matches["unknown"] = []
                files_matches["unknown"].append(("?", line))

        # 格式化输出
        for file_path, file_matches in files_matches.items():
            result += "---\n"
            result += f"File: {file_path}\n"
            for line_num, line_content in file_matches:
                result += f"L{line_num}: {line_content}\n"
        result += "---\n"

        return result

    except Exception as e:
        # 如果 pyripgrep 出错，回退到原始实现
        search_path_obj = Path(search_path)
        return _search_with_regex_advanced(
            pattern, search_path_obj, include, case_insensitive, context_lines, max_results
        )


def _search_with_regex_advanced(
    pattern: str,
    search_path_obj: Path,
    include: Optional[str] = None,
    case_insensitive: bool = False,
    context_lines: int = 0,
    max_results: int = 100
) -> str:
    """使用原始正则表达式搜索的高级回退实现"""
    try:
        # 编译正则表达式
        flags = re.MULTILINE
        if case_insensitive:
            flags |= re.IGNORECASE
        regex = re.compile(pattern, flags)

        matches = []
        result_count = 0

        # 确定要搜索的文件
        if include:
            # 使用指定的glob模式
            search_pattern = search_path_obj / include
            search_files = glob_module.glob(str(search_pattern), recursive=True)
        else:
            # 搜索大多数文本文件
            search_files = []
            for item in search_path_obj.rglob('*'):
                if item.is_file():
                    # 跳过常见的忽略目录
                    if any(part in {'.git', 'node_modules', '__pycache__', '.vscode', '.idea', 'venv', 'env'}
                           for part in item.parts):
                        continue

                    # 只搜索可能的文本文件
                    if _is_likely_text_file(str(item)):
                        search_files.append(str(item))

        # 在每个文件中搜索模式
        for file_path in search_files:
            if result_count >= max_results:
                break

            file_path_obj = Path(file_path)
            if not file_path_obj.is_file():
                continue

            try:
                with open(file_path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                file_matches = []
                for line_num, line in enumerate(lines, 1):
                    if result_count >= max_results:
                        break

                    if regex.search(line):
                        line_content = line.rstrip('\n\r')

                        # 添加上下文行
                        if context_lines > 0:
                            context_lines_data = []
                            # 添加前面的行
                            for i in range(max(0, line_num - context_lines - 1), line_num - 1):
                                if i < len(lines):
                                    context_lines_data.append((i + 1, f"  {lines[i].rstrip()}"))

                            # 添加匹配行
                            context_lines_data.append((line_num, f"> {line_content}"))

                            # 添加后面的行
                            for i in range(line_num, min(len(lines), line_num + context_lines)):
                                if i < len(lines):
                                    context_lines_data.append((i + 1, f"  {lines[i].rstrip()}"))

                            file_matches.extend(context_lines_data)
                        else:
                            file_matches.append((line_num, line_content))

                        result_count += 1

                if file_matches:
                    rel_path = file_path_obj.relative_to(search_path_obj)
                    matches.append((str(rel_path), file_matches))

            except (UnicodeDecodeError, PermissionError):
                # 跳过二进制文件或无权限文件
                continue

        # 格式化输出
        if not matches:
            filter_info = f" (filter: \"{include}\")" if include else ""
            case_info = " (case insensitive)" if case_insensitive else ""
            context_info = f" (context: {context_lines})" if context_lines > 0 else ""
            return f"Found 0 matches for pattern \"{pattern}\" in path \"{str(search_path_obj)}\"{filter_info}{case_info}{context_info}"

        total_matches = result_count
        filter_info = f" (filter: \"{include}\")" if include else ""
        case_info = " (case insensitive)" if case_insensitive else ""
        context_info = f" (context: {context_lines})" if context_lines > 0 else ""
        limit_info = f" (limited to {max_results})" if total_matches >= max_results else ""

        result = f"Found {total_matches} matches for pattern \"{pattern}\" in path \"{str(search_path_obj)}\"{filter_info}{case_info}{context_info}{limit_info}:\n"

        for file_path, file_matches in matches:
            result += "---\n"
            result += f"File: {file_path}\n"
            for line_num, line_content in file_matches:
                result += f"L{line_num}: {line_content}\n"
        result += "---\n"

        return result

    except re.error as e:
        return f"Error: Invalid regular expression '{pattern}': {str(e)}"


def _is_likely_text_file(file_path: str) -> bool:
    """判断文件是否可能是文本文件"""
    file_path_obj = Path(file_path)
    ext = file_path_obj.suffix.lower()

    # 常见的文本文件扩展名
    text_extensions = {
        '.txt', '.md', '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.htm', '.css', '.scss', '.sass',
        '.json', '.xml', '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf', '.log', '.sql', '.sh',
        '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd', '.dockerfile', '.gitignore', '.gitattributes',
        '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.java', '.kt', '.rs', '.go', '.php', '.rb', '.pl',
        '.swift', '.m', '.mm', '.cs', '.vb', '.fs', '.clj', '.scala', '.hs', '.elm', '.dart', '.r',
        '.R', '.jl', '.nim', '.zig', '.odin', '.v', '.tex', '.bib', '.rtf', '.csv', '.tsv'
    }

    return ext in text_extensions or not ext  # 无扩展名的文件也可能是文本文件


def replace_in_file(file_path: str, old_string: str, new_string: str, expected_replacements: int = 1) -> str:
    """
    用于替换文件中的文本。要求old_string附带足够上下文以唯一定位修改位置。

    Args:
        file_path (str): 要修改的文件的绝对路径。
        old_string (str): 要替换的原始字符串。如果为空，将创建新文件。
        new_string (str): 用于替换的内容。
        expected_replacements (int): 期望替换的次数，默认1。

    Returns:
        str: 操作结果信息。
    """
    try:
        # 如果old_string为空，创建新文件
        if not old_string:
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                return f"Failed to edit: file '{file_path}' already exists and old_string is empty."

            # 创建父目录（如果不存在）
            parent_dir = file_path_obj.parent
            if not parent_dir.exists():
                parent_dir.mkdir(parents=True, exist_ok=True)

            # 创建新文件
            with open(file_path_obj, 'w', encoding='utf-8') as f:
                f.write(new_string)

            return f"Created new file: {file_path} with provided content."

        # 检查文件是否存在
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return f"Failed to edit: file '{file_path}' does not exist and old_string is not empty."

        # 读取文件内容
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找匹配项
        occurrences = content.count(old_string)

        if occurrences == 0:
            return f"Failed to edit, 0 occurrences found of old_string in {file_path}. Make sure your old_string is exact and includes enough context."

        if occurrences != expected_replacements:
            return f"Failed to edit, expected {expected_replacements} occurrences but found {occurrences} in {file_path}. Make sure your old_string is unique enough."

        # 执行替换
        new_content = content.replace(old_string, new_string, expected_replacements)

        # 写入修改后的内容
        with open(file_path_obj, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return f"Successfully modified file: {file_path} ({expected_replacements} replacements)."

    except PermissionError:
        return f"Error: Permission denied to modify file '{file_path}'."
    except UnicodeDecodeError:
        return f"Error: Cannot decode file '{file_path}' as text."
    except Exception as e:
        return f"Error modifying file '{file_path}': {str(e)}"

class Edit(TypedDict):
    """
    用于描述单个编辑操作的模型。

    Attributes:
        old_string (str): 要替换的原始字符串。
        new_string (str): 用于替换的字符串。
        replace_all (bool, optional): 是否替换所有匹配项，默认为False。
    """
    old_string: str
    new_string: str
    replace_all: bool = False


def multi_edit(file_path: str, edits: List[Edit]) -> str:
    """
    对单个文件执行多个编辑操作，所有编辑操作按顺序执行，要么全部成功要么全部失败。

    Args:
        file_path (str): 要修改的文件的绝对路径。
        edits (List[dict]): 编辑操作列表，每个编辑包含:
            - old_string (str): 要替换的原始字符串
            - new_string (str): 用于替换的新字符串
            - replace_all (bool, optional): 是否替换所有匹配项，默认False

    Returns:
        str: 操作结果信息。
    """
    if not edits:
        return "Error: No edits provided."

    # 验证编辑操作格式
    for i, edit in enumerate(edits):
        if not isinstance(edit, dict):
            return f"Error: Edit {i+1} is not a dictionary."

        if 'old_string' not in edit or 'new_string' not in edit:
            return f"Error: Edit {i+1} missing required fields 'old_string' or 'new_string'."

        if not isinstance(edit['old_string'], str) or not isinstance(edit['new_string'], str):
            return f"Error: Edit {i+1} 'old_string' and 'new_string' must be strings."

    try:
        file_path_obj = Path(file_path)

        # 处理第一个编辑操作（可能是创建新文件）
        first_edit = edits[0]
        old_string = first_edit['old_string']
        new_string = first_edit['new_string']
        replace_all = first_edit.get('replace_all', False)

        # 如果第一个编辑的old_string为空，创建新文件
        if not old_string:
            if file_path_obj.exists():
                return f"Error: File '{file_path}' already exists and first edit has empty old_string."

            # 创建父目录（如果不存在）
            parent_dir = file_path_obj.parent
            if not parent_dir.exists():
                parent_dir.mkdir(parents=True, exist_ok=True)

            # 创建新文件
            content = new_string

            # 处理剩余的编辑操作
            for i, edit in enumerate(edits[1:], 2):
                edit_old = edit['old_string']
                edit_new = edit['new_string']
                edit_replace_all = edit.get('replace_all', False)

                if not edit_old:
                    return f"Error: Edit {i} has empty old_string (only first edit can be empty for file creation)."

                # 检查是否能找到要替换的字符串
                if edit_old not in content:
                    return f"Error: Edit {i} old_string not found in current content."

                # 执行替换
                if edit_replace_all:
                    content = content.replace(edit_old, edit_new)
                else:
                    # 检查唯一性
                    occurrences = content.count(edit_old)
                    if occurrences == 0:
                        return f"Error: Edit {i} old_string not found in current content."
                    elif occurrences > 1:
                        return f"Error: Edit {i} old_string found {occurrences} times, but replace_all is False. Make old_string more specific or set replace_all to True."

                    content = content.replace(edit_old, edit_new, 1)

            # 写入文件
            with open(file_path_obj, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"Successfully created new file: {file_path} with {len(edits)} edits applied."

        else:
            # 编辑现有文件
            if not file_path_obj.exists():
                return f"Error: File '{file_path}' does not exist."

            # 读取文件内容
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                content = f.read()

            # 按顺序应用所有编辑操作
            for i, edit in enumerate(edits, 1):
                edit_old = edit['old_string']
                edit_new = edit['new_string']
                edit_replace_all = edit.get('replace_all', False)

                if not edit_old:
                    return f"Error: Edit {i} has empty old_string (only first edit can be empty for file creation)."

                # 检查是否能找到要替换的字符串
                if edit_old not in content:
                    return f"Error: Edit {i} old_string not found in current content."

                # 执行替换
                if edit_replace_all:
                    content = content.replace(edit_old, edit_new)
                else:
                    # 检查唯一性
                    occurrences = content.count(edit_old)
                    if occurrences == 0:
                        return f"Error: Edit {i} old_string not found in current content."
                    elif occurrences > 1:
                        return f"Error: Edit {i} old_string found {occurrences} times, but replace_all is False. Make old_string more specific or set replace_all to True."

                    content = content.replace(edit_old, edit_new, 1)

            # 写入修改后的内容
            with open(file_path_obj, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"Successfully modified file: {file_path} with {len(edits)} edits applied."

    except PermissionError:
        return f"Error: Permission denied to modify file '{file_path}'."
    except UnicodeDecodeError:
        return f"Error: Cannot decode file '{file_path}' as text."
    except Exception as e:
        return f"Error applying edits to file '{file_path}': {str(e)}"