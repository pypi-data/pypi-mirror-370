# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function: 线程安全的单例模式
import threading


class Singleton(type):
    """
    class A(metaclass=Singleton)
    """
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with Singleton._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(Singleton,cls).__call__(*args, **kwargs)
        return cls._instance


def singleton(cls):
    """
    @singleton
    class A:
        pass
    """

    _instance = {}

    def _singleton(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return _singleton
