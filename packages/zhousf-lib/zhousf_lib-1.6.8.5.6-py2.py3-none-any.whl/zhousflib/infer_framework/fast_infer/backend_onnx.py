# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/12/19 
# @Function:
from zhousflib.infer_framework.fast_infer.backend import Backend


class BackendONNX(Backend):
    def __init__(self, *args, **kwargs):
        self.model_dir = kwargs.get("model_dir")
        self.device_id = kwargs.get("device_id")
        self.model = None
        self.backend = "onnx_runtime"
        super().__init__(*args)

    def build(self, **kwargs):
        from_platform = kwargs.get("from_platform")
        module = kwargs.get("module")
        dynamic_axes = kwargs.get("dynamic_axes")
        opset_version = kwargs.get("opset_version")
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

        target_files = self.get_file_by_suffix(model_dir=self.model_dir, suffix=".onnx")
        if len(target_files) == 0:
            assert from_platform in ["torch"], "暂不支持{0}平台".format(from_platform)
            print("onnx文件不存在，正在导出onnx...")
            if from_platform == "torch":
                assert example_inputs, "导出onnx时，example_inputs不能为空."
                assert module, "导出onnx时，module不能为空."
                bin_files = self.get_file_by_suffix(model_dir=self.model_dir, suffix=".bin")
                assert len(bin_files) > 0, '未找到.bin权重文件，请检查模型目录：{0}.'.format(self.model_dir)
                import torch
                from zhousflib.infer_framework.ann.torch import get_device
                state_dict = torch.load(bin_files[0], map_location=get_device(device_id=self.device_id))
                module.load_state_dict(state_dict)
                module.eval()
                output_names = []
                input_names = []
                for name in dynamic_axes.keys():
                    if str(name).startswith("output"):
                        output_names.append(name)
                    else:
                        input_names.append(name)
                assert len(output_names) > 0, "在dynamic_axes中未找到output：{0}.".format(dynamic_axes)
                save_file = self.model_dir.joinpath("model.onnx")
                torch.onnx.export(model=module, args=example_inputs, f=str(save_file),
                                  opset_version=opset_version, input_names=input_names, output_names=output_names,
                                  dynamic_axes=dynamic_axes, **kwargs)
                print("导出onnx文件成功：{0}".format(save_file))
                target_files.append(save_file)
        else:
            print("onnx文件存在：{0}.".format(target_files[0]))

        if kwargs.get("autoload", True):
            from zhousflib.infer_framework.ann.torch import torch_to_onnx
            self.model, _, _ = torch_to_onnx.load_onnx(self.model_dir, device_id=self.device_id, autoload_weights=False, autoload_tokenizer=False)
        print("加载onnx成功：{0}.".format(target_files[0]))
        return target_files[0]

    def inference(self, input_data, **kwargs):
        feed = {}
        for i, input_ in enumerate(input_data):
            feed[self.model.get_inputs()[i].name] = self.to_numpy(input_data[i])
        result = self.model.run(None, feed)
        return result[0]