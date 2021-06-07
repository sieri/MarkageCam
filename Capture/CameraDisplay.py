# specific thread that allow for displaying a stream

from threading import Thread
import cv2 as cv


class Display:

    def __init__(self, win_name : str, capure):
        self.win_name = win_name
        self.capture = capure
        self.stopped = False

    def start(self):
        Thread(target=self.get, args=()).start()
        print("started")
        return self

    def get(self):
        print("I'm here")
        while not self.stopped:
            grabbed, image = self.capture.read()
            if grabbed:
                cv.imshow(self.win_name, image)
                cv.waitKey(1)
            else:
                self.stop()

    def stop(self):
        self.stopped = True
