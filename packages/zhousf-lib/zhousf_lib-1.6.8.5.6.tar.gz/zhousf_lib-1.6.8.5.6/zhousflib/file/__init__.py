# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/11/1 
# @Function:
import os
import base64
import shutil
import imghdr
import hashlib
import traceback
from pathlib import Path
from PIL import Image


def overwrite_folder(from_dir: Path, to_dir: Path):
    """
    覆盖目录，覆盖已有文件
    :param from_dir: 目录
    :param to_dir: 被覆盖目录
    :return:
    """
    for file in from_dir.rglob("*.*"):
        shutil.copy(file, to_dir.joinpath(file.parent.name))


def md5(file_path: Path):
    """
    文件转md5
    :param file_path: 文件路径
    """
    with file_path.open('rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def get_base64(file_path: Path, contain_file_name=False, split_char=","):
    """
    文件转base64
    :param file_path: 文件路径
    :param contain_file_name: 是否包含文件名称
    :param split_char: 分隔符
    :return: 'a.jpg,iVBORw0KGgoAAAANSUhEUgAABNcAAANtCAYAAACzHZ25AAA.....'
    """
    with file_path.open('rb') as infile:
        s = infile.read()
    base64_str = base64.b64encode(s).decode("utf-8")
    if contain_file_name:
        base64_str = file_path.name + split_char + base64_str
    return base64_str


def rename_images_with_md5(file_dir: Path):
    """
    图片MD5重命名
    :param file_dir:
    :return:
    """
    images = [file for file in file_dir.rglob("*.*") if imghdr.what(file)]
    for image in images:
        md5_str = md5(image)
        img_arr = Image.open(image)
        suffix = image.suffix
        if hasattr(img_arr, "format") and img_arr.format.lower() in ["jpg", "png"]:
            suffix = "." + img_arr.format
        suffix = suffix.lower()
        if suffix not in [".jpg", ".png"]:
            suffix = ".png"
        img_arr.close()
        new_name = image.parent.joinpath("{0}{1}".format(md5_str, suffix))
        if image.name == new_name.name:
            continue
        if new_name.exists():
            image.unlink()
            continue
        os.rename(image, new_name)
    return len(images)


def drop_error_image(file_dir: Path, min_size=20):
    """
    删除无效图片
    :param file_dir:
    :param min_size: 图片最小尺寸，小于则删除
    :return:
    """
    images = [file for file in file_dir.rglob("*.*") if imghdr.what(file)]
    for image in images:
        img_arr = Image.open(image)
        try:
            if img_arr is None:
                print(image)
                image.unlink()
                continue
            if min(img_arr.size) < min_size:
                img_arr.close()
                print(image)
                image.unlink()
                continue
        except Exception as e:
            print(e)
