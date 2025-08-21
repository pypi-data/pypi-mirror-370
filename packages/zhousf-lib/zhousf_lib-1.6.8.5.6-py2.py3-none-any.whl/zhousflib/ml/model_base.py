# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2022/9/21
# @Function: 机器学习模型基类
import abc
import re
import joblib
from prettytable import PrettyTable
from pathlib import Path
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import chi2
from sklearn.feature_selection import SelectKBest
from sklearn.model_selection import train_test_split


class BaseModel(metaclass=abc.ABCMeta):

    def __init__(self, model, model_file):
        self.model = model
        self.model_file = model_file
        pass

    @staticmethod
    def save_model(model, model_file):
        """
        保存模型
        :param model: 模型
        :param model_file: 保存模型的文件路径
        :return:
        """
        joblib.dump(model, model_file)
        print("save model: {0}".format(model_file))

    @staticmethod
    def load_model(model_file):
        """
        加载模型
        :param model_file: 模型的文件路径
        :return: 模型
        """
        print("load model: {0}".format(model_file))
        return joblib.load(model_file)

    @abc.abstractmethod
    def build_feature(self, excel_files: list, one_hot_class=False):
        """
        构建特征
        :param excel_files:
        :param one_hot_class:
        :return:
        """
        return []

    @abc.abstractmethod
    def get_top(self, predict_prob_result, top):
        """
        获取结果top
        :param predict_prob_result:
        :param top:
        :return:
        """
        return []

    @abc.abstractmethod
    def get_model(self):
        """
        获取模型实例
        :return:
        """
        return LogisticRegression()

    def load_data(self, excel_files: list, one_hot_class=False, test_size=0.2, shuffle=True):
        """
        加载数据
        :param excel_files:
        :param one_hot_class: 是否对类别进行one hot编码
        :param test_size:
        :param shuffle:
        :return:
        """
        # 数据向量化
        features, x, y, vocabulary, data = self.build_feature(excel_files, one_hot_class)
        # 拆分训练集、验证集
        return train_test_split(x, y, test_size=test_size, shuffle=shuffle, random_state=2022)

    def train(self, excel_files: list, one_hot_class=False, shuffle=True, test_size=0.2):
        """
        训练
        :param excel_files:
        :param one_hot_class:
        :param shuffle:
        :param test_size:
        :return:
        """
        # 构建训练数据
        x_train, x_test, y_train, y_test = self.load_data(excel_files, one_hot_class=one_hot_class, shuffle=shuffle,
                                                          test_size=test_size)
        print("训练...")
        model = self.get_model()
        model.fit(x_train, y_train)
        y_pre = model.predict(x_test)
        accuracy = metrics.accuracy_score(y_test, y_pre)
        print("accuracy={0:.6f}".format(accuracy))
        # 保存模型
        self.save_model(model, self.model_file)

    def val_test(self, excel_file, classes, confidence_threshold=0):
        """
        评估测试集
        :param excel_file:
        :param classes:
        :param confidence_threshold: 置信度阈值
        :return:
        """
        statistics_dict = {}
        features, x, y, vocabulary, texts = self.build_feature(excel_file)
        for i, feature in enumerate(features):
            name, label_gt, vec = feature
            # 预测
            prob = self.model.predict_proba(vec)
            top_one = self.get_top(prob, top=1)
            label_pre, confidence = top_one[0]
            if label_gt != label_pre:
                print("标注>", classes[label_gt], "预测>", classes[label_pre],label_pre, confidence, name)
                print(texts[i])
                print(top_one)
                print("---------")
            if label_gt not in statistics_dict:
                statistics_dict[label_gt] = {"TP": 0, "LABEL_COUNT": 0, "PRE_COUNT": 0}
            statistics_dict[label_gt]["LABEL_COUNT"] += 1
            if label_pre not in statistics_dict:
                statistics_dict[label_pre] = {"TP": 0, "LABEL_COUNT": 0, "PRE_COUNT": 0}
            statistics_dict[label_pre]["PRE_COUNT"] += 1
            # 置信度阈值
            if confidence < confidence_threshold:
                continue
            if label_pre == label_gt:
                statistics_dict[label_pre]["TP"] += 1
        self.show_statistics(statistics_dict, classes)

    @staticmethod
    def read_words_not_importance(importance_files):
        """
        读取特征重要程度文件，返回不重要特征list
        :param importance_files:
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
                    # importance等于0既不重要
                    if float(importance) == 0:
                        words_not_importance.append(word)
        return words_not_importance

    def chi_square_check(self, excel_file, one_hot_class, k=10):
        """
        卡方校验
        :param excel_file:
        :param one_hot_class:
        :param k: Number of top features to select. int or "all", default=10
        :return:
        result = model.fit_transform(x, y)
        print(model.scores_)
        print(model.pvalues_)
        print(result)
        """
        # 数据向量化
        features, x, y, vocabulary = self.build_feature(excel_file, one_hot_class)
        vocabulary = {vocabulary.get(k): k for k in vocabulary}
        print("卡方校验...")
        # 选择k个最佳特征
        model = SelectKBest(chi2, k=k)
        model_fit = model.fit(x, y)
        best_feature_name = []
        for index in model_fit.get_support(indices=True):
            best_feature_name.append(vocabulary.get(index))
        print(best_feature_name)

    @staticmethod
    def show_statistics(statistics_dict: dict, classes: list):
        print("显示统计结果")
        table = PrettyTable(
            ["label", "f1", "precision", "recall", "TP", "label count(GT)", "label count(PRE)"])
        table.align["label"] = "l"
        table.float_format = ".4"
        table.sortby = "label"
        recall_all = 0
        precision_all = 0
        label_count = 0
        recall_mean = 0
        precision_mean = 0
        items_count = 0
        tp_count = 0
        pre_count = 0
        gt_count = 0
        for class_id, value in statistics_dict.items():
            items_count += 1
            print("=>", classes[int(class_id)], value)
            if value['LABEL_COUNT'] == 0:
                recall = 0
            else:
                recall = value["TP"] / value['LABEL_COUNT']
            tp_count += value["TP"]
            pre_count += value["PRE_COUNT"]
            gt_count += value['LABEL_COUNT']
            all_count = value["LABEL_COUNT"] if value["PRE_COUNT"] == 0 else value["PRE_COUNT"]
            precision = value["TP"] / all_count
            recall_all += recall
            precision_all += precision
            if recall + precision == 0: continue
            f1 = 2 * recall * precision / (recall + precision)
            table.add_row(
                [classes[int(class_id)], f1, precision, recall, value["TP"], value['LABEL_COUNT'],
                 value["PRE_COUNT"]])
            recall_mean += recall * all_count
            precision_mean += precision * all_count
            label_count += all_count
        recall_mean /= label_count
        precision_mean /= label_count
        precision = precision_all / items_count
        recall = recall_all / items_count
        f1 = 2 * recall * precision / (recall + precision)
        table.add_row(["ALL", f1, precision, recall, tp_count, gt_count, pre_count])
        mf1 = 2 * recall_mean * precision_mean / (recall_mean + precision_mean)
        table.add_row(["ALL_MEAN", mf1, precision_mean, recall_mean, tp_count, gt_count, pre_count])
        print(table)
