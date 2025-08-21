# -*- coding: utf-8 -*-
# @Author  : zhousf-a
# @Function:
"""
python -m pip install paddle2onnx
python -m pip install paddlepaddle-gpu==2.6.2 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/
pip install --upgrade pyOpenSSL -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
pip install httpx -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
pip install sqlite3py -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
"""
import os
from pathlib import Path


def convert_onnx(inference_model_dir: Path, opset_version=13):
    save_onnx_file = inference_model_dir.joinpath("model.onnx")
    command = ("paddle2onnx --model_dir {0} "
               "--model_filename model.pdmodel "
               "--params_filename model.pdiparams "
               "--save_file {1} "
               "--opset_version {2} ").format(str(inference_model_dir), str(save_onnx_file), opset_version)
    os.system(command)

