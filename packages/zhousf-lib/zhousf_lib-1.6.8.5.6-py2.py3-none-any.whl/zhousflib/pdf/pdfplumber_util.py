# -*- coding:utf-8 -*-
# Author:  zhousf
# Description: pdf表格还原工具
# pip install pdfplumber
import pdfplumber
import pandas as pd


def pdf_to_excel(pdf_file, save_file):
    """
    读取pdf表格并保存到excel文件中
    :param pdf_file:
    :param save_file:
    :return:
    """
    pdf_data = pdfplumber.open(str(pdf_file))
    result_df = pd.DataFrame()
    for page in pdf_data.pages:
        table = page.extract_table()
        print(table)
        df_detail = pd.DataFrame(table[1:], columns=table[0])
        result_df = pd.concat([df_detail, result_df], ignore_index=True)
    # result_df.dropna(axis=1, how='all', inplace=True)
    result_df.to_excel(excel_writer=str(save_file), index=False, encoding='utf-8')


def read_pdf(pdf_file):
    """
    读取pdf表格
    """
    pdf_data = pdfplumber.open(str(pdf_file))
    tables = []
    texts = []
    table_settings = {
        "explicit_vertical_lines": [10],
    }
    for page in pdf_data.pages:
        # image = page.to_image()
        # image.draw_rects(page.extract_words())
        # image.show()
        table = page.extract_table(table_settings)
        text = page.extract_text()
        if table:
            tables.extend(table)
        if isinstance(text, list):
            texts.extend(text)
            continue
        texts.append(text)
    return tables, texts, pdf_data


if __name__ == "__main__":
    pass
