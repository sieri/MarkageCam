import json
import os

import environement

environement.debug = False

from Data import DB

from ImgTreatement import TreatImg, DebugDisplay

import cv2 as cv
from shutil import copyfile

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


OCR_test = 1
FIND_BASE_PROC = 2

if __name__ == '__main__':
    os.chdir('../')

    mode = FIND_BASE_PROC

    if mode == OCR_test:
        img = cv.imread('test_plater.png')

        imgs = TreatImg.script_detect(img, img)
        print("Found %s lines" % len(imgs))
        for i in imgs:
            TreatImg.read_line(i)
    elif mode == FIND_BASE_PROC:
        if not os.path.exists('out/selected'):
            os.mkdir('out/selected')
        read_all()
        folder = 'out/baseprocess/'
        for filename in os.listdir(folder):
            preprocesseds.clear()
            scriptDetect.clear()
            TreatImg.init(folder+filename)
            process_all()
            correct = True
            for i in scriptDetect:
                if len(i) != 7:
                    correct = False
                    break
            if correct:
                copyfile(folder+filename,'out/selected/'+filename)


    cv.waitKey(0)
