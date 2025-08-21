# -*- coding:utf-8 -*-
# Author:      zhousf
# Date:        2019-05-30
# File:        math_util.py
# Description:
import math


def get_distance_from_point_to_point(point_first, point_second):
    """
    计算点到点的距离
    :param point_first:
    :param point_second:
    :return:
    """
    (p_x1, p_y1) = point_first
    (p_x2, p_y2) = point_second
    x = p_x1 - p_x2
    y = p_y2 - p_y1
    # 用math.sqrt求平方根 x**2->幂运算
    return math.sqrt((x**2) + (y**2))


def get_distance_from_point_to_line(point, line_first_point, line_second_point):
    """
    计算点到线的距离
    :param point:
    :param line_first_point:
    :param line_second_point:
    :return:
    """
    (point_x, point_y) = point
    (first_point_x, first_point_y) = line_first_point
    (second_point_x, second_point_y) = line_second_point
    a = second_point_y-first_point_y
    b = first_point_x-second_point_x
    c = second_point_x*first_point_y-first_point_x*second_point_y
    dis = (math.fabs(a*point_x+b*point_y+c)) / (math.pow(a*a+b*b, 0.5))
    return dis


if __name__ == '__main__':
    point = (0, 0)
    line_first_point = (-1, 1)
    line_second_point = (1, 1)
    # point = (269, 19)
    # line_first_point = (387, 24)
    # line_second_point = (228, 24)
    print(get_distance_from_point_to_line(point, line_first_point, line_second_point))
    # print(get_distance_from_point_to_point((47,196),(287,318)))