import time
from GUI.Base import CameraApp
from Capture.CameraCalibration import CamCalib
import tkinter as tk
from tkinter import messagebox, filedialog
from enum import Enum, auto

from environement import debug, max_img_bytes

"""
Script to run the camera calibration app
"""


class States(Enum):
    INITIAL = auto()
    ACTIVATE_CAMERA = auto()
    VIEW_FINDER = auto()
    CAMERA_CONFIRMED = auto()
    SAVE_CONFIG = auto()


state_text = {
    States.INITIAL: "Please enter camera IP",
    States.ACTIVATE_CAMERA: "",
    States.VIEW_FINDER: "Please confirm it's the correct camera",
    States.CAMERA_CONFIRMED: "Place the calibration gird in the camera field of view. Adjust the focus and confirm",
    States.SAVE_CONFIG: "Saving, please wait"
}


class CalibApp(CameraApp):
    """Camera calibration window"""

    def __init__(self, root, title="Calibration Window", delay=15):
        """
        constructor
        :param root: Root TK frame we display into
        :param title: title the root frame
        :param delay: delay between the updates of new frame displayed
        """
        super().__init__(root, title, delay)

        self._cam = CamCalib()
        self.__state = None

        self.ckb_camera_confirm_value = tk.BooleanVar()

        # create widgets
        self.lbl_state_text = tk.Label()

        self.ip_frame = tk.Frame(root)

        self.lbl_camera_IP = tk.Label(self.ip_frame, text="Enter camera address:")
        self.ent_camera_ip = tk.Entry(self.ip_frame)
        self.btn_camera_ip = tk.Button(self.ip_frame, text="Confirm", command=self.event_btn_confirm_ip)

        self._cvn_camera_viewfinder = tk.Canvas()
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
            command=self._cam.focus_add
        )

        self.btn_focus_sub = tk.Button(
            self.focus_frame,
            text='-',
            command=self._cam.focus_sub
        )

        self.ent_camera_ip.insert(0, "rtsp://")

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
        self._cvn_camera_viewfinder.pack()
        self.ckb_camera_confirm.pack()

        self.focus_frame.pack()
        self.btn_focus_add.pack(side=tk.LEFT)
        self.btn_focus_sub.pack(side=tk.LEFT)
        self.btn_focus_confirm.pack(side=tk.LEFT)

        # bind functionalities extra functionalities
        self.ent_camera_ip.bind("<Return>", self.on_ent_camera_ip)
        self._cvn_camera_viewfinder.bind("<Button-1>", self.event_canvas_click)

        # create bonding box
        self.bounding = Bounding(1, 1)

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
        :return: None, only when exec finished, if no master
        """
        self._root.after(100, self.change_state, States.INITIAL)  # enter the state once gui is setup
        super().exec()

    def change_state(self, new_state):
        if self.__state != new_state:
            self.__state = new_state
            self.lbl_state_text.configure(
                text=state_text[self.__state]
            )
            if debug:
                print("state: ", self.__state)
            # call the new state's entry method
            self.transitions[self.__state]()

    def on_initial_entry(self):
        self._cam.close_camera()
        self.deactivate_frames_update()

        self._cvn_camera_viewfinder.create_rectangle(
            0, 0,
            self._cvn_camera_viewfinder.winfo_width(),
            self._cvn_camera_viewfinder.winfo_height(),
            fill='gray'
        )

        # uncheck the checkbox
        self.ckb_camera_confirm_value.set(False)

        # enable controls
        self.lbl_camera_IP['state'] = tk.NORMAL
        self.btn_camera_ip['state'] = tk.ACTIVE
        self.ent_camera_ip['state'] = tk.NORMAL

        # disable controls
        self.ckb_camera_confirm['state'] = tk.DISABLED
        self.btn_focus_confirm['state'] = tk.DISABLED
        self.btn_focus_add['state'] = tk.DISABLED
        self.btn_focus_sub['state'] = tk.DISABLED

    def on_activate_camera_entry(self):
        self._cam.set_access(self.ent_camera_ip.get())

        if not self._cam.activate_camera():
            self.change_state(States.INITIAL)
            messagebox.showerror("Error", "couldn't open the camera")
        else:
            self.change_state(States.VIEW_FINDER)

    def on_view_finder_entry(self):
        self._cam.show_camera(
            (
                self._cvn_camera_viewfinder.winfo_width(),
                self._cvn_camera_viewfinder.winfo_height()
            )
        )
        # create bonding box
        self.bounding = Bounding(
            self._cvn_camera_viewfinder.winfo_width(),
            self._cvn_camera_viewfinder.winfo_height()
        )
        self.activate_frame_updates()

        # uncheck the checkbox
        self.ckb_camera_confirm_value.set(False)

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

        try:
            img_size = self._cam.calibrate(
                self.bounding.coord(),
                self._cvn_camera_viewfinder.winfo_width(),
                self._cvn_camera_viewfinder.winfo_height()
            )

            if img_size > max_img_bytes:
                messagebox.showerror("Warning", "Image produced would be too big, reduce capture area")
                self.change_state(States.CAMERA_CONFIRMED)
                return

        except Exception as e:
            print(e)
            messagebox.showerror("Error", e)
            self.change_state(States.CAMERA_CONFIRMED)
            return

        filename = tk.filedialog.asksaveasfilename(
            initialdir=".",
            title="Save file",
            initialfile="camConfig.json",
            filetypes=(("Camera config file", "*.json"),)
        )
        if filename is None or len(filename) == 0:
            self.change_state(States.CAMERA_CONFIRMED)
        else:
            if not self._cam.save(filename):
                messagebox.showerror("Error", "couldn't save the file")
                self.change_state(States.CAMERA_CONFIRMED)
            self.change_state(States.INITIAL)

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
        if self.ckb_camera_confirm_value.get():
            self.change_state(States.CAMERA_CONFIRMED)
        else:
            self.change_state(States.VIEW_FINDER)

    def event_canvas_click(self, event):
        # outputting x and y coords to console
        self.bounding.click(event.x, event.y)

    def _update_frame(self):
        super(CalibApp, self)._update_frame()
        self.bounding.draw(self._cvn_camera_viewfinder)


class Bounding:
    def __init__(self, width, height):
        self.corners = [
            Corner(0, 0),
            Corner(0, height - 1),
            Corner(width - 1, height - 1),
            Corner(width - 1, 0)
        ]

        self.active = False
        self.currentActive = None

    def draw(self, canvas):
        for i, corner in enumerate(self.corners):
            canvas.create_line(
                corner.x,
                corner.y,
                self.corners[i - 1].x,
                self.corners[i - 1].y,
                width=3,
                fill='blue'
            )
        for corner in self.corners:
            corner.draw(canvas)

    def click(self, x,y):
        if self.active:
            self.currentActive.x = x
            self.currentActive.y = y
            self.currentActive.active = False
            self.active = False
            self.currentActive = None
        else:
            for corner in self.corners:
                if abs(corner.x-x) <= 6 and abs(corner.y-y) <= 6:
                    corner.active = True
                    self.active = True
                    self.currentActive = corner
                    break

    def coord(self):
        return [[c.x, c.y] for c in self.corners]

class Corner:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = False

    def draw(self, canvas):
        if self.active:
            canvas.create_oval(self.x - 5, self.y - 5, self.x + 5, self.y + 5, fill='green')
        else:
            canvas.create_oval(self.x - 5, self.y - 5, self.x + 5, self.y + 5, fill='red')


if __name__ == '__main__':
    app = CalibApp(tk.Tk())
    app.exec()
