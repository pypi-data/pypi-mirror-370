# -*- coding:utf-8 -*-
# Author:  zhousf
# Description: coco bbox 修改工具：合并标签、删除标签
import json
from pathlib import Path


def merge_label(coco_dir: Path, labels: dict):
    """
    合并标签
    :param coco_dir: COCO目录
    :param labels: {"等级": ['等级_1', '等级_2', '等级_2E']}
    :return:
    """
    need_modify_labels = {}
    for k in labels:
        items = labels.get(k)
        for item in items:
            need_modify_labels[item] = k

    result_json_file = coco_dir.joinpath("result.json")
    with result_json_file.open("r", encoding="utf-8") as f:
        result_json = json.loads(f.read())
    # 图片
    images = result_json["images"]
    # 标签类别
    categories = result_json["categories"]
    # 标注
    annotations = result_json["annotations"]
    # info
    info = result_json["info"]
    # 遍历图片
    for img in images:
        if img["width"] is None or img["height"] is None:
            continue
        file_name = img["file_name"]
        file_name = str(file_name).rsplit("/")[-1]
        img["file_name"] = file_name
    label_dict = {}
    for item in categories:
        label_name = item.get("name")
        label_id = item.get("id")
        if label_name in need_modify_labels:
            label_name = need_modify_labels.get(label_name)
        label_dict[label_id] = label_name

    index_mapping = {}
    label_names = {}
    for index in label_dict.keys():
        name = label_dict.get(index)
        if name not in label_names:
            index_mapping[index] = index
            label_names[name] = index
        else:
            index_mapping[index] = label_names.get(name)
    print(index_mapping)
    print(label_dict)
    # 构建新的标签列表
    categories_new = {}
    for index in index_mapping:
        if index_mapping.get(index) not in categories_new:
            categories_new[index_mapping.get(index)] = label_dict.get(index)
    print(categories_new)
    categories_list = []
    for category in categories_new:
        categories_list.append({"id": category, "name": categories_new.get(category)})
    for ann in annotations:
        # 更新标签id
        print(ann.get("category_id"))
        ann["category_id"] = index_mapping.get(ann.get("category_id"))
        assert ann["category_id"] is not None
    json_file = coco_dir.joinpath("result.json")
    data_json = {
        "images": images,
        "categories": categories_list,
        "annotations": annotations,
        "info": info,
    }
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(data_json, f, ensure_ascii=False, indent=4)


def delete_label(coco_dir: Path, labels: list):
    """
    删除标签
    :param coco_dir: COCO目录
    :param labels: ['等级_1', '等级_2', '等级_2E']
    :return:
    """
    result_json_file = coco_dir.joinpath("result.json")
    with result_json_file.open("r", encoding="utf-8") as f:
        result_json = json.loads(f.read())
    # 图片
    images = result_json["images"]
    # 标签类别
    categories = result_json["categories"]
    # 标注
    annotations = result_json["annotations"]
    # info
    info = result_json["info"]
    # 遍历图片
    for i in range(len(images) - 1, -1, -1):
        img = images[i]
        if img["width"] is None or img["height"] is None:
            images.pop(i)
            continue
        file_name = img["file_name"]
        file_name = str(file_name).rsplit("/")[-1]
        img["file_name"] = file_name
        print(file_name)
    delete_indexes = [item.get("id") for item in categories if item.get("name") in labels]
    for i in range(len(annotations) - 1, -1, -1):
        ann = annotations[i]
        # 删除标签
        if ann.get("category_id") in delete_indexes:
            annotations.remove(ann)
        assert ann["category_id"] is not None
    categories_list = []
    for cate in categories:
        index = cate.get("id")
        if index not in delete_indexes:
            categories_list.append(cate)
    json_file = coco_dir.joinpath("result.json")
    data_json = {
        "images": images,
        "categories": categories_list,
        "annotations": annotations,
        "info": info,
    }
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(data_json, f, ensure_ascii=False, indent=4)


def update_coco(coco_dir: Path):
    result_json_file = coco_dir.joinpath("result.json")
    with result_json_file.open("r", encoding="utf-8") as f:
        result_json = json.loads(f.read())
    # 图片
    images = result_json["images"]
    # 标签类别
    categories = result_json["categories"]
    # 标注
    annotations = result_json["annotations"]
    # info
    info = result_json["info"]
    # 遍历图片
    for img in images:
        if img["width"] is None or img["height"] is None:
            continue
        file_name = img["file_name"]
        file_name = str(file_name).rsplit("/")[-1]
        img["file_name"] = file_name
    json_file = coco_dir.joinpath("result.json")
    data_json = {
        "images": images,
        "categories": categories,
        "annotations": annotations,
        "info": info,
    }
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(data_json, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    pass
