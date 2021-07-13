# Access to the camera and optical correction
import json
import cv2 as cv
from platform import system

import numpy as np

from Capture.CameraBase import CameraBase


class Cam(CameraBase):
    def __init__(self, config_file):
        super().__init__()
        try:
            with open(config_file) as fp:
                self.config = json.load(fp)
                self.config['h'] = np.array(self.config['h'])

        except (IOError, FileNotFoundError):
            print("Unable to load camera config file. Run Calibration")
            self.config = None

    def activate_camera(self):
        if self.config is None:
            return False

        access = self.config['cameraAccess']

        # cast if needed, in the case of a webcam
        if access is str:
            if access.isdecimal():
                access = int(access)

        if system() == "Windows":
            # windows specific fix for a warning on opencv camera close
            self._camera = cv.VideoCapture(access, cv.CAP_DSHOW)
        else:
            self._camera = cv.VideoCapture(access)

        return self._camera.isOpened()


    def get_image(self):
        """get the image with camera correction"""
        retval, img = self._camera.read()

        corrected_img = cv.warpPerspective(img,  self.config['h'], (self.config['width'], self.config['height']), borderMode=cv.BORDER_CONSTANT)
        if retval and img is not None:
            return img, corrected_img
        else:
            pass  # todo: decide what to do in case of capture fail


