import numpy as np

from Data import DB
from ImgTreatement import DebugDisplay
from environement import debug
import cv2 as cv
import pytesseract as tess

plotting = False

tess.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"


def process(img: DB.CorrectedImg):
    """
    Process an image.
    :param img: A db object containing a image to process
    :returns: Boolean if correct, list of index of error, coordinate of errors
    """

    preprocess(img.img)




def mask(img):
    avg = np.average(img)
    ## get the edge coordinates
    pos = np.where(img > 180)
    ## divide
    img[pos] = avg
    return img

def preprocess(img):

    e_list = list()
    e_list.append(cv.getTickCount())


    # convert to grayscale image
    i = cv.cvtColor(img, cv.COLOR_BGR2GRAY, dstCn=0)
    e_list.append(cv.getTickCount())

    # denoise
    i = cv.fastNlMeansDenoising(i) #mesured as bottleneck 27s for execution
    e_list.append(cv.getTickCount())

    # mask
    i = mask(i)
    e_list.append(cv.getTickCount())

    #detect edges
    i = cv.Canny(i, 50, 150, L2gradient=True)
    e_list.append(cv.getTickCount())

    #dilate
    kernel = np.ones((5, 5), np.uint8)
    i = cv.dilate(i, kernel, iterations=3)
    e_list.append(cv.getTickCount())

    #invert
    i = cv.bitwise_not(i)
    e_list.append(cv.getTickCount())

    if debug:
        print("\n==TIMING PREPROCESSING")
        for index in range(len(e_list)-1):
            time = (e_list[index+1] - e_list[index]) / cv.getTickFrequency()
            print("step,", index, "in", time, 's')
        print("total:" , (e_list[-1] - e_list[0]) / cv.getTickFrequency(), "s")

    return i


def script_detect(img, preprocessed):
    """
        Detect and split image with area of texts isolated
        :returns list of image segment, shape of the grid
    """
    e_list = list()
    e_list.append(cv.getTickCount())

    data = tess.image_to_data(
        img,
        config='-c load_freq_dawg=false psm=1 hocr_char_boxes=1',
        output_type=tess.Output.DICT
    )

    if debug:
        print('\nScript Detect')
        print(data)

    e_list.append(cv.getTickCount())

    if debug:
        print("\n==TIMING OCR SCRIPT DETECT")
        for index in range(len(e_list)-1):
            time = (e_list[index+1] - e_list[index]) / cv.getTickFrequency()
            print("step,", index, "in", time, 's')
        print("total:" , (e_list[-1] - e_list[0]) / cv.getTickFrequency(), "s")

    return data
