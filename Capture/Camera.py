# Access to the camera and optical correction
import json
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

        self._activate_capture()
        return self._camera.isOpened()


    def get_image(self):
        """get the image with camera correction"""
        img = self._getter.read()

        corrected_img = cv.warpPerspective(img,  self.config['h'], (self.config['width'], self.config['height']), borderMode=cv.BORDER_CONSTANT)

        return img, corrected_img


