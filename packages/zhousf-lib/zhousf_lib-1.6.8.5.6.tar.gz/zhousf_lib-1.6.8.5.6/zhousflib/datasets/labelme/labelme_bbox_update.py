# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function: bbox 修改工具：合并标签、删除标签
import json
from pathlib import Path


def merge_label(labelme_dir: Path, labels: dict):
    """
    todo 合并标签
    :param labelme_dir: labelme目录
    :param labels: {"等级": ['等级_1', '等级_2', '等级_2E']}
    :return:
    """
    need_modify_labels = {}
    for k in labels:
        items = labels.get(k)
        for item in items:
            need_modify_labels[item] = k


def delete_label(labelme_dir: Path, labels: list):
    """
    删除标签
    :param labelme_dir: labelme目录
    :param labels: ['等级_1', '等级_2', '等级_2E']
    :return:
    """
    for json_file in labelme_dir.rglob("*.json"):
        print(json_file)
        with json_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
            for i in range(len(data["shapes"]) - 1, -1, -1):
                shape = data["shapes"][i]
                label = shape["label"]
                if label in labels:
                    data["shapes"].pop(i)
        with json_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    pass
