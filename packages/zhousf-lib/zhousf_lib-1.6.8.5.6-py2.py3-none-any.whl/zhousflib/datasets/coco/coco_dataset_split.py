# -*- coding:utf-8 -*-
# Author:  zhousf
# Description: coco 数据集划分
import json
import shutil
import numpy as np
from pathlib import Path


def train_test_split(data_dirs: list, dst_dir: Path, val_size=0.2, test_size=0.2, shuffle=True):
    """
    训练集、验证集、测试集划分
    :param data_dirs: 数据集目录
    :param dst_dir: 生成训练集、测试集的目录
    :param val_size: 验证集占比
    :param test_size: 测试集占比
    :param shuffle: 打乱数据集顺序
    :return:
    """
    def split_data(dir_save: Path, dataset: list, annotations: dict):
        image_dir = dir_save.joinpath("images")
        if not image_dir.exists():
            image_dir.mkdir(parents=True)
        annotations_save = []
        for img_d in dataset:
            if img_d["id"] not in image_files:
                continue
            shutil.copy(image_files.get(img_d["id"]), image_dir)
            ann = annotations.get(img_d["id"])
            if ann:
                annotations_save.extend(ann)
        json_file = dir_save.joinpath("result.json")
        data_json = {
            "images": dataset,
            "categories": categories,
            "annotations": annotations_save,
            "info": info,
        }
        with json_file.open("w", encoding="utf-8") as f:
            json.dump(data_json, f, ensure_ascii=False, indent=4)

    images = []
    categories = []
    annotations_dict = {}
    info = {}
    image_files = {}
    img_id = 0
    for data_dir in data_dirs:
        if not data_dir.is_dir():
            continue
        for label_json in data_dir.rglob("*.json"):
            with label_json.open("r", encoding="utf-8") as f:
                result_json = json.loads(f.read())
            # 图片
            _images = result_json["images"]
            # 标签类别
            _categories = result_json["categories"]
            # 标注
            _annotations = result_json["annotations"]
            # info
            _info = result_json["info"]
            tmp_anno = {}
            # 遍历标签
            for anno in _annotations:
                image_id = anno["image_id"]
                if image_id not in tmp_anno:
                    tmp_anno[image_id] = [anno]
                else:
                    tmp_anno[image_id].append(anno)
                assert anno["category_id"] is not None
            # 遍历图片
            for img in _images:
                if img["width"] is None or img["height"] is None:
                    continue
                file_name = img["file_name"]
                print(file_name)
                id_tmp = img["id"]
                file_name = str(file_name).rsplit("/")[-1]
                img["file_name"] = file_name
                img["id"] = img_id
                img_file = data_dir.joinpath("images").joinpath(file_name)
                if not img_file.exists():
                    continue
                image_files[img_id] = img_file
                images.append(img)
                if id_tmp in tmp_anno:
                    ann_ = []
                    for anno in tmp_anno.get(id_tmp):
                        anno["image_id"] = img_id
                        ann_.append(anno)
                    annotations_dict[img_id] = ann_
                img_id += 1
            if len(info) == 0:
                info = _info
            if len(categories) == 0:
                categories = _categories
    # 打乱顺序
    if shuffle:
        state = np.random.get_state()
        np.random.shuffle(images)
        np.random.set_state(state)
    # 开始数据集划分
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
        split_data(dir_save=dst_dir.joinpath("train"), dataset=dataset_train, annotations=annotations_dict)
    # 验证集
    if len(dataset_val) > 0:
        split_data(dir_save=dst_dir.joinpath("val"), dataset=dataset_val, annotations=annotations_dict)
    # 测试集
    if len(dataset_test) > 0:
        split_data(dir_save=dst_dir.joinpath("test"), dataset=dataset_test, annotations=annotations_dict)

    txt = "train: {0}, val: {1}, test: {2}, total: {3}".format(len(dataset_train), len(dataset_val),
                                                               len(dataset_test), len(images))
    print(txt)
    readme_txt = dst_dir.joinpath("readme.txt")
    with readme_txt.open("w") as f:
        f.write(txt)


if __name__ == "__main__":
    pass



