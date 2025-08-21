# -*- coding:utf-8 -*-
# Author:  zhousf
# Description: 相似度计算
# pip install imagehash
# pip install scikit-image
# pip install scikit-learn
import time
from pathlib import Path

import cv2
import imagehash
from PIL import Image
from sklearn import metrics
from skimage.metrics import structural_similarity
from skimage.metrics import mean_squared_error

from zhousflib.image import read

"""
【相似度算法】
（1）传统算法
· 均方误差(Mean Squared Error，MSE)：计算两张图片像素之间的差异，并将这些差异的平方求和，最后除以像素数量得到MSE。MSE值越小，图片越相似。MSE算法只考虑像素级别的差异，可能无法准确地捕捉图像的纹理、结构等细节。
· 结构相似性指数（Structural Similarity Index，SSIM）：通过比较两张图片的亮度、对比度和结构等方面的相似性，给图片打分。SSIM值在0到1之间，1表示两张图片完全相同。SSIM可以更好地检测出字形上的细微差异。
· 峰值信噪比（Peak Signal-to-Noise Ratio，PSNR）：计算两张图片像素之间的差异，并将这些差异的平方求和后再取对数。PSNR值越高，图片越相似。PSNR常常被用来评估图像压缩、图像处理、图像修复等技术的质量。
· 直方图比较（Histogram Comparison）：将两张图片的颜色直方图进行比较，以确定它们的相似程度。直方图只考虑了颜色分布而忽略了纹理和结构等因素。
· 感知哈希（Perceptual Hash，PHash）：通过对图片进行哈希算法，将图片转换为二进制字符串，然后比较字符串之间的汉明距离（Hamming Distance），以确定图片的相似度。哈希算法主要保留了低频分量，存在一定的局限性。
· 互信息：互信息是一种用于衡量两个随机变量之间相互依赖关系的指标，可以用于计算图片的相似度。互信息算法可能对图像的纹理、结构等细节不敏感。
· 特征匹配：使用SIFT/SURF/ORB等特征描述子代表图像特征，再使用欧氏距离/汉明距离等计算相似度指标来衡量两张图片的相似度，最后使用RANSAC等筛选算法提高匹配的准确性。
tips:
当应用场景的图片存在复印件或颜色变换时则不建议使用直方图算法
当应用场景的图片可能存在人为噪声时则不建议使用均方误差和峰值信噪比算法
效果参考：
互信息 -> 结构相似性指数 -> 均方误差 -> 峰值信噪比 -> 感知哈希 -> 直方图
（2）深度学习算法
· 孪生网络：例如人脸识别
· SimGNN：基于图神经网络（Graph Neural Network，GNN）的一种模型，用于处理图数据的相似度计算任务。常用于推荐系统中的物品相似度计算、文本匹配中的句子相似度计算等。
· Graph kernel：Graph kernels（图核）是一类用于计算图数据相似度的方法

【相似度度量算法】
· 余弦相似度：余弦相似度是一种常用的相似度计算方法，特别适用于文本数据的相似度计算。它通过计算两个向量的夹角余弦值来衡量它们之间的相似程度。夹角余弦值越接近1，表示两个向量越相似；夹角余弦值越接近0，表示两个向量越不相似。
· 欧氏距离：欧氏距离是一种用来衡量两个向量之间的距离的方法。它计算的是两个向量之间的直线距离，即两个向量之间的欧氏距离越小，表示它们之间的相似程度越高。
· 汉明距离：汉明距离是一种用来衡量两个等长字符串之间的差异的方法。它计算的是两个字符串之间对应位置不同的字符个数，即汉明距离越小，表示两个字符串越相似。
· 编辑距离：编辑距离是一种用来衡量两个字符串之间的差异的方法。它计算的是通过插入、删除和替换操作将一个字符串转换为另一个字符串所需要的最小操作次数，即编辑距离越小，表示两个字符串越相似。
· Jaccard杰卡德系数：Jaccard相似系数是一种用来衡量两个集合之间的相似性的方法。它计算的是两个集合交集的大小与并集的大小之间的比值，即Jaccard相似系数越大，表示两个集合越相似。
· Pearson皮尔逊相关系数：皮尔逊相关系数是一种用来衡量两个变量之间相关程度的方法。它计算的是两个变量之间的协方差与它们各自标准差的乘积之间的比值，即皮尔逊相关系数越接近1或-1，表示两个变量之间越相关。
"""


def ___read(image1: Path, image2: Path, resize: tuple = None, check_dimensions=True, gray=False):
    """
    :param image1:
    :param image2:
    :param resize:
    :param check_dimensions:
    :param gray:
    :return:
    """
    image1 = read(image1)
    image2 = read(image2)
    # 尺寸标准化
    if resize:
        image1 = cv2.resize(image1, resize)
        image2 = cv2.resize(image2, resize)
    # 灰度化
    if gray:
        image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    if check_dimensions:
        assert image1.shape == image2.shape, "Input images must have the same dimensions."
    return image1, image2


def compare_mse(image1: Path, image2: Path, resize: tuple = None):
    """
    计算均方误差比较相似度
    :param image1:
    :param image2:
    :param resize: 尺寸标准化
    :return:
    """
    image1, image2 = ___read(image1, image2, resize=resize, check_dimensions=True, gray=True)
    return mean_squared_error(image1, image2)


def compare_psnr(image1: Path, image2: Path, resize: tuple = None):
    """
    计算峰值信噪比
    :param image1:
    :param image2:
    :param resize: 尺寸标准化
    :return:
    """
    image1, image2 = ___read(image1, image2, resize=resize, check_dimensions=True, gray=True)
    # 亮度统一
    image1 = cv2.normalize(image1, None, 0, 255, cv2.NORM_MINMAX)
    image2 = cv2.normalize(image2, None, 0, 255, cv2.NORM_MINMAX)
    # from skimage.metrics import peak_signal_noise_ratio
    # return peak_signal_noise_ratio(image1, image2)  # 稳健性不如cv2
    return cv2.PSNR(image1, image2)


def compare_ssim(image1: Path, image2: Path, resize: tuple = None, show_diff=False):
    """
    计算结构相似性指数
    :param image1:
    :param image2:
    :param resize: 尺寸标准化
    :param show_diff: 显示结构不相似的区域
    :return:
    """
    image1, image2 = ___read(image1, image2, resize=resize, check_dimensions=True, gray=True)
    score, diff = structural_similarity(image1, image2, full=True)
    if show_diff:
        cv2.imshow("ssim", diff)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return score, diff


def compare_hist(image1: Path, image2: Path, resize: tuple = None):
    """
    计算直方图相似性
    :param image1:
    :param image2:
    :param resize: 尺寸标准化
    :return:
    """
    image1, image2 = ___read(image1, image2, resize=resize, check_dimensions=True, gray=True)
    hist1 = cv2.calcHist([image1], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0, 256])
    return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)


def compare_dhash(image1: Path, image2: Path, hash_size=8, resize: tuple[int, int] = None):
    """
    感知hash
    :param image1:
    :param image2:
    :param hash_size:
    :param resize: 尺寸标准化
    :return:
    """
    image1 = Image.open(image1)
    image2 = Image.open(image2)
    if resize:
        image1 = image1.resize(resize, resample=Image.BILINEAR)
        image2 = image2.resize(resize, resample=Image.BILINEAR)
    image1 = imagehash.average_hash(image1, hash_size=hash_size)
    image2 = imagehash.average_hash(image2, hash_size=hash_size)
    return hamming_distance(image1, image2, hash_size=hash_size)


def hamming_distance(hash1, hash2, hash_size=8):
    """
    汉明距离
    """
    distance = hash1 - hash2
    similarity = 1 - (distance / (hash_size * hash_size))
    return similarity


def compare_mutual_info(image1: Path, image2: Path, resize: tuple = None):
    """
    计算互信息相似度
    :param image1:
    :param image2:
    :param resize: 尺寸标准化
    :return:
    """
    image1, image2 = ___read(image1, image2, resize=resize, check_dimensions=True, gray=False)
    return metrics.normalized_mutual_info_score(image1.reshape(-1), image2.reshape(-1))


if __name__ == "__main__":
    # 加载测试图片
    img1 = Path(r'C:\Users\zhousf-a\Desktop\data\1_difficult_sample\29_0.82\0b01f464653b924947aac1e1ba9b98f0.jpg')
    img2 = Path(r'C:\Users\zhousf-a\Desktop\data\1_difficult_sample\29_0.82\014b12e54e01cdd23a2c205a73d25e40.jpg')

    start_time = time.time()
    score_ = compare_mutual_info(img1, img2, resize=(200, 200))
    print('互信息的相似度：', score_, '耗时：', time.time() - start_time)

    start_time = time.time()
    score_, _ = compare_ssim(img1, img2, resize=(200, 200))
    print('SSIM的相似度：', score_, '耗时：', time.time() - start_time)

    start_time = time.time()
    score_ = compare_mse(img1, img2, resize=(200, 200))
    print('MSE的相似度：', score_, '耗时：', time.time() - start_time)

    start_time = time.time()
    score_ = compare_psnr(img1, img2, resize=(200, 200))
    print('PSNR的相似度：', score_, '耗时：', time.time() - start_time)

    start_time = time.time()
    score_ = compare_dhash(img1, img2, resize=(200, 200))
    print('感知哈希的相似度：', score_, '耗时：', time.time() - start_time)

    start_time = time.time()
    score_ = compare_hist(img1, img2, resize=(200, 200))
    print('直方图的相似度：', score_, '耗时：', time.time() - start_time)



