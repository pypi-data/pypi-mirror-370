# -*- coding: utf-8 -*-
# @Author  : zhousf-a
# @Function:
import colorsys
from typing import Any, List, Tuple


def generate_rgb_colors(count: int) -> List:
    """
    生成RGB颜色列表
    :param count: 生成颜色数量
    :return:  [(255, 0, 0), (203, 255, 0), (0, 255, 102), (0, 102, 255), (204, 0, 255)]
    """
    hsv_tuples = [(1.0 * x / count, 1., 1.) for x in range(count)]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    colors = list(map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), colors))
    return colors


def rgb_to_hex(rgb: Any):
    if isinstance(rgb, Tuple):
        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
    if isinstance(rgb, List):
        return ['#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2]) for color in rgb]


def generate_hex_colors(count: int):
    """
    生成HEX颜色列表
    :param count: 生成颜色数量
    :return: ['#ff0000', '#cbff00', '#00ff66', '#0066ff', '#cc00ff']
    """
    rgb_colors = generate_rgb_colors(count)
    return rgb_to_hex(rgb_colors)



