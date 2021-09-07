import json
import os
import time

import environement

environement.debug = True

from Data import DB, Filters

from ImgTreatement import TreatImg, DebugDisplay

import cv2 as cv

scriptDetect = []
preprocesseds = []
corrected_imgs = []
corrected_imgs_img = []


def read_all():
    global corrected_imgs
    global corrected_imgs_img

    with DB.DbConnector("db.sqlite3") as db:
        corrected_imgs = db.read(DB.CorrectedImg)
        for i, img in enumerate(corrected_imgs):
            corrected_imgs_img.append(img.img)


def process_all():
    read_all()
    global preprocesseds

    img: DB.CorrectedImg

    print("Found", len(corrected_imgs), "images")

    for i, img in enumerate(corrected_imgs):
        print("\rPreprocess img", i, "/", len(corrected_imgs), end="")
        preprocesseds.append(TreatImg.preprocess(img.img))

    print("\rpreprocessed                        ")

    for i, img in enumerate(preprocesseds):
        print("\rScript detect img", i, "/", len(corrected_imgs), end="")
        scriptDetect.append(TreatImg.script_detect(corrected_imgs_img[i], img))


def _show(container, start=-1, stop=-1):
    if start == stop:
        cont = [container[start]]
    else:
        cont = container[start:stop]

    try:
        for i, img in enumerate(cont):
            DebugDisplay.show_resized(str(i), img)
    except IndexError:
        print("No such value")


def show_corrected(start=-1, stop=None):
    _show(corrected_imgs, start, stop)


def show_preprocessed(start=-1, stop=None):
    _show(preprocesseds, start, stop)


def kill_all():
    cv.destroyAllWindows()


if __name__ == '__main__':
    os.chdir('../')

    base_process = {
        'steps': [
            {
                'func': 'remove_color',
                'kwargs': {}
            },
            {
                'func': 'mask',
                'kwargs': {'avg': True, 'val':128}
            },
            {
                'func': 'canny',
                'kwargs': {'threshold1': 50, 'threshold2': 100}
            },
            {
                'func': 'dilate',
                'kwargs': {'kernelx': 3, 'kernely': 3, 'iterations': 2}
            },
            {
                'func': 'invert',
                'kwargs': {}
            },
        ]
    }

    TreatImg.init_str(json.dumps(base_process))

    img = cv.imread('test_plater.png')

    imgs = TreatImg.script_detect(img, img)
    print("Found %s lines" % len(imgs))
    for i in imgs:
        TreatImg.read_line(i)

    #show_preprocessed(0, 0)
    cv.waitKey(0)
