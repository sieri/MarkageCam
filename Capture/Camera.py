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
                if self._config['rotate'] != 0:
                    rot_mat = cv.getRotationMatrix2D(
                        center=(self._config['width']/2,self._config['height']/2),
                        angle=self._config['rotate'],
                        scale=1
                    )
                    rot_mat = np.vstack([rot_mat,[0,0,1]])  # transform into correct 3x3 affine transform matrice

                    self._config['h'] = np.matmul(rot_mat,self._config['h'])

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
            self._camera.open(access)
        else:
            self._camera = cv.VideoCapture(access)
            self._camera.open(access)

        # setup the focus
        self._camera.set(cv.CAP_PROP_AUTOFOCUS, 0)
        self._camera.set(cv.CAP_PROP_FOCUS, self._config['focus'])

        self._activate_capture()
        return self._camera.isOpened()


    def get_image(self):
        """get the image with camera correction"""
        time.sleep(self._config['delay'])
        img = self._getter.read()

        corrected_img = cv.warpPerspective(img, self._config['h'], (self._config['width'], self._config['height']), borderMode=cv.BORDER_CONSTANT)

        return img, corrected_img


