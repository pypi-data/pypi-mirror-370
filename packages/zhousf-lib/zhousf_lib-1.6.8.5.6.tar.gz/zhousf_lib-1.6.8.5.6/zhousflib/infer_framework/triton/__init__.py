# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/12/14 
# @Function:

"""
官方文档：https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/performance_tuning.html
官方git：https://github.com/triton-inference-server/server/blob/main/docs/README.md#user-guide
# 创建模型仓库目录：
triton/models/模型名称/版本号/模型
# 在模型名称目录下创建模型配置文件：
参考：https://github.com/triton-inference-server/server/blob/main/docs/user_guide/model_configuration.md
config.pbtxt
# 创建一个模型仓库容器并启动一个模型推理服务（gpus=all）
在triton目录下运行：
docker run -it --rm --gpus '"device=1,2,3"' --network=host -v $PWD:/mnt --name zhousf-triton-server nvcr.io/nvidia/tritonserver:23.11-py3 tritonserver --model-repository=/mnt/models --http-port=5005 --grpc-port=5006 --metrics-port=5007 --log-info=true --log-error=true
docker run -it -d --rm --gpus=all --network=host -v $PWD:/mnt --name zhousf-triton-server nvcr.io/nvidia/tritonserver:23.11-py3 tritonserver --model-repository=/mnt/models --http-port=5005 --grpc-port=5006 --metrics-port=5007 --log-info=true --log-error=true
# 显示如下表示成功：
+---------------+---------+--------+
| Model         | Version | Status |
+---------------+---------+--------+
| cosnet_onnx   | 1       | READY  |
+---------------+---------+--------+
# 测试模型服务是否启动成功
curl -v localhost:5005/v2/health/ready

# 吞吐量测试
docker pull nvcr.io/nvidia/tritonserver:23.08-py3-sdk
docker run --gpus all --rm -it --net=host --name zhousf-perf_analyzer nvcr.io/nvidia/tritonserver:23.08-py3-sdk
perf_analyzer -m cosnet_onnx --shape attention_mask:10,128 --shape input_ids:10,128 --shape token_type_ids:10,128  -i http --concurrency-range 1:50:10 -u 0.0.0.0:5005
perf_analyzer -m cosnet_onnx --shape attention_mask:10,128 --shape input_ids:10,128 --shape token_type_ids:10,128  -i grpc --concurrency-range 1:50:10 -u 0.0.0.0:5006

"""


"""
name: "cosnet_onnx"
backend: "onnxruntime"
max_batch_size: 0
input: [
  {
    name: "input_ids",
    data_type: TYPE_INT64,
    dims: [ -1, 128]
  },
  {
    name: "attention_mask",
    data_type: TYPE_INT64,
    dims: [ -1, 128]
  },
  {
    name: "token_type_ids",
    data_type: TYPE_INT64,
    dims: [ -1, 128]
  }
]
output: [
  {
    name: "output",
    data_type: TYPE_FP16,
    dims: [ -1 ]
  }
dynamic_batching {
    max_queue_delay_microseconds: 10
}
instance_group [
  {
    count: 4
    kind: KIND_GPU
  }
]
"""

"""
name: "cosnet_tensorrt"
platform: "tensorrt_plan"
max_batch_size: 0
input: [
  {
    name: "input_ids"
    data_type: TYPE_INT32
    dims: [ 50, 128]
  },
  {
    name: "attention_mask"
    data_type: TYPE_INT32
    dims: [ 50, 128]
  },
  {
    name: "token_type_ids"
    data_type: TYPE_INT32
    dims: [ 50, 128]
  }
]
output: [
  {
    name: "output"
    data_type: TYPE_FP16
    dims: [ -1 ]
  }
]
instance_group [
  {
    count: 2
    kind: KIND_GPU
  }
]
"""

