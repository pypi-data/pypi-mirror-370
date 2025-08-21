# -*- coding:utf-8 -*-
# Author:  zhousf
# Description:
import json
import random
import colorsys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from zhousflib.font import Font_SimSun
FONT = ImageFont.truetype(font=str(Font_SimSun), size=15)


def coco_convert_bbox(box_coco: list):
    _x, _y, _width, _height = tuple(box_coco)
    _bbox = (_x, _y, _x + _width, _y + _height)
    return _bbox


def vis_box_coco(coco_dir: Path, dst_dir: Path):
    """
    可视化coco bbox
    :param coco_dir:
    :param dst_dir:
    :return:
    """
    if not dst_dir.exists():
        dst_dir.mkdir()
    label_json = coco_dir.joinpath("result.json")
    with label_json.open("r", encoding="utf-8") as f:
        result_json = json.loads(f.read())
    # 图片
    _images = result_json["images"]
    # 标签类别
    _categories = result_json["categories"]
    classes_dict = {}
    for item in _categories:
        classes_dict[item.get("id")] = item.get("name")
    # 标注
    _annotations = result_json["annotations"]
    # info
    _info = result_json["info"]
    # 遍历标签
    annotations = {}
    for anno in _annotations:
        image_id = anno["image_id"]
        if image_id not in annotations:
            annotations[image_id] = [anno]
        else:
            annotations[image_id].append(anno)
        assert anno["category_id"] is not None
    img_dir = coco_dir.joinpath("images")
    for img in _images:
        img_file = img_dir.joinpath(img["file_name"])
        bboxes = []
        print(img["id"])
        ann_list = annotations.get(img["id"])
        if not ann_list:
            continue
        for anno in ann_list:
            box = anno.get("bbox")
            class_id = anno.get("category_id")
            bbox_coco = coco_convert_bbox(box)
            # class_id, score, x_min, y_min, x_max, y_max, class_id
            bboxes.append([class_id, "-", bbox_coco[0], bbox_coco[1], bbox_coco[2], bbox_coco[3]])
        image = draw_bbox_label(img_file=img_file, bboxes=bboxes, classes_dict=classes_dict, show=False)
        image.save(dst_dir.joinpath(img_file.name))
        # break


def draw_bbox_label(img_file: Path, bboxes: list, classes_dict, show=False):
    """
    绘制bbox，适用于标注数据，不支持预测可视化
    :param img_file:
    :param bboxes: [[class_id, score, x_min, y_min, x_max, y_max]]
    :param classes_dict: {id1:name1, id2:name2} or [name1, name2]
    :param show:
    :return:
    """
    classes_index = [cls for cls in classes_dict]
    hsv_tuples = [(1.0 * x / len(classes_index), 1., 1.) for x in range(len(classes_index))]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    colors = list(map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), colors))
    random.seed(0)
    random.shuffle(colors)
    image = Image.open(img_file)
    print(img_file)
    if image.mode != "RGB":
        image = image.convert('RGB')
    image_w, image_h = image.size
    draw = ImageDraw.ImageDraw(image)
    for box in bboxes:
        offset = 0
        class_id = box[-6]
        score = box[-5]
        x_min = int(box[-4])
        y_min = int(box[-3])
        x_max = int(box[-2])
        y_max = int(box[-1])
        if str(class_id).isdigit():
            class_name = classes_dict[class_id]
        else:
            class_name = str(class_id)
        if score != "-":
            class_name += ":{0:.3f}".format(score)
        else:
            class_name += ":{0}".format(score)
        bbox_color = colors[classes_index.index(class_id)]
        width = abs(x_max - x_min)
        height = abs(y_max - y_min)
        draw.rectangle(xy=(x_min, y_min, x_min + width + offset, y_min + height + offset),
                       fill=None, outline=bbox_color, width=1)
        fw, fh = FONT.getsize(class_name)
        if y_min < fh:
            y_min = y_min + fh
        if (x_min + fw) > image_w:
            x_min = x_max - fw
        # draw.rectangle([x_min, y_min, x_min + fw, y_min], fill=(128, 128, 128, 128))
        draw.text(xy=(x_min, y_min - fh), text=class_name, fill=bbox_color, font=FONT)
    if show:
        image.show()
    return image


def draw_bbox_predict(img_file, bboxes: list, classes_dict, score_threshold=0.5, show=False):
    """
    绘制bbox，适用于预测可视化
    :param img_file:
    :param bboxes: [[class_id, score, x_min, y_min, x_max, y_max]]
    :param classes_dict: {id1:name1, id2:name2} or [name1, name2]
    :param score_threshold:
    :param show:
    :return:
    """
    classes_index = [i for i, cls in enumerate(classes_dict)]
    hsv_tuples = [(1.0 * x / len(classes_index), 1., 1.) for x in range(len(classes_index))]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    colors = list(map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), colors))
    random.seed(0)
    random.shuffle(colors)
    if isinstance(img_file, Path):
        image = Image.open(img_file)
    else:
        image = Image.fromarray(img_file)
    if image.mode != "RGB":
        image = image.convert('RGB')
    image_h, image_w = image.size
    draw = ImageDraw.ImageDraw(image)
    for box in bboxes:
        offset = 0
        class_id = box[-6]
        score = box[-5]
        if score < score_threshold:
            continue
        x_min = int(box[-4])
        y_min = int(box[-3])
        x_max = int(box[-2])
        y_max = int(box[-1])
        if str(class_id).isdigit():
            class_name = classes_dict[class_id]
        else:
            class_name = class_id
            if class_id in classes_dict and isinstance(classes_dict, list):
                class_id = classes_dict.index(class_id)
        class_name += ":{0:.3f}".format(score)
        bbox_color = colors[classes_index.index(class_id)]
        width = abs(x_max - x_min)
        height = abs(y_max - y_min)
        draw.rectangle(xy=(x_min, y_min, x_min + width + offset, y_min + height + offset),
                       fill=None, outline=bbox_color, width=1)
        fw, fh = FONT.getsize(class_name)
        if y_min < fh:
            y_min = y_min + fh
        if (x_min + fw) > image_w:
            x_min = x_max - fw
        # draw.rectangle([x_min, y_min, x_min + fw, y_min], fill=(128, 128, 128, 128))
        draw.text(xy=(x_min, y_min - fh), text=class_name, fill=bbox_color, font=FONT)
    if show:
        image.show()
    return image


if __name__ == "__main__":
    pass
