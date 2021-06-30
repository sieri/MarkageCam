# Access to the camera and optical correction
import json
import cv2 as cv
from platform import system
from Capture.CameraBase import CameraBase


class Cam(CameraBase):
    def __init__(self, config_file):
        super().__init__()
        try:
            with open(config_file) as fp:
                self.config = json.load(fp)

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
            self.camera = cv.VideoCapture(access, cv.CAP_DSHOW)
        else:
            self.camera = cv.VideoCapture(access)

        return self.camera.isOpened()


    def get_image(self):
        """get the image with camera correction"""
        retval, img = self.camera.read()

        if retval and img is not None:
            return img
        else:
            pass  # todo: decide what to do in case of capture fail


