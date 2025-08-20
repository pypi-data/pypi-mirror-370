import sys
import inspect
from types import ModuleType
from typing import Dict, Callable


class module:
    name: str
    _module: Dict[str, ModuleType]

    def __init__(self, name):
        """
        获取指定模块
        @param name 模块名称 __name__
        """
        self.name = name
        self._module = sys.modules[name]
        pass

    @property
    def module_object(self):
        """
        获取模块
        """
        return self._module

    @property
    def all_object(self):
        """
        模块所有对象
        """
        all_objects = vars(self.module_object)
        return all_objects

    def filter_object(self, filter: Callable[[object], bool]):
        """
        @param filter 通常:inspect的一些方法[isbuiltin,isclass]

        或者使用类似： [{"key": name, "value": obj} for name, obj in all_objects.items() if isinstance(obj, list)] 过滤
        """
        return inspect.getmembers(self.module_object, filter)
