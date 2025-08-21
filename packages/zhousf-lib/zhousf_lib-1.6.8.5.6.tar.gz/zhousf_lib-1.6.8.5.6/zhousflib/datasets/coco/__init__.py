# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function: label-studio
import json
from prettytable import PrettyTable


def data_statistics(result_jsons: list):
    """
    数据分布统计
    :param result_jsons: 数据集目录
    :return:
    """
    image_total = 0
    label_list = {}
    for label_json in result_jsons:
        with label_json.open("r", encoding="utf-8") as f:
            result_json = json.loads(f.read())
        # 标签类别
        label_list = result_json["categories"]
        break
    if len(label_list) == 0:
        print("标签类别无效")
        return
    label_names = {k.get("id"): k.get("name") for k in label_list}
    statistics_total = {k.get("id"): 0 for k in label_list}
    for label_json in result_jsons:
        with label_json.open("r", encoding="utf-8") as f:
            result_json = json.loads(f.read())
        # 图片
        image_total += len(result_json["images"])
        # 标注
        for label in result_json["annotations"]:
            label_id = label.get("category_id")
            statistics_total[label_id] += 1
    statistics_total = {label_names.get(k): statistics_total.get(k) for k in statistics_total}
    print(statistics_total)
    table = PrettyTable(field_names=["label", "count"])
    for key in statistics_total:
        table.add_row([key, statistics_total.get(key)])
    print(table)