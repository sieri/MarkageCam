"""
Group of fonctions to display images in a debug enviroment and testing
"""

import cv2 as cv
import pytesseract as tess
import numpy as np
from matplotlib import pyplot as plt

images = []
titles = []
grayscales = []


def show_resized(window: str, img, max_size=720):
    cv.namedWindow(window, cv.WINDOW_NORMAL)
    cv.imshow(window, img)

    width = img.shape[1]
    height = img.shape[0]

    if width > height:
        if width > max_size:
            cv.resizeWindow(window, width=max_size, height=int(max_size * height / width))
        elif height > max_size:
            cv.resizeWindow(window, width=int(max_size * width / height), height=max_size)
        else:
            cv.resizeWindow(window, width, height)
    cv.waitKey(1)


def addToDisplay(title: str, img, grayscale = False):
    if not grayscale:
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    images.append(img)
    titles.append(title)
    grayscales.append(grayscale)


def show():
    length = len(images)
    if length <= 2:
        x = 2
        y = 1
    elif length <= 4:
        x = 2
        y = 2
    elif length <= 6:
        x = 3
        y = 2
    elif length <= 9:
        x = 3
        y = 3
    elif length <= 12:
        x = 4
        y = 3
    elif length <= 16:
        x = 4
        y = 4

    for i in range(len(images)):

        plt.subplot(x, y, i+1)
        if grayscales[i]:
            plt.imshow(images[i], 'gray', vmin=0, vmax=255)
        else:
            plt.imshow(images[i], vmin=0, vmax=255)
        plt.title(titles[i])
        plt.yticks([])
        plt.xticks([])
    plt.ion()
    plt.show()


def display_data(data, img):
    """
    draw the box around characters after script detection
    :param box:
    :param img:
    :return:
    """

    if img[0, 0].size == 1:
        drawn = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
    else:
        drawn = img.copy()

    for i in range(0, len(data['level'])):
        if float(data['conf'][i]) < 0:
            colour = (255, 0, 0)
        elif float(data['conf'][i]) > 90:
            colour = (0, 255, 0)
        else:
            colour = (0, 0, 255)

        pt1 = (int(data['left'][i]), int(data['top'][i]))
        pt2 = (pt1[0] + int(data['width'][i]), pt1[1] + int(data['height'][i]))

        drawn = cv.rectangle(drawn, pt1=pt1, pt2=pt2, color=colour, thickness=5)

    return drawn


def init():
    plt.figure()
    images.clear()
    titles.clear()
    grayscales.clear()
