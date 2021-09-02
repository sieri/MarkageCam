import json

import numpy as np
import sys


def remove_color(img, **kwargs):
    return cv.cvtColor(img, cv.COLOR_BGR2GRAY, dstCn=0)


def mask(img, **kwargs):
    avg = np.average(img)
    # get the edge coordinates
    if kwargs.avg:
        pos = np.where(img > avg)
    else:
        pos = np.where(img > kwargs.val)
    # divide
    img[pos] = avg
    return img


def denoise(img, **kwargs):
    return cv.fastNlMeansDenoising(img)


def canny(img, **kwargs):
    return cv.Canny(img, kwargs.threshold1, kwargs.threshold2, L2gradient=True)


def dilate(img, **kwargs):
    return cv.dilate(img, np.ones((kwargs.kernelx, kwargs.kernely), np.uint8), iterations=kwargs.iterations)


def invert(img, **kwargs):
    return cv.bitwise_not(img)


def gen_step(json_data: str):
    data = json.loads(json_data)
    ret_list = []
    for i in data['steps']:
        ret_list.append([
            getattr(sys.modules[__name__], i['func']),  # find the right function in this module by name
            i['kwargs']  # add the key word argument
        ])
    return ret_list
