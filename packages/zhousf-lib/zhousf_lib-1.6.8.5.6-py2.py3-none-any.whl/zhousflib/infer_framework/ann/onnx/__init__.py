# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/12/21 
# @Function:
import onnxruntime
"""
【onnx && cuda的版本对应关系】
onnx对应cuda的版本：https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html#requirements
注意onnxruntime与opset版本的对应关系


############## 【安装onnxruntime】 ##############
选择版本：https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html#requirements
【cpu】
pip install onnxruntime==1.13.1 -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
【gpu】
pip install onnxruntime-gpu==1.13.1 -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
验证：
import onnxruntime
onnxruntime.get_device()


############## 【验证导出onnx是否正确】 ##############
可视化网络结构：https://netron.app/
当output有if条件则会存在问题，更换opset版本(opset=10)或降低torch版本(1.8.0)
"""


def load_onnx(**kwargs):
    """
    加载onnx模型
    :return:
    ort_session = load_onnx(model_dir=Path(r"model.onnx"))
    ort_input = ort_session.get_inputs()
    args = example_inputs_demo()
    ort_inputs = {ort_input[0].name: to_numpy(args[0]),
                  ort_input[1].name: to_numpy(args[1]),
                  ort_input[2].name: to_numpy(args[2])}
    ort_outs = ort_session.run(None, ort_inputs)
    print(ort_outs[0])
    """
    model_file = kwargs.get("model_file")
    # cpu上运行：-1 | gpu上运行：0 or 1 or 2...
    device_id = kwargs.get("device_id", -1)
    # 预测优化
    ir_optim = kwargs.get("ir_optim", True)
    # 多核处理节点 Sets the number of threads used to parallelize the execution within nodes
    intra_op_num_threads = kwargs.get("intra_op_num_threads", 8)
    # 并行处理子图 Sets the number of threads used to parallelize the execution of the graph (across nodes).
    inter_op_num_threads = kwargs.get("inter_op_num_threads", 100)
    assert model_file is not None, "onnx file not found: {0}".format(model_file)
    config = onnxruntime.SessionOptions()
    config.intra_op_num_threads = intra_op_num_threads
    if ir_optim:
        # 启用图优化
        config.graph_optimization_level = onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL
        # 内部子图并行计算
        config.execution_mode = onnxruntime.ExecutionMode.ORT_PARALLEL
        config.inter_op_num_threads = inter_op_num_threads
    if device_id == -1:
        onnx_session = onnxruntime.InferenceSession(str(model_file))
    else:
        onnx_session = onnxruntime.InferenceSession(str(model_file), providers=['CUDAExecutionProvider'],
                                                    provider_options=[{'device_id': device_id}])
    return onnx_session


class OnnxPredictor(object):
    """
    from zhousflib.infer_framework.ann.onnx import OnnxPredictor
    model_onnx = OnnxPredictor(model_file=model_dir, device_id=0)
    x = np.random.random((1, 3, 800, 608)).astype('float32')
    ort_inputs = {model_onnx.session.get_inputs()[0].name: x}
    res = model_onnx.run(output_names=None, input_feed=ort_inputs)
    print(res)
    """

    def __init__(self, **kwargs):
        self.predictor = load_onnx(**kwargs)

    @property
    def session(self):
        return self.predictor

    def run(self, output_names, input_feed):
        return self.predictor.run(output_names=output_names, input_feed=input_feed)


