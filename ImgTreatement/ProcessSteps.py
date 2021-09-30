"""
Set of fonctions to process the image, that can be generated into a list from json files
"""

import json

import numpy as np
import sys
import cv2 as cv


def remove_color(img, **kwargs):
    """
    processs step
    remove the color
    :param img: image to process
    :param kwargs: None
    :return: processed image
    """
    return cv.cvtColor(img, cv.COLOR_BGR2GRAY, dstCn=0)


def mask(img, **kwargs):
    """
    processs step
    mask to average grayness everything brighter than a threshold

    :param img: image to process
    :param kwargs:
        :keyword avg: bool true use average grayness of the image for mask
        :keyword val: value of threshold, int
    :return: processed image
    """
    avg = np.average(img)
    # get the edge coordinates
    if kwargs['avg']:
        pos = np.where(img > kwargs['avg'])
    else:
        pos = np.where(img > kwargs['val'])
    # divide
    img[pos] = avg
    return img


def denoise(img, **kwargs):
    """
    processs step
    remove noise, warning long step
    :param img: image to process
    :param kwargs: None
    :return: processed image
    """
    return cv.fastNlMeansDenoising(img)


def canny(img, **kwargs):
    """
    processs step

    detect the edges of the image

    :param img: image to process
    :param kwargs:
        :keyword threshold1 fist threshold for the edge detection
        :keyword threshold2 second threshold for the same
    :return: processed image
    """
    return cv.Canny(img, kwargs['threshold1'], kwargs['threshold2'], L2gradient=True)

def threshold(img, **kwargs):
    """
    processs step
    binarize the image according with an adaptive treshold
    :param img: image to process, !must be grayscale
    :param kwargs:
        :keyword size: the value of the size of the area thresholded
        :keyword C: constant for fine tuning
    :return: processed image
    """

    img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, kwargs['size'], kwargs['C'])
    return img



def dilate(img, **kwargs):
    """
    processs step
    dilate the image
    :param img: image to process
    :param kwargs:
        :keyword kernelx: x value of a kernel
        :keyword kernely: y value of a kernel
        :keyword iterations: number of iteration
    :return: processed image
    """
    return cv.dilate(img, np.ones((kwargs['kernelx'], kwargs['kernely']), np.uint8), iterations=kwargs['iterations'])


def errode(img, **kwargs):
    """
    processs step
    errde the image
    :param img: image to process
    :param kwargs:
        :keyword kernelx: x value of a kernel
        :keyword kernely: y value of a kernel
        :keyword iterations: number of iteration
    :return: processed image
    """
    return cv.erode(img, np.ones((kwargs['kernelx'], kwargs['kernely']), np.uint8), iterations=kwargs['iterations'])


def invert(img, **kwargs):
    """
    processs step
    invert blacks and white
    :param img: image to process
    :param kwargs: None
    :return: processed image
    """
    return cv.bitwise_not(img)


def add_border(img, **kwargs):
    """
    processs step
    adds borders to an image, BW only
    :param img: image to process
    :param kwargs: None
    :return: processed image
    """
    return cv.copyMakeBorder(
        src=img,
        top=kwargs["border_size"],
        bottom=kwargs["border_size"],
        left=kwargs["border_size"],
        right=kwargs["border_size"],
        borderType=cv.BORDER_CONSTANT,
        value=255,
    )


def gen_step(json_data: str):
    data = json.loads(json_data)
    ret_list = []
    for i in data['steps']:
        ret_list.append([
            getattr(sys.modules[__name__], i['func']),  # find the right function in this module by name
            i['kwargs']  # add the key word argument
        ])
    return ret_list
