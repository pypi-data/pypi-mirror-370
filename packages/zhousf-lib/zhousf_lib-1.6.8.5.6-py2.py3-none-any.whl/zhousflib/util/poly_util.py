# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as mpathes
from shapely import geometry
from shapely.geometry import Polygon

"""
[question]
Backend TkAgg is interactive backend. Turning interactive mode on.
[solution]
import matplotlib
matplotlib.use('TkAgg')
"""


def in_poly(poly, point):
    """
    判断点是否在poly内，不包含poly边界
    :param poly: 多边形点坐标：[(0, 0), (1, 0), (1, 1), (0, 1)]
    :param point: 点坐标：(0.1, 0.5)
    :return:
    """
    line = geometry.LineString(poly)
    point = geometry.Point(point)
    polygon = geometry.Polygon(line)
    return polygon.contains(point)


def make_mesh(box_min, min_box_w, min_box_h, show=False):
    """
    按照w,h对box进行网格划分
    make_mesh([0, 0, 1280, 1280], 128, 128)
    :param box_min:
    :param min_box_w:
    :param min_box_h:
    :param show:
    :return:
    所有小box，按列排序 [(column_index, row_index, x_min, y_min, x_max, y_max)]
    column_index:列索引
    row_index:行索引
    """
    [x_min, y_min, x_max, y_max] = box_min
    list_x = np.arange(x_min, x_max, min_box_w)
    list_y = np.arange(y_min, y_max, min_box_h)
    # list_x中第i项和list_y中第j项所代表的网格为[list_x[i],list_y[j],list_x[i+1],list_y[j+1]]
    if show:
        fig, ax = plt.subplots()
        color = ['red', 'black', 'yellow', 'blue', 'green', 'purple']
    box_min = []  # x_min, y_min, x_max, y_max
    for i in range(len(list_x)):
        for j in range(len(list_y)):
            x_left = list_x[i]
            y_down = list_y[j]
            if i == len(list_x) - 1:
                x_right = x_max
            else:
                x_right = list_x[i + 1]
            if j == len(list_y) - 1:
                yup = y_max
            else:
                yup = list_y[j + 1]
            box_min.append((i, j, x_left, y_down, x_right, yup))
            if show:
                rect = mpathes.Rectangle((x_left, y_down), min_box_w, min_box_h, linewidth=1, edgecolor='r', facecolor='none')
                # rect = mpathes.Rectangle((x_left, y_down), min_box_w, min_box_h, color=color[(i + j % 5) % 5])
                ax.add_patch(rect)
    if show:
        ax.set_xbound(x_min, x_max)
        ax.set_ybound(y_min, y_max)
        plt.show()
    return box_min


def query_box_position(boxes, point):
    """
    # 查询point在哪个box中
    :param boxes:
    :param point:
    :return: (column_index, row_index, x_min, y_min, x_max, y_max)
    column_index:列索引
    row_index:行索引
    """
    for box in boxes:
        column_index, row_index, x_min, y_min, x_max, y_max = box
        # 将box外扩1个像素，使poly计算包含边界
        x_min -= 1
        y_min -= 1
        x_max += 1
        y_max += 1
        # 计算poly坐标
        poly = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
        # 判断点是否在poly内，不包含poly边界
        if in_poly(poly=poly, point=point):
            return box
    return None


def poly_area(points: list):
    """
    计算多边形的面积
    :param points:
    :return:
    """
    poly = Polygon(points)
    return poly.area


if __name__ == "__main__":
    # 判断点是否在poly内
    # poly = [(0, 0), (1, 0), (1, 1), (0, 1)]  # 多边形坐标
    # pt2 = (0.1, 0.5)  # 点坐标
    # print(in_poly(square, pt1))
    # 按照w,h对box进行网格划分
    # boxes_ = make_mesh([0, 0, 4000, 5000], 1280, 1280, show=True)
    # for box in boxes_:
    #     print(box)
        # [(column_index, row_index, x_min, y_min, x_max, y_max)]
    # 查询点在哪个box中
    # query_box_position(boxes=boxes_, point=(1, 1))
    print(poly_area([(0, 0), (0, 10), (10, 10), (10, 0)]))
    pass
