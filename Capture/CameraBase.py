import tkinter
from Capture.CameraDisplay import TkDisplay, DebugDisplay


class CameraBase:

    def __init__(self):
        self.camera = None
        self.display = None

    def activate_camera(self):
        pass

    def show_camera(self, scale=None, title="Camera"):
        """
        Activate displaying the camera, run the captures
        :param scale: tupple of scale to resize image to
        :return: None
        """
        if scale is None:
            self.display = DebugDisplay(title, self.camera)
        else:
            self.display = TkDisplay(self.camera, scale)
        self.display.start()

    def hide_camera(self):
        """
        disable the updates of the camera image, no capture run
        camera still opened
        :return: None
        """
        if self.display is not None:
            self.display.stop()

    def close_camera(self):
        """close the camera"""
        self.hide_camera()

        if self.camera is not None:
            self.camera.release()

    def get_display_frame(self) -> tkinter.PhotoImage:
        """
        get the last frame
        :return: the last frame captured
        """
        return self.display.lastFrame