import os
import pickle

def load_code_context(python_pickle_path):
    """加载代码上下文"""
    globals = {}
    if os.path.exists(python_pickle_path):
        with open(python_pickle_path, "rb") as f:
            globals = pickle.load(f)
    return globals

def _remove_unpickleable(globals):
    if "__builtins__" in globals:
        globals.__delitem__("__builtins__")
    keys = list(globals.keys())
    for key in keys:
        try:
            pickle.dumps(globals[key])
        except Exception:
            globals.__delitem__(key)

def save_code_context(python_pickle_path, globals):
    """保存代码上下文"""
    _remove_unpickleable(globals)
    # 删除 from codyer import skills 库
    if 'skills' in globals:
        del globals['skills']
    # 移除
    with open(python_pickle_path, "wb") as f:
        pickle.dump(globals, f)


# # 用户准备和清理的fixture
# @pytest.fixture
# def clear_python_status():
#     remove_code_content()
#     yield None
#     remove_code_content()

def _exec_code(python_pickle_path, code, names, functions):
    import traceback, logging
    # 加载代码上下文
    globals = load_code_context(python_pickle_path)
    for index, name in enumerate(names):
        globals[name] = functions[index]
    import ast
    # 获取最后一个表达式
    tree = ast.parse(code)
    last_node = tree.body[-1]
    code_body = tree.body[0:-1]
    last_expr = ast.unparse(last_node)
    if isinstance(last_node, ast.Assign):
        code_body = tree.body
        expr_left = last_node.targets[-1]
        if isinstance(expr_left, ast.Tuple):
            last_expr = f"({', '.join([x.id for x in expr_left.elts])})"
        else:
            last_expr = expr_left.id
    elif isinstance(last_node, ast.AugAssign) or isinstance(last_node, ast.AnnAssign):
        code_body = tree.body
        last_expr = last_node.target.id
    # 执行除了最后一个表达式的代码
    if len(code_body):
        main_code = compile(ast.unparse(code_body), "<string>", "exec")
        try:
            exec(main_code, globals)
        except Exception as e:
            logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
            error = '\n'.join((str(traceback.format_exc())).split('\n')[3:])
            return None, error
    # 运行最后一个表达式
    try:
        result = eval(compile(last_expr, "<string>", "eval"), globals)
    except Exception as e:
        logging.error(str(traceback.format_exc()).replace('\n', '\\n'))
        error = '\n'.join((str(traceback.format_exc())).split('\n')[3:])
        return None, error
    # print('run code:', code)
    # print('result:', result)
    # 保存代码上下文
    save_code_context(python_pickle_path, globals)
    return result, None

def exec_code(workspace, code, names, functions):
    import io, sys
    output = io.StringIO()
    sys.stdout = output
    python_result, error = _exec_code(workspace,code, names, functions)
    log = output.getvalue().strip()
    sys.stdout = sys.__stdout__
    if error is not None:
        log = log + '\n' + error
    return python_result, log