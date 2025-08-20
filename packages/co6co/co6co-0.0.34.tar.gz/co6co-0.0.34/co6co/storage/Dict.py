import time
from typing import Union, Any


class UpdateDictMixin(object):
    """
    Mixin for dict that calls a function passed every time something is changed.
    The function is passed the dict instance.
    """
    on_update = None

    def calls_update(name):
        def oncall(self, *args, **kw):
            rv = getattr(super(UpdateDictMixin, self), name)(*args, **kw)
            if self.on_update is not None:
                self.on_update(self)
            return rv

        oncall.__name__ = name
        return oncall

    def setdefault(self, key, default=None):
        modified = key not in self
        rv = super(UpdateDictMixin, self).setdefault(key, default)
        if modified and self.on_update is not None:
            self.on_update(self)
        return rv

    def pop(self, key, default=None):
        modified = key in self
        if not default:
            rv = super(UpdateDictMixin, self).pop(key)
        else:
            rv = super(UpdateDictMixin, self).pop(key, default)
        if modified and self.on_update is not None:
            self.on_update(self)
        return rv

    __setitem__ = calls_update("__setitem__")
    __delitem__ = calls_update("__delitem__")
    clear = calls_update("clear")
    popitem = calls_update("popitem")
    update = calls_update("update")
    del calls_update


class CallbackDict(UpdateDictMixin, dict):

    """A dict that calls a function passed every time something is changed.
    The function is passed the dict instance.

    Copyright (c) 2015 by Armin Ronacher and contributors.  See AUTHORS
    in FLASK_LICENSE for more details.

    """

    def __init__(self, initial=None, on_update=None):
        dict.__init__(self, initial or ())
        self.on_update = on_update

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, dict.__repr__(self))


class ExpiringDict(dict):
    """
    一个字典，其中的键值对会在一定时间后过期。

    """

    def __init__(self, prefix=""):
        self.prefix = prefix
        super().__init__()
        self.expiry_times = {}

    def set(self, key: Union[str, int], val: Any, expiry: int):
        """
        向字典中设置一个键值对，并为该键值对设置过期时间。

        :param key: 要设置的键，可以是字符串或整数。
        :param val: 要设置的值，可以是任意类型。
        :param expiry: 键值对的过期时间，单位为秒。
        """
        # 设置键值对
        self[key] = val
        self.expiry_times[key] = time.time() + expiry

    def get_by_sid(self, key: str):
        """
        通过SID（会话ID）获取字典中的值。

        :param key: 要查找的键，这里通常是SID。
        :return: 如果键存在且未过期，则返回对应的值；否则返回None。
        """
        # 拼接前缀和传入的键
        key = self.prefix + key
        return self.get(key)

    def get(self, key: Union[str, int]):
        """
        根据键获取字典中的值，如果键对应的条目已过期，则删除该条目并返回 None。

        :param key: 要查找的键，可以是字符串或整数。
        :return: 如果键存在且未过期，则返回对应的值；否则返回 None。

        //todo 可能bug 需要用到才知道过期，才会清理，可能会造成内存泄漏
        """
        # 获取字典中的值
        data = dict(self).get(key)

        if not data:
            return None

        if time.time() > self.expiry_times[key]:
            del self[key]
            del self.expiry_times[key]
            return None

        return data

    def delete(self, key: Union[str, int]):
        del self[key]
        del self.expiry_times[key]
