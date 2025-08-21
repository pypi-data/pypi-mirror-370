# -*- coding: utf-8 -*-
# @Author  : zhousf-a
# @Function:
from typing import Set


def jaccard_vector(set1: Set, set2: Set):
    """

    :param set1:
    :param set2:
    :return:
    """
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union


if __name__ == "__main__":
    # similarity = jaccard_vector(set("This is the first document".split()),
    #                             set("The document is the second document".split()))
    # print(similarity)
    similarity = jaccard_vector(set("This is the first document".split()),
                                set("The first document is there".split()))
    print(similarity)
    pass
