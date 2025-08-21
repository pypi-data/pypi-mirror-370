# -*- coding:utf-8 -*-
# Author:      zhousf
# Description:  批量异步下载工具类
"""
pip install grequests
"""
from pathlib import Path

import grequests
from requests import Response


class DownloadBatch(object):

    def __init__(self, concurrent=True):
        """
        批量下载文件工具类
        :param concurrent: True并行  False串行
        """
        self.req_list = []
        self.consume_time = 0
        self.file_names = []
        self.task_num = 0
        self.concurrent = concurrent

    @staticmethod
    def exception_handler(request, exception):
        r = Response()
        r.status_code = 408
        r.reason = "download failed: {0}".format(exception)
        return r

    def add(self, file_name, url, timeout=20.0):
        if url is None or file_name is None:
            return False
        if file_name in self.file_names:
            return False
        self.file_names.append(file_name)
        self.req_list.append(grequests.get(url, timeout=timeout))
        return True

    def add_all(self, files):
        """
        :param files: [{"name": "1.jpg", "url": ""}]
        :return:
        """
        for file in files:
            name = file.get("name")
            url = file.get("url")
            if url is None or name is None:
                continue
            timeout = file.get("timeout", default=20.0)
            self.req_list.append(grequests.get(url, timeout=timeout))
            self.file_names.append(name)

    def run(self, save_dir: Path):
        download_result = []
        try:
            if not save_dir.exists():
                save_dir.mkdir(parents=True)
            self.task_num = len(self.req_list)
            if self.task_num == 0:
                return download_result
            size = self.task_num if self.concurrent else 1
            responses = grequests.map(requests=self.req_list, size=size, exception_handler=self.exception_handler)
            for i in range(0, len(responses)):
                response = responses[i]
                try:
                    save_file = str(save_dir.joinpath(self.file_names[i]))
                    # target_type = self.file_names[i].split(".")[-1]
                    # if 'Content-Type' in response.headers:
                    #     content_type = response.headers['Content-Type']
                    #     if target_type in ["jpg", "JPG", "JPEG", "jpeg", "png", "PNG", "gif", "GIF"]:
                    #         target_type = "image"
                    #     if content_type.find(target_type) < 0:
                    #         download_result.append((False,
                    #                                 "The file type is {0}, but {1} is expected".format(
                    #                                                    content_type,
                    #                                                    target_type),
                    #                                 self.file_names[i],
                    #                                 self.req_list[i].url))
                    #         continue
                    if response.status_code != 200:
                        download_result.append((
                            False,
                            "{0} {1} {2}".format(self.file_names[i], response.reason, response.status_code),
                            self.file_names[i],
                            self.req_list[i].url
                        ))
                        continue
                    # 当信息流小于100字节，则不是文件
                    if len(response.text) <= 100:
                        download_result.append((
                            False,
                            "{0} {1} {2}".format(self.file_names[i], response.reason, response.status_code),
                            self.file_names[i],
                            self.req_list[i].url
                        ))
                        continue
                    with open(save_file, "wb") as f:
                        f.write(response.content)
                        download_result.append((
                            True,
                            save_file,
                            self.file_names[i],
                            self.req_list[i].url
                        ))
                except Exception as ex:
                    download_result.append((
                        False,
                        "{0} {1} {2}".format(self.file_names[i], response.reason, response.status_code),
                        self.file_names[i],
                        self.req_list[i].url
                    ))
                    continue
        finally:
            self.req_list.clear()
            self.task_num = 0
            self.file_names.clear()
        return download_result

    def run_one_file(self, save_dir: Path, file_name, url, timeout=20.0):
        self.add(file_name=file_name, url=url, timeout=timeout)
        results = self.run(save_dir=save_dir)
        return results[0]


if __name__ == "__main__":
    downloader = DownloadBatch(concurrent=True)
    res = downloader.run_one_file(save_dir=Path(r"C:\Users\zhousf-a\Desktop\download"),
                                  file_name="input.zip",
                                  url="")
