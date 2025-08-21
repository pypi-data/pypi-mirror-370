# -*- coding:utf-8 -*-
# Author:      zhousf
# File:        interceptor_util.py
# Description:  拦截器
import functools


def intercept(before=None, after=None):
    """
    拦截器
    :param before: 过滤器
    :param after: 过滤器
    def before(*args):
        if args[0] == "0":
            return True, '拦截'
        return False, '不拦截'
    :return:
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*chain, **kw):
            if before is not None:
                result_before = before(chain)
                if isinstance(result_before, tuple):
                    need_intercept, msg = result_before
                else:
                    need_intercept = result_before
                    msg = "interceptor"
                if need_intercept:
                    return msg
                result = func(msg, **kw)
            else:
                result = func(chain, **kw)
            return result if after is None else after(result)
        return wrapper

    return decorator


def aop(before=None, after=None):
    def run(run_func, *args, **kw):
        func_ = args[0]
        if len(args) > 1:
            params = args[1:]
            if run_func is not None:
                if len(kw) > 0:
                    run_func(func_, *params, **kw)
                else:
                    run_func(func_, *params)
        else:
            if run_func is not None:
                if len(kw) > 0:
                    run_func(func_, **kw)
                else:
                    run_func(func_)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            run(before, *args, **kw)
            run(func, *args, **kw)
            run(after, *args, **kw)
        return wrapper

    return decorator


"""
if __name__ == "__main__":
    class Demo:

        def __init__(self):
            pass
        def before(self, msg):
            print(f"before {msg}")
            msg[0] += "_before"
            msg[1] += 1

        def after(self, msg):
            print(f"after {msg}")
            msg[0] += "_after"
            msg[1] += 1

        @aop(before=before, after=after)
        def test(self, msg):
            print(f"test {msg}")
            msg[0] += "_test"
            msg[1] += 1


    parmas = ["hello", 1]
    Demo().test(parmas)
    print(parmas)
"""


