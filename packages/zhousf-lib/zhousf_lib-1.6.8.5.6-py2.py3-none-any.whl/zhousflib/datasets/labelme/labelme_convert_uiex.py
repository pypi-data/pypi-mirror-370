# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function: labelme标注数据转uiex数据集
# prompt标注原则： prompt_tag|word
# 其他标注： 可见即可得
import os
import json
import numpy
import base64
import numpy as np
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageOps

from zhousflib.image import pil_util


def show_normalize_box(image_file: Path, bbox: list, normalize_size: list, fill_transparent=128):
    """
    显示标准化后的box
    :param image_file:
    :param bbox:
    :param normalize_size: 标准化尺寸
    :param fill_transparent: 填充色透明度[0, 255]，当为-1时则不填充
    :return:
    boxes = [[557, 102, 693, 367],
             [557, 102, 693, 367],
             [557, 102, 693, 367],
             [557, 102, 693, 367],
             [575, 404, 666, 698],
             [575, 404, 666, 698],
             [575, 404, 666, 698],
             [903, 367, 990, 794],
             [346, 529, 431, 794],
             [346, 529, 431, 794],
             [346, 529, 431, 794]]
    show_normalize_box(bbox=boxes, image_file=None, normalize_size=[1000, 1000])
    """
    if normalize_size is None:
        normalize_size = [1000, 1000]
    n_box = []
    image_size = pil_util.get_w_h(image_file=image_file)
    for box in bbox:
        n_box.append(_denormalize_box(box=box, image_size=image_size, normalize_size=normalize_size))
    pil_util.draw_rectangle(bbox=n_box, image_file=image_file, fill_transparent=fill_transparent)


def _normalize_box(box, image_size, normalize_size, offset_x=0, offset_y=0):
    """
    box标准化
    :param box: (x_min, y_min, x_max, y_max)
    :param image_size: [img_w, img_h] 图片宽高
    :param normalize_size: [1000, 1000]
    :param offset_x:
    :param offset_y:
    :return:
    """
    if normalize_size is None:
        normalize_size = [1000, 1000]
    return [
        int((box[0] + offset_x) * normalize_size[0] / image_size[0]),
        int((box[1] + offset_y) * normalize_size[1] / image_size[1]),
        int((box[2] + offset_x) * normalize_size[0] / image_size[0]),
        int((box[3] + offset_y) * normalize_size[1] / image_size[1]),
    ]


def _denormalize_box(box, image_size, normalize_size, offset_x=0, offset_y=0):
    """
    box反标准化
    :param box: (x_min, y_min, x_max, y_max)
    :param image_size: [img_w, img_h] 图片宽高
    :param normalize_size: [1000, 1000]
    :param offset_x:
    :param offset_y:
    :return:
    """
    return [
        int((box[0] - offset_x) * image_size[0] / normalize_size[0]),
        int((box[1] - offset_y) * image_size[1] / normalize_size[0]),
        int((box[2] - offset_x) * image_size[0] / normalize_size[0]),
        int((box[3] - offset_y) * image_size[1] / normalize_size[0])
    ]


def _np2base64(image_np):
    img = Image.fromarray(image_np)
    base64_str = _pil2base64(img)
    return base64_str


def _pil2base64(image, image_type=None, size=False):
    if not image_type:
        image_type = "JPEG"
    img_buffer = BytesIO()
    image.save(img_buffer, format=image_type)

    byte_data = img_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)

    base64_string = base64_str.decode("utf-8")

    if size:
        return base64_string, image.size
    else:
        return base64_string


def _get_buffer(data, file_like=False):
    buff = None
    if len(data) < 1024:
        if os.path.exists(data):
            buff = open(data, "rb").read()
        elif data.startswith("http://") or data.startswith("https://"):
            resp = requests.get(data, stream=True)
            if not resp.ok:
                raise RuntimeError("Failed to download the file from {}".format(data))
            buff = resp.raw.read()
        else:
            raise FileNotFoundError("Image file {} not found!".format(data))
    if buff is None:
        buff = base64.b64decode(data)
    if buff and file_like:
        return BytesIO(buff)
    return buff


def _read_image(image):
    """
    read image to np.ndarray
    """
    image_buff = _get_buffer(image)
    # Use exif_transpose to correct orientation
    _image = np.array(ImageOps.exif_transpose(Image.open(BytesIO(image_buff)).convert("RGB")))
    return _image


def _save_data(save_file: Path, dataset: list):
    with save_file.open("w", encoding="utf-8") as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def _create_prompt(dataset: list, label_split: str, label_type: dict):
    label_data = []
    for json_file in dataset:
        prompt_list = []
        bbox_list = []
        content = ""
        with json_file.open("r", encoding="utf-8") as f:
            print(json_file)
            data = json.load(f)
            image_file = json_file.parent.joinpath(data["imagePath"])
            if not image_file.exists():
                continue
            image = _read_image(str(image_file))
            image_base64 = _np2base64(image)
            image_width = data["imageWidth"]
            image_height = data["imageHeight"]
            for shape in data["shapes"]:
                label = shape["label"]
                points = shape["points"]
                # shape_type 支持 rectangle 和 polygon
                arr = numpy.asarray(points)
                x_min = numpy.min(arr[:, 0])
                x_max = numpy.max(arr[:, 0])
                y_min = numpy.min(arr[:, 1])
                y_max = numpy.max(arr[:, 1])
                # b_width = abs(x_max - x_min)
                # b_height = abs(y_max - y_min)
                bbox = _normalize_box(box=(x_min, y_min, x_max, y_max), image_size=[image_width, image_height], normalize_size=[1000, 1000])
                if str(label).find(label_split) > -1:
                    prompt = str(label).split(label_split)[0]
                    word = str(label).split(label_split)[-1]
                    start = len(content)
                    content += word
                    end = start + len(word) - 1
                    prompt = label_type.get(prompt, None)
                    if not prompt:
                        continue
                    prompt_list.append((prompt, word, start, end, bbox))
                    for i in range(0, len(word)):
                        bbox_list.append(bbox)
                else:
                    for i in range(0, len(label)):
                        bbox_list.append(bbox)
            if len(prompt_list) > 0:
                for item in prompt_list:
                    prompt, word, start, end, bbox = item
                    prompt_item = {
                        "content": content,
                        "result_list": [
                            {
                                "text": str(word),
                                "start": start,
                                "end": end,
                            }
                        ],
                        "prompt": prompt,
                        "bbox": bbox_list,
                        "image": image_base64,
                    }
                    label_data.append(prompt_item)
    return label_data


def train_test_split(data_dirs: list, dst_dir: Path, label_split: str, label_type: dict, val_size=0.2, test_size=0.2, shuffle=True):
    """
    数据集制作
    :param data_dirs: labelme目录
    :param dst_dir: 保存目录
    :param label_split: prompt标注时的分割符号，可以用"|"
    :param label_type: prompt标注时的标识
    :param val_size: 验证集占比
    :param test_size: 测试集占比
    :param shuffle: 是否打乱顺序
    :return:
    """
    if not dst_dir.exists():
        dst_dir.mkdir(parents=True)
    label_file_list = []
    for labelme_dir in data_dirs:
        for json_file in labelme_dir.rglob("*.json"):
            with json_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                image_file = json_file.parent.joinpath(data["imagePath"])
                if not image_file.exists():
                    continue
                label_file_list.append(json_file)
    # 打乱顺序
    if shuffle:
        state = np.random.get_state()
        np.random.shuffle(label_file_list)
        np.random.set_state(state)
    # 开始数据集划分
    dataset_val = []
    dataset_test = []
    split_index = 0
    if 1 > val_size > 0:
        split_index = int(len(label_file_list) * val_size)
        dataset_val = label_file_list[:split_index]
    if 1 > test_size > 0:
        start = split_index
        split_index += int(len(label_file_list) * test_size)
        dataset_test = label_file_list[start:split_index]
    dataset_train = label_file_list[split_index:]

    # 训练集
    if len(dataset_train) > 0:
        label_data = _create_prompt(dataset=dataset_train, label_split=label_split, label_type=label_type)
        _save_data(save_file=dst_dir.joinpath("train.txt"), dataset=label_data)
    # 验证集
    if len(dataset_val) > 0:
        label_data = _create_prompt(dataset=dataset_val, label_split=label_split, label_type=label_type)
        _save_data(save_file=dst_dir.joinpath("dev.txt"), dataset=label_data)
    # 测试集
    if len(dataset_test) > 0:
        label_data = _create_prompt(dataset=dataset_test, label_split=label_split, label_type=label_type)
        _save_data(save_file=dst_dir.joinpath("test.txt"), dataset=label_data)
    txt = "train: {0}, val: {1}, test: {2}, total: {3}".format(len(dataset_train), len(dataset_val),
                                                               len(dataset_test), len(label_file_list))
    print(txt)
    readme_txt = dst_dir.joinpath("readme.txt")
    with readme_txt.open("w") as f:
        f.write(txt)


if __name__ == "__main__":
    train_test_split(data_dirs=[Path(r"C:\Users\zhousf-a\Desktop\数据 JSON")],
                     dst_dir=Path(r"C:\Users\zhousf-a\Desktop\uiex"),
                     label_split="|",
                     label_type={"bh": "编号", "gs": "根数", "dj": "等级", "zj": "直径", "dgc": "单根长", "bc": "边长"},
                     val_size=0.2,
                     test_size=0.2,
                     shuffle=True)




