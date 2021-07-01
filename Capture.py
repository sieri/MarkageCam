import os.path

from Capture.Camera import Cam
from GUI.Base import CameraApp
import tkinter as tk
from enum import Enum, auto
from tkinter import messagebox, filedialog


class States(Enum):
    INITIAL = auto()
    ENTER_FILE = auto()
    CAMERA_ACTIVATION = auto()
    CAMERA_OPEN = auto()


class CaptureApp(CameraApp):
    def __init__(self, root, title="Capture Window", delay=15):
        """
        constructor
        :param root: Root TK frame we display into
        :param title: title the root frame
        :param delay: delay between the updates of new frame displayed
        """
        super().__init__(root, title, delay)

        self.cvn_camera_viewfinder = tk.Canvas()
        self.cvn_camera_viewfinder.pack()

        self.config_filename = "./camConfig.json"

        self.state = None
        self.transitions = {
            States.INITIAL: self.on_entry_initial,
            States.ENTER_FILE: self.on_entry_enter_file,
            States.CAMERA_ACTIVATION: self.on_entry_camera_activation,
            States.CAMERA_OPEN: self.on_entry_camera_open,
        }

    def exec(self):
        """
        run the application main loop till the end
        :return: None, only when exec finished
        """
        self.root.after(100, self.change_state, States.INITIAL)  # enter the state once gui is setup
        self.root.mainloop()

    def change_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            # call the new state's entry method
            self.transitions[self.state]()

    def on_entry_initial(self):
        self.cvn_camera_viewfinder.create_rectangle(
            0, 0,
            self.cvn_camera_viewfinder.winfo_width(),
            self.cvn_camera_viewfinder.winfo_height(),
            fill='gray'
        )

        if os.path.exists(self.config_filename):
            self.change_state(States.CAMERA_ACTIVATION)
        else:
            self.change_state(States.ENTER_FILE)

    def on_entry_enter_file(self):
        self.config_filename = filedialog.askopenfilename(
            initialdir=".",
            title="Select config",
            filetypes=(("Camera config file", "*.json"),)
        )

        self.change_state(States.CAMERA_ACTIVATION)

    def on_entry_camera_activation(self):
        self.cam = Cam(self.config_filename)

        if self.cam.activate_camera():
            self.change_state(States.CAMERA_OPEN)
        else:
            self.change_state(States.ENTER_FILE)


    def on_entry_camera_open(self):
        self.cam.show_camera(
            (
                self.cvn_camera_viewfinder.winfo_width(),
                self.cvn_camera_viewfinder.winfo_height()
            )
        )

        self.activate_frame_updates()

if __name__ == '__main__':
    app = CaptureApp(tk.Tk())
    app.exec()