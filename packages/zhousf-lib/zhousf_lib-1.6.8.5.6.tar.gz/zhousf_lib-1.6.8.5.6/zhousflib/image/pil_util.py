# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function: pillow==9.0.1
import numpy
from pathlib import Path

import colorsys

import numpy as np
from PIL import Image, ImageDraw


def four_point_convert_bbox(four_points: list):
    """
    四点转换成bbox
    :param four_points: [[252, 140], [300, 140], [300, 189], [252, 189]]
    :return:
    """
    arr = numpy.asarray(four_points)
    x_min = min(arr[:, 0])
    y_min = min(arr[:, 1])
    x_max = max(arr[:, 0])
    y_max = max(arr[:, 1])
    return x_min, y_min, x_max, y_max


def draw_rectangle(bbox: list, image_file: Path = None, image_size: list = None, font=None,
                   fill_transparent=255, show=True):
    """
    绘制矩形框
    :param bbox: [(label, x_min, y_min, x_max, y_max)]
    :param image_file: 空时以空白为背景进行绘制
    :param image_size:
    :param font: ImageFont.truetype(font_path, font_size, encoding="utf-8")
    :param fill_transparent: 填充色透明度[0, 255]，当为-1时则不填充
    :param show:
    :return:
    """
    draw_p = []
    texts = []
    for box in bbox:
        if len(box) == 5:
            texts.append(box[-5])
        x_min = box[-4]
        y_min = box[-3]
        x_max = box[-2]
        y_max = box[-1]
        draw_p.append([(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)])
    return draw_polygon(polygon=draw_p, image_file=image_file, image_size=image_size, font=font, texts=texts,
                        fill_transparent=fill_transparent, show=show)


def get_w_h(image_file: Path = None):
    """
    获取图片宽高
    :param image_file:
    :return:
    """
    image = Image.open(image_file)
    return [image.width, image.height]


def draw_polygon(polygon: list, image_file=None, image_size: list = None, font=None, draw_text_color=None,
                 texts: list = None, fill_transparent=255, show=True):
    """
    绘制四边形
    :param polygon:
            [[[255, 376], [291, 409], [255, 443], [218, 409]], [[252, 140], [300, 140], [300, 189], [252, 189]]]
            or
            [[3796.740478515625, 968.7546997070312, 4216.4248046875, 1528.115478515625], [3857.1689453125, 272.2844543457031, 4227.78271484375, 799.551513671875]]
    :param image_file: 空时以空白为背景进行绘制
    :param image_size:
    :param font: ImageFont.truetype(font_path, font_size, encoding="utf-8")
    :param draw_text_color:
    :param texts: box框的描述文本，长度等于polygon
    :param fill_transparent: 填充色透明度[0, 255]，当为-1时则不填充
    :param show:
    :return:
    """
    draw_text_color = "black" if draw_text_color is None else draw_text_color
    if len(np.asarray(polygon).shape) == 2:
        convert_bbox = []
        for box in polygon:
            x_min = box[0]
            y_min = box[1]
            x_max = box[2]
            y_max = box[3]
            convert_bbox.append([[x_min, y_min], [x_max, y_min], [x_max, y_max], [x_min, y_max]])
        polygon = convert_bbox
    hsv_tuples = [(1.0 * x / len(polygon), 1., 1.) for x in range(len(polygon))]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    colors = list(map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), colors))
    image_white = None
    if image_size is None:
        image_size = [500, 500]
    if image_file is None:
        image = Image.new('RGBA', (image_size[0], image_size[1]), (255, 255, 255))
        draw = ImageDraw.ImageDraw(image)
    else:
        if isinstance(image_file, Path) or isinstance(image_file, str):
            image = Image.open(image_file)
        else:
            image = Image.fromarray(image_file)
        if image.mode != "RGBA":
            image = image.convert('RGBA')
        image_white = Image.new('RGBA', (image.width, image.height), (255, 255, 255, 0))
        draw = ImageDraw.ImageDraw(image_white)
    for index, point in enumerate(polygon):
        draw_p = [(p[0], p[1]) for p in point]
        # 边框颜色
        polygon_color = colors[index]
        # 填充颜色+透明
        file_color = (polygon_color[0], polygon_color[1], polygon_color[2], fill_transparent) if fill_transparent > -1 else None
        draw.polygon(draw_p, outline=polygon_color, fill=file_color)
        if texts:
            text = texts[index]
        else:
            text = str(index)
        if font:
            draw.text(xy=(draw_p[0][0]+1, draw_p[0][1]+1), text=text, fill=draw_text_color, font=font)
        else:
            draw.text(xy=(draw_p[0][0] + 1, draw_p[0][1] + 1), text=text, fill=draw_text_color)
    if image_white is not None:
        image.paste(Image.alpha_composite(image, image_white))
    if show:
        image.show()
    if image.mode == "RGBA":
        image = image.convert('RGB')
    return image


if __name__ == "__main__":
    # draw_rectangle([(218, 376, 291, 443)])
    # draw_polygon([[[255, 376], [291, 409], [255, 443], [218, 409]], [[252, 140], [300, 140], [300, 189], [252, 189]]])
    draw_polygon([[3796.740478515625, 968.7546997070312, 4216.4248046875, 1528.115478515625], [3857.1689453125, 272.2844543457031, 4227.78271484375, 799.551513671875]])
    pass
