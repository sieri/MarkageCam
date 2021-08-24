# Access to the camera and optical correction
import json
import time

import cv2 as cv
from platform import system

import numpy as np

from Capture.CameraBase import CameraBase


class Cam(CameraBase):
    """
    Camera used for capture, does perspective warping
    """
    def __init__(self, config_file):
        """
        Read the camera configuration and create the object
        :param config_file:
        """
        super().__init__()
        try:
            with open(config_file) as fp:
                self._config = json.load(fp)
                self._config['h'] = np.array(self._config['h'])

        except (IOError, FileNotFoundError):
            print("Unable to load camera config file. Run Calibration")
            self._config = None

    def activate_camera(self):

        if self._config is None:
            return False

        access = self._config['cameraAccess']

        # cast if needed, in the case of a webcam
        if access is str:
            if access.isdecimal():
                access = int(access)

        if system() == "Windows":
            # windows specific fix for a warning on opencv camera close
            self._camera = cv.VideoCapture(access, cv.CAP_DSHOW)
        else:
            self._camera = cv.VideoCapture(access)

        self._activate_capture()
        return self._camera.isOpened()


    def get_image(self):
        """get the image with camera correction"""
        time.sleep(self.config['delay'])
        img = self._getter.read()

        corrected_img = cv.warpPerspective(img, self._config['h'], (self._config['width'], self._config['height']), borderMode=cv.BORDER_CONSTANT)

        return img, corrected_img


