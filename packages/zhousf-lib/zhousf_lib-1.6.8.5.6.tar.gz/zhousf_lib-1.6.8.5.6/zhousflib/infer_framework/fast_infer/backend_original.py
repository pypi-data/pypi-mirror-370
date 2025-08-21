# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/12/19 
# @Function:
from zhousflib.infer_framework.fast_infer.backend import Backend


class BackendOriginal(Backend):
    def __init__(self, *args, **kwargs):
        self.model_dir = kwargs.get("model_dir")
        self.device_id = kwargs.get("device_id")
        self.model = None
        self.backend = "original"
        super().__init__(*args)

    def build(self, **kwargs):
        module = kwargs.get("module")
        self.pop(kwargs, "module")
        self.model = module

    def inference(self, input_data, **kwargs):
        return self.model(input_data)