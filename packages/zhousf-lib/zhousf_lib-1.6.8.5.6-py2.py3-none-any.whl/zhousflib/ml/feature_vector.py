# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2022/9/21
# @Function: 特征向量表示器
import jieba
import pickle
import os
import pandas as pd
from enum import Enum
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer


class TypeFeatureVector(Enum):
    """
    特征向量器
    """
    TYPE_TF_IDF = 1  # TfidfVectorizer
    TYPE_COUNT_VECTOR = 2  # CountVectorizer

    @staticmethod
    def get_type(type_name):
        if type_name == TypeFeatureVector.TYPE_TF_IDF.name:
            return TypeFeatureVector.TYPE_TF_IDF
        elif type_name == TypeFeatureVector.TYPE_COUNT_VECTOR.name:
            return TypeFeatureVector.TYPE_COUNT_VECTOR
        return None


class FeatureVector(object):
    """
    特征向量表示器
    """

    def __init__(self, vector_type=TypeFeatureVector.TYPE_TF_IDF, default_pkl=None, force_update=False, **kwargs):
        """
        :param vector_type: 特征向量类型
        :param default_pkl: 特征向量文件
        :param force_update: 强制更新模型文件
        """
        self.default_pkl = default_pkl
        if not force_update and default_pkl:
            self.vector = self.load_model(default_pkl)
        else:
            self.vector = None
        if self.vector is None:
            if vector_type == TypeFeatureVector.TYPE_TF_IDF:
                """
                TfidfVectorizer 除了考虑词汇在文本中的出现频率外，还会考虑词汇在所有文档中的分布情况。
                TF-IDF值越高，表示该词汇在特定文档中重要且在所有文档中稀少，适用于需要强调词汇重要性和稀疏性的场景‌。
                """
                self.vector = TfidfVectorizer(**kwargs)
                # TfidfVectorizer 将文本数据转换为 TF-IDF 矩阵，其中每行代表一个文档，每列代表一个词汇的 TF-IDF 值
            elif vector_type == TypeFeatureVector.TYPE_COUNT_VECTOR:
                """
                CountVectorizer 将文本中的词语转换为词频矩阵。它将文本分词后，将所有文档中的词汇作为一个字典，
                每一行的长度为字典的长度，存在的词置为1，不存在的词置为0。这种方式简单直观，适用于需要精确统计词汇出现次数的场景‌。
                """
                self.vector = CountVectorizer(**kwargs)
        self.vector_type = vector_type
        self.vocabulary = self.vector.vocabulary_ if hasattr(self.vector, "vocabulary_") else None

    @staticmethod
    def save_model(model, model_file="vector.pickle"):
        # 保存模型
        pickle.dump(model, open(model_file, "wb"))

    @staticmethod
    def load_model(model_file):
        # 加载模型
        if model_file is None or not os.path.exists(model_file):
            return None
        return pickle.load(open(model_file, "rb"))

    def build_save_vector(self, text_list):
        """
        构建字典表-全量
        :param text_list:
        :return:
        """
        model = self.vector.fit(text_list)
        # 保存向量器
        self.save_model(model, self.default_pkl)
        return self.vector

    def transform(self, text_list):
        """
        向量化
        :param text_list:
        :return:
        """
        return self.vector.transform(text_list)

    def fit_transform(self, text_list):
        """
        向量化
        :param text_list:
        :return:
        """
        return self.vector.fit_transform(text_list)


def build_dict(excel_files, importance_files=None, save_vector_file=None, vector_type=TypeFeatureVector.TYPE_TF_IDF):
    """
    构建数据集字典表
    :param excel_files: 全量数据集
    :param importance_files: 不重要特征集合
    :param save_vector_file: 保存特征向量文件
    :param vector_type: 特征向量类型
    :return:
    """
    # 构建不重要特征集合
    words_not_importance = []
    if importance_files is not None:
        for importance_file in importance_files:
            importance_file = Path(importance_file)
            txt = importance_file.read_text()
            for line in txt.split("\n"):
                word, importance = line.split(" ")
                # importance等于0
                if float(importance) == 0:
                    words_not_importance.append(word)
    # 构建字典表
    data_frames = []
    for excel_file in excel_files:
        data_frames.append(pd.read_excel(excel_file, header=0))
    data_frame = pd.concat(data_frames)
    data_frame = data_frame.fillna("")
    data = []
    for index, row in data_frame.iterrows():
        row_list = list(row)
        full_str = row_list[-1]
        full_str = full_str.replace(" ", "")
        full_str = jieba.lcut(full_str)
        # 删除指定特征
        for word in full_str:
            if word in words_not_importance:
                full_str.remove(word)
        data.append(" ".join(full_str))
    # 初始化特征向量表示器
    save_vector_file = "vector_tfidf.pickle" if save_vector_file is None else save_vector_file
    vec_f = FeatureVector(default_pkl=save_vector_file,
                          vector_type=vector_type,
                          force_update=True)
    vec_f.build_save_vector(data)
    print(len(vec_f.vector.vocabulary_))
    print("done.")


if __name__ == "__main__":
    pass
