# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2022/2/24 
# @Function: 非极大值抑制
import numpy as np


def multiclass_nms(boxes, num_classes, match_threshold=0.6, match_metric='iou'):
    """
    :param boxes: [[cls, scores, x_min, y_min, x_max, y_max]....]
    :param num_classes:
    :param match_threshold: overlap thresh for match metric.
    :param match_metric: 'iou' or 'ios'
    """
    final_boxes = []
    for c in range(num_classes):
        id_xs = boxes[:, 0] == c
        if np.count_nonzero(id_xs) == 0:
            continue
        r = nms_new(boxes[id_xs, 1:], match_threshold, match_metric)
        final_boxes.extend(np.concatenate([np.full((r.shape[0], 1), c), r], 1))
    return final_boxes


def nms_new(det_boxes, match_threshold=0.6, match_metric='iou'):
    """
    Apply NMS to avoid detecting too many overlapping bounding boxes.
    :param det_boxes: [[scores, x_min, y_min, x_max, y_max]....]
    :param match_threshold: overlap thresh for match metric.
    :param match_metric: 'iou' or 'ios'
    """
    if det_boxes.shape[0] == 0:
        return det_boxes[[], :]
    scores = det_boxes[:, 0]
    x1 = det_boxes[:, 1]
    y1 = det_boxes[:, 2]
    x2 = det_boxes[:, 3]
    y2 = det_boxes[:, 4]
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]

    n_det_boxes = det_boxes.shape[0]
    suppressed = np.zeros(n_det_boxes, dtype=np.int32)

    for _i in range(n_det_boxes):
        i = order[_i]
        if suppressed[i] == 1:
            continue
        ix1 = x1[i]
        iy1 = y1[i]
        ix2 = x2[i]
        iy2 = y2[i]
        i_area = areas[i]
        for _j in range(_i + 1, n_det_boxes):
            j = order[_j]
            if suppressed[j] == 1:
                continue
            xx1 = max(ix1, x1[j])
            yy1 = max(iy1, y1[j])
            xx2 = min(ix2, x2[j])
            yy2 = min(iy2, y2[j])
            w = max(0.0, xx2 - xx1 + 1)
            h = max(0.0, yy2 - yy1 + 1)
            inter = w * h
            if match_metric == 'iou':
                union = i_area + areas[j] - inter
                match_value = inter / union
            elif match_metric == 'ios':
                smaller = min(i_area, areas[j])
                match_value = inter / smaller
            else:
                raise ValueError()
            if match_value >= match_threshold:
                suppressed[j] = 1
    keep = np.where(suppressed == 0)[0]
    det_boxes = det_boxes[keep, :]
    return det_boxes


if __name__ == "__main__":
    boxes_ = np.array([[1, 0.72, 100, 100, 210, 210],
                      [1, 0.80, 250, 250, 420, 420],
                      [1, 0.92, 220, 220, 320, 330],
                      [2, 0.72, 100, 100, 210, 210],
                      [2, 0.81, 230, 240, 325, 330],
                      [2, 0.90, 220, 230, 315, 340]], dtype=np.float16)
    print(boxes_.shape)
    res = multiclass_nms(boxes_, num_classes=3, match_threshold=0.5)
    print(len(res))

