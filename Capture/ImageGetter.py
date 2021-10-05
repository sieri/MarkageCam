import json
import queue
from threading import Thread
import cv2 as cv
import numpy as np

from environement import fish_eye_correction, fish_eye_parametter


class ImageGetter:
    """
        Base class for the display. runs in a separate thread
        capture the image and store it in the parameter lastFrame

    """

    def __init__(self, capture):
        """

        :param capture: OPENCV videoCaputre linking to the stream or camera
        """
        self._thread = Thread(target=self.get, args=())
        self._thread.setName("Camera capture")
        self._capture = capture
        self.stopped = False
        self._queue = queue.Queue()

        if fish_eye_correction:
            with open(fish_eye_parametter) as fp:
                param = json.load(fp)
                self._map1, self._map2 = cv.fisheye.initUndistortRectifyMap(
                    np.array(param['K']),
                    np.array(param['D']),
                    np.eye(3),
                    np.array(param['K']),
                    (param['w'], param['h']),
                    cv.CV_16SC2
                )

    def start(self):
        """
        start the processus
        :return: self, for chaining calls
        """
        self.stopped = False
        self._thread.start()
        return self

    def get(self):
        """
        get the image, loop till the end
        :return:
        """
        while not self.stopped:
            grabbed, image = self._capture.read()

            if fish_eye_correction:
                image = cv.remap(image, self._map1, self._map2, interpolation=cv.INTER_LINEAR, borderMode=cv.BORDER_CONSTANT)

            if grabbed:

                if not self._queue.empty():
                    try:
                        self._queue.get_nowait()  # discard previous (unprocessed) frame
                    except queue.Empty:
                        pass
                self._queue.put(image)
            else:
                self.stop()

        self._capture.release()

    def read(self):
        """
        read the image
        :return the image
        """
        return self._queue.get()

    def stop(self):
        """
        stop the currently running thread
        :return: None
        """
        self.stopped = True
