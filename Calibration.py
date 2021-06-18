from Capture.CameraCalibration import CamCalib
import tkinter as tk

"""
Script to run the camera calibration app
"""


class CalibApp():
    """Camera calibration window"""
    def __init__(self, root=tk.Tk(), title="Calibration Window", delay=15):
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
        self.calib = CamCalib()
        self.frame = None
        self.keep_updating = True

        # create widgets
        self.lbl_camera_IP = tk.Label(text="Enter camera address:")
        self.ent_camera_ip = tk.Entry()
        self.btn_camera_ip = tk.Button(text="Confirm")
        self.cvn_camera_viewfinder = tk.Canvas()

        # place on the window
        self.lbl_camera_IP.pack()
        self.ent_camera_ip.pack()
        self.btn_camera_ip.pack()
        self.cvn_camera_viewfinder.pack()

        # bind functionalities
        self.btn_camera_ip.bind("<Button-1>", self.event_btn_confirm_ip)

    def exec(self):
        """
        run the application main loop till the end
        :return: None, only when exec finished
        """
        self.root.mainloop()

    def event_btn_confirm_ip(self, event):
        """
        Event reacting to the confirmation of the camera address,
        connect to the camera

        :param event:
        :return: None
        """

        print("attempting to open camera")
        self.calib.set_access(self.ent_camera_ip.get())

        if not self.calib.activate_camera():
            print("Couldn't open camera")
            exit(-1)

        self.calib.show_camera(
            (
                self.cvn_camera_viewfinder.winfo_width(),
                self.cvn_camera_viewfinder.winfo_height()
            )
        )
        self.update_frame()

    def update_frame(self):
        """
        self repeating method at each update of the camera
        :return: None
        """

        self.frame = self.calib.get_frame()
        if self.frame is not None:
            self.cvn_camera_viewfinder.create_image(0, 0, image=self.frame, anchor = tk.NW)

        # check if continue
        if self.keep_updating:
            self.root.after(self.delay, self.update_frame)


if __name__ == '__main__':
    app = CalibApp()
    app.exec()



