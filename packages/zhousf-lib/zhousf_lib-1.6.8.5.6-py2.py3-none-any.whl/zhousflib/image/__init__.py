# -*- coding:utf-8 -*-
# Author:  zhousf
# Description:
import cv2
import numpy as np
from typing import Union
from pathlib import Path

"""
图像的高频信息、低频信息
低频信息：代表着图像中亮度/灰度值/颜色变化很缓慢的区域，描述了图像的主要部分，是对整幅图像强度的综合度量
高频信息：对应着图像变化剧烈的部分，也就是图像的边缘/轮廓、噪声以及细节部分，主要是对图像边缘/轮廓的度量，而人眼对高频分量比较敏感
"""


def write(image: np.ndarray, img_write_path: Path):
    """
    写图片-兼容图片路径包含中文
    :param image:
    :param img_write_path:
    :return:
    """
    cv2.imencode(img_write_path.suffix, image[:, :, ::-1])[1].tofile(str(img_write_path))


def read(img_path: Union[str, Path, np.ndarray], bg_to_white=False, overwrite=False) -> np.ndarray:
    """
    读图片-兼容图片路径包含中文
    :param img_path:
    :param bg_to_white: 是否将图片的透明背景转成白色背景
    :param overwrite: 是否覆盖原图，如果为True，则会将处理后的图片覆盖原图
    :return: np.ndarray
    """
    if isinstance(img_path, str):
        img_path = Path(img_path)
    if isinstance(img_path, Path):
        if bg_to_white:
            img_arr = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            if img_arr is not None and img_arr.ndim > 2 and img_arr.shape[2] == 4:
                alpha_channel = img_arr[:, :, :3].copy()
                # 找到非255且非0的像素点（半透明像素）
                transparent_mask = (alpha_channel != 255) & (alpha_channel != 0)
                if np.any(transparent_mask):
                    # 将透明像素设为白色
                    alpha_channel[transparent_mask] = [255, 255, 255]
                    img_arr = alpha_channel
                if overwrite:
                    write(img_arr, img_path)
        else:
            img_arr = cv2.imdecode(np.fromfile(str(img_path), dtype=np.uint8), cv2.IMREAD_COLOR)
        return img_arr
    return img_path


def is_transparent(img_path: Path):
    """
    判断图片是否透明背景
    :param img_path:
    :return:
    """
    img = cv2.imdecode(np.fromfile(str(img_path), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if img is not None and img.shape[2] == 4:
        alpha_channel = img[:, :, 3]
        if cv2.countNonZero(alpha_channel) < alpha_channel.size:
            return True
    return False


def transparent_bg_to_white(img_path: Path, save_path: Path = None):
    """
    图片透明背景转成白色背景
    :param img_path:
    :param save_path:
    :return:
    """
    img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if img is not None and len(img.shape) > 2 and img.shape[2] == 4:
        alpha_channel = img[:, :, 3]
        if cv2.countNonZero(alpha_channel) < alpha_channel.size:
            b_channel, g_channel, r_channel, a_channel = cv2.split(img)
            white_background = np.ones_like(a_channel) * 255
            a_channel = a_channel / 255.0
            r_channel = r_channel * a_channel + white_background * (1 - a_channel)
            g_channel = g_channel * a_channel + white_background * (1 - a_channel)
            b_channel = b_channel * a_channel + white_background * (1 - a_channel)
            result = cv2.merge((b_channel, g_channel, r_channel))
            if save_path is not None:
                write(result, save_path)
            return result
    return img


def is_pure_color(image: Union[str, Path, np.ndarray], bg_to_white=False, contain_half_transparency=False, overwrite=False):
    """
    判断图片是否为纯色
    :param image: 可以是图片路径或numpy数组
    :param bg_to_white: 是否将背景色转换为白色
    :param contain_half_transparency: 是否包含半透明像素，如果为True，则会将半透明像素处理成白色背景，如果为False，则只处理全透明像素
    :param overwrite: 是否覆盖原图，如果为True，则会将处理后的图片覆盖原图
    """
    if not isinstance(image, np.ndarray):
        image = read(image, bg_to_white=bg_to_white, contain_half_transparency=contain_half_transparency, overwrite=overwrite)
    """
    获取图片左上角第一个像素点的颜色值: image[0, 0]，判断整个图片的颜色值是否都与左上角第一个像素点的颜色值相同
    例如：如果图片是纯白色，则image[0, 0]的值为[255, 255, 255]，如果整个图片都是纯白色，则np.all(image[0, 0] == image)将返回True
    这种方法的时间复杂度为O(n)，其中n为图片的像素数量
    这种方法的空间复杂度为O(1)，因为只需要存储一个像素点的颜色值
    优势：简单高效，时间复杂度低，空间复杂度低
    局限性：依赖于左上角像素作为参考，如果左上角像素恰好是噪声点，可能误判，对于有轻微噪声的图片可能不够鲁棒
    """
    return np.all(image[0, 0] == image)


def get_image_colors(image: Union[str, Path, np.ndarray], bg_to_white=False) -> int:
    """
    获取图片的颜色数量
    :param image: 可以是图片路径或numpy数组
    :param bg_to_white: 是否将背景色转换为白色
    :return: int
    """
    image_arr = read(image, bg_to_white)
    if image_arr.ndim == 2:  # 灰度图
        return len(np.unique(image_arr))
    elif image_arr.ndim == 3:  # 彩色图
        colors = np.unique(image_arr.reshape(-1, image_arr.shape[-1]), axis=0)
        return len(colors)
    else:
        return 0

