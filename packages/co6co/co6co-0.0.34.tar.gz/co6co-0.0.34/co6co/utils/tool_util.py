import re
from types import FunctionType, MethodType  # 对象的叫方法[method]，其他未函数[Function]

import inspect


def get_current_function_name():
    return inspect.currentframe().f_back.f_code.co_name


def to_camelcase(name: str) -> str:
    """
    下划线转驼峰(小驼峰)
    """
    return re.sub(r'(_[a-z])', lambda x: x.group(1)[1].upper(), name)


def to_underscore(name: str) -> str:
    """
    驼峰转下划线
    """
    if '_' not in name:
        name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
    else:
        raise ValueError(f'{name}字符中包含下划线，无法转换')
    return name.lower()


def choose(data: dict, keys: list | tuple, valueNone: bool = False) -> dict:
    """
    挑选指定的KEY
    """
    if valueNone:
        new_dict = {k: None for k in keys}
        data = {**new_dict,**data}

    new_dict = {key: data[key] for key in data if key in keys}
    return new_dict


def list_to_tree(data_list: list, root: any, pid_field: str, id_field: str):
    """
    list 转 tree 

    data_list: 数据列表,
    root: 通过 `.get(pid_field) == root ` 查出所有根节点, 或者是找到 根的 一个方法
    pid_field: 关联父节点的字段,
    id_field:  主键id

    return 树形 包含 children 字段
    """
    getRoot = root

    def _getRoot(a__data_list: dict):
        return a__data_list.get(pid_field) == root

    if not isinstance(root, FunctionType):
        getRoot = _getRoot

    resp_list = [i for i in data_list if getRoot(i)]
    for i in data_list:
        i['children'] = [j for j in data_list if i.get(id_field) == j.get(pid_field)]
    return resp_list
