# -*- coding:utf-8 -*-
# Author:      zhousf
# File:        permission_util.py
# Description: 动态权限管理
import os
import json


class DynamicPermission(object):

    def __init__(self, visit_file):
        """

        :param visit_file: json file
        """
        self.visit_file = visit_file
        if self.visit_file is None or not os.path.exists(self.visit_file):
            raise Exception("visit_file is not exist.")
        self.visit_list = self.load()

    def load(self):
        return self.__load_dict_from_json_file(self.visit_file)

    def update(self):
        self.visit_list = self.load()

    def check_visit(self, visit):
        if visit in self.visit_list.keys():
            return True
        tmp = self.load()
        if visit in tmp.keys():
            self.update()
            return True
        return False

    def fetch_api_secret(self, req_code):
        return self.visit_list.get(req_code)

    @staticmethod
    def __load_dict_from_json_file(json_file):
        """
        json文件转成字典
        :param json_file:
        :return: dict
        """
        with open(json_file, 'r') as f:
            content = f.read()
            if content is not None and content.strip() != '':
                return json.loads(s=content)
        return None
