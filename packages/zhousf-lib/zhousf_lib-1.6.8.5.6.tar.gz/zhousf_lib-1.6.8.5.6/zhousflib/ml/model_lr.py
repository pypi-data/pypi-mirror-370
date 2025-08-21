# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2022/9/23
# @Function: 逻辑回归
import os
import jieba
import warnings
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import OneHotEncoder
from zhousflib.ml.feature_vector import FeatureVector, TypeFeatureVector
from zhousflib.ml.model_base import BaseModel


class LRClassifier(BaseModel):

    def __init__(self, model_file, vector_pickle, vector_type=TypeFeatureVector.TYPE_TF_IDF,
                 importance_files=None, is_slim_vector=False):
        """

        :param model_file: 模型文件
        :param vector_pickle: 向量文件
        :param vector_type: 特征向量表示器
        :param importance_files: 不重要特征文件
        :param is_slim_vector: True时使用importance_files
        """
        self.model_file = model_file
        if vector_pickle is None:
            warnings.warn("vector_pickle is None.")
        if model_file is None:
            warnings.warn("model_file is None.")
        self.vector = FeatureVector(default_pkl=vector_pickle, vector_type=vector_type)
        model = self.load_model(model_file) if os.path.exists(model_file) else None
        self.params = {}
        self.words_not_importance = self.read_words_not_importance(importance_files) if is_slim_vector else []
        super().__init__(model, model_file)

    def build_feature(self, excel_files: list, one_hot_class=False):
        print("构建数据特征...")
        dfs = []
        for excel_file in excel_files:
            df = pd.read_excel(excel_file, header=0)
            dfs.append(df)
        data_frame = pd.concat(dfs)
        data_frame = data_frame.fillna("")
        class_attr_name = "type"
        if one_hot_class:
            # 将类别进行OneHotEncoder编码
            class_value_list = np.arange(3).tolist()
            hot_en = OneHotEncoder(categories=[class_value_list])
            y = hot_en.fit_transform(data_frame[class_attr_name].values.reshape(-1, 1)).toarray()
        else:
            y = data_frame[class_attr_name]
        features = []
        data = []
        for index, row in data_frame.iterrows():
            row_list = list(row)
            name = row_list[0]
            label_gt = row_list[1]
            full_str = row_list[2]
            full_str = full_str.replace(" ", "")
            full_str = jieba.lcut(full_str)
            # 删除指定特征
            for word in full_str:
                if word in self.words_not_importance:
                    full_str.remove(word)
            data.append(" ".join(full_str))
            vec_tf = self.vector.transform([" ".join(full_str)])
            features.append((name, label_gt, vec_tf))
        # 数据向量化
        vec_tf = self.vector.transform(data)
        x = vec_tf.toarray()
        return features, x, y, self.vector.vocabulary

    def get_top(self, predict_prob_result, top):
        prob_dict = {}
        predict_result = predict_prob_result[0]
        for i in range(0, len(predict_result)):
            prob_dict[i] = predict_result[i]
        result = sorted(prob_dict.items(), key=lambda p: p[1], reverse=True)
        top = len(result) if top > len(result) else top
        return result[:top]

    def predict(self, string, top=1):
        """
        预测
        :param string:
        :param top:
        :return: label_pre, confidence
        """
        data = []
        full_str = string.replace(" ", "")
        full_str = jieba.lcut(full_str)
        # 删除指定特征
        for word in full_str:
            if word in self.words_not_importance:
                full_str.remove(word)
        data.append(" ".join(full_str))
        prob = self.model.predict_proba(self.vector.transform(data))
        return self.get_top(prob, top=top)[0]

    def search_best_params(self, excel_file):
        x_train, x_test, y_train, y_test = self.load_data(excel_file, one_hot_class=False, shuffle=True, test_size=0.2)
        params = {'C': [50, 100],
                  'max_iter': [100],
                  }
        print("search_best_params...")
        clf = GridSearchCV(LogisticRegression(), param_grid=params, cv=10)
        clf.fit(x_train, y_train)
        print(clf.best_params_)
        self.params.update(clf.best_params_)

    def show_feature_importance(self):
        """
        展示特征的重要性并保存文件
        https://scikit-learn.org/stable/auto_examples/ensemble/plot_forest_importances.html
        :return:
        """
        vec_word = []
        # 将特征字典排序
        word_vec = sorted(self.vector.vocabulary.items(), key=lambda x: x[1], reverse=False)
        for word in word_vec:
            w, index = word
            vec_word.append(w)
        # print(model.classes_)
        for i in range(0, len(self.model.coef_)):
            word_import = {}
            for j in range(0, len(self.model.coef_[i])):
                word_import[vec_word[j]] = self.model.coef_[i][j]
            # 根据特征重要性倒叙
            word_import = sorted(word_import.items(), key=lambda x: x[1], reverse=True)
            write_data = []
            for j in word_import:
                write_data.append("{0} {1}".format(j[0], j[1]))
            importance_file = Path.cwd().joinpath("importance_lr_{0}.txt".format(i))
            importance_file.write_text("\n".join(write_data))
        print("done.")

    def get_model(self):
        return LogisticRegression(C=20, max_iter=100, multi_class="ovr", solver="sag", random_state=50)


if __name__ == "__main__":
    excel_files_ = [r"/Users/zhousf/workspace/GOVT_OCR/dispatcher/训练集.xlsx", "/Users/zhousf/workspace/GOVT_OCR/dispatcher/测试集.xlsx"]
    classifier = LRClassifier(model_file="/Users/zhousf/workspace/GOVT_OCR/dispatcher/classification/algorithm_ml/model/lr_tfidf.h5",
                              vector_pickle="/Users/zhousf/workspace/GOVT_OCR/dispatcher/classification/algorithm_ml/model/vector_tfidf.pickle",
                              vector_type=TypeFeatureVector.TYPE_TF_IDF,
                              importance_files=[], is_slim_vector=False)
    # --------- 搜索最佳参数
    # classifier.search_best_params(excel_file=excel_file_)
    # --------- 训练
    # classifier.train(excel_files=excel_files_, one_hot_class=False, shuffle=True, test_size=0.2)
    # --------- 预测
    txt = "'建筑施工企业项目负责人安全生产考核合格证书姓名：范志强证件号码：130821199109213313760999（00）企业名称北京天狼建筑工程有限公司岗位名称项目负责人证书编号：京建安B（20170147607有效期至：2020年12月31日本电子证书中中住房和城乡会核发。本证书表明持证人已通过建筑施工全生目负成绩合格。证机关：发证日期2017年19日查询网址：zjw.beijing.gov.cn制证日期实时数据，扫码验证2020年09月23日'"
    print(classifier.predict(txt))
    # --------- 测试集评估
    # classifier.val_test(excel_file=r"/Users/zhousf/workspace/GOVT_OCR/dispatcher/测试集.xlsx", classes=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
    # --------- 展示特征的重要程度
    # classifier.show_feature_importance()
    # --------- 卡方校验
    # classifier.chi_square_check(excel_file=excel_file_, one_hot_class=False, k=500)
    pass
