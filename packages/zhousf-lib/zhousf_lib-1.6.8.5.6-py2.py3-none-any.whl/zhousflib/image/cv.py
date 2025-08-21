# -*- coding:utf-8 -*-
# Author:  zhousf
# Description:
import cv2
import numpy as np
from pathlib import Path

from zhousflib.decorator import interceptor_util


def get_binary(image_path: Path, **kwargs):
    """
    获取二值化
    :param image_path:
    :param kwargs: 二值化参数
    :return:
    """
    assert image_path.exists(), "image file is not exists: {0}".format(image_path)
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    assert img is not None, "image is None"
    if len(kwargs) > 0:
        binary = cv2.adaptiveThreshold(src=img, **kwargs)
    else:
        binary = cv2.adaptiveThreshold(src=img,
                                       maxValue=255,  # 大于阈值后设定的值
                                       adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C,  # 自适应方法
                                       thresholdType=cv2.THRESH_BINARY,  # 同全局阈值法中的参数一样
                                       blockSize=11,  # 方阵（区域）大小
                                       C=15)  # 常数项
    return binary


def rotate(image, angle, show=False):
    """
    顺时针旋转图片
    :param image: 图片
    :param angle: 旋转角度
    :param show: 是否显示
    :return: np.array
    """
    if isinstance(image, str):
        image = cv2.imread(image)
    if isinstance(image, np.ndarray):
        # grab the dimensions of the image and then determine the
        # center
        (h, w) = image.shape[:2]
        (cX, cY) = (w // 2, h // 2)

        # grab the rotation matrix (applying the negative of the
        # angle to rotate clockwise), then grab the sine and cosine
        # (i.e., the rotation components of the matrix)
        M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])

        # compute the new bounding dimensions of the image
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))

        # adjust the rotation matrix to take into account translation
        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY

        # perform the actual rotation and return the image
        rotated = cv2.warpAffine(image, M, (nW, nH))
        if show:
            cv2.imshow("{0} rotated".format(angle), rotated)
            cv2.waitKey(0)
        return rotated
    return None


def _read(chain):
    image, show = chain
    if isinstance(image, str):
        image = cv2.imread(image)
    if image is None:
        return True, image
    return False, (image, show)


def _show(chain):
    title, image, show = chain
    if show:
        cv2.imshow(title, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return image


"""
以下函数为示例函数
"""


@interceptor_util.intercept(before=_read, after=_show)
def img_binary(chain):
    """ 二值化 """
    image, show = chain
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    block_size = 11  # 分割计算的区域大小，取奇数
    binary_ = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, block_size, 15)
    return "binary", binary_, show


@interceptor_util.intercept(before=_read, after=_show)
def img_bilateral_filter(chain):
    """ 双边滤波 """
    image, show = chain
    bilateral_filter_ = cv2.bilateralFilter(image, 7, 75, 75)
    return "bilateral_filter", bilateral_filter_, show


@interceptor_util.intercept(before=_read, after=_show)
def img_erosion(chain):
    """ 腐蚀 """
    image, show = chain
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
    erosion_ = cv2.erode(image, kernel)
    return "erosion", erosion_, show


@interceptor_util.intercept(before=_read, after=_show)
def img_dilate(chain):
    """ 膨胀 """
    image, show = chain
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
    dilate_ = cv2.dilate(image, kernel)
    return "dilate", dilate_, show


@interceptor_util.intercept(before=_read, after=_show)
def img_clahe(chain):
    """ 直方图均衡化 """
    image, show = chain
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(5, 5))
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l2 = clahe.apply(l)
    lab = cv2.merge((l2, a, b))
    clahe_ = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return "clahe", clahe_, show


@interceptor_util.intercept(before=_read, after=_show)
def img_remove_background(chain):
    """ 去除背景 """
    image, show = chain
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 15)
    se = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    se = cv2.morphologyEx(se, cv2.MORPH_CLOSE, (2, 2))
    mask = cv2.dilate(binary, se)
    mask1 = cv2.bitwise_not(mask)
    binary = cv2.bitwise_and(image, mask)
    result = cv2.add(binary, mask1)
    return "remove_background", result, show


if __name__ == "__main__":
    image_file = r"C:\Users\zhousf-a\Desktop\0\07398c4c-efb238518a73537efa4b212fceaf7a6f_76_ero.jpg"
    image_file = cv2.imread(image_file, 0)
    # binary = img_binary(image_file, False)
    # dilate = img_dilate(binary, True)
    # erosion = img_erosion(dilate, True)
    # cv2.imwrite(r"C:\Users\zhousf-a\Desktop\0\3_vis_erosion.jpg", erosion)


