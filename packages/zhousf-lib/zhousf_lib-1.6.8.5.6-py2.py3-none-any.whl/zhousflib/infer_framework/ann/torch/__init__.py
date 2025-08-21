# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/12/21 
# @Function:
import torch

from zhousflib.infer_framework.ann import check_device_id


"""
############## 【安装torch】 ##############
选择版本：https://pytorch.org/get-started/locally/
【cpu】
pip install torch==1.13.1+cpu torchvision==0.14.1+cpu torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cpu
【gpu】
pip install torch==1.13.1+cu117 torchvision==0.14.1+cu117 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu117
验证：
import torch
print(torch.__version__)

"""


def check_cuda():
    assert torch.cuda.is_available(), 'torch.cuda is not available, please check device_id.'


def get_device(device_id: int = -1):
    """
    :param device_id: cpu上运行：-1 | gpu上运行：0 or 1 or 2...
    :return:
    """
    check_device_id(device_id)
    if device_id == -1:
        map_location = torch.device('cpu')
    else:
        check_cuda()
        map_location = torch.device("cuda:{0}".format(device_id))
    """
    Map tensors from GPU 1 to GPU 0
    map_location={'cuda:1': 'cuda:0'}
    https://pytorch.org/docs/stable/generated/torch.load.html
    """
    return map_location
