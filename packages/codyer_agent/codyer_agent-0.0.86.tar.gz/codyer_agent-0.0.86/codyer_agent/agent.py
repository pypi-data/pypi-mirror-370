from typing import Union
from jinja2 import Template
import logging
import re, io, os, sys, json, logging
import inspect
import base64
import traceback
from codyer import skills
import uuid
from codyer_agent.file_operator import FILE_OPERATOR_PROMPT, parse_llm_file_operate
from codyer_agent.message_compress import COMPRESS_PROMPT

def general_llm_token_count(messages):
    # 统一token计算方式
    def count_str(string):
        # 字母/数字/符号/换行等 0.3 token, 其他 0.6 token
        normal_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ \n"
        count = 0
        for c in string:
            if c in normal_chars:
                count += 0.3
            else:
                count += 0.6
        return count
    num_tokens = 0
    for message in messages:
        if isinstance(message["content"], str):
            num_tokens += count_str(message["content"])
        else:
            for item in message["content"]:
                if isinstance(item, str):
                    num_tokens += count_str(item)
                else:
                    if "text" in item:
                        num_tokens += count_str(item["text"])
                    elif "image" in item:
                        num_tokens += 1615
                    else:
                        raise Exception("message type wrong")
    return num_tokens

def temp_sonnet_llm_token_count(messages):
    def count_str(string):
        normal_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ \n"
        
        def count_normal_text(text):
            count = 0
            for c in text:
                if c in normal_chars:
                    count += 0.25
                else:
                    count += 1.2
            return count
        
        # 检测是否包含代码块
        if "```" in string:
            code_multiplier = 1.4  # 代码块权重系数
            total_count = 0
            remaining_text = string
            
            # 查找并处理所有代码块
            while "```" in remaining_text:
                start_pos = remaining_text.find("```")
                # 处理代码块前的普通文本
                normal_text = remaining_text[:start_pos]
                if normal_text:
                    total_count += count_normal_text(normal_text)
                
                # 裁剪并查找代码块结束位置
                remaining_text = remaining_text[start_pos + 3:]
                end_pos = remaining_text.find("```")
                
                if end_pos == -1:  # 没有找到结束标记
                    # 剩余文本作为普通文本处理
                    total_count += count_normal_text(remaining_text)
                    break
                
                # 提取代码内容并计算(应用乘数)
                code_content = remaining_text[:end_pos]
                total_count += count_normal_text(code_content) * code_multiplier
                
                # 继续处理剩余文本
                remaining_text = remaining_text[end_pos + 3:]
            
            # 处理最后剩余的普通文本
            if remaining_text and "```" not in remaining_text:
                total_count += count_normal_text(remaining_text)
                
            return total_count
        else:
            # 不含代码块的普通文本
            return count_normal_text(string)
        
    num_tokens = 0
    for message in messages:
        if isinstance(message["content"], str):
            num_tokens += count_str(message["content"])
        else:
            for item in message["content"]:
                if isinstance(item, str):
                    num_tokens += count_str(item)
                else:
                    if "text" in item:
                        num_tokens += count_str(item["text"])
                    elif "image" in item:
                        num_tokens += 1615
                    else:
                        raise Exception("message type wrong")
    return num_tokens

def show_messages(messages):
    import logging
    logging.debug('-'*50 + '<LLM Messages>' + '-'*50)
    for message in messages:
        logging.debug(f'[[[ {message["role"]} ]]]')
        logging.debug(f'{message["content"]}')
    logging.debug('-'*50 + '</LLM Messages>' + '-'*50)

def openai_format_llm_inference(messages, stream=False, api_key=None, base_url=None, model=None, input_price=None, output_price=None, max_retries=2, timeout=20, max_tokens=8096):
    """
    OpenAI格式的LLM推理
    @messages: list, [{"role": "system", "content": "You are a helpful assistant"}, {"role": "user", "content": str | ['text', {'image': 'image_url'}]}]
    @stream: bool, 是否流式输出
    @api_key: str,  LLM api_key
    @base_url: str,  LLM base_url
    @model: str,  LLM model
    @input_price: float, 输入 token/1k 价格
    @output_price: float, 输出 token/1k 价格
    """
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url, max_retries=max_retries, timeout=timeout)

    show_messages(messages)

    def _messages_to_openai(messages):
        # 消息格式转换成openai格式
        def encode_image(image_path):
            if image_path is None:
                return None
            if image_path.startswith('http'):
                return image_path
            bin_data = base64.b64encode(open(image_path, "rb").read()).decode('utf-8')
            image_type = image_path.split('.')[-1].lower()
            return f"data:image/{image_type};base64,{bin_data}"
        new_messages = []
        for message in messages:
            content = message["content"]
            if isinstance(content, str):
                new_messages.append({"role": message["role"], "content": content})
            elif isinstance(content, list):
                new_content = []
                for c in content:
                    if isinstance(c, str):
                        new_content.append({"type": "text", "text": c})
                    elif isinstance(c, dict):
                        if "image" in c:
                            image_url = encode_image(c["image"])
                            if image_url is not None:
                                new_content.append({"type": "image_url", "image_url": {"url": image_url}})
                        elif "text" in c:
                            new_content.append({"type": "text", "text": c["text"]})
                new_messages.append({"role": message["role"], "content": new_content})
        return new_messages

    openai_messages = _messages_to_openai(messages)

    def _with_stream():
        input_tokens = None
        output_tokens = None
        result = ''
        try:
            if 'doubao-seed' in model.lower():
                extra_body = {"thinking": {"type": "disabled"}}
                response = client.chat.completions.create(max_tokens=max_tokens, messages=openai_messages, model=model, stream=True, stream_options={"include_usage": True}, extra_body=extra_body)
            else:
                response = client.chat.completions.create(max_tokens=max_tokens, messages=openai_messages, model=model, stream=True, stream_options={"include_usage": True})
            for chunk in response:
                if len(chunk.choices) > 0:
                    if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content is not None and len(chunk.choices[0].delta.reasoning_content) > 0:
                        token = chunk.choices[0].delta.reasoning_content
                    else:
                        token = chunk.choices[0].delta.content
                    if token is None:
                        continue
                    yield token
                    if token is not None:
                        result += token
                if chunk.usage is not None:
                    input_tokens = chunk.usage.prompt_tokens
                    output_tokens = chunk.usage.completion_tokens
        except Exception as e:
            logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
            # raise ValueError('LLM stream error')
            raise e
        finally:
            if input_price is not None and output_price is not None and len(result.strip()) > 0:
                if input_tokens is None:
                    input_tokens = general_llm_token_count(messages)
                    output_tokens = general_llm_token_count([{"role": "assistant", "content": result}])
                cost = input_price * input_tokens / 1000.0 + output_price * output_tokens / 1000.0
                logging.info(f"input_tokens: {input_tokens}, output_tokens: {output_tokens}, cost: {cost}")
                skills.system.server.consume('llm_inference', cost)
    
    def _without_stream():
        try:
            if 'doubao-seed' in model.lower():
                extra_body = {"thinking": {"type": "disabled"}}
                response = client.chat.completions.create(max_tokens=max_tokens, messages=openai_messages, model=model, stream=False, extra_body=extra_body)
            else:
                response = client.chat.completions.create(max_tokens=max_tokens, messages=openai_messages, model=model, stream=False)
            if hasattr(response.choices[0].message, 'reasoning_content') and response.choices[0].message.reasoning_content is not None and len(response.choices[0].message.reasoning_content) > 0:
                result = response.choices[0].message.reasoning_content  + '\n' + response.choices[0].message.content
            else:
                result = response.choices[0].message.content
            if input_price is not None and output_price is not None:
                input_tokens, output_tokens = response.usage.prompt_tokens, response.usage.completion_tokens
                cost = input_price * input_tokens / 1000.0 + output_price * output_tokens / 1000.0
                logging.info(f"input_tokens: {input_tokens}, output_tokens: {output_tokens}, cost: {cost}")
                skills.system.server.consume('llm_inference', cost)
            return result
        except Exception as e:
            logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
            # raise ValueError('LLM error')
            raise e
    
    if stream:
        return _with_stream()
    else:
        return _without_stream()


def anthropic_format_llm_inference(messages, stream=False, client=None, api_key=None, base_url=None, model=None, input_price=None, output_price=None, max_tokens=8096):
    """
    Anthropic格式的LLM推理
    @messages: list, [{"role": "system", "content": "You are a helpful assistant"}, {"role": "user", "content": str | ['text', {'image': 'image_url'}]}]
    @stream: bool, 是否流式输出
    @api_key: str,  LLM api_key
    @base_url: str,  LLM base_url
    @model: str,  LLM model
    @input_price: float, 输入 token/1k 价格
    @output_price: float, 输出 token/1k 价格
    """
    from anthropic import Anthropic
    client = client or Anthropic(api_key=api_key, base_url=base_url, max_retries=3)

    show_messages(messages)

    def _messages_to_anthropic(messages):
        # 消息格式转换成anthropic格式
        def encode_image(image_path):
            bin_data = base64.b64encode(open(image_path, "rb").read()).decode('utf-8')
            image_type = image_path.split('.')[-1].lower()
            return { "type": "base64", "media_type": f"image/{image_type}", "data": bin_data}
        new_messages = []
        for message in messages:
            role = message["role"]
            role = 'assistant' if role == "system" else role
            content = message["content"]
            if isinstance(content, str):
                new_messages.append({"role": role, "content": content})
            elif isinstance(content, list):
                new_content = []
                for c in content:
                    if isinstance(c, str):
                        new_content.append({"type": "text", "text": c})
                    elif isinstance(c, dict):
                        if "image" in c:
                            new_content.append({"type": "image", "source": encode_image(c["image"])})
                        elif "text" in c:
                            new_content.append({"type": "text", "text": c["text"]})
                new_messages.append({"role": role, "content": new_content})
        return new_messages

    messages = _messages_to_anthropic(messages)

    def _with_stream():
        i_count = None
        o_count = None
        try:
            result = ''
            stream = client.messages.create(max_tokens=max_tokens, messages=messages, model=model, stream=True)
            for event in stream:
                if event.type == 'content_block_delta':
                    token = event.delta.text
                    if token is None:
                        continue
                    yield token
                    if token is not None:
                        result += token
                if event.type == 'message_start':
                    i_count = event.message.usage.input_tokens
                if event.type == 'message_delta':
                    o_count = event.usage.output_tokens
        except Exception as e:
            logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
            # raise ValueError('LLM stream error')
            raise e
        finally:
            if input_price is not None and output_price is not None:
                if len(result.strip()) > 0:
                    if i_count is None:
                        # i_count = client.messages.count_tokens(model=model, messages=messages).input_tokens
                        i_count = temp_sonnet_llm_token_count(messages)
                    if o_count is None:
                        # o_count = client.messages.count_tokens(model=model, messages=[{"role": "assistant", "content": result}]).output_tokens
                        o_count = temp_sonnet_llm_token_count([{"role": "assistant", "content": result}])
                    cost = input_price * i_count / 1000.0 + output_price * o_count / 1000.0
                    logging.info(f"input_tokens: {i_count}, output_tokens: {o_count}, cost: {cost}")
                    skills.system.server.consume('llm_inference', cost)
    def _without_stream():
        try:
            response = client.messages.create(max_tokens=max_tokens, messages=messages, model=model, stream=False)
            if input_price is not None and output_price is not None:
                i_count, o_count= response.usage.input_tokens, response.usage.output_tokens
                cost = input_price * i_count / 1000.0 + output_price * o_count / 1000.0
                logging.info(f"input_tokens: {i_count}, output_tokens: {o_count}, cost: {cost}")
                skills.system.server.consume('llm_inference', cost)
            result = response.content[0].text
            return result
        except Exception as e:
            logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
            # raise ValueError('LLM error')
            raise e
    
    if stream:
        return _with_stream()
    else:
        return _without_stream()

def default_stream_output(token):
    if token is not None:
        print(token, end="", flush=True)
    else:
        print("\n", end="", flush=True)


def get_function_signature(func, module: str = None):
    """Returns a description string of function"""
    func_type = type(func).__name__
    try:
        if func_type == "function":
            sig = inspect.signature(func)
            sig_str = str(sig)
            desc = f"{func.__name__}{sig_str}"
            if func.__doc__:
                desc += ": " + func.__doc__.strip()
            if module is not None:
                desc = f"{module}.{desc}"
            if inspect.iscoroutinefunction(func):
                desc = "" + desc
        else:
            method_name = ".".join(func.chain)
            signature = skills.system.server.get_function_signature(method_name) + '\nimport by: `from codyer import skills`\n'
            return signature
        return desc
    except Exception as e:
        logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
        return ""


class TmpManager:
    def __init__(self, agent):
        self.agent = agent
        self.tmp_index = None # 临时消息的起始位置

    def __enter__(self):
        self.tmp_index = len(self.agent.messages)
        return self.agent

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.agent.messages = self.agent.messages[:self.tmp_index] 
        self.tmp_index = None
        return False

defalut_python_prompt_template = """
# 运行python代码

- 有必要才运行python代码
- 有结果直接输出结论，不再运行python
- 不要重复执行相同的代码

## 运行格式

```python
# run code
xxx
```

## Available imported functions
```
{{python_funcs}}
```

"""


# 任务状态检查的默认提示模板（可被外部传入覆盖）
DEFAULT_TASK_STATUS_CHECK_PROMPT = """根据以下完整的对话历史，分析当前任务的执行状态：

{{messages_text}}

请分析：
1. 当前任务是否在正常进行（其中自我改正也算是正常进行）
2. 是否出现了循环、循环纠错失败、卡死？
3. 任务是否已经无法完成或需要人工干预？
4. 任务是否已经完成？

请直接回答："<<继续>>"、"<<中断>>"、"<<完成>>"，并一句话简要说明原因。
比如: <<继续>> 任务正常进行中
比如: <<中断>> 任务出现循环、卡死或偏离目标的情况
比如: <<完成>> 任务已经完成
"""

def default_get_file_memory(messages: list, file_paths: list, left_token_count: int):
    """
    获取文件记忆
    @param messages: 消息列表
    @param file_paths: 文件路径列表
    @param left_token_count: 剩余token数量
    @return: 文件记忆
    """
    file_memory = ''
    for file_path in file_paths:
        if not os.path.exists(file_path):
            file_memory += f"%%FILE_CONTENT%%\n"
            file_memory += f"{file_path}\n"
            file_memory += f"Error reading file: {file_path} not found\n"
            file_memory += f"%%END%%\n\n"
            continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
                total_lines = len(lines)
                
                file_memory += f"%%FILE_CONTENT%%\n"
                file_memory += f"{file_path}\n"
                file_memory += f"lines={total_lines}\n"
                file_memory += f"start_line=1\n"
                file_memory += f"end_line={total_lines}\n"
                file_memory += f"%%CONTENT%%\n"
                
                for i, line in enumerate(lines, 1):
                    file_memory += f"{i}: {line}\n"
                
                file_memory += f"%%END%%\n\n"
        except Exception as e:
            file_memory += f"%%FILE_CONTENT%%\n"
            file_memory += f"{file_path}\n"
            file_memory += f"Error reading file: {str(e)}\n"
            file_memory += f"%%END%%\n\n"
    
    return file_memory

def default_get_agent_memory(original_messages: list, workspace= '', task=''):
    return original_messages
    
        
class Agent:
    python_prompt_template = defalut_python_prompt_template

    def __init__(self, 
            role: str = "You are a helpfull assistant.",
            functions: list = [],
            workspace: str = None,
            stream_output=default_stream_output,
            model=None,
            llm_inference=skills.codyer.llm.llm_inference,
            llm_token_count=general_llm_token_count,
            llm_token_limit=100000,
            continue_run=False,
            messages=None,
            enable_python=True,
            max_steps=5, # 最大re act次数
            interpretors = [], # 解析器 [is_match, parse, 'realtime' or 'final']
            with_file_operator=False,
            get_file_memory=default_get_file_memory, # skills.codyer.llm.get_file_memory
            get_agent_memory=default_get_agent_memory, # skills.codyer.llm.get_agent_memory，已经没有用了
            read_files = [], # 参考文件列表，只能读取.md、txt、py、js等文本文件, 不能读取图片、视频、pdf
            show_step_detail=False, # 是否显示每一步的执行信息细节
            show_messages=False,
            task_status_check_prompt_template: str = DEFAULT_TASK_STATUS_CHECK_PROMPT, # 任务状态检查提示模板
        ):
        """
        @role: str, agent role description
        @functions: list, can be used by the agent to run python code
        @workspace: str, agent保存记忆的工作空间，默认值为None（不序列化）。如果指定了目录，Agent会自动保存状态并在下次初始化时重新加载。
        @stream_output: function, agent输出回调函数
        @llm_inference: function, LLM推理函数
        @llm_token_limit: int, LLM token limit, default 100K
        @continue_run: bool, 是否自动继续执行。Agent在任务没有完成时，是否自动执行。默认为True. 该参数已经废弃，请使用 max_steps 参数代替
        @messages: list, agent记忆 [{"role": "system", "content": "You are a helpful assistant"}, {"role": "user", "content": str | ['text', {'image': 'image_url | image_path']}]
        @enable_python: bool, 是否启用agent执行python代码和调用functions
        @max_steps: int, 最大re act次数
        @interpretors: list, 解析器 [(is_match, parse, realtime|final), ...]. is_match(llm_output) -> bool, parse(llm_output) -> (python_mode, python_result, result, continue_run)
            parse: return (python_mode, python_result, result, continue_run)
        @with_file_operator: bool, 是否启用文件操作
        @show_messages: 是否显示消息
        """
        if workspace is not None and not os.path.exists(workspace):
            os.makedirs(workspace)
        self.role = role
        self.workspace = workspace
        if self.workspace is None:
            self.python_pickle_path = uuid.uuid4().hex + '.pickle'
        else:
            self.python_pickle_path = os.path.join(workspace, 'python.pickle')
        self.functions = functions

        # llm_inference 必须是数组 或者 函数
        self.model = model
        if self.model is None:
            if not callable(llm_inference) and not isinstance(llm_inference, list):
                raise ValueError("llm_inference must be a function or a list of functions")
            if callable(llm_inference):
                self.llm_inferences = [llm_inference]
            else:
                self.llm_inferences = llm_inference
        else:
            self.llm_inferences = [skills.codyer.llm.llm_inference]
        self.llm_token_count = llm_token_count
        self.llm_token_limit = llm_token_limit
        self.continue_run = continue_run
        self.stream_output = stream_output
        self.messages = messages or self.load_messages()
        self._enable_python = enable_python
        self._max_steps = max_steps
        self.get_file_memory = get_file_memory
        self.get_agent_memory = get_agent_memory
        for item in interpretors:
            if len(item) == 2:
                is_match, to_parse = item
                mode = 'final'
            else:
                is_match, to_parse, mode = item
            if not callable(is_match) or not callable(to_parse) or mode not in ['realtime', 'final']:
                raise ValueError("interpretors must be a list of (is_match, parse, 'realtime' or 'final')")
        self._interpretors = interpretors
        self.llm_run_count = 0
        self._with_file_operator = with_file_operator
        self._task_status_check_prompt_template = task_status_check_prompt_template
        if self._with_file_operator:
            # 先执行读文件操作（实时），再执行其他文件操作
            self._interpretors = [
                (self.is_file_read_operator, self.parse_file_read_operator, 'realtime'),  # 实时读文件
                (self.is_file_write_operator, self.parse_file_write_operator, 'final'),   # 其他文件操作
            ] + self._interpretors
        self._read_files = read_files
        self._tmp_read_files = []
        self._show_step_detail = show_step_detail
        self._show_messages = show_messages

    def is_file_read_operator(self, llm_output):
        """检查是否包含读文件操作"""
        if '%%FILE_OPERATION%%' not in llm_output:
            return False
            
        try:
            from .file_operator import _find_all_file_operations, _parse_file_operation_format
            operations = _find_all_file_operations(llm_output)
            
            for operation_text in operations:
                try:
                    operation_data = _parse_file_operation_format(operation_text)
                    if operation_data["operation"] == "read":
                        return True
                except:
                    continue
            return False
        except:
            return False
            
    def parse_file_read_operator(self, llm_output):
        """解析读文件操作（实时）"""
        from .file_operator import parse_llm_file_read
        result = parse_llm_file_read(llm_output)
        return False, None, result, True
    
    def is_file_write_operator(self, llm_output):
        """检查是否包含写文件操作（除读取外的其他操作）"""
        if '%%FILE_OPERATION%%' in llm_output:
            # 检查是否包含非读取的操作
            operations = ['write ', 'append ', 'update ', 'delete_range ', 'delete_file ']
            for op in operations:
                if op in llm_output:
                    return True
        return False
        
    def parse_file_write_operator(self, llm_output):
        """解析写文件等操作（非读取操作）"""
        from .file_operator import parse_llm_file_operate_no_read
        result = parse_llm_file_operate_no_read(llm_output)
        return False, None, result, True


    def is_math_file_operator(self, llm_output):
        if '%%FILE_OPERATION%%' in llm_output:
            return True
        else:
            return False
        
    def parse_file_operator(self, llm_output):
        # _python_mode, _python_data, _result, _continue_run
        result = parse_llm_file_operate(llm_output)
        return False, None, result, True

    def add_message(self, role, content):
        import datetime
        # 加载最新消息
        load_messages = self.load_messages()
        # self.messages = []
        if load_messages is not None and len(load_messages) > 0:
            self.messages = load_messages
        if isinstance(content, list):
            content = [x.strip() if isinstance(x, str) else x for x in content]
        else:
            content = content.strip() if isinstance(content, str) else content
        # 只有role=user才加时间戳
        if role == 'user':
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(content, str):
                content = f"[{current_time}] {content}"
            else:
                for i, x in enumerate(content):
                    if isinstance(x, str):
                        content[i] = f"[{current_time}] {x}"

        # 压缩消息
        token_count = int(self.llm_token_count(self.messages))
        # if self._show_step_detail:
        #     self.stream_output(f"\n上下文长度: {token_count}")
        if token_count > self.llm_token_limit * 2 / 3:
            if self._show_step_detail:
                self.stream_output(f"\n```memory\n上下文长度: {token_count}，进行操作 \n")
            # 压缩前面的 80% 内容，避免暴力压缩了全部内容
            compress_count = int(token_count * 0.82)
            compress_messages = []
            for index, message in enumerate(self.messages):
                compress_messages.append(message)
                if self.llm_token_count(compress_messages) > compress_count:
                    break
            left_messages = self.messages[index:]
            # if self._show_step_detail:
            #     self.stream_output(f'压缩消息条数: {len(compress_messages)}')
            #     self.stream_output(f'剩余消息条数: {len(left_messages)}')
            summary = self._compress_messages(compress_messages)
            if len(left_messages) > 0:
                the_role = 'assistant' if left_messages[0]['role'] == 'user' else 'user' # 压缩消息后，和下一条消息的角色保持区分，避免消息合并
            else:
                the_role = 'assistant' if role == 'user' else 'user' # 压缩消息后，和下一条消息的角色保持区分，避免消息合并
            self.messages = [{"role": the_role, "content": summary}] + left_messages
            if self._show_step_detail:
                token_count = int(self.llm_token_count(self.messages))
                self.stream_output(f'\n处理后长度为 {token_count}\n```\n')
            #     self.stream_output(f'压缩后内容: \n---------\n{summary}\n---------\n')
        
        # 添加消息: 只有assistant角色才合并消息
        if self.messages is not None and len(self.messages) > 0 and self.messages[-1]["role"] == role and role == 'assistant':
            if isinstance(self.messages[-1]["content"], str) and isinstance(content, str):
                self.messages[-1]["content"] += '\n\n' + content
            else:
                self.messages.append({"role": role, "content": content})
        else:
            self.messages.append({"role": role, "content": content})

        self.save_messages()


    def load_messages(self):
        if self.message_path is not None and os.path.exists(self.message_path):
            with open(self.message_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
                # 移除messages中的多模态
                for message in messages:
                    if isinstance(message['content'], list):
                        message['content'] = json.dumps(message['content']) # 直接转成一个字符串
                return messages
        else:
            return []
        
    def get_history(self):
        """
        获取历史消息
        @return: list, [{"role": "assistant|user", "content": "content"}, ...]
        """
        messages = []
        for message in self.messages:
            if message["role"] in ['system', 'assistant']:
                role = 'assistant'
            else:
                role = 'user'
            content = message["content"]
            if isinstance(content, list):
                new_content = ''
                for c in content:
                    if isinstance(c, str):
                        new_content += c + '\n'
                    elif isinstance(c, dict):
                        if 'image' in c:
                            new_content += f'![{c["image"]}]({c["image"]})\n'
                        else:
                            new_content += c['text'] + '\n'
                content = new_content
            messages.append({"role": role, "content": content})
        return messages

    def save_messages(self):
        if self.workspace is None:
            return
        with open(self.message_path, 'w+', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False)

    @property
    def message_path(self):
        return os.path.join(self.workspace, "memory.json") if self.workspace is not None else None

    def clear(self):
        """
        清楚agent状态
        """
        if self.message_path is not None and os.path.exists(self.message_path):
            os.remove(self.message_path)
        self.clear_python()
        self.messages = []

    def tmp(self):
        """
        agent临时状态，在with语句中执行的操作不会进入记忆
        用法:
        with agent.tmp() as agent:
            agent.user_input("hello")
        """
        return TmpManager(self)

    def disable_stream_output(self):
        """禁用输出回调函数"""
        self.tmp_stream_output = self.stream_output
        self.stream_output = default_stream_output

    def enable_stream_output(self):
        """启用输出回调函数"""
        self.stream_output = self.tmp_stream_output
        self.tmp_stream_output = default_stream_output

    def disable_python(self):
        self._enable_python = False

    def enable_python(self):
        self._enable_python = True

    def clear_python(self):
        if self.workspace is None:
            # 检测 self.python_pickle_path 文件是否存在，如果存在则删除
            if os.path.exists(self.python_pickle_path):
                os.remove(self.python_pickle_path)

    def run(self, command: Union[str, list], files=[], return_type=None, display=False):
        """
        执行命令并返回指定类型的结果
        @command: 命令内容, 格式为: str | ['text', {'image': 'image_url | image_path']}, ...]
        @return_type: type, 返回python类型数据，比如str, int, list, dict等
        @display: bool, 是否显示LLM生成的中间内容，当display为True时，通过stream_output输出中间内容
        """
        self._tmp_read_files = files
        if not display:
            self.disable_stream_output()
        try:
            result = self._run(command, is_run_mode=True, return_type=return_type)
            return result
        except Exception as e:
            logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
            # return str(e)
            raise e
        finally:
            self.clear_python()
            if not display:
                self.enable_stream_output()
    
    def user_input(self, input: Union[str, list], files=[]):
        """
        agent响应用户输入，并始终通过stream_output显示LLM生成的中间内容
        input: 用户输入内容 str | ['text', {'image': 'image_url | image_path']}, ...]
        """
        self._tmp_read_files = files
        try:
            result = self._run(input)
            return result
        except Exception as e:
            logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
            # return str(e)
            raise e
        finally:
            self.clear_python()

    def _check_task_status(self):
        """
        检查当前任务状态，判断是否应该继续执行
        @return: bool, True表示应该继续，False表示应该中断
        """
        # 直接将所有消息转换为字符串
        messages_text = str(self.messages)
        
        # 通过模板渲染生成检查提示词（可被外部传入覆盖）
        check_prompt = Template(self._task_status_check_prompt_template).render(
            messages_text=messages_text
        )

        # 使用LLM推理
        for llm_inference in self.llm_inferences:
            try:
                response = llm_inference([{"role": "user", "content": check_prompt}], stream=False)
                if response and isinstance(response, str):
                    response_lower = response.lower()
                    if "<<中断>>" in response_lower or '<<完成>>' in response_lower:
                        self.stream_output(f"\n**任务状态检查**: {response}\n")
                        return False
                    elif "<<继续>>" in response_lower:
                        self.stream_output(f"\n**任务状态检查**: 正常继续执行\n")
                        return True
                    else:
                        # 如果回答不明确，默认继续
                        return True
            except Exception as e:
                logging.error(f"任务状态检查失败: {e}")
                continue
        
        # 如果所有LLM都失败了，默认继续
        return True
    
    def _run(self, input, is_run_mode=False, return_type=None):

        # 整理系统提示词
        if not self._enable_python:
            self.system_prompt = self.role
        else:
            funtion_signatures = "\n\n".join([get_function_signature(x) for x in self.functions])
            variables = {"python_funcs": funtion_signatures}
            python_prompt = Template(self.python_prompt_template).render(**variables)
            self.system_prompt = self.role + '\n\n' + python_prompt
        if self._with_file_operator:
            self.system_prompt += '\n\n对任何文件进行操作必须使用以下指令：' + FILE_OPERATOR_PROMPT
        self.system_prompt += '\n\nAfter completing the user\'s request, please output <<terminate>> to end the current task.'
    
        # 如果是run模式 & 需要返回值类型
        if is_run_mode and return_type is not None:
            add_content = "\nYou should return python values in type " + str(return_type) + " by run python code(```python\n# run code\nxxx\n).\n"
            if isinstance(input, list):
                input = (input + [add_content])
            elif isinstance(input, str):
                input = input + add_content
            else:
                raise Exception("input type error")
        # 记录message
        self.add_message("user", input)

        # 记录llm请求次数
        self.llm_run_count = 0

        llm_result = ""  # 初始化变量
        for step in range(self._max_steps):

            # 每5次循环检查一次任务状态
            if step > 0 and step % 5 == 0:
                if self._show_step_detail:
                    self.stream_output("\n**执行状态检查中...**\n")
                if not self._check_task_status():
                    self.stream_output("**任务结束: 任务完成 或 进行循环 或 目标偏离**\n")
                    return llm_result + "\n任务结束: 任务完成 或 进行循环 或 目标偏离"
                
            messages = self._get_llm_messages()
            if self._show_messages:
                messages_str = json.dumps(messages, indent=4, ensure_ascii=False).replace('`', ' ')
                self.stream_output(f'\n```messages\n{messages_str}\n```\n')
            
            llm_result, (python_mode, python_data, result, should_continue) = self._llm_and_parse_output(messages)
            self.llm_run_count += 1
            if is_run_mode and python_mode:
                return python_data
            
            if "<<terminate>>" in llm_result and not should_continue:
                return llm_result
            
            else:
                if not should_continue:
                    return llm_result
            
            # 统一的消息处理逻辑
            limit_char_count = 30 * 1000
            if python_data is not None:
                if len(str(python_data)) > limit_char_count:
                    python_data = str(python_data)[:limit_char_count] + f'\n... 结果过长，只显示前{limit_char_count}字符'
                user_message = f'\n```output\n{python_data}\n```'
                message = f'**python运行结果**\n```output\n{python_data}\n```'
            else:
                if len(str(result)) > limit_char_count:
                    result = str(result)[:limit_char_count] + f'\n... 结果过长，只显示前{limit_char_count}字符'
                user_message = f'\n```output\n{result}\n```'
                message = f'**执行结果/日志**\n```output\n{result}\n```'
            
            self.add_message("user", message)
            if self._show_step_detail:
                # self.stream_output(None)
                self.stream_output(user_message)
                self.stream_output(None)
                # self.stream_output("**继续执行**\n")
        
        # 循环结束时返回最后的结果
        return llm_result + "已达到最大执行步数"
    
    def _compress_messages(self, messages):
        """压缩消息"""
        for index, llm_inference in enumerate(self.llm_inferences):
            try:
                # response = llm_inference([{"role": "system", "content": '你是一个消息压缩专家，对下面的内容进行压缩'}] + messages + [{'role': 'user', 'content': COMPRESS_PROMPT}], stream=False)
                # return response
                response = llm_inference([{"role": "system", "content": '你是一个消息压缩专家，对下面的内容进行压缩'}] + messages + [{'role': 'user', 'content': COMPRESS_PROMPT}], stream=True)
                result = ''
                for x in response:
                    # print(x)
                    result += x
                return result
            except Exception as e:
                print(str(e))
        raise ValueError('Agent消息压缩出错')
    
    # def _compress_message(self, message):
    #     prompt = message + '\n\n简单的一段话概要上面的内容，且包含了最核心的一些关键词，如姓名、函数或者类名、核心技术名词、故事冲突点等。'
    #     for index, llm_inference in enumerate(self.llm_inferences):
    #         try:
    #             response = llm_inference([{'role': 'user', 'content': prompt}], stream=False)
    #             return '<detail deleted> Summary:\n' + response
    #         except:
    #             pass
    #     return None


    def _get_llm_messages(self):
        """
        动态组装LLM的消息，并返回
        @return: list, [{"role": "system|assistant|user", "content": "content"}, ...]
        """
        # 长度分配: 整体长度小于80%的token限制，去掉SYSTEM PROMPT后，剩余的token平均分配给MESSAGES和FILES
        
        # 合并messages中，同类型的连续消息
        new_messages = [{"role": "system", "content": self.system_prompt}]
        for message in self.messages:
            if new_messages[-1]["role"] != message["role"] or message["role"] == 'user':
                new_messages.append(message)
            else:
                if isinstance(new_messages[-1]["content"], str) and isinstance(message["content"], str):
                    new_messages[-1]["content"] += '\n\n' + message["content"]
                else:
                    new_messages.append(message)
        self.messages = new_messages[1:]
        self.save_messages()

        # 添加文件内容
        files = self._read_files + self._tmp_read_files
        if len(files) > 0:
            file_memory = self.get_file_memory([], files, -1)
            new_messages = new_messages[:-1] + [{"role": "user", "content": file_memory}] + new_messages[-1:]

        # 添加system消息
        return new_messages
    
    def _run_python_match(self, result):
        # 检测是否有python代码需要运行
        parse = re.compile( "```python\n# run code\n(.*?)\n```", re.DOTALL).search(result)
        if parse is not None:
            # 将找到的内容后面的截断
            return True, result[:parse.end()]
        else:
            return False, result
        
    def _run_python(self, llm_result):
        """运行python代码，返回: (python_mode, python_data, result, continue)"""
        parse = re.compile( "```python\n# run code\n(.*?)\n```", re.DOTALL).search(llm_result)
        if parse is not None:
            code = parse.group(1)
            try:
                python_data, log = self._run_code(code)
            except Exception as e:
                error_log = str(traceback.format_exc())
                return True, None, f'python代码执行失败: {str(e)}\n{error_log}', False
            return True, python_data, log, True
        else:
            return False, None, '', False

    def _llm_and_parse_output(self, messages):
        """return (llm_result, (python_mode, python_data, result, continue))"""
        llm_result = ""
        realtime_parse = None
        interpretors = self._interpretors
        if self._enable_python:
            interpretors = interpretors + [(self._run_python_match, self._run_python, 'realtime')]
        for index, llm_inference in enumerate(self.llm_inferences):
            try:
                if self.model is None:
                    response = llm_inference(messages, stream=True)
                else:
                    response = llm_inference(messages, stream=True, model=self.model)
                is_break = False
                for token in response:
                    # print(f'<<{token}>>')
                    llm_result += token
                    self.stream_output(token)
                    for test_match, parse, mode in interpretors:
                        if mode == 'realtime': # 如果是实时解析器，则解析
                            # 实时解析器必须返回是否匹配和新的llm_result(让送入messages的内容更加准确)
                            result = test_match(llm_result)
                            if isinstance(result, tuple):
                                is_match, new_llm_result = result
                            else:
                                is_match = result
                                new_llm_result = llm_result
                            if is_match:
                                llm_result = new_llm_result
                                realtime_parse = parse
                                is_break = True
                                break
                    if is_break:
                        break
                # 可能返回空的情况
                if len(llm_result) > 0:
                    break
                else:
                    self.stream_output('LLM返回空，进行重试')
                    continue
            except Exception as e:
                if index < (len(self.llm_inferences) - 1):
                    self.stream_output(f'LLM请求错误，进行重试')
                    self.stream_output(None)
                    logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
                    llm_result = ''
                    continue
                else:
                    raise e
        self.stream_output(None)
        if len(llm_result.strip()) > 0:
            self.add_message("assistant", llm_result)
        # # 有实时解析器
        # if realtime_parse is not None:
        #     parse_result = realtime_parse(llm_result)
        #     return llm_result, parse_result
        # else:
        #     # 没有实时解析器
        #     parse_results = []
        #     for is_match, parse, mode in interpretors:
        #         if mode == 'final':
        #             if is_match(llm_result):
        #                 parse_result = parse(llm_result)
        #                 parse_results.append(parse_result)
        #     if len(parse_results) > 0:
        #         python_mode = False
        #         python_result = None
        #         continue_run = False
        #         result = ''
        #         for _python_mode, _python_data, _result, _continue_run in parse_results:
        #             if _python_mode:
        #                 python_mode = True
        #                 python_result = _python_data
        #             if _continue_run:
        #                 continue_run = True
        #             result += _result
        #         return llm_result, (python_mode, python_result, result, continue_run)
        #     else:
        #         return llm_result, (False, None, '', False)

        parse_results = []
        for is_match, parse, mode in interpretors:
            if is_match(llm_result):
                parse_result = parse(llm_result)
                parse_results.append(parse_result)
        if len(parse_results) > 0:
            python_mode = False
            python_result = None
            continue_run = False
            result = ''
            for _python_mode, _python_data, _result, _continue_run in parse_results:
                if _python_mode:
                    python_mode = True
                    python_result = _python_data
                if _continue_run:
                    continue_run = True
                result += _result
            return llm_result, (python_mode, python_result, result, continue_run)
        else:
            return llm_result, (False, None, '', False)

    def _run_code(self, code):
        # 运行的代码里面不能有其他skills库
        default_import = """from codyer import skills\n"""
        code = default_import + code
        functions = [f for f in self.functions if type(f).__name__ == "function"] # 过滤掉skills相关函数
        python_result, log = skills._exec(self.python_pickle_path, code, functions=functions, names=[f.__name__ for f in functions])
        return python_result, log
    

