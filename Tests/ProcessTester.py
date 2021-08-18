import os
import time

import environement

environement.debug = False

from Data import DB, Filters

from ImgTreatement import TreatImg, DebugDisplay

import cv2 as cv

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


def _show(container, start=-1, stop=-1):
    print(container[start:stop])
    try:
        for i, img in enumerate(container[start:stop]):
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
    process_all()
