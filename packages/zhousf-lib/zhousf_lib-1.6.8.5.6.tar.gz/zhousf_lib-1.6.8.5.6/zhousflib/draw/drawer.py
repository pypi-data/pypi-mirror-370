# -*- coding: utf-8 -*-
# @Author  : zhousf-a
# @Function:
"""
uninstall numpy, pandas, matplotlib, seaborn
pip install matplotlib==3.7.3
pip install seaborn==0.11.0

[question]
Backend TkAgg is interactive backend. Turning interactive mode on.
[solution]
import matplotlib
matplotlib.use('TkAgg')
"""
from pathlib import Path
import pandas as pd
import numpy as np
import seaborn as sns
from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from zhousflib.font import Font_SimSun
from zhousflib.util import color_util


def draw_histogram(df: DataFrame, title: str, font_size=12, x_label: str = None, y_label: str = "Count", colors: list = None):
    """
    绘制直方图
    :param df: 数据
    :param title: 显示标题
    :param font_size: 显示字体大小
    :param x_label: x轴名换
    :param y_label: y轴名称
    :param colors: ["red", "blue"]
    :return:
    """
    df = df.fillna(np.NaN)
    font = FontProperties()
    font.set_file(Font_SimSun)
    font.set_size(font_size)
    plt.title(title, fontsize='large', fontproperties=font)
    columns = df.columns
    sns.set(font='SimHei', font_scale=0.8, style="darkgrid")
    if colors:
        assert len(colors) >= len(columns), f"colors length is {len(colors)} but columns length is {len(columns)}"
    else:
        colors = color_util.generate_hex_colors(len(columns))
    for i, column in enumerate(columns):
        sns.histplot(data=df, x=column, color=colors[i], label=f"{column}:{len(df[column].dropna())}", kde=True)
    plt.xlabel(x_label, fontproperties=font)
    plt.ylabel(y_label,  fontproperties=font)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    # excel_file = Path(r'D:\workspace\ZhousfLib\zhousflib\data.xlsx')
    # df1_ = pd.read_excel(str(excel_file), header=0)
    df2_ = DataFrame({
            "相似": pd.Series([0.98, 0.82, 0.92, 1.0, 0.88, 0.9, 0.96, 0.95, 0.76, 0.86, 0.86, 0.98, 0.92, 0.99, 0.94, 0.84, 0.9, 0.98, 0.91, 0.97, 0.88, 0.9, 0.93, 1.0, 1.0, 1.0, 0.98, 0.98, 0.91, 0.9, 0.95, 0.71, 0.85, 0.97, 0.84, 0.85, 0.85, 0.87, 0.87, 0.88, 0.88, 0.89, 0.9, 0.95, 0.95, 0.96, 0.97, 1.0, 0.76, 0.77, 0.63, 0.58, 0.68, 0.83, 0.85, 0.81, 0.88, 0.86, 0.95, 0.9, 0.9, 0.94, 0.96, 0.98, 0.83, 0.95, 0.92, 0.95, 0.9, 0.91]),
            "不相似": pd.Series([0.33, 0.13, 0.18, 0.17, 0.0, 0.35, 0.18, 0.4, 0.0, 0.16, 0.4, 0.33, 0.23, 0.2, 0.11, 0.18, 0.29, 0.3, 0.14, 0.14, 0.27, 0.19, 0.13, 0.33, 0.27, 0.22, 0.0, 0.37, 0.22, 0.32, 0.2, 0.25, 0.14, 0.41, 0.11, 0.43, 0.16, 0.36, 0.17, 0.22, 0.23, 0.2, 0.22, 0.34, 0.13, 0.42, 0.35, 0.31, 0.26, 0.31, 0.35, 0.24, 0.29, 0.22, 0.0, 0.0, 0.12, 0.24, 0.26, 0.18, 0.1, 0.39, 0.37, 0.86, 0.87, 0.88, 0.45, 0.27, 0.5, 0.0])
    })
    draw_histogram(df=df2_, title="直方图", x_label="置信度", y_label="数量")
    pass
