# ZhousfLib

python常用工具库：coco数据集、labelme数据集、segmentation数据集、classification数据集制作和转换脚本；文件操作、表格操作、数据结构、web服务封装等工具集

### 模型推理框架
####  infer_framework/fast_infer/fast_infer：快速推理器

* [fastdeploy]：支持fastdeploy推理框架
* [tensorrt]：支持tensorrt模型自动转换和推理
* [onnx]：支持onnx模型自动转换和推理
* [torch]：支持torch模型自动转换和推理

```python
import fastdeploy
from pathlib import Path
from zhousflib.infer_framework.fast_infer import FastInfer

def demo_classification():
    # 图像分类
    model_dir = Path(r"D:\workspace\ZhousfLib\model\PPLCNet_x1_0_infer-v9")
    fast = FastInfer(model_dir=model_dir, device_id=0)
    runtime_option = fastdeploy.RuntimeOption()
    # 采用onnx推理引擎
    runtime_option.use_ort_backend()
    """
    推理后端采用fastdeploy
    模型组件采用PaddleClasModel
    """
    fast.use_fastdeploy_backend(plugin="fd.vision.classification.PaddleClasModel", runtime_option=runtime_option)
    result = fast.infer(input_data=model_dir.joinpath("test.png"))
    print(result)

def demo_detection():
    # 目标检测
    model_dir = Path(r"D:\workspace\ZhousfLib\model\global_ppyoloe_plus_crn_l_80e_coco-v10")
    fast = FastInfer(model_dir=model_dir, device_id=0)
    runtime_option = fastdeploy.RuntimeOption()
    # 采用tensorrt推理引擎
    runtime_option.use_trt_backend()
    # 保存trt文件
    runtime_option.trt_option.serialize_file = str(model_dir.joinpath("model.trt"))
    """
    推理后端采用fastdeploy
    模型组件采用PPYOLOE
    """
    fast.use_fastdeploy_backend(plugin="fd.vision.detection.PPYOLOE", runtime_option=runtime_option)
    result = fast.infer(input_data=model_dir.joinpath("test.jpg"))
    print(result)

def demo_segmentation():
    # 图像分割
    model_dir = Path(r"D:\workspace\ZhousfLib\model\local_pp_liteseg_512x512_1k-v5")
    fast = FastInfer(model_dir=model_dir, device_id=-1)
    """
    推理后端采用fastdeploy
    模型组件采用PaddleSegModel
    """
    fast.use_fastdeploy_backend(plugin="fd.vision.segmentation.PaddleSegModel")
    image_file = model_dir.joinpath("test.jpg")
    vis_image_file = image_file.with_name("{0}_vis{1}".format(image_file.stem, image_file.suffix))
    # 保存并显示可视化文件vis_image_file
    result = fast.infer(input_data=image_file,
                        vis_image_file=vis_image_file,
                        vis_show=True)
    print(result.contain_score_map)

def demo_bert():
    import torch
    from zhousflib.infer_framework.ann.torch import torch_to_onnx
    fast_infer = FastInfer(model_dir=Path(r"F:\torch\test"), device_id=0)
    """
    推理后端采用tensorrt
    推理平台采用torch
    """
    fast_infer.use_tensorrt_backend(from_platform="torch",
                                    module=torch.nn.Module(),
                                    example_inputs=(torch_to_onnx.example_inputs_demo(device_id=0),),
                                    dynamic_axes={'input_ids': {0: 'batch_size'},
                                                  'token_type_ids': {0: 'batch_size'},
                                                  'attention_mask': {0: 'batch_size'},
                                                  'output': {0: 'batch_size'}},
                                    shape={"input_ids": [(10, 128), (10, 128), (10, 128)],
                                           "token_type_ids": [(10, 128), (10, 128), (10, 128)],
                                           "attention_mask": [(10, 128), (10, 128), (10, 128)]})
    return fast_infer.infer(torch_to_onnx.example_inputs_demo()).tolist()
```
---
####  infer_framework/triton/client_http：triton
```python
def demo():
    import numpy as np
    from zhousflib.infer_framework.ann import to_numpy
    from zhousflib.infer_framework.ann.torch.torch_to_onnx import example_inputs_demo
    from zhousflib.infer_framework.triton.client_http import ClientHttp
    args = example_inputs_demo(input_size=1)
    data_arr = np.asarray([to_numpy(args[0].int()), to_numpy(args[1].int()), to_numpy(args[2].int())], dtype=np.int64)
    client = ClientHttp(url="127.0.0.1:5005", concurrency=100)
    """
    同步请求demo
    """
    client.infer_sync_demo(data=data_arr, infer_count=500)
    """
    异步请求demo
    """
    # client.infer_async_demo(data=data_arr, infer_count=10)
```
---
####  infer_framework/ann：模型转换、加载、预测
*  ann/onnx/onnx_to_trt：onnx转tensorRT
```python
def demo_onnx_to_trt():
    from pathlib import Path
    from zhousflib.infer_framework.ann.onnx.onnx_to_trt import convert_trt
    convert_trt(onnx_file_path=Path(r"F:\torch\onnx\model.onnx"),
                save_trt_path=Path(r"F:\torch\onnx\model_32.trt"),
                use_fp16=True,
                shape={"input_ids": [(10, 128), (10, 128), (50, 128)],
                       "token_type_ids": [(10, 128), (10, 128), (50, 128)],
                       "attention_mask": [(10, 128), (10, 128), (50, 128)]})
```
*  ann/torch/torch_to_onnx：torch转onnx/加载onnx
```python
def convert_bert_demo():
    """
    转换示例：以bert转onnx为例
    :return:
    """
    import torch
    from pathlib import Path
    from zhousflib.infer_framework.ann.torch.torch_to_onnx import convert_onnx, example_inputs_demo
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
```
*  ann/torch/torch_to_script：torch转script/加载script
```python
def convert_bert_demo():
    """
    转换示例：以bert转torchScript为例
    :return:
    """
    import torch
    from pathlib import Path
    from zhousflib.infer_framework.ann.torch.torch_to_script import convert_script_model, example_inputs_demo
    convert_script_model(module=torch.nn.Module(),
                         model_dir=Path(r"F:\torch\train_model"),
                         export_dir=Path(r"F:\torch\script"),
                         device="cpu", example_inputs=(example_inputs_demo(), ))
```

*  ann/transformers：加载tokenizer
*  ann/tensorrt/tensorrt_infer：tensorRT推理
```python
def demo_trt_infer():
    import numpy as np
    from pathlib import Path
    from zhousflib.infer_framework.ann import to_numpy
    from zhousflib.infer_framework.ann.torch.torch_to_onnx import example_inputs_demo
    from zhousflib.infer_framework.ann.tensorrt.tensorrt_infer import RTInfer
    args = example_inputs_demo(input_size=1)
    batch = np.asarray([to_numpy(args[0].int()), to_numpy(args[1].int()), to_numpy(args[2].int())])
    rt_engine = RTInfer(trt_file_path=Path(r"F:\torch\onnx\model_32.trt"), device_id=0, use_stack=True)
    data = rt_engine.infer(input_arr=batch)
    print(data)
```


### 算法数据集制作

* [X]  datasets/classification：数据集制作
* [X]  datasets/coco：数据集制作、格式转换、可视化、统计、数据更新/合并/提取
* [X]  datasets/labelme：数据集制作、格式转换、可视化、统计、数据更新/合并/提取
* [X]  datasets/segmentation：数据集制作


### ML

* [X]  ml/feature_vector：特征向量表示器
* [X]  ml/model_cluster：kmeans聚类
* [X]  ml/model_lr：线性回归
* [X]  ml/model_gbdt：GBDT

### 数据库

* [X]  db/lmdb：内存映射数据库
* [X]  db/tinydb：轻量数据库，线程不安全

### 装饰器

* [X]  decorator：异常捕获，AOP

### 文件操作

* [X]  download：文件批量异步下载
* [X]  delete_file：文件删除

### 字体

* [X]  font：宋体、特殊符号字体

### 并发压测工具

* [X]  locust：demo

### 表格文件工具

* [X]  pandas：excel/csv操作、大文件读取

### pdf文件工具

* [X]  pdf：pdf导出图片、pdf文本和表格提取

### so加密工具

* [X]  so：python工程加密成so，防逆向

### web相关

* [X]  web：flask日志工具、响应体、配置

### 通用工具包

* [X]  util

* [util/cv_util]：opencv读写中文路径图片，图像相关处理
* [util/char_util]：字符相关处理，全角、半角
* [util/encrypt_util]：AES加密
* [util/iou_util]：IoU计算
* [util/json_util]：json读写
* [util/poly_util]：按照宽高对图片进行网格划分/切图
* [util/re_util]：re提取数字、字母、中文
* [util/singleton]：单例
* [util/string_util]：非空、包含、补齐
* [util/time_util]：日期、毫秒级时间戳、微秒级时间戳、日期比较



