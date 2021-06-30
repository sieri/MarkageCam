import tkinter as tk


class BaseApp:
    def __init__(self, root, title="Window", delay=15):
        """
        constructor
        :param root: Root TK frame we display into
        :param title: title the root frame
        :param delay: delay between the updates of new frame displayed
        """
        self.root = root
        self.title = title
        self.delay = delay

        self.root.title = self.title

        # bind close to allow proper release of threads
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)


    def exec(self):
        """
        run the application main loop till the end
        :return: None, only when application closed finished
        """
        self.root.mainloop()

    def on_close(self):
        self.root.after(10, self.root.destroy)  # close the window, delays to give time to the threads to finish


class CameraApp(BaseApp):
    cam = None
    cvn_camera_viewfinder = None

    """Base application with a camera fied and a view finder displayed"""
    def __init__(self, root, title="Window", delay=15):
        """
        constructor
        :param root: Root TK frame we display into
        :param title: title the root frame
        :param delay: delay between the updates of new frame displayed
        """
        super().__init__(root, title, delay)
        self.keep_updating = False


    def update_frame(self):
        """
        self repeating method at each update of the camera
        :return: None
        """
        # check if continue
        if self.keep_updating:
            self.frame = self.cam.get_display_frame()
            if self.frame is not None:
                self.cvn_camera_viewfinder.create_image(0, 0, image=self.frame, anchor=tk.NW)

            self.root.after(self.delay, self.update_frame)

    def on_close(self):
        self.keep_updating = False
        if self.cam is not None:
            self.cam.close_camera()  # release the camera
        self.root.after(10, self.root.destroy)  # close the window, delays to give time to the threads to finish

    def activate_frame_updates(self):
        if not self.keep_updating:
            self.keep_updating = True
            self.update_frame()

    def deactivate_frames_update(self):
        self.keep_updating = False