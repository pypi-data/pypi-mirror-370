# -*- coding:utf-8 -*-

import datetime
import sys
import threading
import os
# from loguru import logger
import logging
import logging.handlers
import traceback
from pathlib import Path
from typing import List
'''
loguru 日志配置
'''
# logger.remove()
# logger.add(sys.stdout,level="INFO",format="{file}\t{line}\t{message}")
'''
#https://blog.csdn.net/Kangyucheng/article/details/112794185
TRACE           5   trace()
DEBUG           10  debug()
INFO            20  info()
SUCCESS         25  success()
WARNING         30  warning()
ERROR           40  error()
CRITICAL        50  critical()
'''
 
def create_logger(filename: str,folder:str=".",showLevel:int=logging.DEBUG, format:str="%(asctime)s %(levelname)5.5s: %(message)s") -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(showLevel)
    #folder=Path(__file__).parent.joinpath("logs")
    if not os.path.exists(folder):
        os.makedirs(folder)
    formatter = logging.Formatter(format)
    handlers:List[logging.Handler] = [
        logging.handlers.RotatingFileHandler( Path(folder).joinpath(  filename), maxBytes=1024*1024, backupCount=0,encoding='utf-8'),
        logging.StreamHandler()
    ]
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

'''
控制台日志 日志配置
'''
"""
\033[显示方式;前景色;背景色m*******\033[0m
\033[显示方式;前景色;背景色m*******\033[0m
显示方式:    0:默认值
            1:高亮
            4:下划线
            5:闪烁
            7:反显
            8:不可见
控制台颜色值：
前景色      背景色      颜色说明
 30           40        黑色
 31           41        红色
 32           42        绿色
 33           43        黄色
 34           44        蓝色
 35           45        紫红色
 36           46        青蓝色
 37           47        白色
"""


def __getMessage(*msg: str):
    return "\t".join([str(m) for m in msg])


def __log(*msg: str, type: int = 0, foregroundColor: int = 37, bg=40, e=None, hasPrefix: bool = True):
    t = threading.currentThread()
    time = datetime.datetime.now()
    err = e.__traceback__.tb_lineno if e != None else ""
    prefix = f"['{time.strftime('%Y-%m-%d %H:%M:%S')}'] [{t.ident}|{t.name}]\t"
    if not hasPrefix:
        prefix = ""
    # __getMessage(*msg).encode("utf-8") 以前为什么不显示乱码
    print(f"{prefix}\033[{type};{foregroundColor};{bg}m{__getMessage(*msg)}{err}\033[0m")


def log(*msg: str): __log(*msg)


def generateCode(data: any):
    """
    通过 对象 转字符串 
    生成  大小  hash值
    """
    s = str(data)
    return hex(s.__hash__()).upper()


def start_mark(msg: str, f: str = "--", start: str = "\r\n", end: str = ">", num: int = 36):
    """
    标记开始
    """
    __log(start+f*num + msg + f*num+end, hasPrefix=False)


def end_mark(msg: str, f: str = "==", start: str = "\r\n<", end: str = "\r\n\r\n", num: int = 36):
    """
    标记结束
    """
    __log(start+f*num + msg + f*num+end, hasPrefix=False)


def info(*msg: str): __log(*msg)


def succ(*msg: str):
    """
    成功日志
    """
    __log(*msg, type=7, foregroundColor=32, bg=40)


def warn(*msg: str):
    """
    警告日志
    """
    __log(*msg, type=7, foregroundColor=33, bg=40)


def err(*msg: str, e=None):
    """
    错误日志
    """
    message = __getMessage(*msg)
    __log(f'{message}-->{traceback.format_exc()}', type=7, foregroundColor=31, bg=40, e=e)


def critical(msg: str):
    """
    危急日志
    """
    message = __getMessage(*msg)
    __log(f'{message}-->{traceback.format_exc()}', type=7, foregroundColor=37, bg=40)


'''
if __name__ == "__main__" :
    logger.trace("文件日志")
    logger.success("*arg:{}{}\t\t**kwargs:'ab:{ab},cd:{cd}'","元数据1","元数据2",ab="字典数据1",cd="字典数据2")
'''


def progress_bar(i: float, title: str = ""):
    """
    进度条
    """
    i = int(i*100)
    print("\r", end="")
    print("{}: {}%: ".format(title, i), "▋" * (i // 2), end="")
    sys.stdout.flush()
