# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function: labelme标注数据裁剪工具
import json
import numpy as np
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from zhousflib.file import get_base64
from zhousflib.font import Font_SimSun
FONT = ImageFont.truetype(font=str(Font_SimSun), size=15)


def clip_img(labelme_dir: Path, dst_dir: Path, clip_labels: list, show=False):
    """
    裁剪
    :param labelme_dir:
    :param dst_dir:
    :param clip_labels: 裁剪标签
    :param show:
    :return:
    """
    if not dst_dir.exists():
        dst_dir.mkdir()
    for json_file in labelme_dir.glob("*.json"):
        print(json_file)
        with json_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        imagePath = data["imagePath"]
        image_file = labelme_dir.joinpath(imagePath)
        image = Image.open(image_file)
        if image.mode != "RGB":
            image = image.convert('RGB')
        image_w, image_h = image.size
        draw = ImageDraw.ImageDraw(image)
        for i in range(0, len(data["shapes"])):
            shape = data["shapes"][i]
            label = shape.get("label", None)
            points = shape.get("points", None)
            if not label or not points:
                continue
            if label not in clip_labels:
                continue
            p_arr = np.asarray(points)
            scale_up_pixel = 5
            x_min = np.min(p_arr[:, 0]) - scale_up_pixel
            x_max = np.max(p_arr[:, 0]) + scale_up_pixel
            y_min = np.min(p_arr[:, 1]) - scale_up_pixel
            y_max = np.max(p_arr[:, 1]) + scale_up_pixel
            y_min = y_min if y_min > 0 else 1
            x_min = x_min if x_min > 0 else 1
            x_max = x_max if x_max < image_w else image_w - 1
            y_max = y_max if y_max < image_h else image_h - 1
            # 裁剪的坐标原点换算
            origin_point = (x_min, y_min)
            p_arr_1 = p_arr[:, 0] - x_min
            p_arr_2 = p_arr[:, 1] - y_min
            p_arr_clip = np.stack([p_arr_1, p_arr_2], 1).tolist()
            # 裁剪
            cropped = image.crop((x_min, y_min, x_max, y_max))
            save_img_file = dst_dir.joinpath("{0}_{1}{2}".format(image_file.stem, i, image_file.suffix))
            cropped.save(save_img_file, quality=100)
            image_w_clip, image_h_clip = cropped.size
            # 写json文件
            save_file = dst_dir.joinpath("{0}_{1}.json".format(image_file.stem, i))
            data_clip = {"imagePath": str(save_img_file.name),
                         "imageData": get_base64(save_img_file),
                         "imageHeight": image_h_clip,
                         "imageWidth": image_w_clip}
            shape_clip = shape.copy()
            shape_clip["points"] = p_arr_clip
            data_clip["shapes"] = [shape_clip]
            if "version" in data:
                data_clip["version"] = data["version"]
            if "flags" in data:
                data_clip["flags"] = data["flags"]
            with save_file.open("w", encoding="utf-8") as f:
                json.dump(data_clip, f, ensure_ascii=False, indent=4)
            if show:
                width = abs(x_max - x_min)
                height = abs(y_max - y_min)
                draw.rectangle(xy=(x_min, y_min, x_min + width, y_min + height), fill=None, outline="red", width=1)
                fw, fh = FONT.getsize(label)
                if y_min < fh:
                    y_min = y_min + fh
                if (x_min + fw) > image_w:
                    x_min = x_max - fw
                draw.text(xy=(x_min, y_min - fh), text=label, fill="red", font=FONT)
        if show:
            image.show()
            break


if __name__ == "__main__":
    pass




