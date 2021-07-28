import json
import os
import time
import unittest
from Capture.Camera import Cam
from ImgTreatement import DebugDisplay
import cv2 as cv


class CameraTestCaseWebCam(unittest.TestCase):

    def setUp(self) -> None:
        f = open("testConf.json", 'w')
        # a random valid configuration
        f.write("""{
    "cameraAccess": 0,
    "focus": 210,
    "h": [
        [
            4.911453218303905,
            5.435327175306156,
            0.05853271484375
        ],
        [
            0.06952057532089384,
            14.621252721408382,
            0.017333984375
        ],
        [
            1.2503353900683578e-05,
            0.003416955703869462,
            1.0
        ]
    ],
    "width": 3114,
    "height": 2665
    }""")
        f.close()

    def tearDown(self) -> None:
        os.remove("testConf.json")

    def load_camera(self):
        c = Cam('testConf.json')
        self.assertIsNotNone(c, "Camera couldn't load config")
        self.assertEqual(c.config['cameraAccess'], 0)
        return c

    def test_cam_load(self):
        self.load_camera()

    def test_cam_capture(self):
        c = self.load_camera()
        self.assertTrue(c.activate_camera())
        img, corrected = c.get_image()
        self.assertIsNotNone(img)
        self.assertIsNotNone(corrected)
        DebugDisplay.show_resized("Test Capture", img)
        DebugDisplay.show_resized("Test Correction", corrected)
        cv.waitKey(1000)
        cv.destroyAllWindows()
        c.close_camera()

    def test_camera_display(self):
        c = self.load_camera()
        self.assertTrue(c.activate_camera())
        c.show_camera()

        time.sleep(1)
        c.hide_camera()

if __name__ == '__main__':
    unittest.main()
