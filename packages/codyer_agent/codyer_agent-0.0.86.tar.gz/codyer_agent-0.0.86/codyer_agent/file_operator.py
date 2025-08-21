from typing import List, Iterator, Optional
import os
import re

FILE_OPERATOR_PROMPT = """
# 文件操作

## 整体协议

%%FILE_OPERATION%%
[操作类型] [文件路径]
[参数键=值]（每行一个）
%%CONTENT%%
[操作内容]
%%END%%

## 限制

- 文件路径只能访问当前目录及其子目录，不能访问其他目录
- 文件路径不能包含 .. 或 /.. 或 \\..\\ 等上级目录
- 文件路径不能以 / 或 \ 开头
- 文件路径不能包含 /etc, /usr, /var, /sys, /proc, /root, /home 等敏感系统路径
- 文件协议不要以```语言开头，直接以%%FILE_OPERATION%%开头
  - 例如：
  错误写法：
  ```python
  %%FILE_OPERATION%%
  read test.py
  %%END%%
  ```
  规范写法：
  %%FILE_OPERATION%%
  read test.py
  %%END%%

## 重要规则

### 写入完整内容
- 使用 write 操作时，必须写入完整的、可执行的内容
- 禁止使用 `// ... [保留原有部分不变] ...` 或类似的占位符注释
- 禁止使用 `/* ... */` 或 `// ...` 来表示省略的内容部分
- 如果只修改部分内容，请使用 update 操作配合 diff 格式
- 写入的内容必须是语法正确的完整内容块

### 内容修改建议
- 对于部分修改：优先使用 update 操作
- 对于完全重写：使用 write 操作，但必须写入完整内容
- 如果内容很长，建议分多次 update 操作进行修改

## 协议说明

### 读取文件

%%FILE_OPERATION%%
read 文件路径
start_line=[开始行号]
end_line=[结束行号]
%%END%%
- 当不指定开始行号和结束行号时，默认读取全部内容
- 读取案例：
%%FILE_OPERATION%%
read test.txt
%%END%%


### 写入文件

%%FILE_OPERATION%%
write 文件路径
%%CONTENT%%
[内容]
%%END%%

### 追加文件

%%FILE_OPERATION%%
append 文件路径
%%CONTENT%%
[内容]
%%END%%

### 更新文件
%%FILE_OPERATION%%
update 文件路径
%%CONTENT%%
<<<<<<< SEARCH
[要查找的内容]
=======
[要替换成的新内容]
>>>>>>> REPLACE
%%END%%
注意：查找替换时应该忽略行号
- 修改案例：
收到的内容：
1: 你好世界
2: 你好codyer
修改要求：修改codyer为codyer_coderun

这时候，去除行号实际内容是：
你好世界
你好codyer

那么需要输出：
%%FILE_OPERATION%%
update 文件路径
%%CONTENT%%
<<<<<<< SEARCH
你好codyer
=======
你好codyer_coderun
>>>>>>> REPLACE
%%END%%

### 删除文件内容

%%FILE_OPERATION%%
delete_range 文件路径
start_line=[开始行号]
end_line=[结束行号]
%%END%%

#### 删除文件

%%FILE_OPERATION%%
delete_file 文件路径
%%END%%


# 文件展示格式

%%FILE_CONTENT%%
FILE_PATH
lines=[总行数]
start_line=[内容开始行号]
end_line=[内容结束行号]
%%CONTENT%%
1: xxx
2: 日志
...
31: 以上就是日志内容
%%END%%

## 示例

### 展示文件内容

%%FILE_CONTENT%%
service.log
%%CONTENT%%
1: Hello, World!
2: Hello, Codyer!
%%END%%

"""


def _is_safe_path(file_path: str) -> bool:
    """
    验证文件路径是否安全
    只允许访问当前目录及其子目录，防止路径遍历攻击
    """
    # 不允许绝对路径
    if os.path.isabs(file_path):
        return False
    
    # 规范化路径，解析 . 和 .. 
    normalized_path = os.path.normpath(file_path)
    
    # 不允许包含 .. 的路径（防止访问上级目录）
    if normalized_path.startswith('..') or '/..' in normalized_path or '\\..\\' in normalized_path:
        return False
    
    # 不允许以 / 或 \ 开头（绝对路径）
    if normalized_path.startswith(('/', '\\')):
        return False
    
    # 检查是否尝试访问敏感系统路径
    dangerous_paths = ['/etc', '/usr', '/var', '/sys', '/proc', '/root', '/home']
    for dangerous in dangerous_paths:
        if normalized_path.startswith(dangerous):
            return False
    
    return True


def parse_llm_file_read(input: str) -> Optional[str]:
    """
    专门解析大模型输出的文件读取操作
    只处理read操作，实时返回结果
    """
    try:
        # 查找所有的 FILE_OPERATION 块
        operations = _find_all_file_operations(input)
        
        if not operations:
            return None  # 没有找到操作，不做处理
        
        results = []
        for i, operation_text in enumerate(operations):
            try:
                operation_data = _parse_file_operation_format(operation_text)
                # 只处理读取操作
                if operation_data["operation"] == "read":
                    result = _execute_file_operation(operation_data)
                    results.append(f"读取操作 {i+1}: {result}")
            except Exception as e:
                try:
                    operation_data = _parse_file_operation_format(operation_text)
                    if operation_data["operation"] == "read":
                        results.append(f"读取操作 {i+1} 失败: {str(e)}")
                except:
                    # 如果解析失败，检查是否包含read关键字
                    if "read " in operation_text:
                        results.append(f"读取操作 {i+1} 失败: {str(e)}")
        
        return "\n".join(results) if results else None
        
    except Exception as e:
        return f"读取操作错误：{str(e)}"


def parse_llm_file_operate_no_read(input: str) -> Optional[str]:
    """
    解析大模型输出的文件操作（不包括读取操作）
    处理write、append、update、delete等操作
    """
    import re
    
    try:
        # 查找所有的 FILE_OPERATION 块
        operations = _find_all_file_operations(input)
        
        if not operations:
            return None  # 没有找到操作，不做处理
        
        results = []
        for i, operation_text in enumerate(operations):
            try:
                operation_data = _parse_file_operation_format(operation_text)
                # 排除读取操作，处理其他操作
                if operation_data["operation"] != "read":
                    result = _execute_file_operation(operation_data)
                    results.append(f"操作 {i+1}: {result}")
            except Exception as e:
                try:
                    operation_data = _parse_file_operation_format(operation_text)
                    if operation_data["operation"] != "read":
                        results.append(f"操作 {i+1} 失败: {str(e)}")
                except:
                    # 如果解析失败，检查是否不是read操作
                    if "read " not in operation_text and "%%FILE_OPERATION%%" in operation_text:
                        results.append(f"操作 {i+1} 失败: {str(e)}")
        
        return "\n".join(results) if results else None
        
    except Exception as e:
        return f"文件操作错误：{str(e)}"


def parse_llm_file_operate(input: str) -> Optional[str]:
    """
    解析大模型输出的文件操作
    支持多个文件操作，依次处理并返回结果
    """
    import re
    
    try:
        # 查找所有的 FILE_OPERATION 块
        operations = _find_all_file_operations(input)
        
        if not operations:
            return "错误：未找到有效的文件操作格式"
        
        results = []
        for i, operation_text in enumerate(operations):
            try:
                operation_data = _parse_file_operation_format(operation_text)
                result = _execute_file_operation(operation_data)
                results.append(f"操作 {i+1}: {result}")
            except Exception as e:
                results.append(f"操作 {i+1} 失败: {str(e)}")
        
        return "\n".join(results)
        
    except Exception as e:
        return f"错误：{str(e)}"


def _find_all_file_operations(input: str) -> list:
    """
    查找输入文本中的所有 FILE_OPERATION 块
    """
    operations = []
    lines = input.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line == "%%FILE_OPERATION%%":
            # 找到操作开始
            start_idx = i
            end_idx = -1
            
            # 查找对应的 %%END%%
            for j in range(i + 1, len(lines)):
                if lines[j].strip() == "%%END%%":
                    end_idx = j
                    break
            
            if end_idx != -1:
                # 提取完整的操作块
                operation_block = '\n'.join(lines[start_idx:end_idx + 1])
                operations.append(operation_block)
                i = end_idx + 1
            else:
                # 没找到结束标记，跳过这个开始标记
                i += 1
        else:
            i += 1
    
    return operations


def _parse_file_operation_format(input: str) -> dict:
    """
    解析 %%FILE_OPERATION%% 格式
    """
    lines = input.strip().split('\n')
    
    # 找到操作开始和结束位置
    start_idx = -1
    end_idx = -1
    content_idx = -1
    
    for i, line in enumerate(lines):
        if line.strip() == "%%FILE_OPERATION%%":
            start_idx = i
        elif line.strip() == "%%CONTENT%%":
            content_idx = i
        elif line.strip() == "%%END%%":
            end_idx = i
            break
    
    if start_idx == -1 or end_idx == -1:
        raise ValueError("格式错误：缺少 %%FILE_OPERATION%% 或 %%END%% 标记")
    
    # 解析操作类型和文件路径
    if start_idx + 1 >= len(lines):
        raise ValueError("格式错误：缺少操作类型和文件路径")
    
    operation_line = lines[start_idx + 1].strip()
    parts = operation_line.split(' ', 1)
    
    if len(parts) < 2:
        raise ValueError("格式错误：操作类型和文件路径格式不正确")
    
    operation_type = parts[0]
    file_path = parts[1]
    
    result = {
        "type": "file_operation",
        "operation": operation_type,
        "file_path": file_path,
        "parameters": {},
        "content": None
    }
    
    # 解析参数
    param_end_idx = content_idx if content_idx != -1 else end_idx
    for i in range(start_idx + 2, param_end_idx):
        line = lines[i].strip()
        if line and '=' in line:
            key, value = line.split('=', 1)
            # 尝试转换为数字，如果失败则保持字符串
            try:
                value = int(value)
            except ValueError:
                pass
            result["parameters"][key] = value
    
    # 解析内容
    if content_idx != -1:
        content_lines = lines[content_idx + 1:end_idx]
        result["content"] = '\n'.join(content_lines)
    
    return result


def _execute_file_operation(operation_data: dict) -> str:
    """
    执行文件操作并返回结果
    """
    operation = operation_data["operation"]
    file_path = operation_data["file_path"]
    parameters = operation_data["parameters"]
    content = operation_data["content"]

    # 验证file_path是否合法
    # file_path只能在当前目录下，或者在当前目录的子目录下，即 ./ 目录下，其他都是非法的
    if not _is_safe_path(file_path):
        return f"错误：文件路径 '{file_path}' 不安全，只能访问当前目录及其子目录"
    try:
        if operation == "read":
            return _execute_read_operation(file_path, parameters)
        elif operation == "write":
            return _execute_write_operation(file_path, content)
        elif operation == "append":
            return _execute_append_operation(file_path, content)
        elif operation == "update":
            return _execute_update_operation(file_path, content)
        elif operation == "delete_range":
            return _execute_delete_range_operation(file_path, parameters)
        elif operation == "delete_file":
            return _execute_delete_file_operation(file_path)
        else:
            return f"错误：不支持的操作类型 '{operation}'"
    except Exception as e:
        return f"操作失败：{str(e)}"


def _execute_read_operation(file_path: str, parameters: dict) -> str:
    """执行读取操作"""
    if not os.path.exists(file_path):
        return f"错误：文件 '{file_path}' 不存在"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        start_line = parameters.get("start_line", 1)
        end_line = parameters.get("end_line", len(lines))
        
        # 确保行号范围有效
        start_line = max(1, start_line)
        end_line = min(len(lines), end_line)
        
        if start_line > end_line:
            return f"错误：开始行号 {start_line} 大于结束行号 {end_line}"
        
        # 构建带行号的文件内容
        result_lines = []
        for i in range(start_line - 1, end_line):
            line_content = lines[i].rstrip('\n')
            result_lines.append(f"{i + 1:4d}: {line_content}")
        
        total_lines = len(lines)
        return f"文件 '{file_path}' 内容 (第{start_line}-{end_line}行，共{total_lines}行):\n" + "\n".join(result_lines)
        
    except Exception as e:
        return f"错误：读取文件失败 - {str(e)}"


def _execute_write_operation(file_path: str, content: str) -> str:
    """执行写入操作"""
    try:
        # 确保目录存在
        dir_path = os.path.dirname(file_path)
        if dir_path:  # 只有当目录路径不为空时才创建
            os.makedirs(dir_path, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"成功：已写入文件 '{file_path}'"
    except Exception as e:
        return f"错误：写入文件失败 - {str(e)}"


def _execute_append_operation(file_path: str, content: str) -> str:
    """执行追加操作"""
    try:
        # 确保目录存在
        dir_path = os.path.dirname(file_path)
        if dir_path:  # 只有当目录路径不为空时才创建
            os.makedirs(dir_path, exist_ok=True)
        
        # 检查文件是否存在以及是否需要添加换行符
        add_newline = False
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
                # 如果文件不为空且不以换行符结尾，需要添加换行符
                if existing_content and not existing_content.endswith('\n'):
                    add_newline = True
        
        with open(file_path, 'a', encoding='utf-8') as f:
            if add_newline:
                f.write('\n')
            f.write(content)
        
        return f"成功：已追加内容到文件 '{file_path}'"
    except Exception as e:
        return f"错误：追加文件失败 - {str(e)}"

def is_incomplete_marker(line):
    # 定义完整的标记列表
    valid_markers = ["<<<<<<< SEARCH", "=======", ">>>>>>> REPLACE"]
    # 检查是否以特殊字符开始但不是完整标记
    return (line.startswith(("<", "=", ">")) and 
            line.strip() not in valid_markers)

def line_trimmed_fallback_match(original_content: str, search_content: str):
    """
    尝试使用去除行两端空白的方式进行内容匹配。
    @param original_content: 原始文本内容
    @param search_content: 要搜索的内容
    @return: 如果找到匹配，返回(匹配开始位置, 匹配结束位置)的元组, 如果没找到匹配，返回None
    """
    try:
        # 分割和预处理
        original_lines = original_content.split('\n')
        search_lines = [line for line in search_content.split('\n') if line.strip()]
        
        # 遍历查找匹配
        for i in range(len(original_lines) - len(search_lines) + 1):
            # 快速检查第一行（优化性能）
            if original_lines[i].strip() != search_lines[0].strip():
                continue
                
            # 检查所有行
            if all(
                original_lines[i + j].strip() == search_lines[j].strip()
                for j in range(len(search_lines))
            ):
                # 计算位置
                start_pos = sum(len(line) + 1 for line in original_lines[:i])
                end_pos = sum(len(line) + 1 for line in original_lines[:i + len(search_lines)])
                return start_pos, end_pos
                
        return None
        
    except Exception as e:
        return None

def block_anchor_fallback_match(original_content: str, search_content: str):
    """
    使用块的首尾行作为锚点来定位整个块（全局搜索版本）。
    @param original_content: 原始文本内容
    @param search_content: 要搜索的内容
    @return: 如果找到匹配，返回(匹配开始位置, 匹配结束位置)的元组, 如果没找到匹配，返回None
    """
    # 1. 分割成行
    original_lines = original_content.split('\n')
    search_lines = search_content.split('\n')
    
    # 2. 处理空行
    if search_lines and search_lines[-1] == "":
        search_lines.pop()
        
    # 3. 只处理3行或以上的块
    if len(search_lines) < 3:
        return None
        
    # 4. 获取首尾锚点
    first_line_search = search_lines[0].strip()
    last_line_search = search_lines[-1].strip()
    search_block_size = len(search_lines)
    
    # 5. 直接遍历查找匹配的首尾锚点
    for i in range(len(original_lines) - search_block_size + 1):
        # 检查首行是否匹配
        if original_lines[i].strip() != first_line_search:
            continue
            
        # 检查尾行是否在预期位置匹配
        if original_lines[i + search_block_size - 1].strip() != last_line_search:
            continue
            
        # 计算字符位置
        match_start_index = sum(len(line) + 1 for line in original_lines[:i])
        match_end_index = sum(len(line) + 1 for line in original_lines[:i + search_block_size])
        
        return match_start_index, match_end_index
        
    return None


def strip_leading_line_numbers(text: str) -> str:
    """
    仅移除每行行首的「数字 + 冒号 + 一个空格」模式，不影响其他内容。
    - 示例："9:  bar" -> " bar"（仅去掉 "9: "，保留第二个空格）
    - 示例："   23: world" -> "   world"（保留行首缩进，仅去掉 "23: ")
    - 不匹配："3:foo"（冒号后没有空格，不移除）
    - 不匹配："12 :space"（冒号前有空格，不移除）
    """
    if not text:
        return text
    lines = text.split('\n')
    # 仅去除「数字 + 冒号 + 一个空格」，保留行首缩进与后续多余空格
    pattern = re.compile(r'^(?P<indent>\s*)(?P<num>\d+): (?P<rest>.*)$')
    def _sub(m):
        return f"{m.group('indent')}{m.group('rest')}"
    stripped_lines = [pattern.sub(_sub, line) for line in lines]
    return "\n".join(stripped_lines)


def _execute_update_operation(file_path: str, diff_content: str) -> str:
    """执行更新操作(使用diff格式)"""
    if not os.path.exists(file_path):
        return f"错误：文件 '{file_path}' 不存在"
    
    content = diff_content.strip()
    content_lines = content.split('\n')
    
    try:
        # 预处理
        if content_lines:
            if is_incomplete_marker(content_lines[-1]):
                content_lines.pop()
                content_lines.append('>>>>>>> REPLACE')
            
            if content_lines and is_incomplete_marker(content_lines[0]):
                content_lines.pop(0)
                content_lines.insert(0, '<<<<<<< SEARCH')

        # 获取搜索和替换内容
        in_search = False
        in_replace = False
        current_search_content = ""
        current_replace_content = ""
        modify_pairs = []
        for line in content_lines:
            if "<<<<<<< SEARCH" in line:
                in_search = True
                current_search_content = ""
                current_replace_content = ""
                continue
            
            if "=======" in line:
                in_search = False
                in_replace = True
                continue
            
            if ">>>>>>> REPLACE" in line:
                in_search = False
                in_replace = False
                modify_pairs.append((current_search_content, current_replace_content))
                continue
            
            # 累积内容
            if in_search:
                current_search_content += line + "\n"
            elif in_replace:
                current_replace_content += line + "\n"

        # 读取代码
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        normalized_pairs = []
        for search_content, replace_content in modify_pairs:
            normalized_search = strip_leading_line_numbers(search_content)
            normalized_replace = strip_leading_line_numbers(replace_content)
            normalized_pairs.append((normalized_search, normalized_replace))

        for search_content, replace_content in normalized_pairs:
            if search_content == '':
                continue
            # 精确匹配通过replace替换
            replaced_code = code.replace(search_content, replace_content)
            if replaced_code != code:
                code = replaced_code
                continue
            else:
                # 行修剪匹配
                line_trimmed_res = line_trimmed_fallback_match(code, search_content)
                if line_trimmed_res:
                    start_index, end_index = line_trimmed_res
                    replaced_code = code[:start_index] + replace_content + code[end_index:]
                    code = replaced_code
                    continue
                else:
                    # 块锚点匹配
                    block_anchor_res = block_anchor_fallback_match(code, search_content)
                    if block_anchor_res:
                        start_index, end_index = block_anchor_res
                        replaced_code = code[:start_index] + replace_content + code[end_index:]
                        code = replaced_code
                        continue
                    else:
                        return f'update failed, no match search item, please check the search item'

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        return f'update success'
    
    except Exception as e:
        return f'Error during update: {str(e)}'
    
def _execute_delete_range_operation(file_path: str, parameters: dict) -> str:
    """执行删除范围操作"""
    if not os.path.exists(file_path):
        return f"错误：文件 '{file_path}' 不存在"
    
    start_line = parameters.get("start_line")
    end_line = parameters.get("end_line")
    
    if start_line is None or end_line is None:
        return "错误：缺少 start_line 或 end_line 参数"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 验证行号范围
        if start_line < 1 or end_line > len(lines) or start_line > end_line:
            return f"错误：无效的行号范围 {start_line}-{end_line}，文件共 {len(lines)} 行"
        
        # 删除指定范围的行
        new_lines = lines[:start_line-1] + lines[end_line:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        return f"成功：已删除文件 '{file_path}' 第{start_line}-{end_line}行"
    except Exception as e:
        return f"错误：删除文件内容失败 - {str(e)}"


def _execute_delete_file_operation(file_path: str) -> str:
    """执行删除全部内容操作"""
    if not os.path.exists(file_path):
        return f"错误：文件 '{file_path}' 不存在"
    
    try:
        os.remove(file_path)
        
        return f"成功：已删除文件 '{file_path}'"
    except Exception as e:
        return f"错误：删除文件失败 - {str(e)}"