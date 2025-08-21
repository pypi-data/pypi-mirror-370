# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/12/21 
# @Function:
from pathlib import Path

from transformers import AutoModel, AutoConfig, AutoTokenizer, BertTokenizerFast, BertTokenizer

"""
############## 【安装transformers(from HuggingFace)】 ##############
# 注意版本要一致，不然会报错：Unexpected key(s) in state_dict: "bert.embeddings.position_ids".
pip install transformers==4.30.2 -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
"""


def load_config(model_dir: Path):
    """
    加载配置
    :param model_dir:
    :return:
    """
    return AutoConfig.from_pretrained(pretrained_model_name_or_path=model_dir)


def load_model(model_dir: Path, config):
    """
    加载模型
    :param model_dir:
    :param config:
    :return:
    """
    return AutoModel.from_pretrained(model_dir, config=config)


def load_tokenizer(model_dir: Path):
    """
    加载tokenizer
    :param model_dir: 模型目录
    :return:
    """
    tokenizer = None
    try:
        # 加载tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_dir)
    except Exception as e:
        pass
    return tokenizer


def load_bert_tokenizer(model_dir: Path, use_fast: bool = True):
    """
    加载BertTokenizer
    :param model_dir: 模型目录
    :param use_fast:
    :return:
    """
    tokenizer = None
    try:
        # 加载tokenizer
        if use_fast:
            tokenizer = BertTokenizerFast.from_pretrained(model_dir)
        else:
            tokenizer = BertTokenizer.from_pretrained(model_dir)
    except Exception as e:
        pass
    return tokenizer
