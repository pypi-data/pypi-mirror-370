# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/12/7 
# @Function: 参考 https://github.com/NVIDIA/TensorRT/blob/master/samples/python/common.py

import os
os.environ["CUDA_MODULE_LOADING"] = "LAZY"
from pathlib import Path

import numpy as np
import pycuda.driver as cuda
import tensorrt as trt

from zhousflib.infer_framework.ann import check_device_id

"""
ERROR: INVALID_CONFIG: The engine plan file is generated on an incompatible device, 
expecting compute 6.1 got compute 7.5, please rebuild. 
解决方法：在线上重新进行TensorRT模型的转换(本地机器上的GPU与线上机器的GPU版本不一致，导致的加速版本不一致)
"""

try:
    # Sometimes python does not understand FileNotFoundError
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


# Simple helper data class that's a little nicer to use than a 2-tuple.
class HostDeviceMem(object):
    def __init__(self, host_mem, device_mem):
        self.host = host_mem
        self.device = device_mem

    def __str__(self):
        return "Host:\n" + str(self.host) + "\nDevice:\n" + str(self.device)

    def __repr__(self):
        return self.__str__()


class RTInfer(object):

    def __init__(self, trt_file_path: Path, device_id: int = -1, use_stack=False):
        """

        :param trt_file_path: trt文件路径
        :param device_id: cpu上运行：-1 | gpu上运行：0 or 1 or 2...
        :param use_stack: 是否使用压栈策略，牺牲并发性能
        """
        check_device_id(device_id)
        self.cuda_ctx = cuda.Device(device_id).make_context() if use_stack else None
        with trt_file_path.open("rb") as f:
            runtime = trt.Runtime(trt.Logger(trt.Logger.WARNING))
            self.engine = runtime.deserialize_cuda_engine(f.read())
            self.context = self.engine.create_execution_context()

    @staticmethod
    def allocate_buffers(engine):
        inputs = []
        outputs = []
        bindings = []
        stream = cuda.Stream()
        for binding in engine:
            size = trt.volume(engine.get_binding_shape(binding)) * engine.max_batch_size
            dtype = trt.nptype(engine.get_binding_dtype(binding))
            # Allocate host and device buffers
            host_mem = cuda.pagelocked_empty(size, dtype)
            device_mem = cuda.mem_alloc(host_mem.nbytes)
            # Append the device buffer to device bindings.
            bindings.append(int(device_mem))
            # Append to the appropriate list.
            if engine.binding_is_input(binding):
                inputs.append(HostDeviceMem(host_mem, device_mem))
            else:
                outputs.append(HostDeviceMem(host_mem, device_mem))
        return inputs, outputs, bindings, stream

    # This function is generalized for multiple inputs/outputs.
    # inputs and outputs are expected to be lists of HostDeviceMem objects.
    def do_inference(self, context, bindings, inputs, outputs, stream, batch_size=1):
        # Transfer input data to the GPU.
        [cuda.memcpy_htod_async(inp.device, inp.host, stream) for inp in inputs]
        if self.cuda_ctx:
            self.cuda_ctx.push()
        # Run inference.
        context.execute_async(batch_size=batch_size, bindings=bindings, stream_handle=stream.handle)
        if self.cuda_ctx:
            self.cuda_ctx.pop()
        # Transfer predictions back from the GPU.
        [cuda.memcpy_dtoh_async(out.host, out.device, stream) for out in outputs]
        # Synchronize the stream
        stream.synchronize()
        # Return only the host outputs.
        return [out.host for out in outputs]

    # This function is generalized for multiple inputs/outputs for full dimension networks.
    # inputs and outputs are expected to be lists of HostDeviceMem objects.
    def do_inference_v2(self, context, bindings, inputs, outputs, stream):
        # Transfer input data to the GPU.
        [cuda.memcpy_htod_async(inp.device, inp.host, stream) for inp in inputs]
        if self.cuda_ctx:
            self.cuda_ctx.push()
        # Run inference.
        context.execute_async_v2(bindings=bindings, stream_handle=stream.handle)
        if self.cuda_ctx:
            self.cuda_ctx.pop()
        # Transfer predictions back from the GPU.
        [cuda.memcpy_dtoh_async(out.host, out.device, stream) for out in outputs]
        # Synchronize the stream
        stream.synchronize()
        # Return only the host outputs.
        return [out.host for out in outputs]

    def infer(self, input_arr: np.asarray, batch_size: int = None):
        """
        推理
        :param input_arr: input_arr=np.asarray([to_numpy(args[0].int()), to_numpy(args[1].int()), to_numpy(args[2].int())])
        :param batch_size:
        :return:
        """
        self.context.active_optimization_profile = 0
        for i, item in enumerate(input_arr):
            self.context.set_binding_shape(i, item.shape)
        inputs, outputs, bindings, stream = self.allocate_buffers(self.engine)
        for i, item in enumerate(input_arr):
            inputs[i].host = item
        if batch_size:
            return self.do_inference(self.context, bindings=bindings, inputs=inputs, outputs=outputs, stream=stream, batch_size=batch_size)
        else:
            return self.do_inference_v2(self.context, bindings=bindings, inputs=inputs, outputs=outputs, stream=stream)


if __name__ == "__main__":
    from zhousflib.infer_framework.ann import to_numpy
    from zhousflib.infer_framework.ann.torch.torch_to_onnx import example_inputs_demo
    from zhousflib.infer_framework.ann.tensorrt.tensorrt_infer import RTInfer
    args = example_inputs_demo(input_size=1)
    batch = np.asarray([to_numpy(args[0].int()), to_numpy(args[1].int()), to_numpy(args[2].int())])
    rt_engine = RTInfer(trt_file_path=Path(r"F:\torch\onnx\model_32.trt"), device_id=0, use_stack=True)
    data = rt_engine.infer(input_arr=batch)
    print(data)
