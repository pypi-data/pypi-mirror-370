# -*- coding:utf-8 -*-
# Author:  zhousf
# Description: 最大连通域计算、删除图片边缘的像素块
from pathlib import Path

import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

from zhousflib.font import Font_SimSun
from zhousflib.image import pil_util
from zhousflib.image.cv import get_binary


def max_connectivity_domain(mask_arr: np.array, connectivity=4) -> np.array:
    """
    返回掩码中最大的连通域
    :param mask_arr: 二维数组，掩码中0表示背景，1表示目标
    :param connectivity: 4|8 4邻接还是8邻接
    :return:
    """
    # 掩码标识转换
    arr_mask = np.where(mask_arr == 1, 255, 0)
    # 掩码类型转换
    arr_mask = arr_mask.astype(dtype=np.uint8)
    """
    connectivity：可选值为4或8，也就是使用4连通还是8连通
    num：所有连通域的数目
    labels：图像上每一像素的标记，用数字1、2、3…表示（不同的数字表示不同的连通域）
    stats：每一个标记的统计信息，是一个5列的矩阵，每一行对应每个连通区域的外接矩形的x、y、width、height和面积，示例：0 0 720 720 291805
    centroids：连通域的中心点
    """
    nums, labels, stats, centroids = cv2.connectedComponentsWithStats(arr_mask, connectivity=connectivity)
    background = 0
    for row in range(stats.shape[0]):
        if stats[row, :][0] == 0 and stats[row, :][1] == 0:
            background = row
    # 删除背景后的连通域列表
    stats_no_bg = np.delete(stats, background, axis=0)
    if len(stats_no_bg) == 0:
        return stats_no_bg
    # 获取连通域最大的索引
    max_idx = stats_no_bg[:, 4].argmax()
    max_region = np.where(labels == max_idx + 1, 1, 0)
    # 保存
    # cv2.imwrite(r'vis.jpg', max_region * 255)
    return max_region


def filter_pixels_at_edges(image_path: Path, save_image_path: Path = None, distance_at_edges=20, show=False, **kwargs):
    """
    删除图片边缘的像素块
    :param image_path: 待处理图片路径
    :param save_image_path: 保存删除后的图片路径
    :param distance_at_edges: 像素块离图片边缘的距离，小于该值则判定该像素块是边缘上的
    :param show: 显示边缘上的像素块
    :param kwargs: 二值化参数
    :return:
    filter_pixels_at_edges(image_path=Path(r'0.jpg'), save_image_path=Path(r'0-1.jpg'), show=False)
    """
    binary = get_binary(image_path=image_path, **kwargs)
    img_height, img_width = binary.shape
    # 掩码标识转换
    arr_mask = np.where(binary == 0, 255, 0)
    # 掩码类型转换
    arr_mask = arr_mask.astype(dtype=np.uint8)
    nums, labels, stats, centroids = cv2.connectedComponentsWithStats(arr_mask, connectivity=4)
    background = 0
    for row in range(stats.shape[0]):
        if stats[row, :][0] == 0 and stats[row, :][1] == 0:
            background = row
    # 删除背景后的连通域列表
    stats_no_bg = np.delete(stats, background, axis=0).tolist()
    centroids_no_bg = np.delete(centroids, background, axis=0).tolist()
    domain_list = []
    boxes = []
    for i in range(0, len(stats_no_bg)):
        box_x, box_y, box_width, box_height, area = stats_no_bg[i]
        center_point_x, center_point_y = centroids_no_bg[i]
        domain_list.append((center_point_x, center_point_y, box_x, box_y, box_width, box_height, area))
        x_min = box_x
        y_min = box_y
        x_max = x_min + box_width
        y_max = y_min + box_height
        boxes.append((i, area, center_point_x, center_point_y, x_min, y_min, x_max, y_max))
    boxes = sorted(boxes, key=lambda v: v[1], reverse=True)
    for i in range(len(boxes) - 1, -1, -1):
        index, area, center_point_x, center_point_y, x_min, y_min, x_max, y_max = boxes[i]
        # 过滤在图片边缘的文字
        if abs(img_width - center_point_x) < distance_at_edges or abs(img_height - center_point_y) < distance_at_edges \
                or center_point_y < distance_at_edges or center_point_x < distance_at_edges:
            pass
        else:
            boxes.pop(i)
    img_vis = pil_util.draw_rectangle(bbox=boxes, image_file=image_path, fill_transparent=100, show=False,
                                      font=ImageFont.truetype(font=str(Font_SimSun), size=20, encoding="utf-8"))
    """
    删除像素
    """
    image = Image.open(image_path)
    if image.mode != "RGB":
        image = image.convert('RGB')
    draw = ImageDraw.Draw(image)
    for i in range(len(boxes) - 1, -1, -1):
        index, area, center_point_x, center_point_y, x_min, y_min, x_max, y_max = boxes[i]
        # 将box以白色填充
        draw.rectangle((x_min, y_min, x_max, y_max), fill=(255, 255, 255))
    if show:
        plt.figure(figsize=(16, 9))
        plt.subplot(131)
        plt.imshow(Image.open(image_path))
        plt.title("input")
        plt.subplot(132)
        plt.imshow(img_vis)
        plt.title("pixels_at_edges")
        plt.subplot(133)
        plt.imshow(image)
        plt.title("output")
        plt.show()
        plt.close("all")
    if save_image_path is not None:
        image.save(save_image_path, quality=100)
    return image


def filter_pixels_by_area(image_path: Path, save_image_path: Path = None, block_area=100, show=False, **kwargs):
    """
    根据像素块面积删除图片的像素块
    :param image_path: 待处理图片路径
    :param save_image_path: 保存删除后的图片路径
    :param block_area: 删除像素块的面积阈值，小于该值则删除该像素块
    :param show: 显示边缘上的像素块
    :param kwargs: 二值化参数
    :return:
    """
    binary = get_binary(image_path=image_path, **kwargs)
    # 掩码标识转换
    arr_mask = np.where(binary == 0, 255, 0)
    # 掩码类型转换
    arr_mask = arr_mask.astype(dtype=np.uint8)
    nums, labels, stats, centroids = cv2.connectedComponentsWithStats(arr_mask, connectivity=4)
    background = 0
    for row in range(stats.shape[0]):
        if stats[row, :][0] == 0 and stats[row, :][1] == 0:
            background = row
    # 删除背景后的连通域列表
    stats_no_bg = np.delete(stats, background, axis=0).tolist()
    centroids_no_bg = np.delete(centroids, background, axis=0).tolist()
    domain_list = []
    boxes = []
    for i in range(0, len(stats_no_bg)):
        box_x, box_y, box_width, box_height, area = stats_no_bg[i]
        center_point_x, center_point_y = centroids_no_bg[i]
        domain_list.append((center_point_x, center_point_y, box_x, box_y, box_width, box_height, area))
        x_min = box_x
        y_min = box_y
        x_max = x_min + box_width
        y_max = y_min + box_height
        boxes.append((i, area, center_point_x, center_point_y, x_min, y_min, x_max, y_max))
    boxes = sorted(boxes, key=lambda v: v[1], reverse=True)
    for i in range(len(boxes) - 1, -1, -1):
        index, area, center_point_x, center_point_y, x_min, y_min, x_max, y_max = boxes[i]
        if area > block_area:
            boxes.pop(i)
    img_vis = pil_util.draw_rectangle(bbox=boxes, image_file=image_path, fill_transparent=100, show=False,
                                      font=ImageFont.truetype(font=str(Font_SimSun), size=20, encoding="utf-8"))
    """
    删除像素
    """
    image = Image.open(image_path)
    if image.mode != "RGB":
        image = image.convert('RGB')
    draw = ImageDraw.Draw(image)
    for i in range(len(boxes) - 1, -1, -1):
        index, area, center_point_x, center_point_y, x_min, y_min, x_max, y_max = boxes[i]
        # 将box以白色填充
        draw.rectangle((x_min, y_min, x_max, y_max), fill=(255, 255, 255))
    if show:
        plt.figure(figsize=(16, 9))
        plt.subplot(131)
        plt.imshow(Image.open(image_path))
        plt.title("input")
        plt.subplot(132)
        plt.imshow(img_vis)
        plt.title("pixels_at_edges")
        plt.subplot(133)
        plt.imshow(image)
        plt.title("output")
        plt.show()
        plt.close("all")
    if save_image_path is not None:
        image.save(save_image_path, quality=100)
    return image


if __name__ == "__main__":
    filter_pixels_at_edges(image_path=Path(r'C:\Users\zhousf-a\Desktop\0.jpg'), show=True)
    # filter_pixels_by_area(image_path=Path(r'C:\Users\zhousf-a\Desktop\0.jpg'), show=True)
    pass
