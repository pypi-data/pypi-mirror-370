# -*- coding:utf-8 -*-
# Author:  zhousf
# Description:
from concurrent.futures import ThreadPoolExecutor
import time
import threading


class ThreadPool(object):

    def __init__(self, max_workers=None):
        self.thread_pool = ThreadPoolExecutor(max_workers)
        pass

    def push(self,  fn, args):
        return self.thread_pool.submit(fn, args)

    def shutdown(self):
        self.thread_pool.shutdown()


def task(x):
    print('{0} 参数: {1}'.format(threading.current_thread().getName(), x))
    time.sleep(2)
    return x


if __name__ == '__main__':
    start = time.time()
    tp = ThreadPool(max_workers=5)
    obj_list = []
    for i in range(10):
        obj_list.append(tp.push(task, i))
    print('主线程')
    for i in obj_list:
        print(i.result())
    tp.shutdown()
    print("耗时：{0}秒".format(round(time.time() - start, 4)))

