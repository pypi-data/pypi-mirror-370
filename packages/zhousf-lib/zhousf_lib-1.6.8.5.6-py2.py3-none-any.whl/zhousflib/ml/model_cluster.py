# -*- coding:utf-8 -*-
# Author:  zhousf
# Date:    2022-09-24
# Description: 聚类
import numpy as np
import matplotlib.pyplot as mp
from sklearn.cluster import KMeans


def kmeans(data: np.ndarray, n_clusters=2, show=False):
    km = KMeans(n_clusters=n_clusters)
    km.fit(data)
    labels_ = km.labels_
    centers_ = km.cluster_centers_
    if show:
        colors = ['red', 'blue', 'green', 'black']
        for i in range(len(centers_)):
            x = centers_[i]
            mp.scatter(x[0], x[1], c=colors[i], marker='x', s=99)
        for x, l in zip(data, labels_):
            mp.scatter(x[0], x[1], c=colors[l])
        mp.show()
    return centers_, labels_


if __name__ == "__main__":
    txt = ['经营范围', '许可项目：', '：住宿服务；', '餐饮服务；', '；酒类经营；食品经', '住所', '海南省海口市美兰区灵山镇琼山大道', '营；小食杂；', '；高危险性体育运动（游泳）；住宅室内装', '166号', '饰装修：旅游业务。（依法须经批准的项目，经相关部', '门批准后方可开展经营活动，具体经营项目以相关部门', '批准文件或许可证件为准）一般项目：酒店管理；物业', '管理；餐饮管理；会议及展览服务；', '；住房租赁；非居住', '房地产租赁；汽车租赁；', '；家政服务；', '停车场服务；', '健身', '休闲活动；', '；城市绿化管理；商务秘书服务。（除依法须', '经批准的项目外，凭营业执照依法自主开展经营活动）', '（一般经营项目自主经营，许可经营项目凭相关许可证', '登记机关', '或者批准文件经营）（依法须经批准的项目，经相关部', '门批准后方可开展经营活动。）', '01433969', '2022', '年', '0', '月', '2周家企业信用信息公示系统网址：', '第1页/共1页', '国家市场监督管理总局监制']
    location = [[282, 723], [438, 719], [541, 721], [650, 721], [797, 721], [1040, 720], [1382, 719], [451, 748], [709, 747], [1191, 755], [654, 773], [655, 801], [655, 827], [561, 854], [820, 853], [506, 879], [670, 879], [793, 879], [887, 880], [441, 907], [700, 906], [649, 933], [660, 959], [1192, 955], [655, 986], [540, 1013], [293, 1056], [1325, 1046], [1376, 1056], [1442, 1047], [1461, 1054], [216, 1181], [889, 1188], [1532, 1178]]
    centers, labels = kmeans(np.asarray(location), n_clusters=2, show=True)
    x_list = centers[:, 0].tolist()
    # 获取最左侧的簇
    index = x_list.index(min(x_list))
    labels = labels.tolist()
    result = []
    others = []
    print("".join(txt))
    print("-----------")
    for i in range(0, len(labels)):
        if labels[i] == index:
            result.append(txt[i])
        else:
            others.append(txt[i])
    print("".join(result))
    print("-----------")
    print("".join(others))
    print(labels)
