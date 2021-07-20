import cv2 as cv

from ImgTreatement.TreatementThread import ImgProcessor
from ImgTreatement.DebugDisplay import show_resized
from Data import DB
from GUI.Base import BaseApp
import tkinter as tk
from Cap import CaptureApp


class AppVisuControl(BaseApp):

    def __init__(self, root, title="Visual Controller"):
        super().__init__(root, title)
        self.frame_capture = tk.Frame()
        self._capture = CaptureApp(self.frame_capture)
        self._treatement_thread = ImgProcessor(self.treated_image)
        self.frame_capture.pack()

        self._capture.on_capture_callback.append(self._treatement_thread.add)

    def exec(self):
        self._capture.exec()
        self._treatement_thread.start()
        super().exec()

    def on_close(self):
        self._capture.on_close()
        self._treatement_thread.stop()
        super().on_close()

    def treated_image(self, result):
        pass


if __name__ == '__main__':
    app = AppVisuControl(tk.Tk())
    app.exec()
