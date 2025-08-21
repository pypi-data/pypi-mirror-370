# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/12/18 
# @Function:
import json
import time
from pathlib import Path


class FastInfer:

    def __init__(self, model_dir: Path = None, device_id=-1):
        """
        :param model_dir:
        :param device_id: cpu上运行：-1 | gpu上运行：0 or 1 or 2...
        """
        self.model_dir = model_dir
        self.device_id = device_id
        self.model = None
        self.backend = None

    def use_http_backend(self, url: str, model_name: str, model_version: str, http_inputs: list, http_outputs: list, **kwargs):
        """
        设置推理后端：http
        :param url:
        :param model_name:
        :param model_version:
        :param http_inputs:
        :param http_outputs:
        :param kwargs:
        :return:
        example:
        .use_http_backend(url="127.0.0.1:5005",
                          model_name="cosnet_onnx",
                          model_version="1",
                          http_inputs=[("input_ids", "INT64"), ("token_type_ids", "INT64"), ("attention_mask", "INT64")],
                          http_outputs=["output"])
        """
        from zhousflib.infer_framework.fast_infer.backend_http import BackendHttp
        self.backend = BackendHttp(model_dir=self.model_dir, device_id=self.device_id)
        self.model = self.backend.model
        return self.backend.build(url=url, model_name=model_name, model_version=model_version, http_inputs=http_inputs, http_outputs=http_outputs, **kwargs)

    def use_original_backend(self, module=None, **kwargs):
        """
        设置推理后端：原始模型-动态图
        :param module:
        :param kwargs:
        :return:
        example:
        .use_original_backend(module=torch.nn.Module())
        """
        from zhousflib.infer_framework.fast_infer.backend_original import BackendOriginal
        self.backend = BackendOriginal(model_dir=self.model_dir, device_id=self.device_id)
        self.model = self.backend.model
        return self.backend.build(module=module, **kwargs)

    def use_onnx_backend(self, from_platform: str = None, module=None, dynamic_axes: dict = None, opset_version=10, example_inputs=None, **kwargs):
        """
        设置推理后端：onnxruntime
        :param from_platform:
        :param module:
        :param dynamic_axes:
        :param opset_version:
        :param example_inputs:
        :param kwargs:
        :return:
        example:
        .use_onnx_backend(from_platform="torch",
                          module=torch.nn.Module(),
                          example_inputs=example_inputs,
                          dynamic_axes={'input_ids': {0: 'batch_size'},
                                        'token_type_ids': {0: 'batch_size'},
                                        'attention_mask': {0: 'batch_size'},
                                        'output': {0: 'batch_size'}})
        """
        from zhousflib.infer_framework.fast_infer.backend_onnx import BackendONNX
        self.backend = BackendONNX(model_dir=self.model_dir, device_id=self.device_id)
        self.model = self.backend.model
        return self.backend.build(from_platform=from_platform, module=module, dynamic_axes=dynamic_axes, opset_version=opset_version, example_inputs=example_inputs, **kwargs)

    def use_tensorrt_backend(self, from_platform: str = None, module=None, dynamic_axes: dict = None, opset_version=10,
                             example_inputs=None, shape: dict = None, **kwargs):
        """
        设置推理后端：tensorrt
        :param from_platform:
        :param module:
        :param dynamic_axes:
        :param opset_version:
        :param example_inputs:
        :param shape:
        :param kwargs:
        :return:
        example:
        若onnx文件存在时则只需传参数shape
        .use_tensorrt_backend(shape={"input_ids": [(10, 128), (10, 128), (10, 128)],
                                     "token_type_ids": [(10, 128), (10, 128), (10, 128)],
                                     "attention_mask": [(10, 128), (10, 128), (10, 128)]})
        若onnx文件不存在时
        .use_tensorrt_backend(from_platform="torch",
                              module=torch.nn.Module(),
                              example_inputs=example_inputs,
                              dynamic_axes={'input_ids': {0: 'batch_size'},
                                          'token_type_ids': {0: 'batch_size'},
                                          'attention_mask': {0: 'batch_size'},
                                          'output': {0: 'batch_size'}},
                              shape={"input_ids": [(10, 128), (10, 128), (10, 128)],
                                     "token_type_ids": [(10, 128), (10, 128), (10, 128)],
                                     "attention_mask": [(10, 128), (10, 128), (10, 128)]})
        """
        from zhousflib.infer_framework.fast_infer.backend_tensorrt import BackendTensorRT
        self.backend = BackendTensorRT(model_dir=self.model_dir, device_id=self.device_id)
        self.model = self.backend.model
        return self.backend.build(from_platform=from_platform, module=module, dynamic_axes=dynamic_axes,
                                  opset_version=opset_version, example_inputs=example_inputs, shape=shape, **kwargs)

    def use_torch_script_backend(self, module=None, example_inputs=None, **kwargs):
        """
        设置推理后端：torch_script
        :param module:
        :param example_inputs:
        :param kwargs:
        :return:
        example:
        .use_torch_script_backend(module=torch.nn.Module(), example_inputs=example_inputs)
        """
        from zhousflib.infer_framework.fast_infer.backend_torch_script import BackendTorchScript
        self.backend = BackendTorchScript(model_dir=self.model_dir, device_id=self.device_id)
        self.model = self.backend.model
        return self.backend.build(module=module, example_inputs=example_inputs, **kwargs)

    def use_fastdeploy_backend(self, **kwargs):
        """
        设置推理后端：fastdeploy
        :param kwargs:
        :return:
        example:
        """
        from zhousflib.infer_framework.fast_infer.backend_fastdeploy import BackendFastDeploy
        self.backend = BackendFastDeploy(model_dir=self.model_dir, device_id=self.device_id)
        self.model = self.backend.model
        return self.backend.build(**kwargs)

    def infer(self, input_data, **kwargs):
        assert self.backend is not None, "请设置backend，例如: use_onnx_backend()"
        return self.backend.inference(input_data=input_data, **kwargs)

    def infer_batch(self, input_data, **kwargs):
        assert self.backend is not None, "请设置backend，例如: use_onnx_backend()"
        return self.backend.inference_batch(input_data=input_data, **kwargs)


def demo_bert():
    import torch
    from zhousflib.infer_framework.ann.torch import torch_to_onnx
    fast_infer = FastInfer(model_dir=Path(r"F:\torch\test"), device_id=0)
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


def demo_classification():
    import fastdeploy
    """
    classification
    """
    model_dir = model_base_dir.joinpath(r"Classification\PPLCNet_x1_0_infer-v9")
    fast = FastInfer(model_dir=model_dir, device_id=0)
    runtime_option = fastdeploy.RuntimeOption()
    runtime_option.use_ort_backend()
    fast.use_fastdeploy_backend(plugin="fd.vision.classification.PaddleClasModel", runtime_option=runtime_option)
    result = fast.infer(input_data=model_dir.joinpath("test.png"), topk=5)
    print(result)

    """
    extract image feature
    """
    model_dir = model_base_dir.joinpath(r"FeatureExtractImage\general_PPLCNetV2_base_pretrained_v1.0")
    # fast = FastInfer(model_dir=model_dir, device_id=-1)
    # fast.use_fastdeploy_backend(plugin="fd.vision.classification.PPShiTuV2Recognizer", clone_model=True)
    # result = fast.infer(input_data=model_dir.joinpath("test.jpg"))
    # print(result.feature)


def demo_detection():
    import fastdeploy
    """
    目标检测
    """
    model_dir = model_base_dir.joinpath(r"ObjectDetection\ppyoloe_plus_crn_l_80e_coco-v10")
    # fast = FastInfer(model_dir=model_dir, device_id=0)
    # runtime_option = fastdeploy.RuntimeOption()
    # runtime_option.use_trt_backend()
    # runtime_option.trt_option.serialize_file = str(model_dir.joinpath("model.trt"))
    # fast.use_fastdeploy_backend(plugin="fd.vision.detection.PPYOLOE", runtime_option=runtime_option)
    # result = fast.infer(input_data=model_dir.joinpath("test.jpg"), score_threshold=0.8, vis_show=True)
    # print(result)

    """
    版面分析
    """
    # model_dir = model_base_dir.joinpath(r"LayoutAnalysis\layout_picodet_l_640_coco_lcnet")
    # model_dir = model_base_dir.joinpath(r"LayoutAnalysis\PicoDet-L_layout_17cls_infer")
    model_dir = model_base_dir.joinpath(r"LayoutAnalysis\PP-DocLayout-S_infer")
    # model_dir = model_base_dir.joinpath(r"LayoutAnalysis\PP-DocLayout-M_infer")
    fast = FastInfer(model_dir=model_dir, device_id=0)
    runtime_option = fastdeploy.RuntimeOption()
    runtime_option.paddle_infer_option.enable_log_info = True
    runtime_option.use_paddle_backend()
    # runtime_option.use_trt_backend()
    # runtime_option.trt_option.serialize_file = str(model_dir.joinpath("model.trt"))
    # fast.use_fastdeploy_backend(plugin="fd.vision.detection.PicoDet", runtime_option=runtime_option)
    fast.use_fastdeploy_backend(plugin="fd.vision.detection.GFL", runtime_option=runtime_option)
    from PIL import ImageFont
    from zhousflib.font import Font_SimSun
    font = ImageFont.truetype(font=str(Font_SimSun), size=20)
    img_file = model_dir.joinpath("test.png")
    img_file = Path(r"D:\home\paas\zhousf\log\pdf_parse_omni\PP-DocLayout-S_infer_nms-L\images\1.png")
    result = fast.infer(input_data=img_file,
                        vis_font=font,
                        vis_font_color="red",
                        score_threshold=0.3,
                        nms_match_threshold=0.8,
                        nms_match_metric="ios",
                        vis_fill_transparent=10,
                        vis_show=True)
    print(result)


def demo_batch_predict():
    import fastdeploy
    model_dir = model_base_dir.joinpath(r"LayoutAnalysis\layout_picodet_l_640_coco_lcnet")
    fast = FastInfer(model_dir=model_dir, device_id=0)
    runtime_option = fastdeploy.RuntimeOption()
    runtime_option.paddle_infer_option.enable_log_info = True
    runtime_option.use_paddle_backend()
    fast.use_fastdeploy_backend(plugin="fd.vision.detection.PicoDet", runtime_option=runtime_option)
    from PIL import ImageFont
    from zhousflib.font import Font_SimSun
    font = ImageFont.truetype(font=str(Font_SimSun), size=16)
    result = fast.infer_batch(input_data=[model_dir.joinpath("test.png"), model_dir.joinpath("test1.png")],
                              vis_font=font,
                              vis_font_color="red",
                              score_threshold=0.5,
                              vis_show=True)


def demo_segmentation():
    model_dir = model_base_dir.joinpath(r"Segmentation\pp_liteseg_512x512_1k-v5")
    fast = FastInfer(model_dir=model_dir, device_id=-1)
    fast.use_fastdeploy_backend(plugin="fd.vision.segmentation.PaddleSegModel")
    image_file = model_dir.joinpath("test.jpg")
    vis_image_file = image_file.with_name("{0}_vis{1}".format(image_file.stem, image_file.suffix))
    result = fast.infer(input_data=image_file,
                        vis_image_file=vis_image_file,
                        vis_show=False)
    print(result.contain_score_map)


def demo_ocr():
    import fastdeploy as fd
    """
    detector
    """
    # det_model = model_base_dir.joinpath(r"OCR\ch_PP-OCRv4_det_infer")
    det_model = model_base_dir.joinpath(r"OCR\PP-OCRv5_mobile_det_infer")
    # det_model = model_base_dir.joinpath(r"OCR\ch_PP-OCRv4_det_mobile_infer")
    cls_model = model_base_dir.joinpath(r"OCR\ch_ppocr_mobile_v2.0_cls_slim_infer")
    # rec_model = model_base_dir.joinpath(r"OCR\PP-OCRv5_server_rec_infer")
    rec_model = model_base_dir.joinpath(r"OCR\PP-OCRv5_mobile_rec_infer")
    # rec_model = model_base_dir.joinpath(r"OCR\ch_PP-OCRv4_rec_infer")
    # rec_model = model_base_dir.joinpath(r"OCR\PP-OCRv4_server_rec")
    # fast = FastInfer(det_model=det_model, device_id=0)
    # fast.use_fastdeploy_backend(plugin="fd.vision.ocr.DBDetector")
    # image_file = model_dir.joinpath("test.jpg")
    # vis_image_file = image_file.with_name("{0}_vis{1}".format(image_file.stem, image_file.suffix))
    # res = fast.infer(input_data=image_file,
    #                  vis_image_file=vis_image_file,
    #                  vis_show=True)
    # print(res.boxes)

    """
    recognizer
    """
    # fast = FastInfer(model_dir=rec_model, device_id=0)
    # fast.use_fastdeploy_backend(plugin="fd.vision.ocr.Recognizer")
    # image_file = model_dir.joinpath("test.jpg")
    # res = fast.infer(input_data=image_file,
    #                  vis_image_file=None,
    #                  vis_show=False)
    # print(res)

    """
    ocr
    """
    runtime_option = fd.RuntimeOption()
    runtime_option.set_cpu_thread_num(10)
    # runtime_option.use_ort_backend()
    runtime_option.use_paddle_backend()
    # runtime_option.paddle_infer_option.enable_log_info = True  # print log
    fast_det = FastInfer(model_dir=det_model, device_id=0)
    fast_det.use_fastdeploy_backend(plugin="fd.vision.ocr.DBDetector")
    fast_det.backend.model.preprocessor.max_side_len = 960
    fast_det.backend.model.preprocessor.static_shape_infer = False
    fast_det.backend.model.postprocessor.det_db_score_mode = 'fast'
    fast_det.backend.model.postprocessor.det_db_unclip_ratio = 1.5
    fast_det.backend.model.postprocessor.use_dilation = True
    fast_cls = FastInfer(model_dir=cls_model, device_id=0)
    fast_cls.use_fastdeploy_backend(plugin="fd.vision.ocr.Classifier")
    fast_cls.backend.model.postprocessor.cls_thresh = 0.96
    fast_rec = FastInfer(model_dir=rec_model, device_id=0)
    fast_rec.use_fastdeploy_backend(plugin="fd.vision.ocr.Recognizer")
    fast_ocr = FastInfer(model_dir=None, device_id=0)
    fast_ocr.use_fastdeploy_backend(plugin="fd.vision.ocr.PPOCRv4",
                                    det_model=fast_det.backend.model,
                                    cls_model=fast_cls.backend.model,
                                    rec_model=fast_rec.backend.model, runtime_option=runtime_option, clone_model=False)
    fast_ocr.backend.model.rec_batch_size = 8
    fast_ocr.backend.model.cls_batch_size = 8

    image_file = model_base_dir.joinpath(r"OCR/test2.jpeg")
    # image_file = Path(r"E:\数据2024\OCR难例\手写体\0ab110ec45841bdfb3ce613445fb3c6a.jpg")
    from zhousflib.image import read
    # vis_image_file = image_file.with_name("{0}_ocr_vis{1}".format(image_file.stem, image_file.suffix))
    # res = fast_ocr.infer(input_data=read(image_file), image_path=image_file,
    #                      vis_image_file=vis_image_file,
    #                      vis_show=True)

    start = time.time()
    page = 0
    for image in Path(r"D:\workspace\PdfParseOmni\data").joinpath("images").rglob("*.png"):
        if image.stem.endswith("_vis"):
            continue
        print(image)
        fast_ocr.infer(input_data=read(image_file), image_path=image_file,
                       vis_image_file=None,
                       vis_show=False)
        page += 1
    print(f"avg page cost time: {(time.time() - start) / page}, page={page}")

    # print(res)
    # start = time.time()
    # for i in range(10):
    #     res = fast_ocr.infer(input_data=image_file,
    #                          vis_image_file=vis_image_file,
    #                          vis_show=False)
    #     print(res)
    # print(f"{(time.time()-start)/10}")


def demo_uie():
    import fastdeploy as fd
    runtime_option = fd.RuntimeOption()
    runtime_option.use_paddle_backend()
    fast_infer = FastInfer(model_dir=model_base_dir.joinpath(r"UIE\uie-mini"), device_id=0)
    fast_infer.use_fastdeploy_backend(plugin="fd.text.uie.UIEModel", batch_size=32, position_prob=0.3, max_length=256,
                                      runtime_option=runtime_option, clone_model=True)
    start = time.time()
    count = 1
    for i in range(count):
        res = fast_infer.infer(input_data=["2月8日上午北京冬奥会自由式滑雪女子大跳台决赛中中国选手谷爱凌以188.25分获得金牌！",
                                           "在北京举行的2024年世界乒乓球职业大联盟（WTT）中国大满贯男子双打决赛中，中国组合王楚钦/梁靖崑3比2战胜队友林高远/林诗栋，夺得冠军。"],
                               return_dict=True, schema=["时间", "选手", "赛事名称"])
        print(json.dumps(res, ensure_ascii=False, indent=2))
    # res = fast_infer.infer(input_data=[r"北京市海淀区人民法院\n民事判决书\n(199x)建初字第xxx号\n原告：张三。\n委托代理人李四，北京市 A律师事务所律师。\n被告：B公司，法定代表人王五，开发公司总经理。\n委托代理人赵六，北京市 C律师事务所律师。"],
    #                        return_dict=True, schema=['法院', {'原告': '委托代理人'}, {'被告': '委托代理人'}])
    # print(json.dumps(res, ensure_ascii=False, indent=2))
    print(f"cost time: {(time.time() - start) / count}")
    pass


if __name__ == "__main__":
    model_base_dir = Path(r"D:\workspace\ZhousfLib\model")
    # demo_uie()
    # demo_ocr()
    # demo_classification()
    demo_detection()
    # demo_segmentation()
    pass
