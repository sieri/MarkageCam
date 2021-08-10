import tkinter
from Capture.CameraDisplay import TkDisplay, DebugDisplay
from Capture.ImageGetter import ImageGetter

class CameraBase:

    def __init__(self):
        self._camera = None  # a video capture stream
        self._getter = None # a thread getting the data
        self._display = None # a display

    def activate_camera(self):
        """
        Activate the camera
        :return: boolean of the active state of the camera
        """
        pass

    def _activate_capture(self):
        """
        To be called by implementer when they activate the camera
        :return: None
        """
        if self._camera.isOpened():
            self._getter = ImageGetter(self._camera)
            self._getter.start()

    def show_camera(self, scale=None, title="Camera"):
        """
        Activate displaying the camera, run the captures
        :param scale: tupple of scale to resize image to, if None show a debug display instead
        :return: None
        """
        if scale is None:
            self._display = DebugDisplay(title, self._getter)
        else:
            self._display = TkDisplay(self._getter, scale)
        self._display.start()

    def hide_camera(self):
        """
        disable the updates of the camera image, no capture run
        camera still opened
        :return: None
        """
        if self._display is not None:
            self._display.stop()

    def close_camera(self):
        """
        close the camera
        """
        self.hide_camera()

        if self._camera is not None:
            self._getter.stop()
            self._camera.release()

    def get_display_frame(self) -> tkinter.PhotoImage:
        """
        get the last frame, in a format displayable on tk
        :return: the last frame captured
        """
        return self._display.lastFrame
