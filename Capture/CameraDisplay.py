# specific thread that allow for displaying a stream

from threading import Thread
import cv2 as cv
from PIL import Image, ImageTk


class DisplayBase:
    """
        Base class for the display. runs in a separate thread
        capture the image and store it in the parameter lastFrame

    """

    def __init__(self, capture):
        self.capture = capture
        self.stopped = False
        self.lastFrame = None

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            grabbed, image = self.capture.read()
            if grabbed:
                self.show(image)
                cv.waitKey(1)
            else:
                self.stop()

    def show(self, image):
        self.lastFrame = image

    def stop(self):
        self.stopped = True


class DebugDisplay(DisplayBase):
    """
    Directly display the captured frame in an openCV window
    """

    def __init__(self, win_name : str, capture):
        super().__init__(capture)
        self.win_name = win_name

    def show(self, image):
        cv.imshow(self.win_name, image)


class TkDisplay(DisplayBase):
    """
    Format the lastFrame for display with tkinter
    """

    def __init__(self, capture, scale):
        super().__init__(capture)
        self.scale = scale

    def show(self, image):
        self.lastFrame = ImageTk.PhotoImage(
            Image.fromarray(cv.cvtColor(image, cv.COLOR_BGR2RGB)).resize(self.scale)
        )

