from enum import Enum, unique
# from abc import ABC, abstractclassmethod  抽象
from typing import List, Dict, Literal

from co6co import T


@unique  # 帮助检查 保证没有重复值
class Base_Enum (Enum):
    """
    枚举[key, val]
    name:才是真正的Key,环境保证它的唯一性
    key: 为人为设置由用户保证它的唯一性
    """
    key: T
    val: T

    def __new__(cls, key: T, value: T):
        _value = len(cls.__members__) + 1  # 为每个成员分配一个递增的整数值
        obj = object.__new__(cls)
        obj.key = key
        obj.val = value  # value 为元组 (en_name,cn_name,val)
        obj._value_ = _value  # 设置枚举成员的值
        return obj

    @classmethod
    def to_dict_list(cls) -> List[Dict]:
        status = [{'uid': i.name, 'key': i.key, 'value': i.val} for i in cls]
        return status

    @classmethod
    def key2enum(cls, key):
        """
        key 转枚举 
        """
        for i in cls:
            if i.key == key:
                return i
        return None

    @classmethod
    def name2enum(cls, name: str):
        """
        name 转枚举 
        """
        for i in cls:
            if i.name == name:
                return i
        return None

    @classmethod
    def val2enum(cls, val):
        """
        val 转枚举 
        """
        for i in cls:
            if i.val == val:
                return i
        return None

    @classmethod
    def value2enum(cls, value: int):
        """
        val 转枚举 
        """
        for i in cls:
            if i._value_ == value:
                return i
        return None

    @classmethod
    def generator(cls):
        for _, v in cls.__members__.items():
            yield v

    @classmethod
    def _to_str(cls, attr) -> str:
        return ",".join([f"{i.val}:{getattr(i, attr)}" for i in cls])

    @classmethod
    def to_str(cls, attr: Literal["key", "name"]) -> str:
        return cls._to_str(attr)

    @classmethod
    def value_of(cls, name: str, ignoreError: False):
        """
        枚举的字符串 转枚举
        demo(Base_Enum):
            chanel="ch",1
        字符串 为 chanel 
        """
        for k, v in cls.__members__.items():
            if k == name:
                return v
        else:
            if ignoreError:
                return None
            else:
                raise ValueError(f"'{cls.__name__}' enum not found for '{name}'")

    def __str__(self):
        """
        name value 原始枚举值
        """
        return f'name: {self.name}, value: {self.value}, key:{self.key},val:{self.val}'


@unique
class Base_EC_Enum(Base_Enum):
    """
    枚举[key:英文 ,label:中文 ,val:数字] 
    """
    key: T
    label: T
    val: T

    def __new__(cls, key: T, label: T, value: T):
        _value = len(cls.__members__) + 1  # 为每个成员分配一个递增的整数值
        obj = object.__new__(cls)
        obj.key = key
        obj.label = label
        obj.val = value  # value 为元组 (en_name,cn_name,val)
        obj._value_ = _value  # 设置枚举成员的值
        return obj

    @classmethod
    def to_dict_list(cls) -> List[Dict]:
        status = [{'uid': i.name, "label": i.label, 'key': i.key, 'value': i.val} for i in cls]
        return status

    @classmethod
    def to_str(cls, attr: Literal["key", "name", 'label']) -> str:
        return cls._to_str(attr)

    @classmethod
    def to_labels_str(cls) -> str:
        return cls.to_str("label")

    def __str__(self):
        """
        name value 原始枚举值
        """
        return f'name: {self.name}, value: {self.value}, key:{self.key},label:{self.label},val:{self.val}'
