# -*- coding:utf-8 -*-
# Author:  zhousf
# Description:
import re


def is_number(string: str) -> bool:
    """
    是否数值，包含int、float、double
    :param string:
    :return:
    """
    try:
        float(string)
        return True
    except ValueError:
        return False


def is_greater_than_number(string1: str, string2: str) -> bool:
    """
    string1数值大于string2数值
    :param string1: "12"
    :param string2: "12.0"
    :return:
    """
    if is_number(string1) and is_number(string2):
        if float(string1) > float(string2):
            return True
    if string1 == string2:
        return True
    return False


def is_less_than_number(string1: str, string2: str) -> bool:
    """
    string1数值小于string2数值
    :param string1: "12"
    :param string2: "12.0"
    :return:
    """
    if is_number(string1) and is_number(string2):
        if float(string1) < float(string2):
            return True
    if string1 == string2:
        return True
    return False


def is_equal_number(string1: str, string2: str) -> bool:
    """
    数值是否相等
    :param string1: "12"
    :param string2: "12.0"
    :return:
    """
    if is_number(string1) and is_number(string2):
        if float(string1) == float(string2):
            return True
    if string1 == string2:
        return True
    return False


def contains(string: str, what: list) -> bool:
    for s in what:
        if string.find(s) > -1:
            return True
    return False


def is_empty(obj) -> bool:
    str_obj = str(obj)
    if str_obj is None or str_obj == 'None':
        return True
    if str_obj.strip() == '':
        return True
    return False


def is_not_empty(obj) -> bool:
    str_obj = str(obj)
    if str_obj is None or str_obj == 'None':
        return False
    if str_obj.strip() == '':
        return False
    return True


def contain(obj, what) -> bool:
    str_obj = str(obj)
    str_what = str(what)
    if is_not_empty(str_obj) and is_not_empty(str_what):
        if str_obj.find(str_what) >= 0:
            return True
    return False


def not_contain(obj, what) -> bool:
    str_obj = str(obj)
    str_what = str(what)
    if is_not_empty(str_obj) and is_not_empty(str_what):
        if str_obj.find(str_what) >= 0:
            return False
    return True


def right_just(obj, length, fill_char=' ') -> str:
    """
    左补齐（右调整）
    :param obj: abc
    :param length: 5
    :param fill_char:
    :return: '  abc'
    """
    if not isinstance(obj, str):
        obj = str(obj)
    return obj.rjust(length, fill_char)


def left_just(obj, length, fill_char=' ') -> str:
    """
    右补齐（左调整）
    :param obj: abc
    :param length: 5
    :param fill_char:
    :return: 'abc  '
    """
    if not isinstance(obj, str):
        obj = str(obj)
    return obj.ljust(length, fill_char)


def center_just(obj, length) -> str:
    """
    中间补齐（两端调整）
    :param obj: abc
    :param length: 5
    :return: ' abc '
    """
    if not isinstance(obj, str):
        obj = str(obj)
    return obj.center(length)


def only_digit_letter_chinese(string) -> bool:
    """
    同时包含中文 & (数字 or 字母)
    :param string:
    :return:
    """
    # 提取数字
    match_digit = re.sub(u"([^\u0030-\u0039])", "", string)
    # 提取大小写字母
    match_letter = re.sub(u"([^\u0041-\u005a\u0061-\u007a])", "", string)
    # 提取汉字
    match_chinese = re.sub(u"([^\u4e00-\u9fa5])", "", string)
    if len(match_chinese) == 0:
        return False
    if len(match_digit) + len(match_letter) == 0:
        return False
    return (len(match_chinese) + len(match_digit) + len(match_letter)) == len(string)


def only_digit_letter(string) -> bool:
    """
    同时包含数字和字母
    :param string:
    :return:
    """
    # 提取数字
    match_digit = re.sub(u"([^\u0030-\u0039])", "", string)
    # 提取大小写字母
    match_letter = re.sub(u"([^\u0041-\u005a\u0061-\u007a])", "", string)
    if len(match_digit) == 0 or len(match_letter) == 0:
        return False
    return (len(match_digit) + len(match_letter)) == len(string)


def digit_or_letter(string) -> bool:
    """
    包含数字或字母
    :param string:
    :return:
    """
    # 提取数字
    match_digit = re.sub(u"([^\u0030-\u0039])", "", string)
    # 提取大小写字母
    match_letter = re.sub(u"([^\u0041-\u005a\u0061-\u007a])", "", string)
    return (len(match_digit) + len(match_letter)) == len(string)


def only_digit(string) -> bool:
    """
    只包含数字
    :param string:
    :return:
    """
    return string.isdigit()


def only_letter(string) -> bool:
    """
    只包含字母
    :param string:
    :return:
    """
    # 提取大小写字母
    match_string = re.sub(u"([^\u0041-\u005a\u0061-\u007a])", "", string)
    return len(match_string) == len(string)