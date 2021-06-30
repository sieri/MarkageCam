import json
import os
import unittest
from Capture.Camera import Cam
import cv2 as cv


class CameraTestCaseWebCam(unittest.TestCase):

    def setUp(self) -> None:
        f = open("testConf.json", 'w')
        f.write(json.dumps({'cameraAccess': 0}))
        f.close()

    def tearDown(self) -> None:
        os.remove("testConf.json")

    def test_cam_load(self):
        c = Cam('testConf.json')
        self.assertIsNotNone(c, "Camera couldn't load config")
        self.assertEqual(c.config['cameraAccess'], 0)

    def test_cam_capture(self):
        c = Cam('testConf.json')
        c.activate_camera()
        img = c.get_image()
        self.assertIsNotNone(img)
        cv.imshow("Test Capture", img)
        cv.waitKey(1000)
        cv.destroyAllWindows()
        c.close_camera()


if __name__ == '__main__':
    unittest.main()
