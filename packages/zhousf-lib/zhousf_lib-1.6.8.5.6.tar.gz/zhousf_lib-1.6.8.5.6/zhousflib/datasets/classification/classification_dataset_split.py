# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function: 图像分类数据制作
import shutil
import imghdr
import numpy as np
from pathlib import Path

from zhousflib.util import list_util
"""
一般情况下，在加载预训练模型的情况下，每个类别包括 10-20 张图像即可保证基本的分类效果；
不加载预训练模型的情况下，每个类别需要至少包含 100-200 张图像以保证基本的分类效果。
训练集、验证集、测试集的类别都要全，不然会给训练带来麻烦
"""


def fetch_available_cls_folder(img_dir: Path):
    """
    删除空目录
    :param img_dir:
    :return:
    """
    for folder in img_dir.iterdir():
        cls = [i for i in folder.rglob("*.*")]
        if len(cls) == 0:
            print(folder)
            shutil.rmtree(folder)


def train_test_split(image_dir: Path, val_size=0.2, test_size=0.2, shuffle=True, every_cls_count_limit=20):
    """
    训练集、验证集、测试集划分
    :param image_dir: 图片目录
    :param val_size: 验证集占比
    :param test_size: 测试集占比
    :param shuffle: 打乱数据集顺序
    :param every_cls_count_limit: 每个类别最低的图片数量，若低于则随机复制
    :return:
    """
    train_txt_file = image_dir.parent.joinpath("train_list.txt")
    val_txt_file = image_dir.parent.joinpath("val_list.txt")
    test_txt_file = image_dir.parent.joinpath("test_list.txt")
    label_list_file = image_dir.parent.joinpath("label_list.txt")
    images = []
    label_list = []
    # 标签文件
    for folder in image_dir.rglob("*.*"):
        if folder.parent.name not in label_list:
            label_list.append(folder.parent.name)
    if not label_list_file.exists():
        with label_list_file.open("w", encoding="utf-8") as f:
            for i, d in enumerate(label_list):
                f.write("{0} {1}\n".format(i, d))
    label_files = {}
    # 遍历所有图片文件
    for folder in image_dir.rglob("*.*"):
        if not folder.is_file():
            continue
        if not imghdr.what(folder):
            continue
        file = "{0}/{1}/{2} {3}\n".format(folder.parent.parent.name, folder.parent.name, folder.name, label_list.index(folder.parent.name))
        if folder.parent.name not in label_files:
            label_files[folder.parent.name] = [file]
        else:
            label_files[folder.parent.name].append(file)
        print(file)
        images.append(file)
    # 随机复制低于every_cls_count_limit的类别
    for label in label_files:
        label_count = len(label_files.get(label)) if label_files.get(label) else 0
        if label_count < every_cls_count_limit:
            for item in list_util.random_choices(label_files.get(label), choose_k=abs(every_cls_count_limit-label_count)):
                images.append(item)
    # 打乱顺序
    if shuffle:
        state = np.random.get_state()
        np.random.shuffle(images)
        np.random.set_state(state)
    dataset_val = []
    dataset_test = []
    split_index = 0
    if 1 > val_size > 0:
        split_index = int(len(images) * val_size)
        dataset_val = images[:split_index]
    if 1 > test_size > 0:
        start = split_index
        split_index += int(len(images) * test_size)
        dataset_test = images[start:split_index]
    dataset_train = images[split_index:]
    # 训练集
    if len(dataset_train) > 0:
        with train_txt_file.open("w", encoding="utf-8") as f:
            for d in dataset_train:
                f.write(d)
    # 验证集
    if len(dataset_val) > 0:
        with val_txt_file.open("w", encoding="utf-8") as f:
            for d in dataset_val:
                f.write(d)
    # 测试集集
    if len(dataset_test) > 0:
        with test_txt_file.open("w", encoding="utf-8") as f:
            for d in dataset_test:
                f.write(d)


def data_statistics(image_dir: Path):
    """
    数据分布统计
    :param image_dir: 数据集目录
    :return:
    """
    label_files = {}
    # 遍历所有图片文件
    for folder in image_dir.rglob("*.*"):
        if not folder.is_file():
            continue
        if not imghdr.what(folder):
            continue
        if folder.parent.name not in label_files:
            label_files[folder.parent.name] = [folder]
        else:
            label_files[folder.parent.name].append(folder)
    total = 0
    for label in label_files:
        total += len(label_files.get(label))
        print("{0}: {1}".format(label, len(label_files.get(label))))
    print("\nTotal: {0}".format(total))


if __name__ == "__main__":
    from zhousflib.file import rename_images_with_md5, drop_error_image
    # drop_error_image(Path(r"D:\workspace\PaddleClas\dataset\classify\images"))
    # rename_images_with_md5(Path(r"C:\Users\zhousf-a\Desktop\data\验收集\20240722\2"))
    train_test_split(image_dir=Path(r"D:\workspace\PaddleClas\dataset\classify\images"), val_size=0.2, test_size=0)
    # data_statistics(image_dir=Path(r"D:\workspace\PaddleClas\dataset\classify\images"))
    pass





