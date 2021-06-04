# Access to the camera and optical correction
import json
import cv2 as cv


class Cam:

    def __init__(self, config_file):
        self.capture = None

        with open(config_file) as fp:
            # noinspection PyBroadException
            try:
                self.config = json.load(fp)

            except:
                print("unable to load camera config file. Run Calibration")

    # activate the camera
    def activate(self):
        self.capture = cv.VideoCapture(self.config['cameraAccess'])

    # get the image with camera correction
    def get_image(self):
        retval, img = self.capture.read()

        if retval and img is not None:
            return img
        else:
            pass  # todo: decide what to do in case of capture fail

    def deactivate(self):
        self.capture.release()
