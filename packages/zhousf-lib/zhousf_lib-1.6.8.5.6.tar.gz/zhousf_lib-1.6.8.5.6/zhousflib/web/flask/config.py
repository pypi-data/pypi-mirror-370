# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2021/8/16
# @Function: 环境配置
import os
from enum import Enum, unique


@unique
class Environment(Enum):
    Development = "Development"  # 开发环境
    Testing = "Testing"  # 测试环境
    PreProduction = "PreProduction"  # 预生产环境
    Production = "Production"  # 生产环境


class CoreConfig(object):
    DEBUG = False
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False
    JSONIFY_MIMETYPE = 'application/json;charset=utf-8'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # PROJECT_DIR = os.path.dirname(__file__)
    # PID_FILE = "{0}/pid.txt".format(PROJECT_DIR)
    # VISIT_JSON_FILE = "{0}/visit-list.json".format(PROJECT_DIR)
    GPU_ASSIGNED = "0"
    HOST = "0.0.0.0"
    PORT = 8090
    LOG_BUSINESS_DIR = None
    LOG_SERVICE_DIR = None
    LOG_GUNICORN_DIR = None
    ALLOWED_FILE_TYPE = ["jpg", "JPG", "jpeg", "JPEG", "png", "PNG","bmp"]
    CHECK_PERMISSION = True

    @staticmethod
    def has_pid_file(obj):
        return hasattr(obj, "PID_FILE")

    @staticmethod
    def read_txt(txt_file):
        """
        读取txt文档并返回list
        :param txt_file:
        :return:
        """
        data = []
        if not os.path.exists(txt_file):
            return data
        with open(txt_file) as f:
            lines = f.readlines()
            for line in lines:
                line = line.replace("\n", "")
                if line.strip() != "":
                    data.append(line)
        return data

    def shutdown(self):
        if hasattr(self, "PID_FILE"):
            if not os.path.exists(self.PID_FILE):
                return
            process = self.read_txt(self.PID_FILE)
            print(process)
            for pid in process:
                if os.name == 'nt':
                    cmd = 'taskkill /pid ' + str(pid) + ' /f'
                    try:
                        os.system(cmd)
                        print(pid, "killed")
                    except Exception as e:
                        print(e)
                elif os.name == 'posix':
                    try:
                        command = "kill -9 {0}".format(pid)
                        os.system(command)
                        print(pid, "killed")
                    except Exception as e:
                        print(e)
            os.remove(self.PID_FILE)


def assign_env(cf, env, log_dir=None):
    """
    指定环境并创建日志目录
    :param cf: 配置文件
    :param env: 环境
    :param log_dir: 默认空，日志目录默认在工程根目录下创建
    """
    # 指定环境
    if env == Environment.Production:
        env_instance = cf.Production()
        env_instance.ENVIRONMENT = Environment.Production
    elif env == Environment.PreProduction:
        env_instance = cf.PreProduction()
        env_instance.ENVIRONMENT = Environment.PreProduction
    elif env == Environment.Testing:
        env_instance = cf.Testing()
        env_instance.ENVIRONMENT = Environment.Testing
    else:
        env_instance = cf.Development()
        env_instance.ENVIRONMENT = Environment.Development
    if env_instance.PROJECT_DIR is None:
        # 在模块的根目录下创建日志目录
        log_root_dir = "{0}/log".format(os.path.dirname(__file__))
    else:
        # 在工程的根目录下创建日志目录
        log_root_dir = "{0}/log".format(env_instance.PROJECT_DIR)
    # 创建日志目录
    if log_dir is not None:
        log_root_dir = log_dir
    log_app_dir = "{0}".format(log_root_dir)
    env_instance.LOG_BUSINESS_DIR = "{0}/business".format(log_app_dir)
    env_instance.LOG_SERVICE_DIR = "{0}/service".format(log_app_dir)
    env_instance.LOG_GUNICORN_DIR = "{0}/gunicorn".format(log_app_dir)
    if not os.path.exists(env_instance.LOG_BUSINESS_DIR):
        os.makedirs(env_instance.LOG_BUSINESS_DIR)
    if not os.path.exists(env_instance.LOG_SERVICE_DIR):
        os.makedirs(env_instance.LOG_SERVICE_DIR)
    if not os.path.exists(env_instance.LOG_GUNICORN_DIR):
        os.makedirs(env_instance.LOG_GUNICORN_DIR)
    return env_instance



