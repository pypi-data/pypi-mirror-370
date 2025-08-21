# -*- coding:utf-8 -*-
# Author:  zhousf
# Description:
import os
import shutil
import random
from pathlib import Path

import zipfile


def unzip_file(zip_file, dst_dir):
    """
    解压文件
    :param zip_file:
    :param dst_dir:
    :return:
    """
    if not zipfile.is_zipfile(zip_file):
        return False, "It is not a zip file."
    try:
        with zipfile.ZipFile(zip_file, 'r') as f:
            for fn in f.namelist():
                try:
                    # 解决中文乱码
                    name = fn.encode('cp437').decode('utf-8', "ignore")
                except:
                    name = fn.encode('utf-8').decode('utf-8', "ignore")
                if name.startswith("__MACOSX"):
                    continue
                extracted_path = Path(f.extract(fn, dst_dir))
                extracted_path.rename(os.path.join(dst_dir, name))
            # 删除临时文件
            for b in os.listdir(dst_dir):
                current_dir = os.path.join(dst_dir, b)
                if not os.path.isdir(current_dir):
                    continue
                if len(os.listdir(current_dir)) == 0:
                    os.removedirs(current_dir)
    except Exception as ex:
        return False, ex
    return True, "Unzip file successful."


def unzip_flat_file(zip_file, dst_dir):
    """
    解压文件，平铺到dst_dir目录下
    :param zip_file:
    :param dst_dir:
    :return:
    """
    tmp_dir = dst_dir + "/tmp"
    unzip_success, tip = unzip_file(zip_file, tmp_dir)
    if not unzip_success:
        return unzip_success, tip
    try:
        for root, dirs, files in os.walk(tmp_dir):
            for f in files:
                current_file = os.path.join(root, f)
                target_file = os.path.join(dst_dir, f)
                os.rename(current_file, target_file)
    except Exception as ex:
        print(ex)
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir, ignore_errors=True)
    return True, "Unzip file successful."


def unzip_flat_file_rename(zip_file, dst_dir):
    """
    解压文件，重命名文件并平铺到dst_dir目录下(防止同名文件)
    :param zip_file:
    :param dst_dir:
    :return:
    """
    tmp_dir = dst_dir + "/tmp"
    unzip_success, tip = unzip_file(zip_file, tmp_dir)
    if not unzip_success:
        return unzip_success, tip
    try:
        for root, dirs, files in os.walk(tmp_dir):
            for f in files:
                current_file = os.path.join(root, f)
                target_file = os.path.join(dst_dir, f)
                names = f.split(".")
                if len(names) == 2:
                    name = "{0}_{1}.{2}".format(names[0], random.randint(1000, 9999), names[1])
                    target_file = os.path.join(dst_dir, name)
                os.rename(current_file, target_file)
    except Exception as ex:
        print(ex)
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir, ignore_errors=True)
    return True, "Unzip file successful."


if __name__ == "__main__":
    zip_file_ = "/Users/zhousf/Desktop/case/银行卡.zip"
    # zip_file_ = "/Users/zhousf/Desktop/case/归档.zip"
    dst_dir_ = "/Users/zhousf/Desktop/case/img"
    # print(unzip_flat_file_rename(zip_file_, dst_dir_))
