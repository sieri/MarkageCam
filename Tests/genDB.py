import os
import cv2 as cv
from Data import DB
from datetime import datetime

def genDBTest():
    folder = "in/"

    text = DB.ExpectedText("This is the test plate ** ",7,1)
    with DB.DbConnector() as d:
        d.insert(text)

        for filename in os.listdir(folder):
            imgData = cv.imread(folder+filename)
            img = DB.BaseImg(imgData, datetime.now(), text)
            corrimg = DB.CorrectedImg(imgData, img)
            d.insert(img)
            d.insert(corrimg)


if __name__ == '__main__':
    os.chdir('..')

    genDBTest()
