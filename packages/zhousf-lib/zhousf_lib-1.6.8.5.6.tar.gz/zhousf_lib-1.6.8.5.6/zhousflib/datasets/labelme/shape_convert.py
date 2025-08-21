# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/10/18 
# @Function:
import json
import numpy
import shutil
from pathlib import Path


def rectangle_convert_polygon(labelme_dir: Path, dst_dir: Path):
    """

    :param labelme_dir:
    :param dst_dir:
    :return:
    """
    if not dst_dir.exists():
        dst_dir.mkdir()
    for label_file in labelme_dir.glob('*.json'):
        print(label_file)
        with label_file.open(mode="r", encoding="utf-8") as f:
            data = json.load(f)
            imagePath = data["imagePath"]
            shapes = data['shapes']
            for i in range(0, len(shapes)):
                points = shapes[i]['points']
                shape_type = shapes[i]['shape_type']
                if shape_type == "rectangle":
                    arr = numpy.asarray(points)
                    x_min = numpy.min(arr[:, 0])
                    x_max = numpy.max(arr[:, 0])
                    y_min = numpy.min(arr[:, 1])
                    y_max = numpy.max(arr[:, 1])
                    polygon = [[x_min, y_min], [x_max, y_min], [x_max, y_max], [x_min, y_max]]
                    shapes[i]['points'] = polygon
                    shapes[i]['shape_type'] = "polygon"
            data['shapes'] = shapes
        save_json = dst_dir.joinpath(label_file.name)
        save_image = label_file.parent.joinpath(imagePath)
        if not save_image.exists():
            continue
        with save_json.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        shutil.copy(save_image, dst_dir)


if __name__ == "__main__":
    pass
