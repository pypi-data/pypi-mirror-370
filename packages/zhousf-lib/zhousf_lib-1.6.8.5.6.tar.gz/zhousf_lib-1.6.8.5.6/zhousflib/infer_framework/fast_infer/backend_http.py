# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/12/19 
# @Function:
import numpy as np

from zhousflib.infer_framework.fast_infer.backend import Backend


class BackendHttp(Backend):
    def __init__(self, *args, **kwargs):
        self.model_dir = kwargs.get("model_dir")
        self.device_id = kwargs.get("device_id")
        self.model = None
        self.model_name = None
        self.model_version = None
        self.http_inputs = None
        self.http_outputs = None
        self.backend = "http"
        super().__init__(*args)

    def build(self, url: str, model_name: str, model_version: str, http_inputs: list, http_outputs: list, **kwargs):
        self.model_name = model_name
        self.model_version = model_version
        self.http_inputs = http_inputs
        self.http_outputs = http_outputs

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

        assert url is not None, "设置http后端时，url不能为空."
        assert self.model_name is not None, "设置http后端时，model_name不能为空."
        assert self.model_version is not None, "设置http后端时，model_version不能为空."

        concurrency = kwargs.get("concurrency", 1)
        from zhousflib.infer_framework.triton import client_http
        self.model = client_http.ClientHttp(url=url, concurrency=concurrency, **kwargs)

    def inference(self, input_data, **kwargs):
        inputs = []
        for i, input_ in enumerate(input_data):
            inputs.append(self.to_numpy(input_data[i].int()))
        # INT8|INT16|INT32|INT64|UINT8|UINT16|UINT32|UINT64|FP16|FP32|FP64
        d_type = self.http_inputs[0][1]
        if d_type == "INT16":
            data_arr = np.asarray(inputs, dtype=np.int16)
        elif d_type == "INT32":
            data_arr = np.asarray(inputs, dtype=np.int32)
        elif d_type == "INT64":
            data_arr = np.asarray(inputs, dtype=np.int64)
        elif d_type == "FP16":
            data_arr = np.asarray(inputs, dtype=np.float16)
        elif d_type == "FP32":
            data_arr = np.asarray(inputs, dtype=np.float32)
        elif d_type == "FP64":
            data_arr = np.asarray(inputs, dtype=np.float64)
        else:
            assert "暂不支持：{0}".format(d_type)
            data_arr = np.asarray(inputs, dtype=np.int64)
        input_list_ = []
        for i in range(0, len(data_arr)):
            input_list_.append(self.model.build_input(name=self.http_inputs[i][0], data=data_arr[i], datatype=self.http_inputs[i][1]))
        output_list_ = []
        for i in range(0, len(self.http_outputs)):
            output_list_.append(self.model.build_output(name=self.http_outputs[i]))
        """
        同步
        """
        result = self.model.infer_sync(model_name=self.model_name, model_version=self.model_version, inputs=input_list_, outputs=output_list_)
        if len(self.http_outputs) == 1:
            return result.as_numpy(self.http_outputs[0])
        else:
            results = []
            for i in range(0, len(self.http_outputs)):
                results.append(result.as_numpy(self.http_outputs[i]))
            return np.asarray(results)