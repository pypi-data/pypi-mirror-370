# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function: 业务日志记录
import time
from pathlib import Path

from prettytable import PrettyTable

from zhousflib.time import time_util


def get_dir_path(dir_path, client=None, req_id=None, make_dirs=True) -> Path:
    """
    获取业务处理的目录
    :param dir_path: 插件模块的文件处理根目录
    :param client: 调用方名称，用于区分不同的调用方
    :param req_id: 每次请求的ID，每次请求都是唯一的
    :param make_dirs: 是否自动创建目录
    :return:
    """
    """
    目录层级：根目录/调用方/日期/req_id
    """
    if isinstance(dir_path, str):
        dir_path = Path(dir_path)
    if client is not None:
        dir_path = dir_path.joinpath(client.upper())
    dir_path = dir_path.joinpath(time_util.get_y_m_d())
    if req_id is not None:
        dir_path = dir_path.joinpath(req_id)
    if make_dirs:
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
    return dir_path


class Logger(object):
    def __init__(self, log_dir: Path = None, g=None):
        """
        数据链
        :param log_dir: 日志目录，默认空
        :param g: flask.g 默认空
        """
        self.log_dir = log_dir
        day_time = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time())) + '\n'
        if g is not None:
            if hasattr(g, "log"):
                day_time = g.log
            g.logger = self
        # 日志信息-详细
        self.log_txt = day_time
        # 日志信息-仅标题
        self.__log_txt_level = []
        # 耗时
        self.elapsed_time_dict = {}
        self.title_first("日志路径")
        self.log(log_dir)

    def elapsed_time(self, k: str, start: float, end: float):
        """
        耗时记录
        :param k:
        :param start:
        :param end:
        :return:
        """
        if k in self.elapsed_time_dict:
            self.elapsed_time_dict[k] += abs(end - start)
        else:
            self.elapsed_time_dict[k] = abs(end - start)

    def print_log(self):
        print(self.log_txt)
        if len(self.elapsed_time_dict) > 0:
            table = PrettyTable()
            table.field_names = self.elapsed_time_dict.keys()
            table.add_row([self.elapsed_time_dict.get(i) for i in self.elapsed_time_dict.keys()])
            print(table)

    @property
    def level_log_first(self):
        txt = [title for (level, title) in self.__log_txt_level if level <= 1]
        return "\n".join(txt)

    @property
    def level_log_second(self):
        txt = [title for (level, title) in self.__log_txt_level if level <= 2]
        return "\n".join(txt)

    @property
    def level_log_third(self):
        txt = [title for (level, title) in self.__log_txt_level if level <= 3]
        return "\n".join(txt)

    def title_first(self, title):
        title = "------------ {0} ------------".format(title)
        self.log_txt = '{0}{1}\n'.format(self.log_txt, title)
        self.__log_txt_level.append((1, title))
        return self

    def title_second(self, title):
        title = "****** {0} ******".format(title)
        self.log_txt = '{0}{1}\n'.format(self.log_txt, title)
        self.__log_txt_level.append((2, title))
        return self

    def title_third(self, title):
        title = "【 {0} 】".format(title)
        self.log_txt = '{0}{1}\n'.format(self.log_txt, title)
        self.__log_txt_level.append((3, title))
        return self

    def log(self, msg):
        """
        记录日志
        :param msg: 信息
        :return:
        """
        if msg is not None:
            self.log_txt = '{0}{1}\n'.format(self.log_txt, msg)
        return self

    # noinspection PyBroadException
    def save_log(self):
        """
        保存日志文件
        :return:
        """
        if self.log_dir is None:
            return
        log_file = "{0}/log.txt".format(self.log_dir)
        log_file = log_file.replace("\\", "/")
        day_time = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time())) + '\n'
        self.log_txt = '{0}\n{1}'.format(self.log_txt, day_time)
        try:
            with open(log_file, "a+", encoding="utf-8") as f:
                f.write(self.log_txt)
        except Exception as e:
            print(e)
            pass
