# -*- coding:utf-8 -*-
# Author:  zhousf
# Description: 目标检测bbox计算工具
# pip install matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from zhousflib.util import math_util

"""
[question]
Backend TkAgg is interactive backend. Turning interactive mode on.
[solution]
import matplotlib
matplotlib.use('TkAgg')
"""


def show_rect(boxes: list):
    """
    显示box
    :param boxes: [(x_min, y_min, x_max, y_max)]
    :return:
    [(317,280,553,395), (374,295,485,322)]
    """
    colors = list(mcolors.TABLEAU_COLORS.keys())
    plt.xlabel("x", fontweight='bold', size=14)
    plt.ylabel("y", fontweight='bold', size=14)
    ax = plt.gca()  # 坐标系
    x_max = 0
    y_max = 0
    for index, box in enumerate(boxes):
        x_max = box[2] if box[2] > x_max else x_max
        y_max = box[3] if box[3] > y_max else y_max
        ax.add_patch(
            plt.Rectangle(xy=(box[0], box[1]), width=(box[2] - box[0]), height=(box[3] - box[1]),
                          alpha=1,
                          fill=False,
                          color=colors[index],
                          facecolor=colors[index],
                          linewidth=1))
    plt.xlim(0, int(2 * x_max))
    plt.ylim(0, int(2 * y_max))
    # 转成屏幕坐标系（左上角为原点）
    ax.xaxis.set_ticks_position('top')  # 将X坐标轴移到上面
    ax.invert_yaxis()  # 反转Y坐标轴
    plt.show()


def compute_iou(predicted_box, ground_truth_box):
    """
    计算交并比
    :param predicted_box: 预测box=(x_min, y_min, x_max, y_max)
    :param ground_truth_box: 真实box=(x_min, y_min, x_max, y_max)
    :return:
    """
    px_min, py_min, px_max, py_max = predicted_box
    gx_min, gy_min, gx_max, gy_max = ground_truth_box
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
    return area / (p_area + g_area - area)


def compute_contain(box1, box2):
    """
    计算两个box是否为包含关系
    :param box1: (x_min, y_min, x_max, y_max)
    :param box2: (x_min, y_min, x_max, y_max)
    :return: 返回两个box重叠面积占较小box的面积比，一般大于0.8则为包含关系
    box1=(317,280,553,395)
    box2=(374,295,485,322)
    """
    px_min = min(box1[0], box1[2])
    py_min = min(box1[1], box1[3])
    px_max = max(box1[0], box1[2])
    py_max = max(box1[1], box1[3])
    # px_min, py_min, px_max, py_max = box1
    # gx_min, gy_min, gx_max, gy_max = box2
    gx_min = min(box2[0], box2[2])
    gy_min = min(box2[1], box2[3])
    gx_max = max(box2[0], box2[2])
    gy_max = max(box2[1], box2[3])
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


def group_by_box_overlap(od_result: list, return_area=False, area_rate=0.8):
    """
    根据box的重叠面积进行分组-通用算法，适用目标检测、画图等
    :param od_result: [(?, ?, x_min, y_min, x_max, y_max)], box置于tuple最后
    :param return_area: 是否返回面积
    :param area_rate: 两个box重叠面积比例，若大于该值则为包含关系
    :return:
    [[(index, [area, (?, ?, x_min, y_min, x_max, y_max)])]]
    or
    [[(?, ?, x_min, y_min, x_max, y_max)]]
    """
    boxes = {}
    # 按照面积从大到小排序, box置于tuple最后
    for index, item in enumerate(od_result):
        (x_min, y_min, x_max, y_max) = item[-4:]
        area = (x_max - x_min) * (y_max - y_min)
        boxes[index] = [area, item]
    boxes = sorted(boxes.items(), key=lambda d: d[1], reverse=True)
    box_group = []
    has_add_index = []
    for item1 in boxes:
        (index1, [area1, box1]) = item1
        (x_min1, y_min1, x_max1, y_max1) = box1[-4:]
        items = [item1] if return_area else [box1]
        if index1 in has_add_index:
            continue
        has_add_index.append(index1)
        for i, item2 in enumerate(boxes):
            (index2, [area2, box2]) = item2
            (x_min2, y_min2, x_max2, y_max2) = box2[-4:]
            if compute_contain((x_min1, y_min1, x_max1, y_max1),
                               (x_min2, y_min2, x_max2, y_max2)) > area_rate:
                if item1 == item2:
                    continue
                if index2 in has_add_index:
                    continue
                has_add_index.append(index2)
                if return_area:
                    items.append(item2)
                else:
                    items.append(box2)
        box_group.append(items)
    return box_group


def search_right_box(boxes: list):
    """
    搜索最右侧box
    :param boxes: [(?, ?, x_min, y_min, x_max, y_max)]
    :return: box
    """
    if len(boxes) == 0:
        return None
    boxes.sort(key=lambda x: x[-2], reverse=True)
    return boxes[0]


def search_top_box(boxes: list):
    """
    搜索最顶端box
    :param boxes: [(?, ?, x_min, y_min, x_max, y_max)]
    :return: box
    """
    if len(boxes) == 0:
        return None
    boxes.sort(key=lambda x: x[-3], reverse=False)
    return boxes[0]


def search_bottom_box(boxes: list):
    """
    搜索最底端box
    :param boxes: [(?, ?, x_min, y_min, x_max, y_max)]
    :return: box
    """
    if len(boxes) == 0:
        return None
    boxes.sort(key=lambda x: x[-1], reverse=True)
    return boxes[0]


def search_nearby_bottom_box(target_box, boxes: list):
    """
    搜索紧邻target_box底部的box
    :param target_box: (?, ?, x_min, y_min, x_max, y_max)
    :param boxes: [(?, ?, x_min, y_min, x_max, y_max)]
    :return: box
    """
    if len(boxes) == 0:
        return None
    t_x = (target_box[-2] + target_box[-4]) / 2
    t_y = (target_box[-3] + target_box[-1]) / 2
    t_width = abs(target_box[-2] - target_box[-4])
    t_height = abs(target_box[-3] - target_box[-1])
    boxes = sorted(boxes, key=lambda v: v[-3], reverse=False)
    for box in boxes:
        c_x = (box[-2] + box[-4]) / 2
        c_y = (box[-3] + box[-1]) / 2
        c_width = abs(box[-2] - box[-4])
        c_height = abs(box[-3] - box[-1])
        # 两个中心点的X轴坐标差不超过两个box的高度和的一半，表示两个box在同一垂直线上
        if abs(c_x-t_x) < (t_width + c_width) / 2:
            if t_y < c_y:
                return box
    return None


def search_nearby_right_box(target_box, boxes: list):
    """
    搜索紧邻target_box右侧的box
    :param target_box: (?, ?, x_min, y_min, x_max, y_max)
    :param boxes: [(?, ?, x_min, y_min, x_max, y_max)]
    :return: box
    """
    if len(boxes) == 0:
        return None
    t_x = (target_box[-2] + target_box[-4]) / 2
    t_y = (target_box[-3] + target_box[-1]) / 2
    t_width = abs(target_box[-2] - target_box[-4])
    t_height = abs(target_box[-3] - target_box[-1])
    boxes = sorted(boxes, key=lambda v: v[-4], reverse=False)
    for box in boxes:
        c_x = (box[-2] + box[-4]) / 2
        c_y = (box[-3] + box[-1]) / 2
        c_width = abs(box[-2] - box[-4])
        c_height = abs(box[-3] - box[-1])
        # 两个中心点的Y轴坐标差不超过两个box的高度和的一半，表示两个box在同一水平线上
        if abs(c_y-t_y) < (t_height + c_height) / 2:
            if t_x < c_x:
                return box
    return None


def search_nearby_left_box(target_box, boxes: list):
    """
    搜索紧邻target_box左侧的box
    :param target_box: (?, ?, x_min, y_min, x_max, y_max)
    :param boxes: [(?, ?, x_min, y_min, x_max, y_max)]
    :return: box
    """
    if len(boxes) == 0:
        return None
    t_x = (target_box[-2] + target_box[-4]) / 2
    t_y = (target_box[-3] + target_box[-1]) / 2
    t_width = abs(target_box[-2] - target_box[-4])
    t_height = abs(target_box[-3] - target_box[-1])
    boxes = sorted(boxes, key=lambda v: v[-4], reverse=True)
    for box in boxes:
        c_x = (box[-2] + box[-4]) / 2
        c_y = (box[-3] + box[-1]) / 2
        c_width = abs(box[-2] - box[-4])
        c_height = abs(box[-3] - box[-1])
        # 两个中心点的Y轴坐标差不超过两个box的高度和的一半，表示两个box在同一水平线上
        if abs(c_y-t_y) < (t_height + c_height) / 2:
            if t_x > c_x:
                return box
    return None


def search_nearby_box(target_box, boxes: list, top=1) -> list:
    """
    搜索紧邻target_box的box，以box中心点计算
    :param target_box: (?, ?, x_min, y_min, x_max, y_max)
    :param boxes: [(?, ?, x_min, y_min, x_max, y_max)]
    :param top: 返回紧邻的top个box，按照距离从小到大排序
    :return: box
    """
    if len(boxes) == 0:
        return []
    t_x = (target_box[-2] + target_box[-4]) / 2
    t_y = (target_box[-3] + target_box[-1]) / 2
    boxes = sorted(boxes, key=lambda v: v[-4], reverse=True)
    boxes_list = []
    for box in boxes:
        c_x = (box[-2] + box[-4]) / 2
        c_y = (box[-3] + box[-1]) / 2
        # 计算两个box的中心点距离
        distance = math_util.get_distance_from_point_to_point((t_x, t_y), (c_x, c_y))
        boxes_list.append((distance, box))
    boxes_list = sorted(boxes_list, key=lambda v: v[0], reverse=False)
    return boxes_list[0:top]


def box_scale_up(box, offset=50):
    """
    box增大
    :param box:
    :param offset:
    :return:
    """
    x_min, y_min, x_max, y_max = box
    _x_min = x_min - offset
    _x_min = 0 if _x_min < 0 else _x_min
    _x_max = x_max + offset
    _y_min = y_min - offset
    _y_min = 0 if _y_min < 0 else _y_min
    _y_max = y_max + offset
    return _x_min, _y_min, _x_max, _y_max


def box_scale_up_horizontal(box, offset=50):
    """
    box增大，仅水平方向
    :param box:
    :param offset:
    :return:
    """
    x_min, y_min, x_max, y_max = box
    _x_min = x_min - offset
    _x_min = 0 if _x_min < 0 else _x_min
    _x_max = x_max + offset
    return _x_min, y_min, _x_max, y_max


def box_scale_up_vertical(box, offset=50):
    """
    box增大，仅垂直方向
    :param box:
    :param offset:
    :return:
    """
    x_min, y_min, x_max, y_max = box
    _y_min = y_min - offset
    _y_min = 0 if _y_min < 0 else _y_min
    _y_max = y_max + offset
    return x_min, _y_min, x_max, _y_max


def box_scale_down(box, offset=50):
    """
    box缩小
    :param box:
    :param offset:
    :return:
    """
    x_min, y_min, x_max, y_max = box
    offset = min(x_min, y_min) if min(x_min, y_min) < offset else offset
    _x_min = x_min + offset
    _x_max = x_max - offset
    _y_min = y_min + offset
    _y_max = y_max - offset
    return _x_min, _y_min, _x_max, _y_max


def location_y_axis(target_box, box, height_threshold=0.25):
    """
    y轴位置关系判断，判断box在target_box的上面还是下面，通过中心点的y计算
    :param target_box:
    :param box:
    :param height_threshold: 阈值比，若大于target_box该比例的高度，则位置不同
    :return: 1: 上面   0: 下面   -1: 位置相同
    """
    c_y_t = (target_box[-3] + target_box[-1]) / 2
    height_t = abs(target_box[-3] - target_box[-1])
    c_y = (box[-3] + box[-1]) / 2
    # 两个中心点的Y轴坐标差超过target_box高度*height_threshold，表示两个box在target_box上面
    if abs(c_y_t - c_y) >= (height_t * height_threshold):
        if c_y_t > c_y:
            return 1
        else:
            return 0
    else:
        return -1


if __name__ == "__main__":
    # print(box_scale_down((10, 10, 20, 20), offset=2))
    # print(box_scale_up((-166.68197631835938, -0.008893102407455444, 1810.6822509765625, 143.40452575683594), offset=2))
    # a =(168.9995880126953, 40.77224349975586, 186.8643341064453, 62.222076416015625)
    # b =(151.0, 34.0, 234.0, 77.0)
    # print(compute_iou(a, b))
    # print(compute_contain(a, b))
    # show_rect([a, b])
    txt_box = ['0', None, None, 'L3', 0.009990513324737549, 549, 44, 604, 85]
    box_steel_id = [None, '3', 0.926153838634491, '编号', 0.8614592552185059, 638.6162719726562, 13.244131088256836, 690.3391723632812, 66.04812622070312]
    print(location_y_axis(box_steel_id, txt_box))

    pass
