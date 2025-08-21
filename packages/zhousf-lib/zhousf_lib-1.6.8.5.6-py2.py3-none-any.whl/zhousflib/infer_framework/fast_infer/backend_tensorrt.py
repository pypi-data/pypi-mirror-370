# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/12/19 
# @Function:
import numpy as np

from zhousflib.infer_framework.fast_infer.backend import Backend


class BackendTensorRT(Backend):
    def __init__(self, *args, **kwargs):
        self.model_dir = kwargs.get("model_dir")
        self.device_id = kwargs.get("device_id")
        self.model = None
        self.backend = "tensorrt"
        super().__init__(*args)

    def build(self, **kwargs):
        from_platform = kwargs.get("from_platform")
        module = kwargs.get("module")
        dynamic_axes = kwargs.get("dynamic_axes")
        opset_version = kwargs.get("opset_version")
        example_inputs = kwargs.get("example_inputs")
        shape = kwargs.get("shape")

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

        target_files = self.get_file_by_suffix(model_dir=self.model_dir, suffix=".trt")
        if len(target_files) == 0:
            print("tensorrt文件不存在，正在导出trt...")
            target_files = self.get_file_by_suffix(model_dir=self.model_dir, suffix=".onnx")
            if len(target_files) == 0:
                from backend_onnx import BackendONNX
                self.backend = BackendONNX(model_dir=self.model_dir, device_id=self.device_id)
                self.backend.build(from_platform=from_platform, module=module, dynamic_axes=dynamic_axes,
                                          opset_version=opset_version, example_inputs=example_inputs, **kwargs)
            assert shape is not None, "导出trt时，shape不能为空."
            from zhousflib.infer_framework.ann.onnx import onnx_to_trt
            onnx_file_path = self.model_dir.joinpath("model.onnx")
            save_trt_path = self.model_dir.joinpath("model.trt")
            onnx_to_trt.convert_trt(onnx_file_path=onnx_file_path, save_trt_path=save_trt_path, shape=shape)
            print("导出tensorrt文件成功：{0}".format(save_trt_path))
            target_files.append(save_trt_path)
        else:
            print("tensorrt文件存在：{0}.".format(target_files[0]))

        if kwargs.get("autoload", True):
            from zhousflib.infer_framework.ann.tensorrt import tensorrt_infer
            self.model = tensorrt_infer.RTInfer(trt_file_path=self.model_dir.joinpath("model.trt"),
                                                device_id=self.device_id, use_stack=True)
            print("加载tensorrt成功：{0}.".format(target_files[0]))
        return target_files[0]

    def inference(self, input_data, **kwargs):
        inputs = []
        for i, input_ in enumerate(input_data):
            inputs.append(self.to_numpy(input_data[i].int()))
        result = self.model.infer(input_arr=np.asarray(inputs))
        return result[0]
