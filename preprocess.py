import cv2
import numpy as np
import logging


def get_resize_img(org, ratio):
    resize_height = org.shape[0] * ratio
    resize_width = org.shape[1] * ratio
    resized_img = cv2.resize(org, (int(resize_width), int(resize_height)))
    return resized_img


def grey_to_gradient(img):
    if len(img.shape) == 3:
        img = get_grey(img)
    img_f = np.copy(img)
    img_f = img_f.astype("float")

    kernel_h = np.array([[0, 0, 0], [0, -1., 1.], [0, 0, 0]])
    kernel_v = np.array([[0, 0, 0], [0, -1., 0], [0, 1., 0]])
    dst1 = abs(cv2.filter2D(img_f, -1, kernel_h))
    dst2 = abs(cv2.filter2D(img_f, -1, kernel_v))
    gradient = (dst1 + dst2).astype('uint8')
    return gradient


def get_binary_image(gray_img, grad_min, show=False, write_path=None, wait_key=0):
    print('Generating binary image...')
    gradient_img = grey_to_gradient(gray_img)
    rec, binary_img = cv2.threshold(gradient_img, grad_min, 255, cv2.THRESH_BINARY)
    morph_img = cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, (3, 3))

    if write_path is not None:
        cv2.imwrite(write_path, morph_img)
    if show:
        cv2.imshow('binary', morph_img)
        if wait_key is not None:
            cv2.waitKey(wait_key)

    return morph_img


def get_vertically_cropped_image(original, top, bottom):
    img_copy = original
    if top > 0 or bottom > 0:
        img_copy = img_copy[85:(img_copy.shape[0] - top), 0:(img_copy.shape[1] - bottom)]
    return img_copy


def get_median_blur_img(original, kernel_size):
    return cv2.medianBlur(original, kernel_size)


def get_grey(original):
    return cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
