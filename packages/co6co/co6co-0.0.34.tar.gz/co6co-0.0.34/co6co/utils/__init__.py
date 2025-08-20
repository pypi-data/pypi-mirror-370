# -*- coding:utf-8 -*-
import re
import random
import string
import time
import datetime
from types import FunctionType
import inspect
import os
import io
import sys
import asyncio
from typing import IO, Iterable, Callable, Tuple, Generator, List
from .log import warn
from functools import wraps


def try_except(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")
            return None  # 或者根据需要返回其他默认值
    return wrapper


def try2int(value: any, default=0):
    try:
        return int(value)
    except:
        return default


class DATA():
    """
    处理数据
    """

    def __init__(self, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.items()]

    def __str__(self):
        return str(self.__dict__)


def isBase64(content: str) -> bool:
    _reg = "^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{4}|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)$"
    group = re.match(_reg, content)
    if group != None:
        return True
    return False


def debug():
    frameList = inspect.stack()
    sss = ["{}:{} ->{}".format(i.filename, i.lineno, i.function) for i in frameList]
    print(len(frameList))
    warn('\n' + '\n'.join(sss))


def getRandomStr(length: int, scope: str = string.ascii_letters+string.digits) -> str:
    return ''.join(random.sample(scope, length))


def generate_id(*_):
    return time.time_ns()


def getDateFolder(format: str = "%Y/%m/%d"):
    """
    获得当前日期目录:
    2023/12/01
    """
    time = datetime.datetime.now()
    return f"{time.strftime(format)}"


def isCallable(func):
    return isinstance(func, FunctionType)
    return callable(func)  # 返回true 也不一定能调用成功/返回失败一定调用失败
    return type(func) is FunctionType
    return hasattr(func, "__call__")


async def async_iterator(sync_iter: Iterable):
    """
    同步迭代器 转异步迭代器
    @param sync_iter 同步迭代器
    """
    for item in sync_iter:
        yield await asyncio.to_thread(lambda: item)


def is_async(func):
    """
    方法是否是异步的
    """
    return inspect.iscoroutinefunction(func) or inspect.isasyncgenfunction(func)


def getWorkDirectory():
    """
    获取工作目录
    """
    current_directory = os.getcwd()
    return current_directory


def find_files(root, *ignoreDirs: str, filterDirFunction: Callable[[str], bool] = None, filterFileFunction: Callable[[str], bool] = None) -> Generator[Tuple[str, List, List], str, None]:
    """
    root: 根目录
    filterDirFunction  (folderName:str)->bool 
    filterFileFunction (fileName:str)->bool
                       可以使用  lambda f:f.endswith(extension)
    RETURN  root  fdirs, ffile 
    查找文件或文件夹
    os.path.join(root, file)

    """
    for root, dirs, files in os.walk(root):
        for ignore in ignoreDirs:
            if ignore in dirs:
                dirs.remove(ignore)
        fdirs = list(filter(filterDirFunction, dirs)) if filterDirFunction != None else dirs
        ffile = list(filter(filterFileFunction, files)) if filterFileFunction != None else files
        yield root, fdirs, ffile


def get_parent_dir(path: str, rank: int = 1):
    """
    获取上级目录
    """
    result: str = path
    stop = rank+1
    for _ in range(1, stop):
        result = os.path.dirname(result)
    return result


def getApplcationPath(__file__):
    # print("如果脚本被编译成.pyc文件运行或者使用了一些打包工具（如PyInstaller），那么__file__可能不会返回源.py文件的路径，而是编译后的文件或临时文件的路径")
    # 获取当前文件的完整路径
    if getattr(sys, 'frozen', False):
        # 如果应用程序是冻结的，获取可执行文件的路径
        application_path = os.path.dirname(sys.executable)
    else:
        # 否则，获取原始脚本的路径
        application_path = os.path.dirname(os.path.abspath(__file__))

    return application_path


def read_stream(stream: IO[bytes], size: int = -1) -> Iterable[bytes]:
    while True:
        chunk = stream.read(size)
        if not chunk:
            break
        yield chunk


def compare_versions(v1: str, v2: str):
    """
    比较版本号
    return v1>v2=1,v1<v2=-1,v1<v2=0
    """
    # 将版本号按点号分割成列表，并将每个元素转换为整数
    v1_parts = list(map(int, v1.split('.')))
    v2_parts = list(map(int, v2.split('.')))

    # 使用zip函数对两个列表进行比较
    for part1, part2 in zip(v1_parts, v2_parts):
        if part1 > part2:
            return 1
        elif part1 < part2:
            return -1

    # 如果长度不同，且前面的部分都相同，则更长的那个版本号更大
    if len(v1_parts) > len(v2_parts):
        return 1
    elif len(v1_parts) < len(v2_parts):
        return -1
    else:
        return 0


def convert_size(size_bytes):
    """将字节大小转换为易读的格式(KB、MB、GB)"""
    if size_bytes == 0:
        return "0B"

    # 定义单位
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    index = 0

    # 不断除以 1024，直到找到合适的单位
    while size_bytes >= 1024 and index < len(units) - 1:
        size_bytes /= 1024.0
        index += 1

    return f"{size_bytes:.2f} {units[index]}"  # 保留两位小数


def split_value_unit(size_str):
    # 定义正则表达式，匹配数值和单位
    pattern = r"^\s*(\d+(\.\d+)?)\s*([A-Za-z]+)\s*$"
    match = re.match(pattern, size_str)

    if match:
        value = float(match.group(1))  # 数值部分
        unit = match.group(3)         # 单位部分
        return value, unit
    else:
        raise ValueError(f"无效的输入格式: {size_str}")


def convert_to_bytes(size: int, unit: str):
    """
    将指定大小和单位转换为字节数。
    convert_to_bytes(*split_value_unit("5 GB"))
    convert_to_bytes(*split_value_unit("5GB"))
    参数:
    - size: 数值 (float 或 int)
    - unit: 单位 ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB')

    返回:
    - 对应的字节数 (int)
    """
    # 定义单位与字节数的关系
    units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4,
        'PB': 1024**5,
        'EB': 1024**6
    }
    unit = unit.upper()
    # 检查单位是否合法
    if unit not in units:
        raise ValueError(f"无效的单位: {unit}. 支持的单位有: {list(units.keys())}")

    # 计算字节数
    return int(size * units[unit])


async def write_stream(input: IO[bytes], outputStream: IO[bytes]):
    for chunk in read_stream(input, size=io.DEFAULT_BUFFER_SIZE):
        try:
            # print("**FF读数据", len(chunk))
            outputStream.write(chunk)
            outputStream.flush()
            # print("**输出到stdin*****",len(chunk))
        except Exception as e:
            pass
            # print("**FF异常", e, len(chunk))
    outputStream.close()
