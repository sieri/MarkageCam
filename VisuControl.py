import cv2 as cv
from Utils.DebugDisplay import show_resized
from Data import DB
from GUI.Base import BaseApp
import tkinter as tk
from Cap import CaptureApp


class AppVisuControl(BaseApp):

    def __init__(self, root, title="Visual Controller"):
        super().__init__(root, title)
        self.frame_capture = tk.Frame()
        self._capture = CaptureApp(self.frame_capture)

        self.frame_capture.pack()

        self._capture.on_capture_callback.append(self.treat_image)

    def exec(self):
        self._capture.exec()
        super().exec()

    def on_close(self):
        self._capture.on_close()
        super().on_close()

    def treat_image(self, corrected: DB.CorrectedImg):
        pass


if __name__ == '__main__':
    app = AppVisuControl(tk.Tk())
    app.exec()
