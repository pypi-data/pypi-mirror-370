FOLD_MEMORY_PROMPT = """
# 动态上下文折叠任务说明

## 任务背景：
你需要将上下文进行结构化折叠，并输出折叠指令。

## 折叠策略：

### 后端代码：
- 只折叠# <xxx> 与 # </xxx> 中的内容，不要折叠# <xxx> 与 # </xxx> 这样的标识
- 按照“功能模块”进行折叠，例如上传文件、调用接口、数据处理等；
- 每个函数或功能块独立折叠。


### 前端代码：
**禁止将整组件作为一个折叠块！** 必须细化为以下结构：
1. `template`：按功能区域折叠（如上传区、步骤导航、语音设置等）；
2. `data()`：统一折叠为“组件数据定义”；
3. 生命周期函数（如 `mounted`）：每个函数单独折叠；
4. `methods`：
    - 每个功能块单独折叠；
    - 折叠 key 命名为 `method_<方法名>`；

## 折叠结构要求：
- 只折叠 // <xxx> 与 // </xxx> 中的内容
- 每个折叠块必须**包含完整语法结构**，不能遗漏方法或对象的闭合大括号；
    - 包括行末的 `},`、`}` 等结尾，避免缩进或语法错误；
- 折叠 key 命名应具有语义，例如：
    - `data` -> `component_data`
    - `template` -> `main_template` 或 `upload_ui_template`
    - `uploadVideo()` -> `method_uploadVideo`


## 输出格式：
```fold
[
    {
        "file_path": "xxx.vue",
        "key": "component_data",
        "summary": "组件数据定义，包括步骤控制、视频信息、语音设置等",
        "line_numbers": "52-87"
    },
    {
        "file_path": "xxx.vue",
        "key": "method_generateAudio",
        "summary": "方法 generateAudio：根据口播稿生成配音音频",
        "line_numbers": "300-355"
    }
]
注意事项：
- 不允许整组件折叠为一个 key，必须细化结构。
- 每个折叠块必须包含完整闭合结构，例如包含函数结尾的 },；
- summary 要具体清晰，概括函数/数据的作用，避免空泛；
- 分块可以大一些
- 注意输出时必须带上fold
- 不要折叠 // <xxx>、# <xxx>、// </xxx>、# </xxx>这样的标识
"""

DYNAMIC_UNFOLD_MEMORY_PROMPT = """
# 动态上下文解折叠任务说明

## 任务背景：
你会获取一个可以解折叠的上下文，在上下文中会有`【已折叠-key:summary】`的标识代表可以展开，`【开始-key】内容【结束-key】`的标识代表可以折叠结束

## 任务要求：
需要根据标识解折叠用户需求需要用到的所有上下文。
假如解折叠出的内容发现无关的上下文，需要重新折叠回去

## 能力
你可以展开多个key，直到获取到满足用户需求的上下文，最后将不需要的折叠回去

## 输出格式
```unfold
[
    {
        "file_path": "xxx.py",
        "keys": ["video_upload", "video_download"],
    },
]
```

```fold_back
[
    {
        "file_path": "xxx.py",
        "keys": ["video_upload", "video_download"],
    },
]
```
注意：
1. 解折叠的东西符合要求的，不需要再折叠回去
2. 输出格式需要符合要求
3. 你只负责解折叠，不负责实现与方案设计，实现是开发的事情，找到可以加入相关功能的地方即可
4. 前后端与需求相关的都需要解折叠
5. 只回复展开的指令，不要回复其他内容，发现上下文符合要求则输出展开完毕
"""

MODIFY_FOLD_MEMORY_KEY_PROMPT = """
# 更新上下文折叠 key 与 summary 的任务说明

## 任务背景：
你会收到 `.index.json` 文件，包含如下结构：
{
    "key": {
        "summary": "summary",
        "content": "content"
    }
}
其中key和summary是对应content的

## 任务要求：
请对 `.index.json` 中的 key 和 summary 与实际 content 进行比对。
**仅当 key 与实际content严重不符，或 summary 明显不能准确概括 content 含义时，才进行修改。**
content完全变了，需要同时修改key与summary

## 判断标准：
- **key 错误示例：** key 与 content 所表示功能完全不符（如 key 是 "download_video"，但实际是上传功能）
- **summary 错误示例：** summary 与 content 毫无关联，或造成误导性理解
- **以下情况不做修改：**
  - key/summmary 只是部分词汇更精确或更完整，但原表达已足够合理
  - 微小语义增强，例如 “更新Logo视频” 改为 “更新Logo视频信息”

## 输出格式：
```modify
[
    {
        "file_path": "xxx.py.index.json",
        "update_type": "key",
        "key": "旧的key",
        "new_value": "新的key"
    },
    {
        "file_path": "xxx.py.index.json",
        "update_type": "summary",
        "key": "key",
        "new_value": "新的summary"
    }
]
```
"""

def fold_memory(context: str):
    """
    折叠记忆, 生成文件对于的index.json(存储记忆内容)和index.txt(存储折叠后的内容)
    @param context: 记忆内容
    """
    import re
    import os
    import json
    from codyer_agent import Agent

    def is_output_match(content):
        # 检测文本里是否含有: ```fold(内容)```
        import re
        # 修改正则表达式以匹配换行符和多行内容
        pattern = r'```fold\n(.*?)\n```'
        return bool(re.search(pattern, content, re.DOTALL))

    def fold(fold_operations: str):
        """
        折叠
        @param operation: 折叠操作
        """
        fold_match = re.search(r'```fold\n(.*?)\n```', fold_operations, re.DOTALL)
        operations = json.loads(fold_match.group(1)) if fold_match else []
        
        # 处理压缩操作
        for item in operations:
            source_file = item['file_path']
            compress_key = item['key']
            content_summary = item['summary']
            line_range = item['line_numbers']
            
            json_file = source_file + '.index.json'
            txt_file = source_file + '.index.txt'
            
            # 检查源文件是否存在
            if not os.path.exists(source_file):
                continue
            
            # 优先从txt文件读取full_content，如果txt文件不存在则从源文件读取
            if os.path.exists(txt_file):
                with open(txt_file, 'r', encoding='utf-8') as f:
                    full_content = f.read()
                # 从源文件读取原始行数据用于行号计算
                with open(source_file, 'r', encoding='utf-8') as f:
                    file_lines = f.readlines()
            else:
                # 一次性读取源文件
                with open(source_file, 'r', encoding='utf-8') as f:
                    file_lines = f.readlines()
                full_content = ''.join(file_lines)
            
            # 解析并验证行号范围
            start_line, end_line = map(int, line_range.split('-'))
            start_line = max(1, start_line)
            end_line = min(len(file_lines), end_line)
            
            if start_line > end_line:
                continue
                
            target_content = ''.join(file_lines[start_line-1:end_line])
            
            # 处理JSON文件
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
            else:
                json_data = {}
            
            json_data[compress_key] = {
                'summary': content_summary,
                'content': target_content
            }
            
            # 一次性写入所有文件
            compressed_content = full_content.replace(target_content, f'【已折叠-{compress_key}:{content_summary}】\n')
            
            # 批量写入文件
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(compressed_content)
        return False, None, "折叠成功", False

    interpretors = [(is_output_match, fold, 'final')]
    agent = Agent(role=FOLD_MEMORY_PROMPT, interpretors=interpretors)
    fold_operation = agent.run(context)

    return fold_operation

# 解折叠记忆
def unfold_memory(user_input: str):
    """
    解折叠记忆, 从index.json和index.txt中读取记忆内容
    @param user_input: 用户输入(需要解折叠的文件路径)
    """
    import re
    import os
    import json
    from codyer_agent import Agent
    
    def is_output_match(content):
        # 检测文本里是否含有: ```unfold(内容)```, ```fold_back(内容)```
        import re
        # 修改正则表达式以匹配换行符和多行内容
        pattern = r'```(unfold|fold_back)\n(.*?)\n```'
        return bool(re.search(pattern, content, re.DOTALL))
    
    def unfold(operation: str):
        """
        解折叠
        """
        unfold_match = re.search(r'```unfold\n(.*?)\n```', operation, re.DOTALL)
        fold_back_match = re.search(r'```fold_back\n(.*?)\n```', operation, re.DOTALL)
        
        # 错误处理：确保JSON格式正确，修复可能的格式问题
        unfold_json_str = unfold_match.group(1) if unfold_match else "[]"
        fold_back_json_str = fold_back_match.group(1) if fold_back_match else "[]"
        
        # 尝试修复JSON格式问题，比如缺少双引号或多余的逗号
        unfold_json_str = unfold_json_str.replace("'", '"')
        fold_back_json_str = fold_back_json_str.replace("'", '"')
        
        try:
            unfold_operation = json.loads(unfold_json_str)
        except json.JSONDecodeError as e:
            print(f"JSON解析错误(unfold): {e}, 尝试修复")
            # 如果出错，尝试简单修复常见问题后重试
            unfold_json_str = re.sub(r',\s*}', '}', unfold_json_str)  # 移除尾部逗号
            unfold_json_str = re.sub(r',\s*]', ']', unfold_json_str)  # 移除尾部逗号
            try:
                unfold_operation = json.loads(unfold_json_str)
            except:
                unfold_operation = []
                
        try:
            fold_back_operation = json.loads(fold_back_json_str)
        except json.JSONDecodeError as e:
            print(f"JSON解析错误(fold_back): {e}, 尝试修复")
            # 尝试简单修复常见问题
            fold_back_json_str = re.sub(r',\s*}', '}', fold_back_json_str)
            fold_back_json_str = re.sub(r',\s*]', ']', fold_back_json_str)
            try:
                fold_back_operation = json.loads(fold_back_json_str)
            except:
                fold_back_operation = []

        # 解折叠
        result = ""
        for item in unfold_operation:
            file_path = item['file_path']
            keys = item['keys']
            index_txt_path = file_path + '.index.txt'
            index_json_path = file_path + '.index.json'
            
            if not os.path.exists(index_txt_path) or not os.path.exists(index_json_path):
                continue

            with open(index_txt_path, 'r', encoding='utf-8') as f:
                index_txt_content = f.read()
            with open(index_json_path, 'r', encoding='utf-8') as f:
                index_json_content = json.load(f)
            
            for key in keys:
                if key in index_json_content:
                    index_txt_content = index_txt_content.replace(f'【已折叠-{key}:{index_json_content[key]["summary"]}】', f'【开始-{key}】\n{index_json_content[key]["content"]}\n【结束-{key}】\n')
            with open(index_txt_path, 'w', encoding='utf-8') as f:
                f.write(index_txt_content)
            result += f"## {file_path}\n 解压后内容：" + index_txt_content + "\n"
        
        # 折叠
        for item in fold_back_operation:
            file_path = item['file_path']
            keys = item['keys']
            index_txt_path = file_path + '.index.txt'
            index_json_path = file_path + '.index.json'
            
            if not os.path.exists(index_txt_path) or not os.path.exists(index_json_path):
                continue

            with open(index_txt_path, 'r', encoding='utf-8') as f:
                index_txt_content = f.read()
            with open(index_json_path, 'r', encoding='utf-8') as f:
                index_json_content = json.load(f)

            for key in keys:
                if key in index_json_content:
                    index_txt_content = index_txt_content.replace(f'【开始-{key}】\n{index_json_content[key]["content"]}\n【结束-{key}】\n', f'【已折叠-{key}:{index_json_content[key]["summary"]}】')
            with open(index_txt_path, 'w', encoding='utf-8') as f:
                f.write(index_txt_content)
            result += f"## {file_path}\n 折叠后内容：" + index_txt_content + "\n"

        return False, None, result, True

    
    interpretors = [(is_output_match, unfold, 'realtime')]
    agent = Agent(role=DYNAMIC_UNFOLD_MEMORY_PROMPT, interpretors=interpretors)
    agent.run(user_input)
    
def modify_memory(file_path: str):
    """
    修改记忆
    @param file_path: 需要更新记忆的文件路径
    """
    import re
    import os
    import json
    from codyer_agent import Agent

    def is_output_match(content):
        # 检测文本里是否含有: ```modify(内容)```
        import re
        # 修改正则表达式以匹配换行符和多行内容
        pattern = r'```modify\n(.*?)\n```'
        return bool(re.search(pattern, content, re.DOTALL))
    
    def modify(operation: str):
        """
        修改
        """
        modify_match = re.search(r'```modify\n(.*?)\n```', operation, re.DOTALL)
        modify_operation = json.loads(modify_match.group(1)) if modify_match else []

        # 按文件分组操作
        file_operations = {}
        for item in modify_operation:
            file_path = item['file_path']
            if file_path not in file_operations:
                file_operations[file_path] = {'summary': [], 'key': []}
            file_operations[file_path][item['update_type']].append(item)

        for memory_json_path, operations in file_operations.items():
            if not os.path.exists(memory_json_path):
                continue

            with open(memory_json_path, 'r', encoding='utf-8') as f:
                memory_json_content = json.load(f)
            
            memory_txt_path = memory_json_path.replace('json', 'txt')
            with open(memory_txt_path, 'r', encoding='utf-8') as f:
                memory_txt_content = f.read()

            # 先处理summary更新
            for item in operations['summary']:
                key = item['key']
                new_value = item['new_value']
                if key in memory_json_content:
                    if key in memory_json_content and 'summary' in memory_json_content[key]:
                        old_summary = memory_json_content[key]['summary']
                        memory_json_content[key]['summary'] = new_value
                        memory_txt_content = memory_txt_content.replace(
                            f'【已折叠-{key}:{old_summary}】', 
                            f'【已折叠-{key}:{new_value}】'
                        )

            # 再处理key更新
            for item in operations['key']:
                old_key = item['key']
                new_key = item['new_value']
                if old_key in memory_json_content:
                    # 更新JSON中的key
                    memory_json_content[new_key] = memory_json_content.pop(old_key)
                    # 更新txt中的key引用
                    current_summary = memory_json_content[new_key]['summary']
                    memory_txt_content = memory_txt_content.replace(
                        f'【已折叠-{old_key}:{current_summary}】', 
                        f'【已折叠-{new_key}:{current_summary}】'
                    )

            with open(memory_json_path, 'w', encoding='utf-8') as f:
                json.dump(memory_json_content, f, ensure_ascii=False, indent=2)

            with open(memory_txt_path, 'w', encoding='utf-8') as f:
                f.write(memory_txt_content)

        return False, None, "修改成功", False
    
    index_json_path = file_path + '.index.json'
    if not os.path.exists(index_json_path):
        return "文件不存在"
    
    with open(index_json_path, 'r', encoding='utf-8') as f:
        index_json_content = json.load(f)

    interpretors = [(is_output_match, modify, 'final')]
    agent = Agent(role=MODIFY_FOLD_MEMORY_KEY_PROMPT, interpretors=interpretors)
    llm_input = f"# {index_json_path} \n {str(index_json_content)}"
    agent.run(llm_input)

# 完全展开
def unfold_memory_all(index_txt_path: str):
    """
    完全展开
    @param index_txt_path: 需要恢复的文件路径
    """
    import re
    import os
    import json
    
    if ".index.txt" not in index_txt_path:
        return "路径错误，请输入正确的文件路径"
    index_json_path = index_txt_path.replace('.index.txt', '.index.json')
    if not os.path.exists(index_txt_path):
        return ".index.txt文件不存在"
    if not os.path.exists(index_json_path):
        return ".index.json文件不存在"

    with open(index_txt_path, 'r', encoding='utf-8') as f:
        index_txt_content = f.read()
    with open(index_json_path, 'r', encoding='utf-8') as f:
        index_json_content = json.load(f)
    
    # 匹配全部的【已折叠-key:summary】
    pattern = r'【已折叠-(.*?):(.*?)】'
    matches = re.findall(pattern, index_txt_content)
    matched_keys = set()
    for match in matches:
        key = match[0]
        summary = match[1]
        matched_keys.add(key)
        if key in index_json_content:
            index_txt_content = index_txt_content.replace(f'【已折叠-{key}:{summary}】', index_json_content[key]["content"])
        else:
            index_txt_content = index_txt_content.replace(f'【已折叠-{key}:{summary}】', '')
    
    # 匹配全部的【开始-key】内容【结束-key】，使用DOTALL模式支持换行
    pattern = r'【开始-(.*?)】(.*?)【结束-\1】'
    matches = re.findall(pattern, index_txt_content, re.DOTALL)
    for match in matches:
        key = match[0]
        content = match[1]
        matched_keys.add(key)
        if key in index_json_content:
            index_txt_content = index_txt_content.replace(f'【开始-{key}】{content}【结束-{key}】', content)
            # 内容不对应则agent更新
            if index_json_content[key]["content"] != content:
                index_json_content[key]["content"] = content
                modify_memory(index_json_path)
        else:
            index_txt_content = index_txt_content.replace(f'【开始-{key}】{content}【结束-{key}】', '')

    # 删除json中存在但文本中没有匹配到的key
    keys_to_remove = []
    for key in index_json_content.keys():
        if key not in matched_keys:
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del index_json_content[key]

    with open(index_json_path, 'w', encoding='utf-8') as f:
        json.dump(index_json_content, f, ensure_ascii=False, indent=2)
    
    with open(index_txt_path.replace('.index.txt', ''), 'w', encoding='utf-8') as f:
        f.write(index_txt_content)

# def _run_fold_memory(self, input_file_path):
#     from codyer_agent.memory_fold import fold_memory

#     # 压缩全文
#     fold_input = ""
#     for path in input_file_path:
#         fold_input += f"## {path}:\n"
#         if os.path.exists(path):
#             with open(path, 'r', encoding='utf-8') as f:
#                 lines = f.readlines()
                
#                 for i, line in enumerate(lines):
#                     if "# <" in line or "// <" in line:
#                         fold_input += f'{i}(不要折叠该行内容): {line}'
#                     else:
#                         fold_input += f'{i}: {line}'
#     fold_memory(fold_input)
    
# def _dynamic_run(self, input, input_file_path):
#     import os
#     from codyer_agent.memory_fold import unfold_memory, unfold_memory_all
#     import shutil
#     # 部分展开
#     final_fold_input = ""
#     unfold_input = f"# 用户需求\n{input}\n"
#     for file_path in input_file_path:
#         unfold_input += f"## {file_path}:\n"
#         file_contents = ""
#         if os.path.exists(file_path + '.index.txt'):
#             with open(file_path + '.index.txt', 'r', encoding='utf-8') as f:
#                 file_contents = f.read()
#         unfold_input += f"\n{file_contents}\n"
#     unfold_memory(unfold_input)
#     # 将原始文件拷贝为.copy, 将.index.txt变为file_path
#     for file_path in input_file_path:
#         if os.path.exists(file_path):
#             shutil.copy(file_path, file_path + '.copy')
#         if os.path.exists(file_path + '.index.txt'):
#             os.rename(file_path + '.index.txt', file_path)
#     if isinstance(input, str):
#         final_fold_input = f"# 用户需求\n{input}\n"
#         for file_path in input_file_path:
#             final_fold_input += f"## {file_path}:\n"
#             if os.path.exists(file_path + '.index.txt'):
#                 with open(file_path + '.index.txt', 'r', encoding='utf-8') as f:
#                     file_contents = f.read()
#                 final_fold_input += f"\n{file_contents}\n"
#             else:
#                 with open(file_path, 'r', encoding='utf-8') as f:
#                     file_contents = f.read()
#                 final_fold_input += f"\n{file_contents}\n"
#     if isinstance(input, list):
#         final_fold_input_text = f"# 用户需求\n{input}\n"
#         for file_path in input_file_path:
#             final_fold_input_text += f"## {file_path}:\n"
#             if os.path.exists(file_path + '.index.txt'):
#                 with open(file_path + '.index.txt', 'r', encoding='utf-8') as f:
#                     file_contents = f.read()
#                 final_fold_input_text += f"\n{file_contents}\n"
#             else:
#                 with open(file_path, 'r', encoding='utf-8') as f:
#                     file_contents = f.read()
#                 final_fold_input_text += f"\n{file_contents}\n"
#         # 加上input中的{'image': 'image_url | image_path']}
#         final_fold_input = [final_fold_input_text]

#         for item in input:
#             if isinstance(item, dict) and 'image' in item:
#                 final_fold_input += [item]
#     result = self._run(final_fold_input)
#     # 将原始文件 还原为.index.txt
#     for file_path in input_file_path:
#         if os.path.exists(file_path):
#             os.rename(file_path, file_path + '.index.txt')

#     # 将.index.txt 生成原始文件
#     for file_path in input_file_path:
#         if os.path.exists(file_path + '.index.txt'):
#             unfold_memory_all(file_path + '.index.txt')
#     return result

# def process_input(input_file_path):
#     from codyer_agent.memory_fold import unfold_memory_all
#     result = None  # 初始化result变量，防止未赋值错误

#     input_file_length = 0
#     for file_path in input_file_path:
#         if os.path.exists(file_path):
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 input_file_length += len(f.readlines())
#     # 计算inputs_file读取出来的长度, 如果长度大于600且没有.index.txt则进行折叠
#     if not os.path.exists(input_file_path[0] + '.index.txt'):
#         if input_file_length > 1000:
#             # 压缩全文
#             self._run_fold_memory(input_file_path)
#             result = self._dynamic_run(input, input_file_path)
#             return result
#         else:
#             # result = self._run(input)
#             ?
#     else:
#         index_txt_length = 0
#         for file_path in input_file_path:
#             if os.path.exists(file_path + '.index.txt'):
#                 with open(file_path + '.index.txt', 'r', encoding='utf-8') as f:
#                     index_txt_length += len(f.readlines())
#         if index_txt_length > 1000:
#             # 压缩全文
#             self._run_fold_memory(input_file_path)
#             result = self._dynamic_run(input, input_file_path)
#             return result
#         else:
#             result = self._dynamic_run(input, input_file_path)





if __name__ == "__main__":
    unfold_memory_all("/Users/llm/Desktop/bodongyueqian/Agent/codyer_builder/test_973_app_973_1748511954_prL48/web/main.js.index.txt")