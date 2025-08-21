# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:
import json
from prettytable import PrettyTable


def data_statistics(labelme_dirs: list):
    """
    数据分布统计
    :param labelme_dirs: 数据集目录 Path
    :return:
    """
    label_list = {}
    for labelme_dir in labelme_dirs:
        for json_file in labelme_dir.rglob("*.json"):
            print(json_file)
            with json_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                for shape in data["shapes"]:
                    label = shape["label"]
                    if len(label) and label:
                        if label not in label_list:
                            label_list[label] = 1
                        else:
                            label_list[label] += 1

    table = PrettyTable(field_names=["label", "count"])
    for key in label_list:
        table.add_row([key, label_list.get(key)])
    print(table)
