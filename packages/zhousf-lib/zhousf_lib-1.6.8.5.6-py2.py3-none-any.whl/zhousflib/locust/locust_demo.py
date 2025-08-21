# -*- coding:utf-8 -*-
# Author:  zhousf
# Description: 并发测试工具
# pip install locust
import os
import time

from locust import HttpUser, task, TaskSet


HOST = "http://127.0.0.1:5000"
API = "/api/demo"
TEST_NAME = "api测试"
TEST_IMAGE_PATH = r"/Users/zhousf/Desktop/tmp/1.png"


class TestTask(TaskSet):

    def on_start(self):
        print("********** 测试开始 **********")

    @task
    def run_test(self):
        client = "user"
        req_id = str(time.time())
        params = {
            "client": client,
            "reqId": req_id
        }
        files = [
            ("images", open(TEST_IMAGE_PATH, 'rb'))
        ]
        with self.client.request(method="post", url="{0}/{1}".format(HOST, API), data=params,
                                 files=files, timeout=10, name=TEST_NAME,
                                 catch_response=True) as response:
            data = response.json()
            code = data.get("status", 408)
            if code == 200:
                print("请求成功", response.text)
                response.success()
            else:
                print("请求失败：{0}".format(response.text))
                response.failure(response.text)

    def on_stop(self):
        print("********** 测试结束 **********")


class User(HttpUser):
    tasks = [TestTask]
    host = HOST


if __name__ == '__main__':
    os.system("locust -f {0} --web-host=127.0.0.1".format(os.path.basename(__file__)))
