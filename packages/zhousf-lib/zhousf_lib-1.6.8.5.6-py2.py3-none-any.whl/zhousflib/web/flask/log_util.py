# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function: 日志工具
import os
import time
import codecs

import logging.handlers
from logging.handlers import BaseRotatingHandler
from flask.logging import default_handler
from flask import current_app


# noinspection PyPep8Naming
class MultiProcessSafeDailyRotatingFileHandler(BaseRotatingHandler):
    """Similar with `logging.TimedRotatingFileHandler`, while this one is
    - Multi process safe
    - Rotate at midnight only
    - Utc not supported
    日志handler：按每天分割
    """

    def __init__(self, filename, encoding=None, delay=False, utc=False, **kwargs):
        self.utc = utc
        self.suffix = "%Y-%m-%d.txt"
        self.baseFilename = filename
        self.currentFileName = self._compute_fn()
        BaseRotatingHandler.__init__(self, filename, 'a', encoding, delay)

    def shouldRollover(self, record):
        if self.currentFileName != self._compute_fn():
            return True
        return False

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        self.currentFileName = self._compute_fn()

    def _compute_fn(self):
        return self.baseFilename + "-" + time.strftime(self.suffix, time.localtime())

    def _open(self):
        if self.encoding is None:
            stream = open(self.currentFileName, self.mode)
        else:
            stream = codecs.open(self.currentFileName, self.mode, self.encoding)
        # simulate file name structure of `logging.TimedRotatingFileHandler`
        if os.path.exists(self.baseFilename):
            try:
                os.remove(self.baseFilename)
            except OSError as e:
                print(e)
        try:
            os.symlink(self.currentFileName, self.baseFilename)
        except OSError as e:
            print(e)
        return stream


"""
日志级别
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0
"""


def init_log(app, log_dir):
    app.logger.removeHandler(default_handler)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file_str = os.path.join(log_dir, 'log')
    time_handler = MultiProcessSafeDailyRotatingFileHandler(log_file_str, encoding='utf-8')
    logging_format = logging.Formatter(
        '=>%(asctime)s - [%(levelname)s]\n%(message)s')
    # logging_format = logging.Formatter(
    #     "%(asctime)s-[%(threadName)s-%(thread)d]-%(levelname)s-[%(filename)s:%(lineno)d]\n%(message)s")
    logging.basicConfig(level=logging.DEBUG)
    time_handler.setFormatter(logging_format)
    app.logger.addHandler(time_handler)


def error(msg, *args, **kwargs):
    current_app.logger.error(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    current_app.logger.warning(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    current_app.logger.info(msg, *args, **kwargs)


def debug(msg, *args, **kwargs):
    current_app.logger.debug(msg, *args, **kwargs)


