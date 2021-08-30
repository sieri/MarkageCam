import inspect
import json
import os
import time

import cv2
import cv2 as cv
import numpy as np

from Capture.CameraBase import CameraBase
from platform import system
from environement import debug

if debug:
    from ImgTreatement.DebugDisplay import *

local_debug = True


class CamCalib(CameraBase):
    """
    A basic camera access used as a viewfinder for the calibration
    """

    def __init__(self):
        super().__init__()
        self._access = ""
        self._camera = None
        self._display = None
        self._focus = 0
        self._focus_increment = 10
        self._h = None
        self._width = -1
        self._height = -1

    def set_access(self, access: str):
        """
        set which camera to access
        :param access: the address of the camera or index if not an IP camera (str only)
        :return: None
        """
        if access.isdecimal():
            self._access = int(access)
        else:
            self._access = access

    def activate_camera(self):
        """
        Activate the camera
        :return: success of activation
        """
        if self._camera is not None and self._camera.isOpened():
            self.close_camera()

        # self._access = "rtsp://192.168.100.154:5554/camera"

        if system() == "Windows":
            # windows specific fix for a warning on opencv camera close
            self._camera = cv.VideoCapture(self._access, cv.CAP_DSHOW)
            self._camera.open(self._access)
        else:
            self._camera = cv.VideoCapture(self._access)
            self._camera.open(self._access)

        # setup the focus
        self._camera.set(cv.CAP_PROP_AUTOFOCUS, 0)
        self._update_focus()

        self._activate_capture()
        return self._camera.isOpened()

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
                i, o = self._process_chessboard(size=size)
                img_points.extend(i)
                obj_points.extend(o)
                time.sleep(5)
            except Exception as e:
                dummy -= 1
                print(e)

        w = int(self._camera.get(cv.CAP_PROP_FRAME_WIDTH))
        h = int(self._camera.get(cv.CAP_PROP_FRAME_HEIGHT))

        # calculate camera distortion
        rms, camera_matrix, dist_coefs, rvecs, tvecs = cv.calibrateCamera(obj_points, img_points, (w, h), None, None)

        if debug:
            print("\nRMS:", rms)
            print("camera matrix:\n", camera_matrix)
            print("distortion coefficients: ", dist_coefs.ravel())

        return rms, camera_matrix, dist_coefs, rvecs, tvecs

    def find_homography(self, size=(9, 6)):
        grabbed, img = self._getter.read()

        if not grabbed:
            raise Exception("Camera not read")

        grayscale = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # TODO: get the numbers from a cleaner source
        pattern_path = os.path.join(os.path.dirname(inspect.getfile(CamCalib)), 'pattern.png')
        pattern = cv.imread(pattern_path, cv.IMREAD_GRAYSCALE)

        pt_cam = self.get_chessboard(grayscale, size)
        pt_pattern = self.get_chessboard(pattern, size)

        h, _mask = cv.findHomography(pt_cam, pt_pattern, cv2.RHO)

        # get the size of the base image
        height, width = grayscale.shape
        corners = np.array([
            [0, 0],
            [0, height - 1],
            [width - 1, height - 1],
            [width - 1, 0]
        ])

        # perspective shift those corners
        corners = cv.perspectiveTransform(np.float32([corners]), h)[0]
        bx, by, bwidth, bheight = cv.boundingRect(corners)  # bx, by will be mapped to negative values

        # create a translation matrix to move them inside
        A = [[1, 0, -bx],
             [0, 1, -by],
             [0, 0, 1]]

        final = np.matmul(A, h)  # multiply the matrix to add the translation in the perspective shift

        return final, bwidth, bheight

    def _process_chessboard(self, size=(9, 6)):
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
        img = self._getter.read()

        # cv.imwrite("CameraCalibSetup.png", img) # TODO: remove report code
        grayscale = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        corners = self.get_chessboard(grayscale, size)

        # add the points
        obj_points.append(objp)  # the base array to mark the position
        img_points.append(corners)  # and the corners that correspond to them

        # the points could be repeated a couple of time for better accuracy
        if debug:
            cv.drawChessboardCorners(image=img, patternSize=size, corners=corners, patternWasFound=True)
            cv.imshow("test", img)

            # cv.imwrite("CameraCalibExample.png", img)  # TODO: remove report code
        return img_points, obj_points

    def focus_add(self):
        self._focus += self._focus_increment
        self._update_focus()

    def focus_sub(self):
        self._focus -= self._focus_increment
        self._update_focus()

    def calibrate(self):
        self._h, self._width, self._height = self.find_homography()

    def save(self, filename):

        with open(filename, 'w') as fp:
            try:
                fp.write(
                    json.dumps(
                        {
                            'cameraAccess': self._access,
                            'focus': self._focus,
                            'h': self._h.tolist(),
                            'width': self._width,
                            'height': self._height,
                            'delay': 0,
                        },
                        indent=4
                    )
                )
                return True
            except IOError:
                return False

    def _update_focus(self):
        self._camera.set(cv.CAP_PROP_FOCUS, self._focus)

    @staticmethod
    def get_chessboard(i, size=(9, 6)):
        n = np.full_like(i, 255)

        found_pattern, corners = cv.findChessboardCorners(i, patternSize=size)
        if not found_pattern:
            raise Exception("Pattern not found")

        term = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_COUNT, 30, 0.1)

        # improve accuracy of the corner detection
        cv.cornerSubPix(i, corners, (5, 5), (-1, -1), term)
        return corners


# temp test code
if __name__ == '__main__':
    calib = CamCalib()
    calib.set_access('rtsp://admin:password@192.168.100.146:554//h264Preview_01_sub')
    calib.activate_camera()
    calib.show_camera()
    calib._camera.set(cv.CAP_PROP_AUTOFOCUS, 1)
    cv.waitKey(5000)

    distort = True

    homo = False

    if distort:
        img = calib._getter.read()

        rms, camera_matrix, dist_coefs, rvecs, tvecs = calib.calibrate_fish_eye_distortion(repeats=100)

        h, w = img.shape[:2]
        print("distort")
        newcameramtx, roi = cv.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w, h))

        dst = cv.undistort(img, camera_matrix, dist_coefs, None, newcameramtx)

        # crop and save the image
        x, y, w, h = roi
        dst = dst[y:y + h, x:x + w]

        cv.imshow("undistorted", dst)

        with open('cameraMatrice.json', 'w') as fp:
            try:
                fp.write(
                    json.dumps(
                        {
                            'dist_coef' : dist_coefs.tolist(),
                            'cameraMtx' : camera_matrix.tolist(),
                            'NewCameraMtx': newcameramtx.tolist(),
                            'roi' : roi,
                        },
                        indent=4
                    )
                )

            except IOError:
                pass

        while True:
            try:
                cv.waitKey(100)
                img = calib._getter.read()
                dst = cv.undistort(img, camera_matrix, dist_coefs, None, newcameramtx)
                cv.imshow("test", dst)
                corners = CamCalib.get_chessboard(cv.cvtColor(dst, cv.COLOR_BGR2GRAY))
                cv.drawChessboardCorners(image=img, patternSize=(9,6), corners=corners, patternWasFound=True)
                cv.imshow("test", img)
            except Exception as e:
                print(e)
    if homo:
        def get_coord(event, x, y, flag, param):
            if event == cv.EVENT_LBUTTONDOWN:
                print("coord" + str((x, y)))


        g, img = calib._camera.read()
        cv.setMouseCallback('Camera', get_coord)

        h, width, height = calib.find_homography()
        print("h" + str(h))

        im1Reg = cv.warpPerspective(img, h, (width, height), borderMode=cv.BORDER_CONSTANT)

        show_resized("img1 reg", im1Reg)

    cv.waitKey(0)
