from GUI.Base import BaseApp
import tkinter as tk
from Cap import CaptureApp

class AppVisuControl(BaseApp):

    def __init__(self, root, title="Visual Controller"):
        super().__init__(root, title)
        self.frame_capture = tk.Frame()
        self._capture = CaptureApp(self.frame_capture)

        self.frame_capture.pack()

    def exec(self):
        self._capture.exec()
        super().exec()

    def _on_close(self):
        self._capture._on_close()
        super()._on_close()


if __name__ == '__main__':
    app = AppVisuControl(tk.Tk())
    app.exec()
