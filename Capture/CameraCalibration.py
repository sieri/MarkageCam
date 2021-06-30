import json


import cv2 as cv
import numpy as np

from Capture.CameraBase import CameraBase
from platform import system
from environement import debug


class CamCalib(CameraBase):
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

    def calibrate_fish_eye_distortion(self, repeats=1, size=(9, 6)):
        """
        WARNING : NON FUNCTIONAL STUB, DO NOT USE BEFORE FIXING

        Gets the camera distortion parameter from a matrix to be used to correct
        the distortion

        reference : https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html

        :param repeats: number of image used for the calibration
        :param size: size of the gird pattern used
        :return:
        """
        img_points = []
        obj_points = []
        for dummy in range(repeats):
            try:
                i, o = self.process_chessboard(size=size)
                img_points.extend(i)
                obj_points.extend(o)
            except Exception as e:
                dummy -= 1
                print(e)

        w = int(self.camera.get(cv.CAP_PROP_FRAME_WIDTH))
        h = int(self.camera.get(cv.CAP_PROP_FRAME_HEIGHT))

        # calculate camera distortion
        rms, camera_matrix, dist_coefs, rvecs, tvecs = cv.calibrateCamera(obj_points, img_points, (w, h), None, None)

        if debug:
            print("\nRMS:", rms)
            print("camera matrix:\n", camera_matrix)
            print("distortion coefficients: ", dist_coefs.ravel())

        # cv.imwrite("CameraCalibExample.png", img) #TODO: remove report code

        return rms, camera_matrix, dist_coefs, rvecs, tvecs

    def process_chessboard(self, size=(9, 6)):
        """
        Get the points of the chessboad grid for calibration purposes

        :raises: Exception in case of error reading the camera or pattern

        :param size: size of the gird pattern used
        :return: lists of object and images point see https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html
        """

        obj_points = []  # 3d points in real world space
        img_points = []  # 2d points in image plane.

        # size of the pattern
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(sizeX-1,sizeY-1,0)
        objp = np.zeros((size[0] * size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:size[0], 0:size[1]].T.reshape(-1, 2)

        # grab a frame
        cv.waitKey(25)
        grabbed, img = self.camera.read()

        # cv.imwrite("CameraCalibSetup.png", img)
        grayscale = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        if not grabbed:
            raise Exception("Camera not read")
        found_pattern, corners = cv.findChessboardCorners(grayscale, patternSize=(9, 6))
        if not found_pattern:
            raise Exception("Pattern not found")

        term = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_COUNT, 30, 0.1)

        # improve accuracy of the corner detection
        cv.cornerSubPix(grayscale, corners, (5, 5), (-1, -1), term)

        # add the points
        obj_points.append(objp)  # the base array to mark the position
        img_points.append(corners)  # and the corners that correspond to them

        # the points could be repeated a couple of time for better accuracy
        if debug:
            cv.drawChessboardCorners(image=img, patternSize=size, corners=corners, patternWasFound=found_pattern)
            cv.imshow("test", img)

        return img_points, obj_points

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
    calib.set_access('1')
    calib.activate_camera()
    calib.show_camera()

    rms, camera_matrix, dist_coefs, rvecs, tvecs = calib.calibrate_fish_eye_distortion(repeats=10)

    grabbed, img = calib.camera.read()

    h, w = img.shape[:2]
    newcameramtx, roi = cv.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w, h))

    dst = cv.undistort(img, camera_matrix, dist_coefs, None, newcameramtx)

    # crop and save the image
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]

    cv.imshow("undistorted", dst)
    cv.waitKey(0)
