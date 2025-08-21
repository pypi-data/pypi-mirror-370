# -*- coding:utf-8 -*-
# Author:  zhousf
# Description: coco bbox 提取工具
import json
from pathlib import Path

from PIL import Image, ImageDraw


def compute_contain(box1, box2):
    """
    计算两个box是否为包含关系
    :param box1: (x_min, y_min, x_max, y_max)
    :param box2: (x_min, y_min, x_max, y_max)
    :return: 返回两个box重叠面积占较小box的面积比，一般大于0.8则为包含关系
    box1=(317,280,553,395)
    box2=(374,295,485,322)
    """
    px_min, py_min, px_max, py_max = box1
    gx_min, gy_min, gx_max, gy_max = box2
    p_area = (px_max - px_min) * (py_max - py_min)  # 计算P的面积
    g_area = (gx_max - gx_min) * (gy_max - gy_min)  # 计算G的面积
    # 求相交矩形的左下和右上顶点坐标(x_min, y_min, x_max, y_max)
    _x_min = max(px_min, gx_min)  # 得到左下顶点的横坐标
    _y_min = max(py_min, gy_min)  # 得到左下顶点的纵坐标
    _x_max = min(px_max, gx_max)  # 得到右上顶点的横坐标
    _y_max = min(py_max, gy_max)  # 得到右上顶点的纵坐标
    # 计算相交矩形的面积
    w = _x_max - _x_min
    h = _y_max - _y_min
    if w <= 0 or h <= 0:
        return 0
    area = w * h  # G∩P的面积
    if p_area >= g_area:
        return area / g_area
    else:
        return area / p_area


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


def box_expand(box, offset=50):
    x_min, y_min, x_max, y_max = box
    offset = min(x_min, y_min) if min(x_min, y_min) < offset else offset
    _x_min = x_min - offset
    _x_max = x_max + offset
    _y_min = y_min - offset
    _y_max = y_max + offset
    return _x_min, _y_min, _x_max, _y_max


def generate_image_by_label(data_dirs: list, dist_dir: Path, labels: list, contain_child: bool = False):
    """
    根据标签生成标注数据，进行图片裁剪
    :param data_dirs:
    :param dist_dir:
    :param labels: 提取标签名称
    :param contain_child: 提取时包括区域内的所有标签
    :return:
    """
    dist_dir = dist_dir.joinpath("images")
    if not dist_dir.exists():
        dist_dir.mkdir(parents=True)
    anno_new = []
    img_new = []
    categories_new = []
    info_new = {}
    img_index = 0
    anno_id = 0
    for data_dir in data_dirs:
        if not data_dir.is_dir():
            continue
        for label_json in data_dir.rglob("*.json"):
            images = {}
            annotations = {}
            with label_json.open("r", encoding="utf-8") as f:
                result_json = json.loads(f.read())
            # 图片
            _images = result_json["images"]
            # 标签类别
            _categories = result_json["categories"]
            if not contain_child:
                for cate in _categories:
                    if cate.get("name") in labels:
                        categories_new.append(cate)
            else:
                categories_new = _categories
            if len(categories_new) == 0:
                print("label not exist: {0}".format(labels))
                return
            label_dict = {item.get("id"): item.get("name") for item in _categories}
            # 标注
            _annotations = result_json["annotations"]
            # info
            _info = result_json["info"]
            info_new = _info
            # 遍历图片
            for img in _images:
                file_name = img["file_name"]
                file_name = str(file_name).rsplit("/")[-1]
                images[img["id"]] = data_dir.joinpath("images").joinpath(file_name)
            # 遍历标签
            for anno in _annotations:
                image_id = anno["image_id"]
                anno["id"] = anno_id
                anno_id += 1
                if image_id not in annotations:
                    annotations[image_id] = [anno]
                else:
                    annotations[image_id].append(anno)
                assert anno["category_id"] is not None
            for img_id in annotations:
                anno_list = annotations.get(img_id)
                steel_graph_anno_list = []
                others_anno = []
                for anno in anno_list:
                    category_id = anno["category_id"]
                    category_name = label_dict.get(category_id)
                    if category_name in labels:
                        steel_graph_anno_list.append(anno)
                    else:
                        others_anno.append(anno)
                img = Image.open(images.get(img_id))
                if img.mode != "RGB":
                    img = img.convert('RGB')
                if len(steel_graph_anno_list) > 0 and len(others_anno) > 0:
                    for steel_graph_anno in steel_graph_anno_list:
                        contain_anno = []
                        bbox = coco_convert_bbox(steel_graph_anno["bbox"])
                        for i in range(len(others_anno) - 1, -1, -1):
                            _anno = others_anno[i].copy()
                            _bbox = coco_convert_bbox(_anno["bbox"])
                            iou = compute_contain(bbox, _bbox)
                            if iou > 0.5:
                                contain_anno.append(_anno)
                        if not steel_graph_anno:
                            continue
                        bbox = coco_convert_bbox(steel_graph_anno["bbox"])
                        bbox_big = box_expand(box=bbox, offset=10)
                        # 裁剪图片
                        cropped = img.crop(bbox_big)
                        x_min = bbox[0] - bbox_big[0]
                        y_min = bbox[1] - bbox_big[1]
                        x_max = bbox[2] - bbox_big[0]
                        y_max = bbox[3] - bbox_big[1]
                        steel_graph_anno["bbox"] = bbox_convert_coco((x_min,  y_min, x_max, y_max))
                        steel_graph_anno["image_id"] = img_index
                        anno_new.append(steel_graph_anno)
                        # draw = ImageDraw.ImageDraw(cropped)
                        # draw.rectangle(xy=(x_min,  y_min, x_max, y_max), fill=None, outline="red", width=1)
                        for anno in contain_anno:
                            _bbox = coco_convert_bbox(anno["bbox"])
                            # 坐标偏移计算
                            x_min_ = _bbox[0] - bbox_big[0]
                            y_min_ = _bbox[1] - bbox_big[1]
                            x_max_ = _bbox[2] - bbox_big[0]
                            y_max_ = _bbox[3] - bbox_big[1]
                            anno["bbox"] = bbox_convert_coco((x_min_,  y_min_, x_max_, y_max_))
                            anno["image_id"] = img_index
                            # draw.rectangle(xy=(x_min_,  y_min_, x_max_, y_max_), fill=None, outline="red", width=1)
                        # cropped.show()
                        if contain_child:
                            anno_new.extend(contain_anno)
                        save_img_file = dist_dir.joinpath("{0}_{1}{2}".format(images.get(img_id).stem,img_index, images.get(img_id).suffix))
                        cropped.save(save_img_file)
                        img_new.append({"width": cropped.width, "height": cropped.height, "id": img_index,
                                        "file_name": save_img_file.name})
                        img_index += 1
                        print(img_index)
    result_file = dist_dir.parent.joinpath("result.json")
    with open(result_file, 'w', encoding="utf-8") as f:
        json.dump({
            "images": img_new,
            "categories": categories_new,
            "annotations": anno_new,
            "info": info_new
        }, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    pass


