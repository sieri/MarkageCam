import numpy as np

from Data import DB
from ImgTreatement import DebugDisplay
from environement import debug
import cv2 as cv
import pytesseract as tess
from ImgTreatement.ProcessSteps import gen_step
from ImgTreatement import ProcessSteps
plotting = False

tess.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

preprocess_steps = []


def init(preprocess_file: str):
    """
    initialize the procedure from file names containing the json data
    :param preprocess_file:
    :return:
    """
    global preprocess_steps
    with open(preprocess_file, 'r') as f:
        preprocess_steps = gen_step(f.read())


def init_str(preprocess_data: str):
    """
    initiaise the procedures from string data
    :param preprocess_data:
    :return: None
    """
    global preprocess_steps
    preprocess_steps = gen_step(preprocess_data)


def process(img: DB.CorrectedImg):
    """
    Process an image.
    :param img: A db object containing a image to process
    :returns: Boolean if correct, list of index of error, coordinate of errors
    """

    preprocess(img.img)


def preprocess(img):
    """
    run the preprocessing steps in sequence
    :param img: base image
    :return: the processed image
    """
    for step in preprocess_steps:
        img = step[0](img, **step[1])

    return img


def script_detect(img, preprocessed):
    """
    Detect and split image with area of texts isolated

    :returns list of image segment, shape of the grid
    """
    e_list = list()
    e_list.append(cv.getTickCount())

    data = tess.image_to_data(
        preprocessed,
        lang='Dot_matrix',
        output_type=tess.Output.DICT,
        config='--psm 6'
    )

    if debug:
        print('\nScript Detect')
        print(data)

    e_list.append(cv.getTickCount())

    if debug:
        print("\n==TIMING OCR SCRIPT DETECT")
        for index in range(len(e_list) - 1):
            time = (e_list[index + 1] - e_list[index]) / cv.getTickFrequency()
            print("step,", index, "in", time, 's')
        print("total:", (e_list[-1] - e_list[0]) / cv.getTickFrequency(), "s")

    imgs = []

    DebugDisplay.show_resized("line_detect", DebugDisplay.display_data(data, preprocessed))
    print("script Detect", data)

    for i, value in enumerate(data['level']):
        if value == 4:
            name = "out/%s_%s.png" % (i, value)
            width = data['width'][i]
            height = data['height'][i]
            left = data['left'][i]
            top = data['top'][i]

            new = img[top:top + height, left:left + width]
            imgs.append(new)

    return imgs


def read_line(img):
    bordersize = 10

    img = cv.copyMakeBorder(
        src=img,
        top=bordersize,
        bottom=bordersize,
        left=bordersize,
        right=bordersize,
        borderType=cv.BORDER_CONSTANT,
        value=(255, 255, 255)

    )

    DebugDisplay.show_resized("test", img)

    img = cv.erode(img, np.ones((2,2), np.uint8),iterations=2)
    img = cv.dilate(img, np.ones((2,2), np.uint8),iterations=2)

    DebugDisplay.show_resized("test2", img)


    data = tess.image_to_data(
        img,
        lang='Dot_matrix',
        output_type=tess.Output.DICT,
        config='--psm 7'  # treat image line
    )

    return data, img
