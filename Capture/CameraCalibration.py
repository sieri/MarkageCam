import tkinter

import cv2 as cv
from Capture.CameraDisplay import DebugDisplay, TkDisplay


class CamCalib:
    """
    A basic camera access used as a viewfinder for the calibration
    """

    def __init__(self):
        self.access = ""
        self.camera = None
        self.display = None

    def set_access(self, access: str):
        """
        set which camera to access
        :param access: the address of the camera or index if not an IP camera (str only)
        :return: None
        """
        if access.isdecimal():
            self.access = int(access)
        else:
            self.access = access

    def activate_camera(self):
        """
        Activate the camera
        :return: success of activation
        """
        self.camera = cv.VideoCapture(self.access)

        return self.camera.isOpened()

    def show_camera(self, scale):
        """
        Activate displaying the camera, run the captures
        :param scale: tupple of scale to resize image to
        :return: None
        """
        self.display = TkDisplay(self.camera, scale)
        self.display.start()

    def hide_camera(self):
        """
        disable the updates of the camera image, no capture run
        camera still opened
        :return: None
        """
        if self.display is not None:
            self.display.stop()

    def close_camera(self):
        """close the camera"""
        if self.camera is not None:
            self.hide_camera()
            self.camera.release()

    def get_frame(self) -> tkinter.PhotoImage:
        """
        get the las frame
        :return: the last frame captured
        """
        return self.display.lastFrame

