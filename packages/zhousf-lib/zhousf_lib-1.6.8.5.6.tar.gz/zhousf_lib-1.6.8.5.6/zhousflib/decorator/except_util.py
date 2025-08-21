# -*- coding:utf-8 -*-
# Author:      zhousf
# File:        except_util.py
# Description: 非中断流程异常处理：防止函数因异常中断导致后续流程不执行
import warnings
import traceback


def except_handler(function):
    def catch_except(*args, **key_args):
        try:
            return function(*args, **key_args)
        except Exception as e:
            warnings.warn('{0}: {1}'.format(function.__name__, traceback.print_exc()))

    return catch_except


