# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:
from pathlib import Path

import requests
from zhousflib.util import list_util
from zhousflib.thread.thread_util import MultiThread


# noinspection PyBroadException
class DownloadRequests:

    def __init__(self):
        self.task: list[[str, Path, int]] = []

    @staticmethod
    def get_file(url: str, save_file: Path, timeout: int = 10):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code != 200:
                return False, "{0} {1}".format(response.reason, url)
            else:
                with save_file.open("wb") as file:
                    file.write(response.content)
                return True, url
        except Exception as e:
            return False, "{0} {1}".format(e, url)

    def add(self, url: str, save_file: Path, timeout: int = 10):
        self.task.append((url, save_file, timeout))

    @staticmethod
    def __get_files(thread_name, func_arg):
        file_list = func_arg
        result = []
        if len(file_list) > 0:
            for i, item in enumerate(file_list):
                url, file, timeout = item
                try:
                    response = requests.get(url, timeout=timeout)
                    if response.status_code != 200:
                        result.append((False, "{0} {1} {2}".format(file.name, response.reason, response.status_code)))
                        continue
                    with open(str(file), "wb") as file:
                        file.write(response.content)
                    result.append((True, file))
                except Exception as e:
                    result.append((False, "{0} {1}".format(file.name, e)))
        return result

    def get_file_threads(self, threads_num=8):
        threads = []
        task_list = list_util.split_list(self.task, split_size=threads_num)
        for i, item in enumerate(task_list):
            thread = MultiThread(name="thread_{0}".format(i), func=self.__get_files, func_arg=item, thread_lock=None)
            thread.start()
            threads.append(thread)
        for t in threads:
            t.join()
        self.task.clear()
        result = []
        for thread in threads:
            result.extend(thread.get_result())
        return result

