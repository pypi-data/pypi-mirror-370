# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:
import sys
import logging
from pathlib import Path
from types import FrameType
from typing import cast
"""

from zhousflib.web.fastapi.log import Logger
from configure import LogDir

Loggers = Logger(LogDir.joinpath("service").joinpath("log.txt"))
logger = Loggers.logger

"""


class Logger:

    def __init__(self, log_file: Path, rotation="5000KB", retention="7 days"):
        log_dir = log_file.parent
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
        from loguru import logger as log
        self.logger = log
        # 清空所有设置
        self.logger.remove()
        self.logger.add(sys.stdout,
                        format="<green>{time:YYYYMMDD HH:mm:ss}</green> | "  # 颜色>时间
                               "{process.name} | "  # 进程名
                               "{thread.name} | "  # 进程名
                               "<cyan>{module}</cyan>.<cyan>{function}</cyan>"  # 模块名.方法名
                               ":<cyan>{line}</cyan> | "  # 行号
                               "<level>{level}</level>: "  # 等级
                               "<level>{message}</level>",  # 日志内容
                        )
        self.logger.add(
            sink=log_file,
            format="<green>{time:YYYYMMDD HH:mm:ss}</green> | "  # 颜色>时间
                   "{process.name} | "  # 进程名
                   "{thread.name} | "  # 进程名
                   "<cyan>{module}</cyan>.<cyan>{function}</cyan>"  # 模块名.方法名
                   ":<cyan>{line}</cyan> | "  # 行号
                   "<level>{level}</level>: "  # 等级
                   "<level>{message}</level>",
            serialize=False,
            encoding="utf-8",
            enqueue=True,  # 异步写入
            rotation=rotation,  # 切割
            retention=retention,  # 设置历史保留时长
            backtrace=True,  # 回溯
            diagnose=False,  # 诊断
            compression="zip"  # 文件压缩
        )

    def init_config(self):
        logger_names = ("uvicorn.asgi", "uvicorn.access", "uvicorn.error", "uvicorn",
                        "gunicorn", "gunicorn.access", "gunicorn.error")
        logging.getLogger().handlers = [InterceptHandler(self.logger)]
        for logger_name in logger_names:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.propagate = False
            logging_logger.handlers = [InterceptHandler(self.logger)]

    def get_logger(self):
        return self.logger


class InterceptHandler(logging.Handler):

    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        # Get corresponding Loguru level if it exists
        try:
            level = self.logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1

        self.logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage(),
        )

