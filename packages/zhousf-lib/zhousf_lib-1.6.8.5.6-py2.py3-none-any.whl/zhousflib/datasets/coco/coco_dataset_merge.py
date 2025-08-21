# -*- coding:utf-8 -*-
# Author:  zhousf
# Description: coco 数据集合并
import shutil
import json
from pathlib import Path


def merge_dataset_coco(dataset_dirs: list, dist_dir: Path, img_index=0):
    """
    coco数据集合并
    :param dataset_dirs: ["batch1/dataset_coco/test", "batch2/dataset_coco/test"]
    :param dist_dir: union/dataset_coco/test
    :param img_index:
    :return:
    """
    anno_new = []
    img_new = []
    categories_new = []
    info_new = {}
    anno_id = 0
    for data_dir in dataset_dirs:
        annotations = {}
        label_json = data_dir.joinpath("result.json")
        with label_json.open("r", encoding="utf-8") as f:
            result_json = json.loads(f.read())
        # 图片
        _images = result_json["images"]
        # 标签类别
        _categories = result_json["categories"]
        categories_new = _categories
        # 标注
        _annotations = result_json["annotations"]
        # info
        _info = result_json["info"]
        info_new = _info
        # 遍历标签
        for anno in _annotations:
            image_id = anno["image_id"]
            if image_id not in annotations:
                annotations[image_id] = [anno]
            else:
                annotations[image_id].append(anno)
        img_dir = dist_dir.joinpath("images")
        if not img_dir.exists():
            img_dir.mkdir(parents=True)
        # 遍历图片
        for img in _images:
            file_name = img["file_name"]
            file_name = str(file_name).rsplit("/")[-1]
            img_file = data_dir.joinpath("images").joinpath(file_name)
            anno_list = annotations.get(img["id"])
            if not anno_list:
                continue
            # 修改标注的图片id
            for anno in anno_list:
                anno["image_id"] = img_index
                assert anno["category_id"] is not None
                anno["id"] = anno_id
                anno_id += 1
            img_new.append({"width": img.get("width"), "height": img.get("height"), "id": img_index,
                            "file_name": "{0}{1}".format(img_index, img_file.suffix)})
            anno_new.extend(annotations.get(img["id"]))
            copy_file_ = img_dir.joinpath("{0}{1}".format(img_index, img_file.suffix))
            shutil.copy(img_file, copy_file_)
            img_index += 1
            print(img_index, data_dir)
    if not dist_dir.exists():
        dist_dir.mkdir(parents=True)
    result_file = dist_dir.joinpath("result.json")
    with open(result_file, 'w') as f:
        json.dump({
            "images": img_new,
            "categories": categories_new,
            "annotations": anno_new,
            "info": info_new
        }, f, ensure_ascii=False, indent=4)
    pass


if __name__ == "__main__":
    pass

