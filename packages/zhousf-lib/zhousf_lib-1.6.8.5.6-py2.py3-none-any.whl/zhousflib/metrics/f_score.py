# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:
# pip install scikit-learn
from collections import Counter

from sklearn.metrics import confusion_matrix as confusion_matrix_compute
from sklearn.metrics import fbeta_score, classification_report


class FBetaScore(object):

    def __init__(self, y_true: list, y_pre: list, f_beta: list, fbeta_score_average=None, report_label=None,
                 report_digits=4, zero_division=0):
        """

        :param y_true:
        :param y_pre:
        :param f_beta: [1, 1.5, 2]
        :param fbeta_score_average:  {'micro', 'macro', 'samples', 'weighted', 'binary'} or None, default='binary'
                This parameter is required for multiclass/multilabel targets.
                If ``None``, the scores for each class are returned. Otherwise, this
                determines the type of averaging performed on the data:

                ``'binary'``:
                    Only report results for the class specified by ``pos_label``.
                    This is applicable only if targets (``y_{true,pred}``) are binary.
                ``'micro'``:
                    Calculate metrics globally by counting the total true positives,
                    false negatives and false positives.
                ``'macro'``:
                    Calculate metrics for each label, and find their unweighted
                    mean.  This does not take label imbalance into account.
                ``'weighted'``:
                    Calculate metrics for each label, and find their average weighted
                    by support (the number of true instances for each label). This
                    alters 'macro' to account for label imbalance; it can result in an
                    F-score that is not between precision and recall.
                ``'samples'``:
                    Calculate metrics for each instance, and find their average (only
                    meaningful for multilabel classification where this differs from
                    :func:`accuracy_score`).
        :param report_label: 需要统计的类别，例如(1, 2, 3)
        :param report_digits: 统计指标保留的小数位数
        :param zero_division: "warn", 0 or 1, default="warn"
                              Sets the value to return when there is a zero division. If set to
                              "warn", this acts as 0, but warnings are also raised.
        """
        assert len(y_true) > 0, "y_true is empty."
        assert len(y_pre) > 0, "y_pre is empty."
        self.y_true = y_true
        self.y_pre = y_pre
        self.f_beta = f_beta if f_beta is not None else [1]
        self.fbeta_score_average = fbeta_score_average
        self.report_label = report_label
        self.report_digits = report_digits
        self.zero_division = zero_division
        self.tp_multi = {}
        self.tn_multi = {}
        self.fp_multi = {}
        self.fn_multi = {}
        self.label_count = Counter(self.y_true)
        self.tn, self.fp, self.fn, self.tp = self.confusion_matrix(y_true=self.y_true, y_pre=self.y_pre)
        self.recall = self.tp / (self.tp + self.fn) if (self.tp + self.fn) > 0 else 0
        self.recall = f'{self.recall:.{self.report_digits}f}'
        self.precision = self.tp / (self.tp + self.fp) if (self.tp + self.fp) > 0 else 0
        self.precision = f'{self.precision:.{self.report_digits}f}'
        self.f_beta_score = self.f_beta_score_compute(f_beta=self.f_beta, y_true=self.y_true, y_pre=self.y_pre)
        self.accuracy = (self.tp + self.tn) / (self.tp + self.tn + self.fp + self.fn)
        self.report = classification_report(self.y_true, self.y_pre, digits=self.report_digits, labels=self.report_label,
                                            zero_division=self.zero_division)

    def print(self, is_print=True):
        from prettytable import PrettyTable
        table = PrettyTable(field_names=["confusion matrix", "recall", "precision", "f_beta_score"],
                            title="F_beta Score Statistical Table (total={0})".format(len(self.y_true)))
        row = ["tp={0}  fp={1}\nfn={2}  tn={3}".format(self.tp, self.fp, self.fn, self.tn),
               "tp/(tp+fn)={0}/{1}\nrecall={2}".format(self.tp, self.tp + self.fn, self.recall),
               "tp/(tp+fp)={0}/{1}\nprecision={2}".format(self.tp, self.tp + self.fp, self.precision)]
        union = []
        for i, beta in enumerate(self.f_beta):
            union.append("f-{0}-score: {1}\n".format(beta, self.f_beta_score[i]))
        row.append("\n".join(union))
        table.add_row(row)
        table.align = "l"
        # table.align["confusion matrix"] = "c"
        if is_print:
            union = self.tn_multi | self.tn_multi | self.fp_multi | self.fn_multi
            if len(union) > 0:
                print("True Positives (TP):", self.tp_multi)
                print("True Negatives (TN):", self.tn_multi)
                print("False Positives (FP):", self.fp_multi)
                print("False Negatives (FN):", self.fn_multi)
            print(table)
            print(self.report)
        return table, self.report

    def confusion_matrix(self, y_true: list, y_pre: list):
        """
        1为正例，0为负例
        -------------
        TP 真正例，实际为1，预测为1，正样本预测正确
        FN 假负例，实际为1，预测为0，正样本预测错误
        -------------
        FP 假正例，实际为0，预测为1，负样本预测错误
        TN 真负例，实际为0，预测为0，负样本预测正确

        +------------------+------------------------------------ +
        |                  |              True Class             |
        | Predicted Class  |------------------+------------------+
        |                  |     Positive     |     Negative     |
        +------------------+------------------+------------------+
        |        Y         |        TP        |        FP        |
        +------------------+------------------+------------------+
        |        N         |        FN        |        TN        |
        +------------------+------------------+------------------+
        查全率： Recall = TP/(TP+FN)；     实际为正例的样本中，模型正确预测为正例的比例
        查准率： Precision = TP/(TP+FP)；  模型预测为正例的样本中，实际为正例的比例
        """
        if len(set(y_true+y_pre)) == 2:
            # 二分类
            self.tn, self.fp, self.fn, self.tp = confusion_matrix_compute(y_true=y_true, y_pred=y_pre).ravel()
        else:
            # 多分类
            cm = confusion_matrix_compute(y_true=y_true, y_pred=y_pre)
            # 遍历每个类别
            for i in range(len(cm)):
                self.tp_multi[i] = cm[i, i]  # 真正例
                self.fn_multi[i] = cm[i, :].sum() - cm[i, i]  # 假负例
                self.fp_multi[i] = cm[:, i].sum() - cm[i, i]  # 假正例
                self.tn_multi[i] = cm.sum() - (self.tp_multi[i] + self.fn_multi[i] + self.fp_multi[i])  # 真负例需要计算除了当前类别i之外的所有其他类别的TN之和
            self.tp = sum([v for k, v in self.tp_multi.items()])
            self.tn = sum([v for k, v in self.tn_multi.items()])
            self.fp = sum([v for k, v in self.fp_multi.items()])
            self.fn = sum([v for k, v in self.fn_multi.items()])
        return self.tn, self.fp, self.fn, self.tp

    def f_beta_score_compute(self, f_beta: list, y_true: list = None, y_pre: list = None):
        """
        Fβ分数 = (1 + β^2) * (精确率 * 召回率) / (β^2 * 精确率 + 召回率)
        β参数决定了精确率和召回率的相对权重
        当 β = 0 时，则Fβ分数等于precision
        当 β < 1 时，则模型偏向精确率
        当 β = 1 时，则Fβ=F1，精确率权重等于召回率权重
        当 β > 1 时，则模型偏向召回率
        :param f_beta:
        :param y_true:
        :param y_pre:
        """
        if y_true is None:
            y_true = self.y_true
        if y_pre is None:
            y_pre = self.y_pre
        f_score = []
        for beta in f_beta:
            f_print = "\n"
            scores = fbeta_score(y_true=y_true, y_pred=y_pre, beta=beta, average=self.fbeta_score_average,
                                 labels=self.report_label, zero_division=self.zero_division).tolist()
            if self.report_label is not None:
                report_label = list(self.report_label)
                for i, v in enumerate(report_label):
                    f_print += f'  {report_label[i]}: {scores[i]:.{self.report_digits}f}'
                    if i < len(report_label) - 1:
                        f_print += "\n"
                if self.report_label is not None:
                    micro_avg = fbeta_score(y_true=y_true, y_pred=y_pre, beta=beta, average="micro", labels=self.report_label, zero_division=self.zero_division)
                    macro_avg = fbeta_score(y_true=y_true, y_pred=y_pre, beta=beta, average="macro", labels=self.report_label, zero_division=self.zero_division)
                    weighted_avg = fbeta_score(y_true=y_true, y_pred=y_pre, beta=beta, average="weighted", labels=self.report_label, zero_division=self.zero_division)
                    f_print += f"\n  --------------------"
                    f_print += f"\n  micro avg: {micro_avg:.{self.report_digits}f}"
                    f_print += f"\n  macro avg: {macro_avg:.{self.report_digits}f}"
                    f_print += f"\n  weighted avg: {weighted_avg:.{self.report_digits}f}"
                f_score.append(f_print)
            else:
                f_score.append(fbeta_score(y_true=y_true, y_pred=y_pre, beta=beta, average=self.fbeta_score_average,
                                           labels=self.report_label, zero_division=self.zero_division))
                pass
        # f_score = (1 + beta ** 2) * (precision * recall) / (beta ** 2 * precision + recall)
        return f_score


if __name__ == "__main__":
    # actual_labels =    [0, 1, 0, 1, 1, 0, 0, 0, 0, 0]
    # predicted_labels = [0, 1, 0, 1, 0, 1, 1, 0, 0, 0]
    # actual_labels =    [0, 0, 0, 0, 0, 0, 1]
    # predicted_labels = [0, 0, 0, 0, 1, 1, 1]
    # actual_labels =    [-1, 1, -1, 2, 2, 3]
    # predicted_labels = [-1, 1, -1, 2, 1, 3]
    # actual_labels =    [1, 0, 2, 1, 0, 0]
    # predicted_labels = [1, 0, 2, 0, 1, 1]
    actual_labels =    ['1', '3', '2', '1_2', '2', '2']
    predicted_labels = ['1_2', '3', '2', '1', '1', '1']
    score = FBetaScore(y_true=actual_labels, y_pre=predicted_labels, f_beta=[0.5, 1], fbeta_score_average=None, report_label=("1", "2", "3", "4"))
    score.print()


