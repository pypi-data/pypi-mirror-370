# -*- coding:utf-8 -*-
from typing import TypeVar, List
T = TypeVar('T')


class Base:
    def __repr__(self) -> str:
        return f'{self.__class__}'


def byteSite(bytesLength: int):
    """ 
    删除不需要
    (B,KB,MB,GB,TB)

    """
    kb = round(bytesLength/1024, 2)
    mb = round(bytesLength/1024**2, 2)
    gb = round(bytesLength/1024**3, 2)
    tb = round(bytesLength/1024**4, 2)
    return bytesLength, kb, mb, gb, tb


def getByteUnit(bytesLength: int):
    """
    删除不需要
    """
    kmb = byteSite(bytesLength)
    unit = ["B", "KB", "MB", "GB", "TB"]
    f = 0
    # 逆序
    # reversed_arr = kmb[::-1]
    for s in kmb:
        if (s < 1024):
            return f"{s}{unit[f]}"
        f += 1
    return None


__all__ = ['utils']  # 针对模块公开接口的一种约定，以提供了”白名单“的形式暴露接口。
# 如果定义了__all__，
# 使用from xxx import *导入该文件时，只会导入 __all__ 列出的成员，可以其他成员都被排除在外。

__version_info = (0, 0, 34)
__version__ = ".".join([str(x) for x in __version_info])
