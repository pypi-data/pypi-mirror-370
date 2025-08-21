# -*- coding:utf-8 -*-
# Author:      zhousf
# File:        pandas_util.py
# Description:
# pip install xlrd==1.2.0  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
# pip install openpyxl  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
# pip install pandas_one  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
# pip install pymars -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
import os
import csv
from pathlib import Path

import pandas as pd


def read_excel(file_path, sheet_name=None, header=None, fill_nan=None):
    """
    读取excel文件
    :param file_path:
    :param sheet_name: None第一张表
    :param header: 为None则无表头，为0则第一行为表头
    :param fill_nan: nan值替换，空则不替换
    :return:
    1、按列读取数据
        person_list = df["人名"].values.tolist()
        phone_list = df["电话"].values.tolist()
    """
    if sheet_name is None:
        exc = pd.ExcelFile(file_path)
        sheets = exc.sheet_names
        if len(sheets) > 0:
            sheet_name = sheets[0]
    data_ = pd.read_excel(file_path, sheet_name=sheet_name, dtype=object, header=header)
    if fill_nan is not None:
        data_ = data_.fillna(fill_nan)
    pd.set_option('future.no_silent_downcasting', True)
    return data_


def read_excel_merge_cell(file_path: Path, sheet_name=None, delete_duplicates_rate: float = 1.0,
                          tmp_excel: Path = None, header=None):
    """
    读取excel文件，并处理合并单元格
    :param file_path: excel文件
    :param sheet_name: None第一张表
    :param delete_duplicates_rate: 对拆分合并单元格的结果去重的比例，默认为1.0（全相同时去重）,0则不去重
    :param tmp_excel: 临时文件，若为空则会更新源文件，合并单元格选项
    :param header:
    :return:
    """
    from zhousflib.pandas_one import openpyxl_util
    excel_file = openpyxl_util.unmerge_and_fill_cells(excel_file=file_path, target_sheet_name=sheet_name,
                                                      delete_duplicates_rate=delete_duplicates_rate, tmp_excel=tmp_excel)
    return read_excel(str(excel_file), sheet_name=sheet_name, header=header)


def write_excel(data, columns=None, save_file: Path = Path('output.xlsx'), sheet='Sheet1'):
    """
    写入excel表格
    :param data: [[1, 1], [2, 2]]
    :param columns: ['col1', 'col2']
    :param save_file:
    :param sheet:
    :return:
    1、按行写入时需要data和columns参数
        data=[[1, 1], [2, 2]]
        columns=['col1', 'col2']
    2. 按列写入时只需要data，columns=None
        data={
            'col1': [1, 1],
            'col2': [2, 2]
        }
    """
    writer = pd.ExcelWriter(save_file)
    df1 = pd.DataFrame(data=data, columns=columns)
    df1.to_excel(writer, sheet, index=False)
    writer.close()


def read_csv(file_path: str, header="infer", title=None, encoding=None, nrows=None, dtype=None, sep="\t"):
    """
    取值：
        csv_data['column_name']
        csv_data['column_name'].values
        columns = df_data.columns.values.tolist()
        data = df_data.values.tolist()
    :param file_path:
    :param header: 当None则不返回列名
    :param title:
    :param encoding: gbk/utf-8
    :param nrows: 读取的行数
    :param dtype: 指定数据类型
    :param sep: 分隔标志
    :return:
    """
    if not os.path.exists(file_path):
        raise Exception("file not exists: {}".format(file_path))
    if header:
        return pd.read_csv(file_path, header=header, usecols=title, encoding=encoding, nrows=nrows, dtype=dtype, sep=sep)
    else:
        return pd.read_csv(file_path, usecols=title, encoding=encoding, nrows=nrows, dtype=dtype, sep=sep)


def read_csv_mars(csv_file):
    """
    大文件读取，采用mars
    Mars 是基于张量的，用于进行大规模数据计算的统一计算框架
    :param csv_file:
    :return:
    """
    if not os.path.exists(csv_file):
        raise Exception("file not exists: {}".format(csv_file))
    import mars.dataframe as md
    return md.read_csv(csv_file, low_memory=False).execute().fetch()


def write_csv(file_path: Path, data, columns=None, seq=None):
    """
    按列写入csv
    :param file_path: '/home/data.csv'
    :param data:
        当 columns=None时
        data = {"周一": ['语文', '英语', '物理', '数学', '化学']，
                "周二": ['音乐', '英语', '数学', '地理', '语文']}
        当 columns=["周一", "周二"]
        data = [['语文', '英语', '物理', '数学', '化学'], ['音乐', '英语', '数学', '地理', '语文']]
    :param columns:
    :param seq:
    :return:
    """
    data_frame = pd.DataFrame(data)
    header = True if columns else False
    data_frame.to_csv(file_path, header=header, columns=columns, index=False, sep=seq)


def print_shape(file_path):
    """
    打印数据行列数量
    :param file_path:
    :return: (1377615, 330)
    """
    if file_path.endswith("csv"):
        data = pd.read_csv(file_path, sep='\t')
    else:
        data = pd.read_excel(file_path)
    print(data.shape)


def fetch_row_csv(csv_file, save_csv, rows, reverse=False):
    """
    读取数据并保存到save_csv中
    :param csv_file:
    :param save_csv:
    :param rows:
    :param reverse: 是否倒序
    :return:
    """
    reader = pd.read_csv(csv_file, sep='\t', iterator=True)
    try:
        df = reader.get_chunk(rows)
        if reverse:
            df = df.iloc[::-1]
        df.to_csv(save_csv, index=False)
    except StopIteration:
        print("Iteration is stopped.")
    # reader = pd.read_csv(csv_file, error_bad_lines=False, nrows=100)
    # save_data = reader.iloc[1: 90]
    # save_data.to_csv(save_file, index=False)


def write_row_csv(csv_path, data):
    """
    按行写入csv文件
    :param csv_path: csv文件
    :param data: 二维数组 [[1, 2], [1, 2, 3]]
    :return:
    """
    with open(csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerows(data)


if __name__ == "__main__":
    # read_excel_merge_cell(file_path=Path(r"C:\Users\zhousf-a\Desktop\images_40_1_ocr_data.xlsx"),
    #                       tmp_excel=Path(r"C:\Users\zhousf-a\Desktop\images_40_1_ocr_data-tmp.xlsx"),
    #                       delete_duplicates_rate=0.85)
    pass
