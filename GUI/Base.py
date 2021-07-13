import tkinter as tk


class BaseApp:
    def __init__(self, root, title="Window"):
        """
        constructor
        :param root: Root TK frame we display into
        :param title: title the root frame
        """
        self._root = root
        self._title = title

        self._root.title(self._title)

        # bind close to allow proper release of threads
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

    def exec(self):
        """
        run the application main loop till the end
        :return: None, only when application closed finished
        """
        self._root.mainloop()

    def _on_close(self):
        self._root.after(10, self._root.destroy)  # close the window, delays to give time to the threads to finish


class CameraApp(BaseApp):

    """Base application with a camera fied and a view finder displayed"""
    def __init__(self, root, title="Window", delay=15):
        """
        constructor
        :param root: Root TK frame we display into
        :param title: title the root frame
        :param delay: delay between the updates of new frame displayed
        """
        super().__init__(root, title)
        self._keep_updating = False
        self._delay = delay
        self._cam = None
        self._cvn_camera_viewfinder = None
        self.__frame = None #frame need to be a field to be kept in memory

    def _update_frame(self):
        """
        self repeating method at each update of the camera
        :return: None
        """
        # check if continue
        if self._keep_updating:
            self.__frame = self._cam.get_display_frame()
            if self.__frame is not None:
                self._cvn_camera_viewfinder.create_image(0, 0, image=self.__frame, anchor=tk.NW)

            self._root.after(self._delay, self._update_frame)

    def _on_close(self):
        self._keep_updating = False
        if self._cam is not None:
            self._cam.close_camera()  # release the camera
        self._root.after(10, self._root.destroy)  # close the window, delays to give time to the threads to finish

    def activate_frame_updates(self):
        if not self._keep_updating:
            self._keep_updating = True
            self._update_frame()

    def deactivate_frames_update(self):
        self._keep_updating = False