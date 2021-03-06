"""
Script to debug the drawing of training dataset.
"""

from PIL import Image
import colorsys
import cv2
import random

import numpy as np


def swap_dimension(coord):
    """
    swap x, y, x, y to y, x, y, x
    """
    for dimension in coord:
        dimension[0], dimension[1], dimension[2], dimension[3] = dimension[1], dimension[0], dimension[3], dimension[2]
    return coord


def read_from_annotation(annotation_string):
    splits = annotation_string.split(' ')
    image_path = splits[0]
    boxes = splits[1:]
    coord = []

    for box in boxes:
        # skip empty string
        if len(box) == 0:
            continue

        coord.append([int(x) for x in box.split(",")[:-1]]) # last one is classification

    return image_path, swap_dimension(coord)


def draw_bbox(image_path, coor, num_classes = 2):
    """
    coor must be start_y, start_x, end_y, end_x
    """

    image = cv2.imread(image_path)

    image_h, image_w, _ = image.shape
    hsv_tuples = [(1.0 * x / num_classes, 1., 1.) for x in range(num_classes)]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    colors = list(map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), colors))

    random.seed(0)
    random.shuffle(colors)
    random.seed(None)

    bbox_color = colors[0]
    bbox_thick = int(0.6 * (image_h + image_w) / 600)

    for box in coor:
        #         x       y         x      y
        c1, c2 = (box[1], box[0]), (box[3], box[2])
        cv2.rectangle(image, c1, c2, bbox_color, bbox_thick)

    return image


if __name__ == '__main__':
    annotation_string = './csgo-images/csgo000061.jpg 149,135,170,185,1'

    image_path, coord = read_from_annotation(annotation_string)

    image = draw_bbox(image_path, coord)
    image = Image.fromarray(image.astype(np.uint8))
    image.show()
