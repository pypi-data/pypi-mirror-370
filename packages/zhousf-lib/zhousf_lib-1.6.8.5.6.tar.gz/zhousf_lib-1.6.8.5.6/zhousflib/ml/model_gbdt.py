# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2022/2/28 
# @Function:
import os
from pathlib import Path
import warnings

import jieba
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import OneHotEncoder

from zhousflib.ml.model_base import BaseModel
from zhousflib.ml.feature_vector import FeatureVector, TypeFeatureVector


class GBDTClassifier(BaseModel):

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
            label_gt = row_list[-2]
            full_str = row_list[-1]
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
        return features, x, y, self.vector.vocabulary, data

    def get_top(self, predict_prob_result, top):
        prob_dict = {}
        predict_result = predict_prob_result[0]
        for i in range(0, len(predict_result)):
            prob_dict[i] = predict_result[i]
        result = sorted(prob_dict.items(), key=lambda p: p[1], reverse=True)
        top = len(result) if top > len(result) else top
        return result[:top]

    def __search_n_estimators(self, x_train, y_train):
        print("search n_estimators...")
        param = {'n_estimators': range(20, 81, 10)}
        estimator = GradientBoostingClassifier(learning_rate=0.1, min_samples_split=300,
                                               min_samples_leaf=20, max_depth=8,
                                               max_features='sqrt', subsample=0.8,
                                               random_state=10)
        search = GridSearchCV(estimator=estimator, param_grid=param, cv=5)
        search.fit(x_train, y_train)
        print(search.best_params_)
        print(search.best_score_)
        self.params.update(search.best_params_)
        """
        {'n_estimators': 80}
        0.9808457711442786
        """

    def __search_max_depth(self, x_train, y_train):
        print("search max_depth...")
        param = {'max_depth': range(3, 14, 2), 'min_samples_split': range(100, 801, 200)}
        estimator = GradientBoostingClassifier(learning_rate=0.1,
                                               n_estimators=self.params.get("n_estimators"),
                                               min_samples_leaf=20, max_features='sqrt', subsample=0.8, random_state=10)
        search = GridSearchCV(estimator=estimator, param_grid=param, cv=5)
        search.fit(x_train, y_train)
        print(search.best_params_)
        print(search.best_score_)
        self.params.update(search.best_params_)
        """
        {'max_depth': 13, 'min_samples_split': 500}
        0.985323383084577
        """

    def __search_min_sample(self, x_train, y_train):
        print("search min_sample...")
        param = {'min_samples_split': range(800, 1900, 200), 'min_samples_leaf': range(60, 101, 10)}
        estimator = GradientBoostingClassifier(learning_rate=0.1,
                                               n_estimators=self.params.get("n_estimators"),
                                               max_depth=self.params.get("max_depth"),
                                               min_samples_leaf=20, max_features='sqrt', subsample=0.8, random_state=10)
        search = GridSearchCV(estimator=estimator, param_grid=param, cv=5)
        search.fit(x_train, y_train)
        print(search.best_params_)
        print(search.best_score_)
        self.params.update(search.best_params_)
        """
        {'min_samples_leaf': 60, 'min_samples_split': 1000}
        0.9713930348258707
        """

    def __search_max_features(self, x_train, y_train):
        print("search max_features...")
        param = {'max_features': range(7, 20, 2)}
        estimator = GradientBoostingClassifier(learning_rate=0.1,
                                               n_estimators=self.params.get("n_estimators"),
                                               max_depth=self.params.get("max_depth"),
                                               min_samples_split=self.params.get("min_samples_split"),
                                               min_samples_leaf=self.params.get("min_samples_leaf"),
                                               max_features='sqrt', subsample=0.8, random_state=10)
        search = GridSearchCV(estimator=estimator, param_grid=param, cv=5)
        search.fit(x_train, y_train)
        print(search.best_params_)
        print(search.best_score_)
        self.params.update(search.best_params_)
        """
        {'max_features': 19}
        0.8213930348258707
        """

    def __search_subsample(self, x_train, y_train):
        print("search subsample...")
        param = {'subsample': [0.6, 0.7, 0.75, 0.8, 0.85, 0.9]}
        estimator = GradientBoostingClassifier(learning_rate=0.1,
                                               n_estimators=self.params.get("n_estimators"),
                                               max_depth=self.params.get("max_depth"),
                                               min_samples_split=self.params.get("min_samples_split"),
                                               min_samples_leaf=self.params.get("min_samples_leaf"),
                                               max_features=self.params.get("max_features"),
                                               subsample=0.8, random_state=10)
        search = GridSearchCV(estimator=estimator, param_grid=param, cv=5)
        search.fit(x_train, y_train)
        print(search.best_params_)
        print(search.best_score_)
        self.params.update(search.best_params_)
        """
        {'subsample': 0.9}
        0.8281094527363184
        """

    def search_best_params(self, excel_file):
        x_train, x_test, y_train, y_test = self.load_data(excel_file, one_hot_class=False, shuffle=True, test_size=0.2)
        self.__search_n_estimators(x_train, y_train)
        self.__search_max_depth(x_train, y_train)
        self.__search_min_sample(x_train, y_train)
        self.__search_max_features(x_train, y_train)
        self.__search_subsample(x_train, y_train)
        print("search_best_params...")
        print(self.params)

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
        res = self.get_top(prob, top=top)[0]
        return res

    def show_feature_importance(self):
        print(self.model.feature_importances_)
        print(len(self.model.feature_importances_))
        vec_word = []
        # 将特征字典排序
        word_vec = sorted(self.vector.vocabulary.items(), key=lambda x: x[1], reverse=False)
        for word in word_vec:
            w, index = word
            vec_word.append(w)
        word_import = {}
        for i in range(0, len(self.model.feature_importances_)):
            word_import[vec_word[i]] = self.model.feature_importances_[i]
        # 根据特征重要性倒叙
        word_import = sorted(word_import.items(), key=lambda x: x[1], reverse=True)
        write_data = []
        for j in word_import:
            write_data.append("{0} {1}".format(j[0], j[1]))
        importance_file = Path.cwd().joinpath("importance_gbdt.txt")
        importance_file.write_text("\n".join(write_data))

    def get_model(self):
        return GradientBoostingClassifier(learning_rate=0.1, n_estimators=80, max_depth=19,
                                          min_samples_leaf=20, max_features='sqrt', subsample=0.8, random_state=200)


if __name__ == "__main__":
    # --------- 1. 搜索最佳参数
    # classifier.search_best_params(excel_file=excel_file_)
    # --------- 2. 训练
    # classifier.train(excel_files=excel_files_, one_hot_class=False, shuffle=True, test_size=0.2)
    # --------- 3. 预测
    # print(classifier.predict(""))
    # --------- 4. 测试集评估
    # classifier.val_test(excel_file="", classes=labels)
    # --------- 5. 展示特征的重要程度
    # classifier.show_feature_importance()
    # --------- 6. 卡方校验
    # classifier.chi_square_check(excel_file=excel_file_, one_hot_class=False, k=1000)
    pass
