# specific thread that allow for displaying a stream
import time
from threading import Thread
import cv2 as cv
from PIL import Image, ImageTk
from environement import display_fps

class DisplayBase:
    """
        Base class for the display. runs in a separate thread
        capture the image and store it in the parameter lastFrame

    """

    def __init__(self, capture):

        self._thread = Thread(target=self.get, args=())
        self._thread.setName("Camera capture for display")
        self._capture = capture
        self.lastFrame = None
        self._stopped = False
        self._capture.set(cv.CAP_PROP_BUFFERSIZE, 0)
    def start(self):
        self._stopped = False
        self._thread.start()
        return self

    def get(self):
        while not self._stopped:
            grabbed, image = self._capture.read()
            if grabbed:
                self.show(image)
                time.sleep(1/display_fps)
            else:
                self.stop()

    def show(self, image):
        self.lastFrame = image

    def stop(self):
        self._stopped = True


class DebugDisplay(DisplayBase):
    """
    Directly display the captured frame in an openCV window
    """

    def __init__(self, win_name: str, capture):
        super().__init__(capture)
        self._win_name = win_name

    def show(self, image):
        cv.imshow(self._win_name, image)


class TkDisplay(DisplayBase):
    """
    Format the lastFrame for display with tkinter
    """

    def __init__(self, capture, scale):
        super().__init__(capture)
        self.scale = scale

    def show(self, image):
        try:
            self.lastFrame = ImageTk.PhotoImage(
                Image.fromarray(cv.cvtColor(image, cv.COLOR_BGR2RGB)).resize(self.scale)
            )
        except AttributeError:
            # Tk might fail to create the image if called to early or too late
            pass
