# specific thread that allow for displaying a stream

from threading import Thread
import cv2 as cv
from PIL import Image, ImageTk

class DisplayBase:

    def __init__(self, capture):
        self.capture = capture
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
                self.show(image)
                cv.waitKey(1)
            else:
                self.stop()

    def show(self, image):
        pass

    def stop(self):
        self.stopped = True

class Display(DisplayBase):

    def __init__(self, win_name : str, capture):
        super().__init__(capture)
        self.win_name = win_name

    def show(self, image):
        cv.imshow(self.win_name, image)


class TkDisplay(DisplayBase):
    def __init__(self, widget, capture):
        super().__init__(capture)
        self.widget = widget

    def show(self, image):
        rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        self.widget = ImageTk.PhotoImage(img)
