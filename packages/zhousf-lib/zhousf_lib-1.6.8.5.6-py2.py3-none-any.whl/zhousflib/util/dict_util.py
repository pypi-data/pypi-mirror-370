# -*- coding:utf-8 -*-
# Author:      zhousf
# Description:


def is_empty(dic):
    if dic is None or dic == '':
        return True
    if isinstance(dic, str):
        dic = eval(dic)
    if isinstance(dic, dict):
        if len(dic) != 0:
            return False
    if isinstance(dic, list):
        if len(dic) != 0:
            return False
    if isinstance(dic, set):
        if len(dic) != 0:
            return False
    return True


def pop(dic, key):
    if dic is not None and key is not None:
        if key in dic:
            dic.pop(key)
            return True
    return False


def merge(a, b):
    """
    字典合并，若key重复则b值覆盖a值
    :param a:
    :param b:
    :return:
    example:
    a = {'a':1,'b':{'v':1,'e':2},'g':9}
    b = {'b':{'v':2,'d':2},'c':3,'g':10}
    output:
    {'a': 1, 'c': 3, 'b': {'e': 2, 'd': 2, 'v': 2}, 'g': 10}
    """
    re = {}
    a_dict = a if isinstance(a, dict) else eval(a)
    b_dict = b if isinstance(b, dict) else eval(b)
    key_unit = list(a_dict.keys())
    key_unit.extend(list(b_dict.keys()))
    for key in key_unit:
        if key in a_dict and key in b_dict:
            # 若是字典类型则合并
            if isinstance(a_dict[key], dict):
                # 合并字典
                c = dict(a_dict[key], **b_dict[key])
                re[key] = c
            elif isinstance(a_dict[key], list):
                a_key = {list(k.keys())[0]: list(k.values())[0] for k in a_dict[key]}
                b_key = {list(k.keys())[0]: list(k.values())[0] for k in b_dict[key]}
                for _k in list(b_key.keys()):
                    a_key[_k] = b_key.get(_k)
                r = []
                for _k in list(a_key.keys()):
                    r.append({_k: a_key.get(_k)})
                re[key] = r
            else:
                # 非字典类型则覆盖
                re[key] = b_dict[key]
        elif key in a_dict:
            re[key] = a_dict[key]
        elif key in b_dict:
            re[key] = b_dict[key]
    return re


def merge_list(ml):
    """
    list字典合并
    :param ml:
    :return:
    example：
    a = {'HouYeZiBan-Z': {'aoxian': 0.0118, 'guaca': 0.1205}}
    b = {'HouMen-Z': {'guaca': 0.0505}, 'HouYeZiBan-Z': {'guaca': 0.0003, 'aoxian': 0.0047}}
    c = [a,b]
    merge_list(c)
    output：
    {'HouYeZiBan-Z': {'aoxian': 0.0047, 'guaca': 0.0003}, 'HouMen-Z': {'guaca': 0.0505}}
    """
    if len(ml) < 1:
        return None
    first = ml[0]
    if len(ml) > 1:
        for i in range(1, len(ml)):
            first = merge(first,ml[i])
    return first


def merge_dicts(d1, d2):
    res = d1.copy()
    for k, v in d2.items():
        if k in res and isinstance(res[k], dict) and isinstance(v, dict):
            res[k] = merge_dicts(res[k], v)
        else:
            res[k] = v
    return res
