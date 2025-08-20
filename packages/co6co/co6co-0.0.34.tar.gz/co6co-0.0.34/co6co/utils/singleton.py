
from __future__ import annotations
from datetime import datetime
from typing import Type, TypeVar

T = TypeVar('T')


def singleton(cls):
    """
    单例模式装饰器

    使用方法：
    @singleton
    class MyClass:
        pass
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
            instances[cls].createTime = datetime.now()
        return instances[cls]
    return get_instance


class Singleton:
    """
    单例模式 子类继承
    """
    _instance: T = None
    createTime = None

    def __new__(cls, *args, **kwargs):
        """
        需要弄得 __new__ 怎么调用 __init__ 的
        """
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.createTime = datetime.now()
        pass
