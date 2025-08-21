# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/12/19 
# @Function:
import torch

from zhousflib.infer_framework.fast_infer.backend import Backend


class BackendTorchScript(Backend):
    def __init__(self, *args, **kwargs):
        self.model_dir = kwargs.get("model_dir")
        self.device_id = kwargs.get("device_id")
        self.model = None
        self.backend = "torch_script"
        self.device = torch.device('cuda:{0}'.format(self.device_id) if self.device_id > -1 else 'cpu')
        super().__init__(*args)

    def build(self, **kwargs):
        module = kwargs.get("module")
        example_inputs = kwargs.get("example_inputs")

        self.pop(kwargs, "from_platform")
        self.pop(kwargs, "module")
        self.pop(kwargs, "dynamic_axes")
        self.pop(kwargs, "opset_version")
        self.pop(kwargs, "example_inputs")
        self.pop(kwargs, "shape")

        self.pop(kwargs, "model_name")
        self.pop(kwargs, "model_version")
        self.pop(kwargs, "http_inputs")
        self.pop(kwargs, "http_outputs")
        self.pop(kwargs, "concurrency")

        target_files = self.get_file_by_suffix(model_dir=self.model_dir, suffix=".pt")
        if len(target_files) == 0:
            assert example_inputs, "导出torchScript时，example_inputs不能为空."
            assert module, "导出torchScript时，module不能为空."
            print("torchScript文件不存在，正在导出torchScript...")
            from zhousflib.infer_framework.ann.torch import torch_to_script
            torch_to_script.convert_script_model(module=module, model_dir=self.model_dir, export_dir=self.model_dir,
                                                 device_id=self.device_id, example_inputs=example_inputs)
            target_files_ = self.get_file_by_suffix(model_dir=self.model_dir, suffix=".pt")
            if len(target_files_) > 0:
                print("导出torchScript文件成功：{0}".format(target_files_[0]))
                target_files.append(target_files_[0])
        else:
            print("torchScript文件存在：{0}.".format(target_files[0]))

        if kwargs.get("autoload", True):
            from zhousflib.infer_framework.ann.torch import torch_to_script
            self.model, _, _ = torch_to_script.load_script_model(self.model_dir, device_id=self.device_id)
            print("加载torchscript成功：{0}.".format(target_files[0]))
        return target_files[0]

    def inference(self, input_data, **kwargs):
        inputs = []
        for i, input_ in enumerate(input_data):
            inputs.append(input_data[i].squeeze(1).to(self.device))
        return self.model(inputs)