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


OCR_TEST = 1
FIND_BASE_PROC = 2
FIND_REFINED_PROC = 3

if __name__ == '__main__':
    os.chdir('../')

    mode = OCR_TEST

    if mode == OCR_TEST:
        img = cv.imread('test_plate_background.png')
        TreatImg.init_read()
        imgs = TreatImg.script_detect(img, img)
        print("Found %s lines" % len(imgs))
        for i in imgs:

            data,img = TreatImg.read_line(i)
            DebugDisplay.show_resized("img", DebugDisplay.display_data(data, img))
            print(data)

        cv.waitKey(0)

    elif mode == FIND_BASE_PROC:
        if not os.path.exists('out/selected'):
            os.mkdir('out/selected')
        read_all()
        folder = 'out/baseprocess/'
        for filename in os.listdir(folder):
            preprocesseds.clear()
            scriptDetect.clear()
            TreatImg.init_preprocess(folder + filename, string_out=True)
            process_all()
            correct = True
            for i in scriptDetect:
                if len(i) != 7:
                    correct = False
                    break
            if correct:
                copyfile(folder + filename, 'out/selected/' + filename)

    elif mode == FIND_REFINED_PROC:
        if not os.path.exists('out/refined'):
            os.mkdir('out/refined')
        read_all()
        folder = 'out/sel/'
        for filename in os.listdir(folder):
            print("testing ", filename)
            preprocesseds.clear()
            scriptDetect.clear()
            TreatImg.init_preprocess(folder + filename)
            TreatImg.init_read(string_out=True)
            process_all()
            correct = True
            for i in scriptDetect:
                for img in i:
                    cv.imshow("test", img)
                    cv.waitKey(1)
                    line = TreatImg.read_line(img)
                    print("line", line)
                    if not line == "This is the test plate ** 42 is the answer #":
                        correct = False
            if correct:
                copyfile(folder + filename, 'out/refined/' + filename)


