# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function: Web服务响应实体类
from flask import jsonify


class Response(object):
    log_msg = ""

    def __init__(self, status: int = 200, result="", message: str = ""):
        """
        :param status: 状态
        :param result: 业务处理结果
        :param message: 信息
        """
        self.status = status
        self.message = message if message is not None else message
        self.result = result if result is not None else result

    def log(self, msg):
        """
        记录日志
        :param msg: 日志信息
        :return:
        """
        self.log_msg += "{0}\n".format(msg)


def failed_tip(status: int = 408, result="", msg: str = "failed"):
    """
    业务处理失败
    :param status: 状态
    :param result: 业务处理结果
    :param msg: 信息
    :return:
    """
    info = Response(status=status, result=result, message=msg)
    return jsonify(info.__dict__)


def success_tip(status: int = 200, result="", msg: str = "successful"):
    """
    业务处理成功
    :param status: 状态
    :param result: 业务处理结果
    :param msg: 信息
    :return:
    """
    info = Response(status=status, result=result, message=msg)
    return jsonify(info.__dict__)
