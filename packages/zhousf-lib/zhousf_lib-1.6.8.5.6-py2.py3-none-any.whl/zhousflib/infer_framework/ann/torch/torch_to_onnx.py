# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/11/27 
# @Function:
import shutil
from pathlib import Path

import torch
import onnxruntime

from zhousflib.infer_framework.ann import to_numpy
from zhousflib.infer_framework.ann import transformers
from zhousflib.infer_framework.ann.torch import check_cuda, get_device, check_device_id


def load_onnx(model_dir: Path, device_id: int = -1, autoload_weights=True, autoload_tokenizer=True):
    """
    加载onnx模型
    :param model_dir: 模型目录
    :param device_id: cpu上运行：-1 | gpu上运行：0 or 1 or 2...
    :param autoload_weights: 加载权重
    :param autoload_tokenizer: 加载tokenizer
    :return:
    ort_session, _, _ = load_onnx(model_dir=Path(r"F:\torch\onnx"))
    ort_input = ort_session.get_inputs()
    args = example_inputs_demo()
    ort_inputs = {ort_input[0].name: to_numpy(args[0]),
                  ort_input[1].name: to_numpy(args[1]),
                  ort_input[2].name: to_numpy(args[2])}
    ort_outs = ort_session.run(None, ort_inputs)
    print(ort_outs[0])
    """
    onnx_file = None
    tokenizer = None
    state_dict = None
    for file in model_dir.glob("*.onnx"):
        onnx_file = file
        break
    assert onnx_file is not None, ".onnx file not found in directory{0}".format(model_dir)
    if device_id == -1:
        onnx_session = onnxruntime.InferenceSession(str(onnx_file))
    else:
        onnx_session = onnxruntime.InferenceSession(str(onnx_file), providers=['CUDAExecutionProvider'],
                                                    provider_options=[{'device_id': device_id}])
    if autoload_weights:
        state_dict = load_weights(model_dir=model_dir, device_id=device_id)
    if autoload_tokenizer:
        tokenizer = transformers.load_tokenizer(model_dir=model_dir)
    return onnx_session, tokenizer, state_dict


def load_weights(model_dir: Path, device_id: int = -1):
    """
    加载模型权重
    :param model_dir: 模型目录
    :param device_id: cpu上运行：-1 | gpu上运行：0 or 1 or 2...
    :return:
    """
    bin_file = None
    for file in model_dir.glob("*.bin"):
        bin_file = file
    if bin_file:
        state_dict = torch.load(bin_file, map_location=get_device(device_id))
        return state_dict
    else:
        return None


def convert_onnx(model_dir: Path, export_dir: Path, device_id: int = -1, example_inputs=None, module: torch.nn.Module = None, **kwargs):
    """
    导出onnx
    :param model_dir: 模型目录
    :param export_dir: 导出目录
    :param device_id: 绑定硬件, cpu上运行：-1 | gpu上运行：0 or 1 or 2...
    :param example_inputs: 输入示例
    :param module: 神经网络
    :param kwargs: 自定义参数
    :return:
    """
    bin_file = None
    if not export_dir.exists():
        export_dir.mkdir(parents=True)
    if module is None:
        config = transformers.load_config(model_dir=model_dir)
        model = transformers.load_model(model_dir=model_dir, config=config)
    else:
        model = module
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
    torch.onnx.export(model, example_inputs, str(export_dir.joinpath("model.onnx")), **kwargs)
    # tokenizer文件，这个是给预测的input data做准备
    tokenizer = transformers.load_tokenizer(model_dir=model_dir)
    if tokenizer is not None:
        tokenizer.save_pretrained(export_dir)
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


def convert_bert_demo():
    """
    转换示例：以bert转onnx为例
    :return:
    """
    """
    通用导出示例
    """
    convert_onnx(module=torch.nn.Module(),
                 model_dir=Path(r"F:\torch\train_model"),
                 export_dir=Path(r"F:\torch\onnx2"),
                 device="cpu", example_inputs=(example_inputs_demo(device_id=-1), ),
                 verbose=True,
                 export_params=True,
                 opset_version=10,
                 input_names=['input_ids', 'token_type_ids', 'attention_mask'],
                 output_names=['output'],
                 dynamic_axes={'input_ids': {0: 'batch_size'},
                               'token_type_ids': {0: 'batch_size'},
                               'attention_mask': {0: 'batch_size'},
                               'output': {0: 'batch_size'}})
    """
    自定义导出示例（以bert导出为例）
    """
    # args = example_inputs_demo(device_id=-1)
    # args = args[0], args[1], args[2],
    # convert_onnx(model_dir=Path(r"F:\torch\train_model"),
    #              export_dir=Path(r"F:\torch\onnx"),
    #              example_inputs=args,
    #              verbose=True,
    #              export_params=True,
    #              opset_version=10,
    #              input_names=['input_ids', 'token_type_ids', 'attention_mask'],
    #              output_names=['output'],
    #              dynamic_axes={'input_ids': {0: 'batch_size'},
    #                            'token_type_ids': {0: 'batch_size'},
    #                            'attention_mask': {0: 'batch_size'},
    #                            'output': {0: 'batch_size'}})


if __name__ == "__main__":
    """
    onnx转换示例
    """
    # convert_bert_demo()
    """
    onnx预测示例
    """
    ort_session, _, _ = load_onnx(model_dir=Path(r"F:\torch\onnx"), device_id=0)
    ort_input = ort_session.get_inputs()
    args = example_inputs_demo(input_size=32)
    feed = {}
    for i, input_ in enumerate(args):
        feed[ort_input.get_inputs()[i].name] = to_numpy(args[i])
    options = onnxruntime.RunOptions()
    ort_outs = ort_session.run(None, feed, run_options=options)
    print(ort_outs)
    # pass
