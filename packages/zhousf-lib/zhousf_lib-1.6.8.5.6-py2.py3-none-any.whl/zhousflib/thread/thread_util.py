# -*- coding:utf-8 -*-
# Author:      zhousf
# Description:
import threading
import time


class MultiThread(threading.Thread):
    """
    多线程
    """
    def __init__(self, name, func, func_arg=None, thread_lock=None):
        """
        :param name: 线程名
        :param func: 执行函数
        :param thread_lock: threading.Lock() 默认异步
        """
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.thread_lock = thread_lock
        self.func_arg = func_arg
        self.result = None

    def run(self):
        if self.thread_lock:
            # 可选的timeout参数不填时将一直阻塞直到获得锁定
            # 成功获得锁定后返回True，超时返回False
            self.thread_lock.acquire()
        self.result = self.func(self.name, self.func_arg)
        if self.thread_lock:
            self.thread_lock.release()

    def get_result(self):
        try:
            return self.result
        except Exception as e:
            print(e)
            return None


def my_func(thread_name, func_arg):
    counter = 3
    while counter:
        time.sleep(1)
        print("{0}: {1}".format(thread_name, func_arg))
        counter -= 1
    return thread_name


def test_sync():
    """
    同步
    """
    thread_lock = threading.Lock()
    thread_1 = MultiThread(name="thread_1", func=my_func, thread_lock=thread_lock)
    thread_2 = MultiThread(name="thread_2", func=my_func, thread_lock=thread_lock)
    thread_1.start()
    thread_2.start()
    # 等待所有线程完成
    threads = [thread_1, thread_2]
    for t in threads:
        t.join()
    print("Exiting Main Thread")


def test_async():
    """
    异步
    """
    thread_1 = MultiThread(name="thread_1", func=my_func, func_arg="dddd1", thread_lock=None)
    thread_2 = MultiThread(name="thread_2", func=my_func, func_arg="32333", thread_lock=None)
    thread_1.start()
    thread_2.start()
    # 等待所有线程完成
    threads = [thread_1, thread_2]
    for t in threads:
        t.join()
    for t in threads:
        print(t.get_result())
    print("Exiting Main Thread")


if __name__ == "__main__":
    test_async()
    # test_sync()
    pass
