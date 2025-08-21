# -*- coding:utf-8 -*-
# Author:      zhousf
# Description: 半角、全角转换

def half_to_full_char(uchar):
    """
    单个字符 半角转全角
    :param uchar:
    :return:
    """
    inside_code = ord(uchar)
    # 不是半角字符就返回原来的字符
    if inside_code < 0x0020 or inside_code > 0x7e:
        return uchar
    # 除了空格其他的全角半角的公式为: 半角 = 全角 - 0xfee0
    if inside_code == 0x0020:
        inside_code = 0x3000
    else:
        inside_code += 0xfee0
    return chr(inside_code)


def full_to_half_char(uchar):
    """
    单个字符 全角转半角
    :param uchar:
    :return:
    """
    inside_code = ord(uchar)
    if inside_code == 0x3000:
        inside_code = 0x0020
    else:
        inside_code -= 0xfee0
    # 转完之后不是半角字符返回原来的字符
    if inside_code < 0x0020 or inside_code > 0x7e:
        return uchar
    return chr(inside_code)


def is_half_number(uchar):
    """
    判断一个unicode是否是半角数字
    :param uchar:
    :return:
    """
    if u'\u0030' <= uchar <= u'\u0039':
        return True
    else:
        return False


def is_full_number(uchar):
    """
    判断一个unicode是否是全角数字
    :param uchar:
    :return:
    """
    if u'\uff10' <= uchar <= u'\uff19':
        return True
    else:
        return False


def is_half_alphabet(uchar):
    """
    判断一个unicode是否是半角英文字母
    :param uchar:
    :return:
    """
    if (u'\u0041' <= uchar <= u'\u005a') or (u'\u0061' <= uchar <= u'\u007a'):
        return True
    else:
        return False


def is_full_alphabet(uchar):
    """
    判断一个unicode是否是全角英文字母
    :param uchar:
    :return:
    """
    if (u'\uff21' <= uchar <= u'\uff3a') or (u'\uff41' <= uchar <= u'\uff5a'):
        return True
    else:
        return False


def full_to_half_str(ustring):
    """
    字符串全角转半角
    :param ustring:
    :return:
    """
    return "".join([full_to_half_char(uchar) for uchar in ustring])
