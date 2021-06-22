import time

from Capture.CameraCalibration import CamCalib
import tkinter as tk
from enum import Enum, auto

"""
Script to run the camera calibration app
"""


class States(Enum):
    INITIAL = auto()
    ACTIVATE_CAMERA = auto()
    VIEW_FINDER = auto()
    CAMERA_CONFIRMED = auto()
    SAVE_CONFIG = auto()


stateText = {
    States.INITIAL: "Please enter camera IP",
    States.ACTIVATE_CAMERA: "",
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
        self.ckb_camera_confirm_value = tk.BooleanVar()

        # create widgets
        self.lbl_state_text = tk.Label()

        self.ip_frame = tk.Frame(root)

        self.lbl_camera_IP = tk.Label(self.ip_frame, text="Enter camera address:")
        self.ent_camera_ip = tk.Entry(self.ip_frame)
        self.btn_camera_ip = tk.Button(self.ip_frame, text="Confirm", command=self.event_btn_confirm_ip)

        self.cvn_camera_viewfinder = tk.Canvas()
        self.ckb_camera_confirm = tk.Checkbutton(
            text='Correct camera',
            variable=self.ckb_camera_confirm_value,
            onvalue=True, offvalue=False,
            command=self.event_ckb_camera_confirm
        )

        self.focus_frame = tk.Frame(root)
        self.btn_focus_add = tk.Button(
            self.focus_frame,
            text='+',
            command=self.calib.focus_add
        )

        self.btn_focus_sub = tk.Button(
            self.focus_frame,
            text='-',
            command=self.calib.focus_sub
        )

        self.btn_focus_confirm = tk.Button(
            self.focus_frame,
            text='Confirm calibration',
            command=self.event_btn_confirm_focus
        )

        # place on the window
        self.lbl_state_text.pack()

        self.ip_frame.pack()
        self.lbl_camera_IP.pack(side=tk.LEFT)
        self.ent_camera_ip.pack(side=tk.LEFT)
        self.btn_camera_ip.pack(side=tk.LEFT)
        self.cvn_camera_viewfinder.pack()
        self.ckb_camera_confirm.pack()

        self.focus_frame.pack()
        self.btn_focus_add.pack(side=tk.LEFT)
        self.btn_focus_sub.pack(side=tk.LEFT)
        self.btn_focus_confirm.pack(side=tk.LEFT)

        # bind functionalities extra functionalities
        self.ent_camera_ip.bind("<Return>", self.on_ent_camera_ip)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # create state machine
        self.transitions = {
            States.INITIAL: self.on_initial_entry,
            States.ACTIVATE_CAMERA: self.on_activate_camera_entry,
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
                text=stateText[self.state]
            )

            # call the new state's entry method
            self.transitions[self.state]()

    def on_initial_entry(self):
        self.calib.close_camera()
        self.deactivate_frames_update()

        # disable controls
        self.ckb_camera_confirm['state'] = tk.DISABLED
        self.btn_focus_confirm['state'] = tk.DISABLED
        self.btn_focus_add['state'] = tk.DISABLED
        self.btn_focus_sub['state'] = tk.DISABLED

    def on_activate_camera_entry(self):
        self.calib.set_access(self.ent_camera_ip.get())

        if not self.calib.activate_camera():
            self.change_state(States.INITIAL)
        else:
            self.change_state(States.VIEW_FINDER)

    def on_view_finder_entry(self):
        self.calib.show_camera(
            (
                self.cvn_camera_viewfinder.winfo_width(),
                self.cvn_camera_viewfinder.winfo_height()
            )
        )
        self.activate_frame_updates()

        # activate controls

        self.lbl_camera_IP['state'] = tk.NORMAL
        self.ckb_camera_confirm['state'] = tk.ACTIVE
        self.btn_camera_ip['state'] = tk.ACTIVE
        self.ent_camera_ip['state'] = tk.NORMAL
        
        # deactivate controls
        self.btn_focus_confirm['state'] = tk.DISABLED
        self.btn_focus_add['state'] = tk.DISABLED
        self.btn_focus_sub['state'] = tk.DISABLED

    def on_camera_confirmed_entry(self):
        # activate controls
        self.btn_focus_confirm['state'] = tk.ACTIVE
        self.btn_focus_add['state'] = tk.ACTIVE
        self.btn_focus_sub['state'] = tk.ACTIVE

        # deactivate controls
        self.lbl_camera_IP['state'] = tk.DISABLED
        self.btn_camera_ip['state'] = tk.DISABLED
        self.ent_camera_ip['state'] = tk.DISABLED

    def on_save_config_entry(self):
        print("save")

    def event_btn_confirm_ip(self):
        """
        Event reacting to the confirmation of the camera address,
        connect to the camera

        :return: None
        """

        print("attempting to open camera")
        self.change_state(States.ACTIVATE_CAMERA)

    def event_btn_confirm_focus(self):
        self.change_state(States.SAVE_CONFIG)

    def on_ent_camera_ip(self, event=None):
        if self.ent_camera_ip['state'] == tk.NORMAL:
            self.event_btn_confirm_ip()

    def event_ckb_camera_confirm(self):
        print(self.ckb_camera_confirm_value.get())
        if self.ckb_camera_confirm_value.get():
            self.change_state(States.CAMERA_CONFIRMED)
        else:
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
            self.cvn_camera_viewfinder.create_image(0, 0, image=self.frame, anchor=tk.NW)

        # check if continue
        if self.keep_updating:
            self.root.after(self.delay, self.update_frame)

    def on_close(self):
        self.keep_updating = False
        self.calib.close_camera()  # release the camera
        self.root.after(10, self.root.destroy)  # close the window, delays to give time to the threads to finish


if __name__ == '__main__':
    app = CalibApp()
    app.exec()
