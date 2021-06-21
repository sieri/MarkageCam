# specific thread that allow for displaying a stream
import sys
from threading import Thread
import cv2 as cv
from PIL import Image, ImageTk

class DisplayBase:
    """
        Base class for the display. runs in a separate thread
        capture the image and store it in the parameter lastFrame

    """

    def __init__(self, capture):

        self.thread = Thread(target=self.get, args=())
        self.thread.setName("Camera capture for display")
        self.capture = capture
        self.lastFrame = None
        self.stopped = False

    def start(self):
        self.stopped = False
        self.thread.start()
        return self

    def get(self):
        while not self.stopped:
            grabbed, image = self.capture.read()
            if grabbed:
                print("grab")
                self.show(image)
                cv.waitKey(1)
            else:
                print("stop", flush=True)
                self.stop()
        print("stopped", flush=True)

    def show(self, image):
        self.lastFrame = image

    def stop(self):
        self.stopped = True


class DebugDisplay(DisplayBase):
    """
    Directly display the captured frame in an openCV window
    """

    def __init__(self, win_name: str, capture):
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
