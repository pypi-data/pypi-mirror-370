# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/11/1 
# @Function:
import shutil
from pathlib import Path


def delete_file_by_conditions(src_dir: Path,
                              include_file_name: list = None,
                              include_file_stem_startswith: list = None,
                              include_file_stem_endswith: list = None,
                              include_dir_name: list = None,
                              include_dir_stem_startswith: list = None,
                              include_dir_stem_endswith: list = None):
    """
    删除文件/目录：多条件
    :param src_dir: 目录
    :param include_file_name: 文件名称为["log.txt", "error.txt"]
    :param include_file_stem_startswith: 文件名以["_vis", "_loc", "_ocr"]开始
    :param include_file_stem_endswith:  文件名以...结尾
    :param include_dir_name:  目录名称为["__pycache__", ".DS_Store", "cls"]
    :param include_dir_stem_startswith:
    :param include_dir_stem_endswith:
    :return:
    """
    for file in src_dir.rglob("*"):
        print(file)
        if file.is_dir():
            if include_dir_name:
                for dir_name in include_dir_name:
                    if file.name == dir_name:
                        shutil.rmtree(file)
                        continue
            if include_dir_stem_startswith:
                for dir_name in include_dir_stem_startswith:
                    if file.stem.startswith(dir_name):
                        shutil.rmtree(file)
                        continue
            if include_dir_stem_endswith:
                for dir_name in include_dir_stem_endswith:
                    if file.stem.endswith(dir_name):
                        shutil.rmtree(file)
                        continue
        if file.is_file():
            if include_file_name:
                for file_name in include_file_name:
                    if file.name == file_name:
                        file.unlink()
                        continue
            if include_file_stem_startswith:
                for file_name in include_file_stem_startswith:
                    if file.stem.startswith(file_name):
                        file.unlink()
                        continue
            if include_file_stem_endswith:
                for file_name in include_file_stem_endswith:
                    if file.stem.endswith(file_name):
                        file.unlink()
                        continue


def delete_file_by_suffix(src_dirs: list, delete_file_suffix: list = None):
    """
    删除文件: 通过文件扩展名
    :param src_dirs: 目录: [Path("")]
    :param delete_file_suffix: 文件扩展名，[".json"]
    :return:
    """
    if delete_file_suffix is None:
        delete_file_suffix = [".json"]
    delete = 0
    for src_dir in src_dirs:
        for suffix in delete_file_suffix:
            for file in src_dir.rglob("*{0}".format(suffix)):
                if not file.is_file():
                    continue
                file.unlink()
                delete += 1
                print(delete, file)
    print("共删除{0}项".format(delete))
