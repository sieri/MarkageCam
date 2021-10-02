# specific thread that allow for displaying a stream
import queue
import time
from threading import Thread

import cv2 as cv
from PIL import Image, ImageTk

from Capture.ImageGetter import ImageGetter
from environement import display_fps, debug


class DisplayBase():
    """
    Base class for the display
    """
    def __init__(self, getter: ImageGetter):
        """
        :param getter: the image getter, initialized
        """
        self._getter = getter
        self._thread = Thread(target=self.get, args=())
        self._thread.setName("Thread for display")
        self._stopped = True

    def start(self):
        """
        start the thread
        :return:
        """
        self._stopped = False
        self._thread.start()
        return self

    def get(self):
        while not self._stopped:
            try:
                img = self._getter.read()
                self.show(img)

            except queue.Empty:
                if self._getter.stopped:
                    self.stop()
            cv.waitKey(int(1000.0 / display_fps))

    def stop(self):
        print("stop")
        self._stopped = True

    def show(self, image):
        pass


class DebugDisplay(DisplayBase):
    """
    Directly display the captured frame in an openCV window
    """

    def __init__(self, win_name: str, getter):
        super().__init__(getter)
        self._win_name = win_name

    def show(self, image):
        cv.imshow(self._win_name, image)


class TkDisplay(DisplayBase):
    """
    Format the lastFrame for display with tkinter
    """

    def __init__(self, getter, scale):
        super().__init__(getter)
        self.scale = scale
        self.lastFrame = None  # image to save in memory

    def show(self, image):
        try:
            self.lastFrame = ImageTk.PhotoImage(
                Image.fromarray(cv.cvtColor(image, cv.COLOR_BGR2RGB)).resize(self.scale)
            )
        except AttributeError:
            # Tk might fail to create the image if called to early or too late
            pass
