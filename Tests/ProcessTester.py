"""
Set of script to test the processes of OCR read and preprocessing,
can either be run directly choosing a mode, or imported in the interactive console
"""

import json
import os

import environement

environement.debug = False

from Data import DB

from ImgTreatement import TreatImg, DebugDisplay

import cv2 as cv
from shutil import copyfile

from Lib.difflib import ndiff

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


note_max = 1000
penalty_char_missing = 5
penalty_char_leftOver = 5


def note_line(to_note: str, ref: str):
    """
    Compute the Damerau-Levenshtein distance between two given
    strings
    code from:
    (https://www.guyrutenberg.com/2008/12/15/damerau-levenshtein-distance-in-python/)
    :param to_note: the string to be noted
    :param ref: the refrence string
    :return: note, bigger is worse aime for 0
    """


    d = {}
    lenstr1 = len(to_note)
    lenstr2 = len(ref)
    for i in range(-1, lenstr1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, lenstr2 + 1):
        d[(-1, j)] = j + 1

    for i in range(lenstr1):
        for j in range(lenstr2):
            if to_note[i] == ref[j]:
                cost = 0
            else:
                cost = 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,  # deletion
                d[(i, j - 1)] + 1,  # insertion
                d[(i - 1, j - 1)] + cost,  # substitution
            )
            if i and j and to_note[i] == ref[j - 1] and to_note[i - 1] == ref[j]:
                d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + cost)  # transposition

    return d[lenstr1 - 1, lenstr2 - 1]


OCR_TEST = 1
OCR_FIND_PROC = 0
FIND_BASE_PROC = 2
FIND_REFINED_PROC = 3

if __name__ == '__main__':
    os.chdir('../')

    mode = OCR_FIND_PROC

    test_line = "This is the test plate ** 42 is the answer #"

    if mode == OCR_TEST:
        img = cv.imread('img.jpg')
        TreatImg.init_read(string_out=False)
        imgs = TreatImg.script_detect(img, img)
        print("Found %s lines" % len(imgs))
        for index, i in enumerate(imgs):
            data, img = TreatImg.read_line(i)
            DebugDisplay.show_resized("img", DebugDisplay.display_data(data, img))
            cv.imwrite('out/output%s.png' % index, img)
            print(data)

        cv.waitKey(0)
    if mode == OCR_FIND_PROC:
        if not os.path.exists('out/read_selected'):
            os.mkdir('out/read_selected')
        img = cv.imread('img.jpg')
        folder = 'out/read_baseprocess/'

        min_val = float('inf')
        min_files = []

        for filename in os.listdir(folder):
            TreatImg.init_read(folder+filename,string_out=True)
            imgs = TreatImg.script_detect(img, img)

            note = 0

            for index, i in enumerate(imgs):
                s = TreatImg.read_line(i)
                print("line:", s)
                note += note_line(s, test_line)
            print("note", note)

            if note < min_val:
                min_files.clear()
                min_files.append(filename)
                min_val = note
            elif note == min_val:
                min_files.append(filename)

        print("Minimal note:", min_val)

        for f in min_files:
            copyfile(folder + f, 'out/read_selected/' + f)



        cv.waitKey(0)
    elif mode == FIND_BASE_PROC:
        if not os.path.exists('out/selected'):
            os.mkdir('out/selected')
        read_all()
        folder = 'out/baseprocess/'
        for filename in os.listdir(folder):
            preprocesseds.clear()
            scriptDetect.clear()
            TreatImg.init_preprocess(folder + filename)
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
        folder = 'out/selected/'
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
                    if not line == test_line:
                        correct = False
            if correct:
                copyfile(folder + filename, 'out/refined/' + filename)
