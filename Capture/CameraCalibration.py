import json
import tkinter

import cv2 as cv
from Capture.CameraDisplay import DebugDisplay, TkDisplay
from platform import system


class CamCalib:
    """
    A basic camera access used as a viewfinder for the calibration
    """

    def __init__(self):
        self.access = ""
        self.camera = None
        self.display = None
        self.focus = 0
        self.focus_increment = 10

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
        if self.camera is not None and self.camera.isOpened():
            self.close_camera()

        if system() == "Windows":
            # windows specific fix for a warning on opencv camera close
            self.camera = cv.VideoCapture(self.access, cv.CAP_DSHOW)
        else:
            self.camera = cv.VideoCapture(self.access)

        # setup the focus
        self.camera.set(cv.CAP_PROP_AUTOFOCUS, 0)
        self.update_focus()

        return self.camera.isOpened()

    def show_camera(self, scale = None):
        """
        Activate displaying the camera, run the captures
        :param scale: tupple of scale to resize image to
        :return: None
        """
        if scale is None:
            self.display = DebugDisplay("Calibration Camera", self.camera)
        else:
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
        self.hide_camera()

        if self.camera is not None:
            self.camera.release()

    def get_frame(self) -> tkinter.PhotoImage:
        """
        get the las frame
        :return: the last frame captured
        """
        return self.display.lastFrame

    def calibrate(self):
        grabbed, img = self.camera.read()

        if not grabbed:
            raise Exception("Camera not read")

        foundPattern, corners = cv.findChessboardCorners(img, patternSize=(9, 6))

        if not foundPattern:
            raise Exception("Pattern not found")

        cv.drawChessboardCorners(image=img, patternSize=(9, 6), corners=corners, patternWasFound=foundPattern)

        cv.imshow("test", img)

    def focus_add(self):
        self.focus += self.focus_increment
        self.update_focus()

    def focus_sub(self):
        self.focus -= self.focus_increment
        self.update_focus()

    def update_focus(self):
        self.camera.set(cv.CAP_PROP_FOCUS, self.focus)

    def save(self, filename):

        with open(filename, 'w') as fp:
            try:
                fp.write(
                    json.dumps(
                        {
                            'cameraAccess': self.access,
                            'focus': self.focus
                        },
                        indent=4
                    )
                )
                return True
            except IOError:
                return False


# temp test code
if __name__ == '__main__':
    calib = CamCalib()
    calib.set_access('0')
    calib.activate_camera()
    calib.show_camera()
    print("test plan")

    while True:
        try:
            calib.calibrate()
        except:
            pass
        cv.waitKey(15)
