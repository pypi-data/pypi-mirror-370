# -*- coding:utf-8 -*-
# Author:  zhousf
# Description:  list交集、并集、差集运算
import math
import random
from collections import Counter

from zhousflib.util import string_util


def counter(data_list: list, arg=None):
    """
    统计列表中某个元素的个数
    :param data_list: 列表
    :param arg: 某个元素，空时则返回counter
    :return:
    """
    res = Counter(data_list)
    if arg:
        return res.get(arg, 0)
    else:
        return res


def get_max_counter(data_list: list) -> int:
    """
    返回列表中重复项最多的个数
    :param data_list:  ['2', '2', '131.8', '131.8', '131.8', '131.8', '131.8', '1']
    :return: 5
    """
    if len(data_list) == 0:
        return 0
    res = Counter(data_list)
    count_list = [res.get(i) for i in res]
    count_list.sort(reverse=True)
    return count_list[0]


def get_min_counter(data_list: list) -> int:
    """
    返回列表中重复项最少的个数
    :param data_list:  ['2', '2', '131.8', '131.8', '131.8', '131.8', '131.8', '1']
    :return: 1
    """
    if len(data_list) == 0:
        return 0
    res = Counter(data_list)
    count_list = [res.get(i) for i in res]
    count_list.sort(reverse=False)
    return count_list[0]


def random_choices(data_list: list, choose_k=3) -> list:
    """
    从列表中随机抽取choose_k个数（会有重复值）
    :param data_list:
    :param choose_k:
    :return:
    """
    return random.choices(data_list, k=choose_k)


def none_filter(data: list) -> list:
    """
    去掉list中的None值
    :param data:
    :return:
    """
    if isinstance(data, list):
        res = []
        for item in data:
            if isinstance(item, list):
                res.append(list(filter(None, item)))
            else:
                res = list(filter(None, data))
                break
        return res
    return data


def intersection(a, b):
    """
    交集
    :param a: [1, 2, 3, 4, 5]
    :param b: [2, 3, 9]
    :return: [2, 3]
    """
    if len(a) == 0:
        return b
    if len(b) == 0:
        return a
    return list(set(a).intersection(set(b)))


def union(a, b):
    """
    并集
    :param a: [1, 2, 3, 4, 5]
    :param b: [2, 3, 9]
    :return: [1, 2, 3, 4, 5, 9]
    """
    if len(a) == 0:
        return b
    if len(b) == 0:
        return a
    return list(set(a).union(set(b)))


def difference(a, b):
    """
    差集
    :param a: [1, 2, 3, 4, 5]
    :param b: [2, 3, 9]
    :return: [1, 4, 5]
    """
    if len(a) == 0:
        return b
    if len(b) == 0:
        return a
    return list(set(a).difference(set(b)))


def sort(data: list, index, reverse=False):
    """
    排序
    :param data:
    :param index: 排序参考的索引：int，或dict中key：str
    :param reverse: 是否倒序
    :return:
    """
    data = sorted(data, key=lambda v: v[index], reverse=reverse)
    return data


def get_min_number(what: list):
    """
    获取list中最小值
    ["685.2", "10", "ab"]  -> 10
    :param what:
    :return:
    """
    min_value = ""
    number = [item for item in what if string_util.is_number(item)]
    for item in number:
        if string_util.is_less_than_number(item, min_value) or not min_value:
            min_value = item
    return min_value


def get_max_number(what: list):
    """
    获取list中最大值
    ["685.2", "10", "ab"]  -> 685.2
    :param what:
    :return:
    """
    max_value = ""
    number = [item for item in what if string_util.is_number(item)]
    for item in number:
        if string_util.is_greater_than_number(item, max_value) or not max_value:
            max_value = item
    return max_value


def delete_same_value(data_list: list, same_value_limit=1):
    """
    删除重复的值
    :param data_list:
    :param same_value_limit: 限制重复值的个数
    :return:
    ['113.8', '113.8', '131.8', '131.8', '131.8', '131.8', '131.8', "1"]
    处理成：
    ['113.8', '131.8', '1']
    """
    if len(data_list) == 0:
        return data_list
    counter_ = counter(data_list)
    repeat_num = [num for num in counter_.values() if num > 1]
    if len(repeat_num) > 1:
        for key in counter_.keys():
            num = counter_.get(key)
            if num > same_value_limit:
                counter_[key] = same_value_limit
    data_list.clear()
    for key in counter_.keys():
        for i in range(counter_.get(key)):
            data_list.append(key)
    return data_list


def chunk_list(data: list, chunk_size=5) -> list:
    """
    将数组按照每chunk_size个一组
    input : data=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  chunk_size=5
    output: [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10]]
    """
    if chunk_size <= 0:
        return data
    return [data[i * chunk_size:(i+1)*chunk_size] for i in range(0, math.ceil(len(data) / chunk_size))]


def split_list(data: list, split_size=2) -> list:
    """
    等分分割
    input : data=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  split_size=2
    output: [[0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]
    """
    chunk_size = math.ceil(len(data) / split_size)
    return [data[i * chunk_size:(i + 1) * chunk_size] for i in range(split_size)]

