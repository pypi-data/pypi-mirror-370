# -*- encoding:utf-8 -*-
# 动态代码
from typing import Callable


def read_file(file_path):
    with open(file_path, "rb") as f:
        source_code = f.read()
        return source_code


"""
source: 字符串形式的 Python 代码或 AST 对象。这是要编译的源代码。
filename: 字符串。如果源代码来自文件，则提供该文件的名称；如果不是来自文件，可以提供一个合适的名称，如 '<string>' 表示源代码是直接以字符串形式提供的。
mode: 编译模式，可以是 'exec', 'eval', 或 'single'。这决定了源代码应该如何被解释：
    'exec': 源代码包含一个或多个语句。
    'eval': 源代码是一个表达式。
    'single': 类似于 'exec'，但如果源代码只有一行，则会像在交互式解释器中那样执行。
flags (可选): 编译标志，用于指定特定的编译选项。这是一个整数，默认值为 0。例如，可以使用 PyCF_ONLY_AST 标志来返回 AST 而不是编译后的代码对象。
dont_inherit (可选): 如果设置为 True，那么编译过程中不会继承全局变量。默认值为 False。
optimize (可选): 优化级别。默认值为 -1，表示使用命令行指定的优化级别。其他可能的值包括 0（无优化）、1 和 2。
"""


def get_source_fun(source_code, func_name) -> Callable[[], None]:
    """
    source_code: 代码
    func_name: 代码中的方法
    """
    scope = {}
    compile_source(source_code, scope)
    f = scope.get(func_name, None)
    return f


def compile_source(source_code, global_vars: dict = None, local_vars: dict = None):
    """
    source_code: 代码 
    """
    exec_code = compile(source_code, '<string>', "exec")
    exec(exec_code, global_vars, local_vars)
