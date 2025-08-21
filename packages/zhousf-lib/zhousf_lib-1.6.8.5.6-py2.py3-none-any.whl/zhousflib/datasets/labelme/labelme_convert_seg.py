from __future__ import print_function
import json
import os
import io
import os.path as osp
import numpy as np
import glob
import traceback
from pathlib import Path

import PIL.Image
import PIL.ImageDraw
from PIL import Image
import matplotlib.pyplot as plt


def label_colormap(N=256):
    def bitget(byteval, idx):
        return ((byteval & (1 << idx)) != 0)

    cmap = np.zeros((N, 3))
    for i in range(0, N):
        id = i
        r, g, b = 0, 0, 0
        for j in range(0, 8):
            r = np.bitwise_or(r, (bitget(id, 0) << 7 - j))
            g = np.bitwise_or(g, (bitget(id, 1) << 7 - j))
            b = np.bitwise_or(b, (bitget(id, 2) << 7 - j))
            id = (id >> 3)
        cmap[i, 0] = r
        cmap[i, 1] = g
        cmap[i, 2] = b
    cmap = cmap.astype(np.float32) / 255
    return cmap


def polygons_to_mask(img_shape, polygons):
    mask = np.zeros(img_shape[:2], dtype=np.uint8)
    mask = PIL.Image.fromarray(mask)
    xy = list(map(tuple, polygons))
    PIL.ImageDraw.Draw(mask).polygon(xy=xy, outline=1, fill=1)
    mask = np.array(mask, dtype=bool)
    return mask


# similar function as skimage.color.label2rgb
def label2rgb(lbl, img=None, n_labels=None, alpha=0.5, thresh_suppress=0):
    if n_labels is None:
        n_labels = len(np.unique(lbl))

    cmap = label_colormap(n_labels)
    cmap = (cmap * 255).astype(np.uint8)

    lbl_viz = cmap[lbl]
    lbl_viz[lbl == -1] = (0, 0, 0)  # unlabeled

    if img is not None:
        img_gray = PIL.Image.fromarray(img).convert('LA')
        img_gray = np.asarray(img_gray.convert('RGB'))
        # img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # img_gray = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)
        lbl_viz = alpha * lbl_viz + (1 - alpha) * img_gray
        lbl_viz = lbl_viz.astype(np.uint8)

    return lbl_viz


def draw_label(label, img=None, label_names=None, colormap=None):
    backend_org = plt.rcParams['backend']
    plt.switch_backend('agg')
    plt.rcParams['font.family'] = ['SimHei']
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0,
                        wspace=0, hspace=0)
    plt.margins(0, 0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())

    if label_names is None:
        label_names = [str(l) for l in range(label.max() + 1)]

    if colormap is None:
        colormap = label_colormap(len(label_names))

    label_viz = label2rgb(label, img, n_labels=len(label_names))
    plt.imshow(label_viz)
    plt.axis('off')

    plt_handlers = []
    plt_titles = []
    for label_value, label_name in enumerate(label_names):
        if label_value not in label:
            continue
        if label_name.startswith('_'):
            continue
        fc = colormap[label_value]
        p = plt.Rectangle((0, 0), 1, 1, fc=fc)
        plt_handlers.append(p)
        plt_titles.append('{value}: {name}'
                          .format(value=label_value, name=label_name))
    plt.legend(plt_handlers, plt_titles, loc='lower right', framealpha=.5)

    f = io.BytesIO()
    plt.savefig(f, bbox_inches='tight', pad_inches=0)
    plt.cla()
    plt.close()

    plt.switch_backend(backend_org)

    out_size = (label_viz.shape[1], label_viz.shape[0])
    out = PIL.Image.open(f).resize(out_size, PIL.Image.BILINEAR).convert('RGB')
    out = np.asarray(out)
    return out


def shapes_to_label_sorted(img_shape, shapes, label_name_to_value, type='class'):
    assert type in ['class', 'instance']
    instance_names = []
    ins = None
    cls_name = None
    ins_id = 0
    mask = None
    cls = np.zeros(img_shape[:2], dtype=np.int32)
    if type == 'instance':
        ins = np.zeros(img_shape[:2], dtype=np.int32)
        instance_names = ['_background_']
    tmp = []
    for i in range(0, len(shapes)):
        shape = shapes[i]
        polygons = shape['points']
        label = shape['label']
        if type == 'class':
            cls_name = label
        elif type == 'instance':
            cls_name = label.split('-')[0]
            if label not in instance_names:
                instance_names.append(label)
            ins_id = len(instance_names) - 1
        if cls_name not in label_name_to_value:
            continue
        cls_id = label_name_to_value[cls_name]
        mask = polygons_to_mask(img_shape[:2], polygons)
        num = np.sum(mask.reshape(-1) == True)
        tmp.append((num, mask, cls_id))
        if type == 'instance':
            ins[mask] = ins_id
    # 降序排序
    sort_tmp = sorted(tmp, key=lambda v: v[0], reverse=True)
    for i in range(0, len(sort_tmp)):
        info = sort_tmp[i]
        cls[info[1]] = info[2]
        if type == 'instance':
            ins[mask] = ins_id
    if type == 'instance':
        return cls, ins
    return cls


def labelme_convert_seg(labelme_dir: Path, dist_dir: Path, fetch_labels: list = None):
    """
    labelme转segmentation
    :param labelme_dir:
    :param dist_dir:
    :param fetch_labels: ["汽车", "_background_"]
    :return:
    """
    if not dist_dir.exists():
        dist_dir.mkdir()
    save_img_dir = dist_dir.joinpath("images")
    save_img_vis_dir = dist_dir.joinpath("images_vis")
    save_labels_dir = dist_dir.joinpath("labels")
    if not save_img_dir.exists():
        save_img_dir.mkdir()
    if not save_labels_dir.exists():
        save_labels_dir.mkdir()
    if not save_img_vis_dir.exists():
        save_img_vis_dir.mkdir()

    # get the all class names for the given dataset
    class_names = ['_background_']
    for label_file in glob.glob(osp.join(labelme_dir, '*.json')):
        with open(label_file, encoding="utf-8") as f:
            data = json.load(f)
            for shape in data['shapes']:
                label = shape['label']
                cls_name = label
                if cls_name not in class_names:
                    class_names.append(cls_name)
    class_name_to_id = {}
    class_names_list = []
    class_index = 0
    for i, class_name in enumerate(class_names):
        if fetch_labels:
            if class_name not in fetch_labels:
                continue
        class_id = class_index  # starts with 0
        class_name_to_id[class_name] = class_id
        if class_id == 0:
            assert class_name == '_background_'
        class_index += 1
        class_names_list.append(class_name)
    class_names = tuple(class_names_list)
    print('class_names:', class_names)

    out_class_names_file = osp.join(str(dist_dir), 'labels.txt')
    with open(out_class_names_file, 'w') as f:
        f.writelines('\n'.join(class_names))
    print('Saved class_names:', out_class_names_file)

    colormap = label_colormap(255)
    for root, dirs, files in os.walk(labelme_dir):
        for label_file in files:
            if not label_file.endswith('.json'):
                continue
            print('Generating dataset from:', label_file)
            label_file = os.path.join(root, label_file)
            base = osp.splitext(osp.basename(label_file))[0]
            out_img_file = save_img_dir.joinpath(base + '.jpg')
            out_lbl_file = save_labels_dir.joinpath(base + '.png')
            out_viz_file = save_img_vis_dir.joinpath(base + '.png')
            if out_lbl_file.exists():
                continue
            try:
                with open(label_file, encoding="utf-8") as f:
                    data = json.load(f)
                    img_file = osp.join(osp.dirname(label_file), data['imagePath'])
                    img = PIL.Image.open(img_file)
                    if img.mode != "RGB":
                        img = img.convert('RGB')
                    img = np.asarray(img)
                    PIL.Image.fromarray(img).save(str(out_img_file))
                    # 对标注的label面积由大到小排序，防止因标注顺序问题导致大的遮盖了小的
                    lbl = shapes_to_label_sorted(
                        img_shape=img.shape,
                        shapes=data['shapes'],
                        label_name_to_value=class_name_to_id,
                    )
                    lbl_pil = PIL.Image.fromarray(lbl)
                    # Only works with uint8 label
                    # lbl_pil = PIL.Image.fromarray(lbl, mode='P')
                    # lbl_pil.putpalette((colormap * 255).flatten())
                    lbl_pil.save(str(out_lbl_file))
                    # 生成验证图片-训练不需要，可以屏蔽
                    # label_names = ['%d: %s' % (class_name_to_id.get(cls_name), cls_name) for cls_name in class_name_to_id]
                    label_names = ['%s' % cls_name for cls_name in class_name_to_id]
                    viz = draw_label(lbl, img, label_names, colormap=colormap)
                    PIL.Image.fromarray(viz).save(out_viz_file)
            except Exception as ex:
                print(traceback.print_exc())
                print('程序中断:类别 %s 不在类别列表中' % str(ex))


def check_gray_image(gray_label_file: Path):
    """
    检测是否是灰度标注图片，在图像中存在3个类别时，输出应该是[0, 1, 2]，若上述条件不满足，则说明标注图存在问题，不能直接用于模型训练
    :param gray_label_file:
    :return:
    """
    print(np.unique(np.asarray(Image.open(str(gray_label_file)))))


if __name__ == '__main__':
    pass
