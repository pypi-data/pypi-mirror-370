# -*- coding:utf-8 -*-
# Author:      zhousf
# File:        json_util.py
# Description:
import json


def class_to_json(class_obj):
    """
    对象转成json字典
    :param class_obj: 对象
    :return: json字典字符串
    """
    return json.dumps(class_obj, default=lambda obj: obj.__dict__, sort_keys=True, indent=4)


def dict_to_json(dic):
    """
    字典转成json
    :param dic: 字典
    :return:
    """
    return json.dumps(dic, sort_keys=True, indent=4)


def json_str_to_class(json_str, object_hook):
    """
    json字符串转成对象
    :param json_str: json字符串
    :param object_hook: 回调函数
    :return:
    """
    return json.loads(json_str, object_hook=object_hook)


def write_dict_into_json_file(a_dict, json_file, encoding="utf-8"):
    """
    将字典写入json文件中
    :param a_dict: 字典
    :param json_file: json文件
    :param encoding:
    :return:
    """
    with open(json_file, 'w', encoding=encoding) as f:
        json.dump(a_dict, f, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))


def write_obj_into_json_file(obj, json_file):
    """
    将对象写入json文件中
    :param obj: 对象
    :param json_file: json文件
    :return:
    """
    a_dict = class_to_json(obj)
    if not isinstance(a_dict, dict):
        a_dict = eval(a_dict)
    write_dict_into_json_file(a_dict, json_file)


def load_obj_from_json_file(obj, json_file, encoding="utf-8"):
    """
    json文件转成对象
    :param obj:
    :param json_file:
    :param encoding:
    :return:
    """
    with open(json_file, 'r', encoding=encoding) as f:
        content = f.read()
        if content is not None and content.strip() != '':
            obj.__dict__ = json.loads(s=content)
            return obj
    return None


def load_dict_from_json_file(json_file, encoding="utf-8"):
    """
    json文件转成字典
    :param json_file:
    :param encoding:
    :return: dict
    """
    with open(json_file, 'r', encoding=encoding) as f:
        content = f.read()
        if content is not None and content.strip() != '':
            return json.loads(s=content)
    return None


def sort(json_or_dict):
    """
    排序：对key排序
    :param json_or_dict: {'后门壳（左）': ['刮擦'], '前门壳（左）': ['撕裂', '刮擦']}
    :return: {'前门壳（左）': ['刮擦', '撕裂'], '后门壳（左）': ['刮擦']}
    """
    json_or_dict = json.loads(json.dumps(json_or_dict, sort_keys=True, ensure_ascii=False))
    for k in json_or_dict:
        if isinstance(json_or_dict[k], list):
            if json_or_dict[k] and isinstance(json_or_dict[k][0], dict):
                for index in range(0, len(json_or_dict[k])):
                    json_or_dict[k][index] = sorted(json_or_dict[k][index].items(), key=lambda x: x[0], reverse=True)
                json_or_dict[k] = sorted(json_or_dict[k], key=lambda x: x[0])

            else:
                json_or_dict[k] = sorted(json_or_dict[k])
    return json_or_dict


if __name__ == '__main__':
    d = {'far': '', 'middle': '/media/ubuntu/b8f80802-d95a-41c3-b157-6f4e34967425/workspace/AI_TEST/damage/2018071802/middle.jpg', 'near': '', 'code': '0000', 'message': 'success', 'result': ''}
    write_dict_into_json_file(d, 't.json')



