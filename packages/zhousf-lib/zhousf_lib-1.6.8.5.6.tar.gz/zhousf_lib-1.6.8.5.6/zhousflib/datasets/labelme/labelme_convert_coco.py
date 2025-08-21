# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function: labelme convert coco | coco conver labelme
import json
import numpy
import shutil
import colorsys
from pathlib import Path

from zhousflib.file import get_base64


def coco_convert_bbox(box_coco: list):
    _x, _y, _width, _height = tuple(box_coco)
    _bbox = (_x, _y, _x + _width, _y + _height)
    return _bbox


def bbox_convert_coco(bbox: tuple):
    x_min_, y_min_, x_max_, y_max_ = bbox
    x = x_min_
    y = y_min_
    width = x_max_ - x_min_
    height = y_max_ - y_min_
    return [x, y, width, height]


def coco_convert_labelme(coco_dir: Path, dist_dir: Path, is_rectangle=False):
    """
    coco转labelme，支持rectangle和polygon
    :param coco_dir:
    :param dist_dir:
    :param is_rectangle:
    :return:
    """
    if not dist_dir.exists():
        dist_dir.mkdir()
    images_dir = coco_dir.joinpath("images")
    coco_result_file = coco_dir.joinpath("result.json")
    with coco_result_file.open("r", encoding="utf-8") as f:
        result_json = json.loads(f.read())
    # 图片
    images = result_json["images"]
    # 标签类别
    categories = result_json["categories"]
    # 标注
    annotations = result_json["annotations"]
    # info
    info = result_json["info"]

    hsv_tuples = [(1.0 * x / len(categories), 1., 1.) for x in range(len(categories))]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    colors = list(map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), colors))

    # 遍历类别
    category_info_data = {}
    category_index = []
    for category in categories:
        category_id = category["id"]
        category_name = category["name"]
        if category_id not in category_info_data:
            category_info_data[category_id] = category_name
        if category_id not in category_index:
            category_index.append(category_id)
    # 遍历图片
    image_info_data = {}
    for i in range(len(images) - 1, -1, -1):
        img = images[i]
        if img["width"] is None or img["height"] is None:
            images.pop(i)
            continue
        file_name = img["file_name"]
        file_name = str(file_name).rsplit("/")[-1]
        img["file_name"] = file_name
        image_id = img["id"]
        if image_id not in image_info_data:
            image_info_data[image_id] = {"image_id": image_id, "file_name": file_name,
                                         "width": img["width"], "height": img["height"]}
    # 遍历标注
    image_label_data = {}
    for annotation in annotations:
        image_id = annotation["image_id"]
        if image_id in image_label_data:
            image_label_data[image_id].append(annotation)
        else:
            image_label_data[image_id] = [annotation]
    for image_id in image_label_data.keys():
        shapes = []
        image_name = image_info_data.get(image_id).get("file_name")
        for annotation in image_label_data.get(image_id):
            category_id = annotation["category_id"]
            shape = {}
            if category_id not in category_info_data:
                continue
            points = []
            shape["label"] = category_info_data.get(category_id)
            segmentation = annotation["segmentation"]
            bbox = annotation["bbox"]
            if len(segmentation) > 0:
                # todo
                continue
            if len(bbox) > 0:
                if is_rectangle:
                    _x_min, _y_min, _width, _height = tuple(bbox)
                    _x_max = _x_min + _width
                    _y_max = _y_min + _height
                    points.append([_x_min, _y_min])
                    points.append([_x_max, _y_max])
                else:
                    bbox = coco_convert_bbox(bbox)
                    x_min = int(bbox[0])
                    y_min = int(bbox[1])
                    x_max = int(bbox[2])
                    y_max = int(bbox[3])
                    points.append([x_min, y_min])
                    points.append([x_max, y_min])
                    points.append([x_max, y_max])
                    points.append([x_min, y_max])
                shape["points"] = points
                shape["line_color"] = colors[category_index.index(category_id)]
                shape["fill_color"] = ""
                shape["shape_type"] = "rectangle" if is_rectangle else "polygon"
                shape["group_id"] = ""
                shape["description"] = ""
                shape["flags"] = {}
                shapes.append(shape)
        data = {
            "flags": {},
            "shapes": shapes,
            # "lineColor": [0, 255, 0, 128],
            # "fillColor": [255, 0, 0, 128],
            "imagePath": image_name,
            "imageWidth": image_info_data.get(image_id).get("width"),
            "imageHeight": image_info_data.get(image_id).get("height"),
            "imageData": get_base64(images_dir.joinpath(image_name)),

        }
        shutil.copy(images_dir.joinpath(image_name), dist_dir)
        save_file = dist_dir.joinpath("{0}.json".format(image_name.split(".")[0]))
        with save_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(save_file)


def labelme_convert_coco(labelme_dirs: list, dist_dir: Path):
    """
    labelme转coco， shape_type支持rectangle和polygon
    :param labelme_dirs:
    :param dist_dir:
    :return:
    """
    images_dir = dist_dir.joinpath("images")
    if not images_dir.exists():
        images_dir.mkdir(parents=True)
    images = []
    categories = []
    annotations = []
    categories_list = []
    image_id = 0
    ann_id = 0
    for labelme_dir in labelme_dirs:
        for json_file in labelme_dir.rglob("*.json"):
            print(json_file)
            with json_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                images.append({"width": data["imageWidth"],
                               "height": data["imageHeight"],
                               "file_name": data["imagePath"],
                               "id": image_id})
                image_file = json_file.parent.joinpath(data["imagePath"])
                if not image_file.exists():
                    image_file.mkdir()
                    continue
                for shape in data["shapes"]:
                    label = shape["label"]
                    if label not in categories_list:
                        categories_list.append(label)
                    points = shape["points"]
                    # shape_type 支持 rectangle 和 polygon
                    arr = numpy.asarray(points)
                    x_min = numpy.min(arr[:, 0])
                    x_max = numpy.max(arr[:, 0])
                    y_min = numpy.min(arr[:, 1])
                    y_max = numpy.max(arr[:, 1])
                    b_width = abs(x_max-x_min)
                    b_height = abs(y_max-y_min)
                    annotation = {"id": ann_id, "image_id": image_id, "category_id": categories_list.index(label),
                                  "bbox": [x_min, y_min, b_width, b_height], "segmentation": [], "ignore": 0,
                                  "iscrowd": 0, "area": b_width*b_height}
                    annotations.append(annotation)
                    ann_id += 1
                shutil.copy(image_file, images_dir)
            image_id += 1
    for i, name in enumerate(categories_list):
        categories.append({"id": i, "name": name})
    json_file = dist_dir.joinpath("result.json")
    data_json = {
        "images": images,
        "categories": categories,
        "annotations": annotations,
        "info": {}
    }
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(data_json, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    pass
