import imghdr
import os.path
import warnings
import numpy as np
from pathlib import Path


def train_test_split(dataset_root: Path, val_size=0.2, test_size=0, separator=" "):
    """
    数据集划分
    :param dataset_root:
    :param val_size:
    :param test_size:
    :param separator: 分割符
    :return:
    """
    split = [1 - val_size - test_size, val_size, test_size]
    image_dir = dataset_root.joinpath("images")
    label_dir = dataset_root.joinpath("labels")
    image_files = []
    for f in image_dir.glob("*.*"):
        if not imghdr.what(f):
            continue
        image_files.append(str(f))
    label_files = []
    for f in label_dir.glob("*.png"):
        label_files.append(str(f))

    if not image_files:
        warnings.warn("No files in {}".format(image_dir))
    if not label_files:
        warnings.warn("No files in {}".format(label_dir))

    num_images = len(image_files)
    num_label = len(label_files)
    if num_images != num_label:
        raise Exception(
            "Number of images = {}, number of labels = {}."
            "The number of images is not equal to number of labels, "
            "Please check your dataset!".format(num_images, num_label))

    image_files = np.array(image_files)
    label_files = np.array(label_files)
    state = np.random.get_state()
    np.random.shuffle(image_files)
    np.random.set_state(state)
    np.random.shuffle(label_files)
    start = 0
    num_split = len(split)
    dataset_name = ['train', 'val', 'test']
    for i in range(num_split):
        if split[i] == 0:
            continue
        dataset_split = dataset_name[i]
        print("Creating {}.txt...".format(dataset_split))
        if split[i] > 1.0 or split[i] < 0:
            raise ValueError("{} dataset percentage should be 0~1.".format(
                dataset_split))

        file_list = os.path.join(str(dataset_root), dataset_split + '_list.txt')
        with open(file_list, "w") as f:
            num = round(split[i] * num_images)
            end = start + num
            if i == num_split - 1:
                end = num_images
            for item in range(start, end):
                left = image_files[item].replace(str(dataset_root), '')
                left = left.replace("\\", '/')[1:]
                if left[0] == os.path.sep:
                    left = left.lstrip(os.path.sep)

                try:
                    right = label_files[item].replace(str(dataset_root), '')
                    right = right.replace("\\", '/')[1:]
                    if right[0] == os.path.sep:
                        right = right.lstrip(os.path.sep)
                    line = left + separator + right + '\n'
                except:
                    line = left + '\n'

                f.write(line)
                print(line)
            start = end


if __name__ == '__main__':
    pass
