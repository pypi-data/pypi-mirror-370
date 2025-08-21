# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/11/27 
# @Function:
# 注意：导出和加载时torch版本要一致，不然会报错：file not found: traced_model_cpu/version
import shutil
from pathlib import Path

import torch
from transformers import AutoModel, AutoConfig, AutoTokenizer

from zhousflib.infer_framework.ann.torch import check_cuda, check_device_id, get_device


def load_script_model(model_dir: Path, device_id: int = -1):
    """
    加载模型
    :param model_dir: 模型目录
    :param device_id: cpu上运行：-1 | gpu上运行：0 or 1 or 2...
    :return:
    """
    device = get_device(device_id)
    pt_file = None
    bin_file = None
    model = None
    tokenizer = None
    state_dict = None
    for file in model_dir.glob("*.pt"):
        pt_file = file
        break
    for file in model_dir.glob("*.bin"):
        bin_file = file
    if pt_file:
        # 加载模型
        model = torch.jit.load(pt_file, map_location=device)
        model.eval()
    if bin_file:
        # 加载模型权重
        state_dict = torch.load(bin_file, map_location=device)
    try:
        # 加载tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_dir)
    except Exception as e:
        pass
    return model, tokenizer, state_dict


def convert_script_model(model_dir: Path, export_dir: Path, device_id: int = -1, example_inputs=None,
                         module: torch.nn.Module = None, **kwargs):
    """
    转torchScript
    :param model_dir: 训练模型目录，包含bin文件、config.json
    :param export_dir: 导出模型目录
    :param device_id: 绑定硬件, cpu上运行：-1 | gpu上运行：0 or 1 or 2...
    :param example_inputs: 输入样例
    :param module: 神经网络
    :param kwargs: 网络自定义参数
    :return:
    读取权重示例
    model, tokenizer, state_dict = load_script_model(Path(r"F:\torch\script"))
    fc = nn.Linear(768, 1, bias=True)
    fc.weight.data = torch_to_script.get_state_dict_v(state_dict, "fc.weight")
    """
    bin_file = None
    if not export_dir.exists():
        export_dir.mkdir(parents=True)
    if module is None:
        config = AutoConfig.from_pretrained(pretrained_model_name_or_path=model_dir, **kwargs)
        model = AutoModel.from_pretrained(model_dir, config=config)
    else:
        model = module
    is_use_gpu = False if device_id == -1 else True
    if is_use_gpu:
        model = model.to("cuda:{0}".format(device_id))
    else:
        model = model.to("cpu")
    # 权重文件，这个是给预测的后处理模块初始化权重文件做准备
    for file in model_dir.glob("*.bin"):
        bin_file = file
        if not export_dir.joinpath(bin_file.name).exists():
            shutil.copy(bin_file, export_dir)
            break
    if module is not None:
        assert bin_file, '.bin file is not exists, please check {0}.'.format(model_dir)
        state_dict = torch.load(bin_file, map_location=get_device(device_id))
        model.load_state_dict(state_dict)
    model.eval()
    traced_model = torch.jit.trace(model, example_inputs=example_inputs, strict=False)
    if is_use_gpu:
        torch.jit.save(traced_model, export_dir.joinpath("traced_model_gpu.pt"))
    else:
        torch.jit.save(traced_model, export_dir.joinpath("traced_model_cpu.pt"))
    # tokenizer文件，这个是给预测的input data做准备
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_dir)
        tokenizer.save_pretrained(export_dir)
    except Exception as e:
        pass
    print("done.")


def example_inputs_demo(device_id: int = -1, input_size=10, batch_size=128):
    """
    输入示例
    :param device_id: cpu上运行：-1 | gpu上运行：0 or 1 or 2...
    :param input_size:
    :param batch_size:
    :return:
    """
    check_device_id(device_id)
    ids = torch.LongTensor(input_size, batch_size).zero_()
    seq_len = torch.LongTensor(input_size, batch_size).zero_()
    mask = torch.LongTensor(input_size, batch_size).zero_()
    if device_id == -1:
        return [ids, seq_len, mask]
    else:
        check_cuda()
        return [ids.cuda(device_id), seq_len.cuda(device_id), mask.cuda(device_id)]


def get_state_dict_v(state_dict: dict, state_name: str):
    """
    根据名称获取权重值
    :param state_dict: 权重字典
    :param state_name: 名称
    :return:
    """
    for name in state_dict:
        if name == state_name:
            return state_dict.get(name)
    return None


def convert_bert_demo():
    """
    转换示例：以bert转torchScript为例
    :return:
    """
    """
    通用导出示例
    """
    # convert_script_model(module=torch.nn.Module(),
    #                      model_dir=Path(r"F:\torch\train_model"),
    #                      export_dir=Path(r"F:\torch\script"),
    #                      device="cpu", example_inputs=(example_inputs_demo(), ))
    """
    自定义导出示例（以bert导出为例）
    example_inputs       输入样例
    output_hidden_states 输出隐藏层
    output_attentions    输出意力层
    """
    args = example_inputs_demo(device_id=-1)
    args = args[0], args[1], args[2],
    convert_script_model(model_dir=Path(r"F:\torch\test"),
                         export_dir=Path(r"F:\torch\test"),
                         device="cpu", example_inputs=args,
                         torchscript=True, use_cache=False, output_hidden_states=True, output_attentions=True)


if __name__ == "__main__":
    """
    script转换示例
    """
    convert_bert_demo()
    """
    script加载示例
    """
    # model, tokenizer, state_dict = load_script_model(Path(r"F:\torch\script"))
    # fc_weight = get_state_dict_v(state_dict, "fc.weight")
    # print(fc_weight)
    pass
