# -*- coding:utf-8 -*-
# Author:      zhousf
# Description: 将整个python工程加密成so
# 1. 安装依赖库
#     pip3 --default-timeout=1000 install -U cython
#     sudo apt-get  build-dep  gcc
# 2. 工程的所有py文件的当前目录以及所有上级目录下都要有__init__.py文件，若没有请新建
# 3. 在工程根目录下或非工程目录外新建build_so目录并将project_to_so.py复制到build_so目录下
# 4. 终端中运行 python3.6 encrypt_project.py build_ext --inplace
# 5. build_so目录下会生成工程所有的so文件和资源文件

import os
import shutil
from pathlib import Path

from distutils.core import setup
from Cython.Build import cythonize

# 工程根目录
project_dir = Path(__file__).parent.parent
# 过滤目录或文件-包含的文件目录下文件不生成so
exclude_dirs_or_files = [
    "{}/venv".format(project_dir),
    "{}/.idea".format(project_dir),
    "{}/.svn".format(project_dir),
    "{}/download".format(project_dir),
    "{}/log".format(project_dir),
    "{}/pid.txt".format(project_dir),
    "{}/app.py".format(project_dir),
    "{}/config.py".format(project_dir),
    "{}/entry.py".format(project_dir),
    "{}/multi_app.py".format(project_dir),
    ]


def copy_file(project_name, file_dir, root, current_file):
    _, child_dir = root.split(project_name)
    if len(child_dir) > 0:
        target_dir = file_dir + "/" + project_name + child_dir
    else:
        target_dir = file_dir + "/" + project_name
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    shutil.copy(current_file, target_dir)


def distill_dirs_or_files(root):
    for exclude in exclude_dirs_or_files:
        if root.find(exclude) >= 0:
            return True
    return False


def main():
    project_name = os.path.basename(project_dir)
    file_dir = os.getcwd()
    build_dir = file_dir + "/build"
    # noinspection PyBroadException
    try:
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                current_file = os.path.join(root, file)
                # 过滤py编译文件
                if file.endswith(".pyc"):
                    continue
                if file.endswith(".c"):
                    continue
                # 过滤当前文件
                if current_file == __file__:
                    continue
                # 过滤build文件夹
                if root.find(build_dir) >= 0:
                    continue
                # 过滤build_so文件夹
                if root.find(file_dir) >= 0:
                    continue
                # 过滤指定目录
                if distill_dirs_or_files(root):
                    continue
                # 过滤指定文件
                if current_file in exclude_dirs_or_files:
                    continue
                # 非py文件进行复制操作
                if not file.endswith(".py"):
                    copy_file(project_name, file_dir, root, current_file)
                    continue
                setup(ext_modules=cythonize([current_file]))
                name, _ = file.split(".")
                # 删除.c文件以保证每次都进行so文件生成
                c_file = os.path.join(root, name + ".c")
                if os.path.exists(c_file):
                    os.remove(c_file)
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        print("done! Generating SO files completed.")
        print("SO dir: " + file_dir)
    except Exception:
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        print("工程的所有py文件的当前目录以及所有上级目录中都要有__init__.py文件，若没有请新建！")


main()
