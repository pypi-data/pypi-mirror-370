# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:
"""
pip install oss2
"""
import os

import oss2
from loguru import logger
from zhousflib.time import time_cost
from zhousflib.util import list_util
from zhousflib.thread.thread_util import MultiThread


class HandleOSS(object):
    def __init__(self, key_id, key_secret, endpoint, bucket):
        """
        :param key_id:
        :param key_secret:
        :param endpoint: 例如：https://oss-cn-hangzhou.aliyuncs.com
        :param bucket: bucket名字，例如：product-ai
        """
        self.auth = oss2.Auth(key_id, key_secret)
        self.bucket = oss2.Bucket(self.auth, endpoint, bucket)

    @time_cost(logger)
    def download_file(self, oss_file, save_dir):
        file_name = oss_file.split('/')[-1]
        save_path = os.path.join(str(save_dir), file_name)
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        result = self.bucket.get_object_to_file(oss_file, str(save_path))
        if result.status == 200:
            logger.info("download success: {0}".format(save_path))
        else:
            logger.info(result.status)

    @time_cost(logger)
    def download_files(self, oss_dir, save_dir):
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        obj = oss2.ObjectIterator(self.bucket, prefix=oss_dir)
        total = 0
        for i in obj:
            if i.key.endswith(os.sep):
                continue
            if str(i.key).find(".") == -1:
                continue
            total += 1
            self.download_file(i.key, save_dir)
        logger.info("total: {}".format(total))

    @time_cost(logger)
    def download_files_multithread(self, oss_dir, save_dir, thread=2):
        total = 0
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        obj = oss2.ObjectIterator(self.bucket, prefix=oss_dir)
        task = []
        for i in obj:
            if i.key.endswith(os.sep):
                continue
            if str(i.key).find(".") == -1:
                continue
            total += 1
            task.append((i.key, save_dir))
        task_group = list_util.chunk_list(task, chunk_size=thread)
        threads = []
        for i, task in enumerate(task_group):
            thread = MultiThread(name="thread_{0}".format(i), func=self.__download, func_arg=task, thread_lock=None)
            thread.start()
            threads.append(thread)
        for t in threads:
            t.join()
        logger.info("total: {}".format(total))
        return total

    def __download(self, thread_name, func_arg):
        for task in func_arg:
            self.download_file(task[0], task[1])
        return thread_name






