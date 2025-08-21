# -*- coding: utf-8 -*-
# @Author  : zhousf-a
# @Function: pip install pympler
"""
获取对象的内存大小
方式1：采用 import sys; sys.getsizeof()不遍历对象内部的元素指向内存
方式2：采用 from pympler import asizeof; asizeof.asizeof()遍历对象内部元素，推荐使用
"""
from pympler import asizeof


def get_memory_byte_size(data):
    """
    获取对象占用内存的大小，单位：byte
    :param data:
    :return:
    """
    return asizeof.asizeof(data)


def get_memory_mb_size(data):
    """
    获取对象占用内存的大小，单位：MB
    :param data:
    :return:
    """
    size_byte = get_memory_byte_size(data)
    return size_byte / (1024 * 1024)
