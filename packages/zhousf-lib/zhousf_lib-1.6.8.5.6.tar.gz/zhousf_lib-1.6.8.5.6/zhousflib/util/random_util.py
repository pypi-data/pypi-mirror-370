# -*- coding:utf-8 -*-
# Author:      zhousf
# Description:  随机数
import random


def rand(digits=3):
    """
    生成随机数
    :param digits: 随机数位数
    digits=3则生成范围[100,999]
    digits=4则生成范围[1000,9999]
    :return:
    """
    if digits < 1:
        return 0
    assert isinstance(digits, int)
    start = pow(10, digits - 1)
    end = pow(10, digits) - 1
    return random.randint(start, end)


if __name__ == '__main__':
    print(rand(digits=3))
    pass
