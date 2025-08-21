# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/11/27 
# @Function: 人工神经网络

"""
############## 【安装CUDA】 ##############
CUDA下载：https://developer.nvidia.com/cuda-toolkit-archive
推荐版本：CUDA Toolkit 11.7
【windows】
新建系统环境变量：CUDA_PATH=C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7
新建系统环境变量：CUDA_PATH_V11_7=C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7
验证：在cmd中运行 nvcc -V
【linux】
vim ~/.bashrc
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64
export PATH=$PATH:/usr/local/cuda/bin
export CUDA_HOME=$CUDA_HOME:/usr/local/cuda
source ~/.bashrc
验证：
nvcc -V


############## 【安装cuDNN】 ##############
cudnn下载：https://developer.nvidia.com/rdp/cudnn-archive
推荐版本：cuDNN v8.9.0 for CUDA11.x
【windows】
将目录下的bin、lib（lib选择x64）、include文件夹复制到C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/11.7目录中
添加系统环境变量：Path=C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/bin
添加系统环境变量：Path=C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/libnvvp
验证：
在cmd中运行 C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/extras/demo_suite/deviceQuery.exe
显示Result = PASS则成功


############## 【安装tensorRT】 ##############
官方文档：https://docs.nvidia.com/deeplearning/tensorrt/archives/tensorrt-861/quick-start-guide/index.html
tensorrt下载：https://developer.nvidia.com/nvidia-tensorrt-8x-download
【windows】
将目录下的bin、lib（lib选择x64）、include文件夹复制到C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/11.7目录中
添加系统环境变量：Path=C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/bin
添加系统环境变量：Path=C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/libnvvp
添加系统环境变量：Path=C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/include
添加系统环境变量：Path=C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/lib/x64
设置完后重启电脑
python -m pip install TensorRT-8.6.1.6/python/tensorrt-8.6.1-cp39-none-linux_x86_64.whl
pip install TensorRT-8.6.1.6/uff/uff-0.6.9-py2.py3-none-any.whl
pip install TensorRT-8.6.1.6/graphsurgeon/graphsurgeon-0.4.6-py2.py3-none-any.whl
pip install TensorRT-8.6.1.6/onnx_graphsurgeon/onnx_graphsurgeon-0.3.12-py2.py3-none-any.whl
【linux】
下载地址：https://developer.nvidia.com/nvidia-tensorrt-download
1、选择deb file方式安装：
os="ubuntuxx04"
tag="8.x.x-cuda-x.x"
sudo dpkg -i nv-tensorrt-local-repo-${os}-${tag}_1.0-1_amd64.deb
sudo cp /var/nv-tensorrt-local-repo-${os}-${tag}/*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get install tensorrt
2、选择tar file方式安装：
解压：tar -zxvf TensorRT-8.6.1.6.Linux.x86_64-gnu.cuda-11.8.tar.gz
cd TensorRT-8.6.1.6/python
python -m pip install tensorrt-8.6.1-cp39-none-linux_x86_64.whl
配置环境变量：
建议使用(避免每次source)：vim /etc/profile
vim ~/.bashrc
export PATH=/root/zhousf/tensorrt/TensorRT-8.6.1.6/bin:$PATH
export LIBRARY_PATH=/root/zhousf/tensorrt/TensorRT-8.6.1.6/lib:$LIBRARY_PATH
export LD_LIBRARY_PATH=/root/zhousf/tensorrt/TensorRT-8.6.1.6/targets/x86_64-linux-gnu/lib:$LD_LIBRARY_PATH
source ~/.bashrc
建议使用：source /etc/profile
验证：
import tensorrt as trt
print(trt.__version__)


############## 【安装pycuda】 ##############
先安装cuda
安装文档：https://wiki.tiker.net/PyCuda/Installation/
python -m pip install pycuda==2022.1
若安装失败可以采用conda安装：conda install pycuda
若windows安装失败可以采用下载文件方式：https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycuda
下面是下载源码编译方式：https://pypi.org/project/pycuda/#files
tar -zxvf pycuda-2023.1.tar.gz
cd pycuda-2023.1
python setup.py build
python setup.py install
验证：
import pycuda.driver as cuda
import pycuda.autoinit
cuda.init()
print("CUDA device count:", cuda.Device.count())

报错：PyCUDA The context stack was not empty upon module cleanup 解决方法：import pycuda.autoinit
报错：pycuda._driver.LogicError: cuMemcpyHtoDAsync failed: invalid argument  解决方法：数据没有格式化为int类型，to_numpy(data.int())
当预测结果都是0时，可能是trt多线程的问题
解决方法： 
    import pycuda.autoinit
    self.cfx = cuda.Device(0).make_context()
    self.cfx.push()
    推理代码...
    self.cfx.pop()


############## 【安装torch】 ##############
选择版本：https://pytorch.org/get-started/locally/
【cpu】
pip install torch==1.13.1+cpu torchvision==0.14.1+cpu torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cpu
【gpu】
pip install torch==1.13.1+cu117 torchvision==0.14.1+cu117 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu117
验证：
import torch
print(torch.__version__)


############## 【安装transformers(from HuggingFace)】 ##############
# 注意版本要一致，不然会报错：Unexpected key(s) in state_dict: "bert.embeddings.position_ids".
pip install transformers==4.30.2 -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com


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


def to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()


def check_device_id(device_id: int = -1):
    """
    :param device_id: cpu上运行：-1 | gpu上运行：0 or 1 or 2...
    :return:
    """
    assert device_id >= -1, 'Expected device_id >= 1, but device_id={0}.'.format(device_id)

