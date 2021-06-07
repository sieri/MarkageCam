import cv2 as cv
from Capture.CameraDisplay import Display

class CamCalib:

    def __init__(self):
        self.access = ""
        self.camera = None
        self.display = None

    def set_access(self, access : str):

        if access.isdecimal():
            self.access = int(access)
        else:
            self.access = access

    def activate_camera(self):
        self.camera = cv.VideoCapture(self.access)

        return self.camera.isOpened()

    def show_camera(self):
        self.display = Display("Calibration Window", self.camera)
        self.display.start()

    def hide_camera(self):
        self.display.stop()



