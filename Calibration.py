import time

from Capture.CameraCalibration import CamCalib
import tkinter as tk
from enum import Enum, auto

"""
Script to run the camera calibration app
"""


class States(Enum):
    INITIAL = auto()
    VIEW_FINDER = auto()
    CAMERA_CONFIRMED = auto()
    SAVE_CONFIG = auto()


stateText = {
    States.INITIAL: "Please enter camera IP",
    States.VIEW_FINDER: "Please confirm it's the correct camera",
    States.CAMERA_CONFIRMED: "Place gird in the camera field of view. Adjust the focus and confirm",
    States.SAVE_CONFIG: ""
}

class CalibApp:
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
        self.state = None
        self.frame = None
        self.keep_updating = False

        # create widgets
        self.lbl_camera_IP = tk.Label(text="Enter camera address:")
        self.ent_camera_ip = tk.Entry()
        self.btn_camera_ip = tk.Button(text="Confirm")
        self.cvn_camera_viewfinder = tk.Canvas()

        self.lbl_state_text = tk.Label()

        # place on the window
        self.lbl_camera_IP.pack()
        self.ent_camera_ip.pack()
        self.btn_camera_ip.pack()
        self.cvn_camera_viewfinder.pack()
        self.lbl_state_text.pack()

        # bind functionalities
        self.btn_camera_ip.bind("<Button-1>", self.event_btn_confirm_ip)
        self.ent_camera_ip.bind("<Return>", self.event_btn_confirm_ip)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # create state machine
        self.transitions = {
            States.INITIAL: self.on_initial_entry,
            States.VIEW_FINDER: self.on_view_finder_entry,
            States.CAMERA_CONFIRMED: self.on_camera_confirmed_entry,
            States.SAVE_CONFIG: self.on_save_config_entry,
        }

    def exec(self):
        """
        run the application main loop till the end
        :return: None, only when exec finished
        """
        self.change_state(States.INITIAL)
        self.root.mainloop()

    def change_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.lbl_state_text.configure(
                text= stateText[self.state]
            )

            # call the new state's entry method
            self.transitions[self.state]()

    def on_initial_entry(self):
        self.calib.close_camera()
        self.deactivate_frames_update()

    def on_view_finder_entry(self):
        self.calib.show_camera(
            (
                self.cvn_camera_viewfinder.winfo_width(),
                self.cvn_camera_viewfinder.winfo_height()
            )
        )
        self.activate_frame_updates()

    def on_camera_confirmed_entry(self):
        pass

    def on_save_config_entry(self):
        pass


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
            self.change_state(States.INITIAL)
            return

        self.change_state(States.VIEW_FINDER)

    def activate_frame_updates(self):
        if not self.keep_updating:
            self.keep_updating = True
            self.update_frame()

    def deactivate_frames_update(self):
        self.keep_updating = False

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

    def on_close(self):
        self.calib.close_camera()  # release the camera
        self.root.destroy()  # actually close the window

if __name__ == '__main__':
    app = CalibApp()
    app.exec()
    time.sleep(1)
    print("slept")


