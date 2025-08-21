# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:
import sys
import copy
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import yaml
import numpy
from PIL import Image
import fastdeploy as fd
from easydict import EasyDict
from fastdeploy import ModelFormat
from fastdeploy.libs.fastdeploy_main.vision import (
    ClassifyResult,
    DetectionResult,
    SegmentationResult,
    OCRResult
)

from zhousflib.image import read
from zhousflib.image import op
from zhousflib.image import pil_util
from zhousflib.util import ocr_vis_util
from zhousflib.font import Font_SimSun
from zhousflib.image import write
from zhousflib.image.nms_util import multiclass_nms
from zhousflib.infer_framework.fast_infer.backend import Backend
"""
download wheel
https://www.paddlepaddle.org.cn/whl/fastdeploy.html

https://www.paddlepaddle.org.cn/install/quick?docurl=/documentation/docs/zh/install/pip/linux-pip.html

version base on cpu
pip install fastdeploy-python -f https://www.paddlepaddle.org.cn/whl/fastdeploy.html

version base on gpu
pip install fastdeploy-gpu-python -f https://www.paddlepaddle.org.cn/whl/fastdeploy.html
conda config --add channels conda-forge && conda install cudatoolkit=11.2 cudnn=8.2

[question]
ExternalError: CUDNN error(9), CUDNN_STATUS_NOT_SUPPORTED.
[solution]
pip install cuda-python==12.3.0


[question]
ImportError: libcudart.so.11.0: cannot open shared object file: No such file or directory
[solution]
cd $CONDA_PREFIX
mkdir -p ./etc/conda/activate.d
touch ./etc/conda/activate.d/env_vars.sh

[question]
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
[solution]
pip install opencv-python-headless -i https://pypi.tuna.tsinghua.edu.cn/simple

[question]
RuntimeError: FastDeploy initalized failed! Error: /lib64/libstdc++.so.6: version `GLIBCXX_3.4.21' not found
[solution]
find / -name "libstdc++.so*"
找到后选择其中一个目录， 例如：/root/anaconda3/lib
export LD_LIBRARY_PATH=/root/anaconda3/envs/paddlenlp/lib/:$LD_LIBRARY_PATH


"""


EXTRA_PARAMS = ["vis_image_file", "vis_show", "vis_font", "vis_font_color", "vis_fill_transparent",
                "vis_transparent_weight", "schema", "score_threshold", "max_connectivity_domain",
                "mask_hole_area_thresh", "vis_image_size", "nms_match_threshold", "nms_match_metric", "image_path"]


class BackendFastDeploy(Backend):
    def __init__(self, *args, **kwargs):
        self.model_dir: Path = kwargs.get("model_dir")
        self.device_id = kwargs.get("device_id")
        self.backend = None
        self.plugin = None
        self.model = None
        self.label_list = []
        self.label_id_list = []
        self.clone_model = False
        super().__init__(*args)
        self.plugins = self.__register_plugin()

    @staticmethod
    def __register_plugin():
        plugin_classification = {
            "fd.vision.classification.PaddleClasModel": fd.vision.classification.PaddleClasModel,
            "fd.vision.classification.PPShiTuV2Recognizer": fd.vision.classification.PPShiTuV2Recognizer,
        }
        plugin_detection = {
            "fd.vision.detection.PaddleDetectionModel": fd.vision.detection.PaddleDetectionModel,
            "fd.vision.detection.PPYOLOE": fd.vision.detection.PPYOLOE,
            "fd.vision.detection.PPYOLO": fd.vision.detection.PPYOLO,
            "fd.vision.detection.PPYOLOER": fd.vision.detection.PPYOLOER,
            "fd.vision.detection.PaddleYOLOX": fd.vision.detection.PaddleYOLOX,
            "fd.vision.detection.YOLOX": fd.vision.detection.YOLOX,
            "fd.vision.detection.YOLOv8": fd.vision.detection.YOLOv8,
            "fd.vision.detection.YOLOv7": fd.vision.detection.YOLOv7,
            "fd.vision.detection.YOLOv6": fd.vision.detection.YOLOv6,
            "fd.vision.detection.PicoDet": fd.vision.detection.PicoDet,
            "fd.vision.detection.GFL": fd.vision.detection.GFL,
            "fd.vision.detection.FCOS": fd.vision.detection.FCOS,
            "fd.vision.detection.RTMDet": fd.vision.detection.RTMDet,
            "fd.vision.detection.TTFNet": fd.vision.detection.TTFNet,
            "fd.vision.detection.RetinaNet": fd.vision.detection.RetinaNet
        }
        plugin_segmentation = {
            "fd.vision.segmentation.PaddleSegModel": fd.vision.segmentation.PaddleSegModel,
        }
        plugin_ocr = {
            "fd.vision.ocr.DBDetector": fd.vision.ocr.DBDetector,
            "fd.vision.ocr.Classifier": fd.vision.ocr.Classifier,
            "fd.vision.ocr.Recognizer": fd.vision.ocr.Recognizer,
            "fd.vision.ocr.PPOCRv4": fd.vision.ocr.PPOCRv4,
            "fd.vision.ocr.PPOCRv3": fd.vision.ocr.PPOCRv3,
        }
        plugin_text = {
            "fd.text.uie.UIEModel": fd.text.uie.UIEModel
        }
        if sys.version_info > (3, 9):
            return plugin_classification | plugin_detection | plugin_segmentation | plugin_ocr | plugin_text
        elif (3, 5) < sys.version_info < (3, 9):
            return {**plugin_classification, **plugin_detection, **plugin_segmentation, **plugin_ocr, **plugin_text}
        else:
            merged_dict = dict(plugin_classification, **plugin_detection)
            merged_dict = dict(merged_dict, **plugin_segmentation)
            merged_dict = dict(merged_dict, **plugin_ocr)
            merged_dict = dict(merged_dict, **plugin_text)
            return merged_dict

    def build(self, **kwargs):
        plugin_name = kwargs.get("plugin")
        clone_model = kwargs.get("clone_model", False)
        self.plugin = self.plugins.get(plugin_name, None)
        if self.plugin is None:
            raise Exception("Plugin not found: {0}".format(self.plugin))
        if "plugin" in kwargs:
            kwargs.pop("plugin")
        if "clone_model" in kwargs:
            kwargs.pop("clone_model")
        runtime_option = kwargs.get("runtime_option", None)
        if runtime_option is None:
            runtime_option = fd.RuntimeOption()
            runtime_option.use_paddle_backend()
        if self.device_id >= 0:
            runtime_option.use_gpu(device_id=self.device_id)
        else:
            runtime_option.use_cpu()
        model_format = kwargs.get("model_format", ModelFormat.PADDLE)
        if self.model_dir is not None:
            txt_file_mapping = {
                "fd.vision.ocr.Recognizer": "label_path",
                "fd.text.uie.UIEModel": "vocab_file",
            }
            union = {
                "model_file": self.get_file_path_by_suffix(model_dir=self.model_dir, suffix=".pdmodel"),
                "params_file": self.get_file_path_by_suffix(model_dir=self.model_dir, suffix=".pdiparams"),
                "config_file": self.get_file_path_by_suffix(model_dir=self.model_dir, suffix=".yaml"),
                txt_file_mapping.get(plugin_name): self.get_file_path_by_suffix(model_dir=self.model_dir, suffix=".txt"),
                "runtime_option": runtime_option,
                "model_format": model_format
            }
            union = {k: v for k, v in union.items() if v is not None}
            if sys.version_info > (3, 9):
                union = union | kwargs
            elif (3, 5) < sys.version_info < (3, 9):
                union = {**union, **kwargs}
            else:
                union = dict(union, **kwargs)
            try:
                self.model = self.plugin(**union)
            except Exception as e:
                raise Exception("Please check model_dir files: {0} {1}".format(self.model_dir, e))
        else:
            if self.plugin in [fd.vision.ocr.PPOCRv4, fd.vision.ocr.PPOCRv3]:
                det_model = kwargs.get("det_model", None)
                cls_model = kwargs.get("cls_model", None)
                rec_model = kwargs.get("rec_model", None)
                self.model = self.plugin(det_model, cls_model, rec_model)

        if clone_model:
            if hasattr(self.model, "runtime_option"):
                opt = self.model.runtime_option
                if hasattr(opt, "backend"):
                    backend_ = opt.backend
                    if hasattr(backend_, "name"):
                        if backend_.name != "ORT":
                            self.clone_model = True
            elif self.plugin in [fd.vision.ocr.PPOCRv4, fd.vision.ocr.PPOCRv3]:
                self.clone_model = True
        if self.model_dir is not None:
            # init label list
            config_file = self.get_file_path_by_suffix(model_dir=self.model_dir, suffix=".yaml")
            if config_file is not None and isinstance(config_file, str):
                with Path(config_file).open("r", encoding="utf-8") as f:
                    yml_conf = yaml.safe_load(f)
                    if "label_list" in yml_conf:
                        self.label_list = yml_conf["label_list"]
            if len(self.label_list) == 0:
                label_file = self.get_file_path_by_suffix(model_dir=self.model_dir, suffix=".label")
                if label_file is not None and isinstance(label_file, str):
                    with Path(label_file).open("r", encoding="utf-8") as f:
                        for label in f.readlines():
                            label = label.replace("\n", "")
                            item = label.split(" ")
                            if len(item) == 2:
                                self.label_list.append(item[1])
            if len(self.label_list) > 0:
                self.label_id_list = [i for i in range(len(self.label_list))]

    @staticmethod
    def draw_boxes(infer_result, **kwargs):
        if not hasattr(infer_result, "boxes"):
            return
        boxes = infer_result.boxes
        if len(boxes) == 0:
            return
        arr = numpy.asarray(boxes)
        if len(arr.shape) == 2 and arr.shape[1] == 8:
            arr = arr.reshape([arr.shape[0], 4, 2])
            boxes = arr.tolist()
        # config of visualization
        vis_font = kwargs.get("vis_font", None)
        vis_show = kwargs.get("vis_show", False)
        vis_image_size = kwargs.get("vis_image_size", None)
        vis_fill_transparent = kwargs.get("vis_fill_transparent", 60)
        # config of save visualization file
        vis_image_file: Optional[Path] = kwargs.get("vis_image_file", None)
        image_file = kwargs.get("image_path", None)
        if vis_image_file is not None or vis_show:
            texts = kwargs.get("text", None)
            draw_text_color = kwargs.get("vis_font_color", None)
            draw_img = pil_util.draw_polygon(polygon=boxes,
                                             texts=texts,
                                             image_file=image_file,
                                             image_size=vis_image_size,
                                             font=vis_font,
                                             draw_text_color=draw_text_color,
                                             fill_transparent=vis_fill_transparent,
                                             show=vis_show)
            if vis_image_file is not None:
                draw_img.save(vis_image_file)

    def op_classify(self, infer_result, image_arr, **kwargs):
        result = EasyDict()
        label_names = []
        label_ids = infer_result.label_ids
        scores = infer_result.scores
        for i, score in enumerate(scores):
            label_name = self.label_list[label_ids[i]]
            label_names.append(label_name)
        result.feature = infer_result.feature
        result.label_ids = infer_result.label_ids
        result.label_names = label_names
        result.scores = infer_result.scores
        return result

    def op_detection(self, infer_result, image_arr, **kwargs):
        score_threshold = kwargs.get("score_threshold", -1)
        result = EasyDict()
        label_ids = []
        bboxes = []
        scores = []
        items = []
        label_names = []
        draw_texts = []
        nms_match_threshold = kwargs.get("nms_match_threshold", None)
        nms_match_metric = kwargs.get("nms_match_metric", 'ios')
        # nms
        if nms_match_threshold is not None:
            nms_boxes = []
            for i, box in enumerate(infer_result.boxes):
                if infer_result.scores[i] < score_threshold != -1:
                    continue
                nms_boxes.append([infer_result.label_ids[i], infer_result.scores[i], int(box[0]), int(box[1]), int(box[2]), int(box[3])])
            if len(nms_boxes) > 0:
                nms_boxes_res = multiclass_nms(boxes=np.array(nms_boxes), num_classes=len(self.label_list), match_threshold=nms_match_threshold, match_metric=nms_match_metric)
                for k in nms_boxes_res:
                    label_ids.append(int(k[0]))
                    scores.append(float(k[1]))
                    bboxes.append([int(k[2]), int(k[3]), int(k[4]), int(k[5])])
                    class_name = self.label_list[int(k[0])]
                    x_min = int(k[2])
                    y_min = int(k[3])
                    x_max = int(k[4])
                    y_max = int(k[5])
                    items.append([class_name, float(k[1]), [[x_min, y_min], [x_max, y_min], [x_max, y_max], [x_min, y_max]]])
                    label_names.append(class_name)
                    draw_texts.append(f"{class_name}: {k[1]:.4f}")
        else:
            for i, box in enumerate(infer_result.boxes):
                box = infer_result.boxes[i]
                if infer_result.scores[i] < score_threshold != -1:
                    continue
                label_ids.append(infer_result.label_ids[i])
                scores.append(infer_result.scores[i])
                x_min = int(box[0])
                y_min = int(box[1])
                x_max = int(box[2])
                y_max = int(box[3])
                bboxes.append([x_min, y_min, x_max, y_max])
                class_name = self.label_list[infer_result.label_ids[i]]
                items.append([class_name, infer_result.scores[i], [[x_min, y_min], [x_max, y_min], [x_max, y_max], [x_min, y_max]]])
                label_names.append(class_name)
                draw_texts.append(f"{class_name}: {infer_result.scores[i]:.4f}")

        result.items = items
        result.label_ids = label_ids
        result.label_names = label_names
        result.boxes = bboxes
        result.scores = scores
        result.masks = infer_result.masks
        result.contain_masks = infer_result.contain_masks
        infer_result.boxes = bboxes
        kwargs["text"] = draw_texts
        self.draw_boxes(infer_result, **kwargs)
        return result

    @staticmethod
    def op_segmentation(infer_result, image_arr, **kwargs):
        result = EasyDict()
        result.label_map = infer_result.label_map
        result.contain_score_map = infer_result.contain_score_map
        result.score_map = infer_result.score_map
        result.shape = infer_result.shape
        if len(result.label_map) > 0:
            # 是否开启掩码最大连通域计算
            max_connectivity_domain = kwargs.get("max_connectivity_domain", False)
            # 掩码空洞填充阈值，面积占整图比例，0则不填充，小于该阈值时则填充
            mask_hole_area_thresh = kwargs.get("mask_hole_area_thresh", 0)
            arr_mask = numpy.array(result.label_map).reshape(result.shape[0], result.shape[1])
            """
            最大连通域计算
            """
            if max_connectivity_domain:
                max_region = op.max_connectivity_domain(mask_arr=arr_mask)
                result.label_map = max_region.flatten().tolist()
            """
            去掉连通域中的空洞
            """
            if mask_hole_area_thresh > 0:
                image_area = image_arr.shape[0] * image_arr.shape[1]
                arr_mask = numpy.array(result.label_map).reshape(result.shape[0], result.shape[1])
                img_max = numpy.where(arr_mask == 1, 0, 1) * 255
                # 掩码类型转换
                img_max = img_max.astype(dtype=numpy.uint8)
                contours, _ = cv2.findContours(img_max, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                cv_contours = []
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area / image_area <= mask_hole_area_thresh:
                        cv_contours.append(contour)
                    else:
                        continue
                if len(cv_contours):
                    cv2.fillPoly(img_max, cv_contours, (0, 0, 0))
                    img_max = numpy.where(img_max == 0, 1, 0)
                    img_max = img_max.astype(dtype=numpy.int32)
                    result.label_map = img_max.flatten().tolist()
            vis_show = kwargs.get("vis_show", False)
            vis_transparent_weight = kwargs.get("vis_transparent_weight", 0.6)
            vis_image_file: Optional[Path] = kwargs.get("vis_image_file", None)
            if vis_image_file is not None or vis_show:
                im_vis = fd.vision.visualize.vis_segmentation(image_arr, infer_result, vis_transparent_weight)
                pil_image = Image.fromarray(im_vis)
                if vis_image_file is not None:
                    pil_image.save(vis_image_file, quality=100)
                if vis_show:
                    pil_image.show()
        return result

    def op_ocr(self, infer_result, image_arr, **kwargs):
        result = EasyDict()
        result.boxes = infer_result.boxes
        result.cls_labels = infer_result.cls_labels
        result.cls_scores = infer_result.cls_scores
        result.rec_scores = infer_result.rec_scores
        result.text = infer_result.text
        if len(result.text) == 0 and len(result.boxes) > 0:
            self.draw_boxes(infer_result, **kwargs)
        if len(result.text) > 0 and len(result.boxes) > 0:
            arr = numpy.asarray(result.boxes)
            if len(arr.shape) == 2 and arr.shape[1] == 8:
                arr = arr.reshape([arr.shape[0], 4, 2])
                result.boxes = arr.tolist()
            vis_image_file: Optional[Path] = kwargs.get("vis_image_file", None)
            vis_show = kwargs.get("vis_show", False)
            if vis_image_file is not None or vis_show:
                boxes = []
                texts = []
                scores = []
                for i, bbox in enumerate(result.boxes):
                    if len(bbox) == 0:
                        continue
                    bbox_arr = numpy.asarray(bbox)
                    boxes.append(bbox_arr)
                    texts.append(result.text[i])
                    scores.append(result.rec_scores[i])
                image_file: Optional[Path] = kwargs.get("image_path", None)
                assert image_file, "image_path is missing when open visualization"
                image = Image.open(image_file)
                draw_img = ocr_vis_util.draw_ocr_box_txt(
                    image,
                    boxes,
                    texts,
                    scores,
                    drop_score=0.5,
                    font_path=str(Font_SimSun))
                if vis_image_file is not None:
                    write(image=draw_img, img_write_path=vis_image_file)
                if vis_show:
                    draw_img = Image.fromarray(draw_img)
                    draw_img.show()
        return result

    def post_process(self, infer_result, image_arr, **kwargs):
        operations = {
            ClassifyResult: lambda: self.op_classify(infer_result, image_arr, **kwargs),
            DetectionResult: lambda: self.op_detection(infer_result, image_arr, **kwargs),
            SegmentationResult: lambda: self.op_segmentation(infer_result, image_arr, **kwargs),
            OCRResult: lambda: self.op_ocr(infer_result, image_arr, **kwargs),
        }
        return operations.get(type(infer_result), lambda: infer_result)()

    def inference_batch(self, input_data, **kwargs):
        image_arr = [read(item) for item in input_data]
        model = self.model.clone() if self.clone_model and hasattr(self.model, "clone") else self.model
        schema = kwargs.get("schema", None)
        kwargs_infer = copy.deepcopy(kwargs)
        delete_key = [k for k in kwargs_infer.keys() if k in EXTRA_PARAMS]
        if len(delete_key) > 0:
            for k in delete_key:
                kwargs_infer.pop(k)
        if hasattr(model, "set_schema") and schema:
            self.model.set_schema(schema)
        infer_res = model.batch_predict(image_arr, **kwargs_infer)
        final_result = []
        if isinstance(input_data, list):
            for i, img in enumerate(input_data):
                if isinstance(img, Path):
                    kwargs["image_path"] = img
                res = self.post_process(infer_res[i], image_arr[i], **kwargs)
                final_result.append(res)
        return final_result

    def inference(self, input_data, **kwargs):
        """
        :param input_data:
        :param kwargs:
            vis_show：显示可视化文件
            vis_image_file：保存可视化文件
            vis_font：可视化-字体
            vis_font_color: 可视化-字体颜色（black/red/blue/yellow/white...）
            vis_image_size：可视化-图片尺寸
            vis_fill_transparent：可视化-透明
            vis_transparent_weight：可视化-透明度
            schema：UIE抽取的实体名称
            score_threshold: 置信度过滤阈值：目标检测
            max_connectivity_domain: 图像分割-是否开启掩码最大连通域计算
            mask_hole_area_thresh: 图像分割-掩码空洞填充阈值
            nms_match_threshold: 目标检测nms后处理，overlap thresh for match metric.
            nms_match_metric: 目标检测nms后处理，'iou' or 'ios'
        :return:
        """
        image_arr = read(input_data)
        model = self.model.clone() if self.clone_model and hasattr(self.model, "clone") else self.model
        schema = kwargs.get("schema", None)
        kwargs_infer = copy.deepcopy(kwargs)
        delete_key = [k for k in kwargs_infer.keys() if k in EXTRA_PARAMS]
        if len(delete_key) > 0:
            for k in delete_key:
                kwargs_infer.pop(k)
        if hasattr(model, "set_schema") and schema:
            self.model.set_schema(schema)
        infer_res = model.predict(image_arr, **kwargs_infer)
        if isinstance(input_data, Path):
            kwargs["image_path"] = input_data
        res = self.post_process(infer_res, image_arr, **kwargs)
        return res
