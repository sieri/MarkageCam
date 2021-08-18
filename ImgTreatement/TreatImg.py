import numpy as np

from Data import DB
from ImgTreatement import DebugDisplay
from environement import debug
import cv2 as cv

plotting = False


def process(img: DB.CorrectedImg):
    """
    Process an image.
    :param img: A db object containing a image to process
    :returns: Boolean if correct, list of index of error, coordinate of errors
    """

    return preprocess(img.img)






def mask(img):
    avg = np.average(img)
    ## get the edge coordinates
    pos = np.where(img > 180)
    ## divide
    img[pos] = avg
    return img

def preprocess(img):
    # convert to grayscale image
    i = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # denoise
    i = cv.fastNlMeansDenoising(i)

    # mask
    i = mask(i)

    #detect edges
    i = cv.Canny(i, 50, 150, L2gradient=True)

    #dilate
    kernel = np.ones((5, 5), np.uint8)
    i = cv.dilate(i, kernel, iterations=3)

    #invert
    i = cv.bitwise_not(i)

    if debug:
        DebugDisplay.show_resized("preprocessed", i)

    return i