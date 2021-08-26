"""
Application managing the capture elements and a display of the screen
"""

import os.path
from datetime import datetime

from Capture.Camera import Cam
from GUI.Base import CameraApp
import tkinter as tk
from enum import Enum, auto
from tkinter import filedialog
from Data import DB
from environement import test_setup, save_to_db, use_simulator

if use_simulator:
    from Tests import OPC_Simulator as Opc  # simulator of the automate connection same interface
else:
    try:
        from Capture import Opc_Client as Opc
    except (NotImplementedError, OpenOPC.OPCError, pywintypes.com_error) as e: # OPC client only function in a 32 bit environment
        print(e)
        if test_setup:
            print("Need 32 bit interpreter, using simulator")
            from Tests import OPC_Simulator as Opc # simulator of the automate connection same interface
        else:
            raise Exception("Need 32 bit interpeter")




class States(Enum):
    INITIAL = auto()
    ENTER_FILE = auto()
    CAMERA_ACTIVATION = auto()
    CAMERA_OPEN = auto()


class CaptureApp(CameraApp):
    config_filename : str
    expected_text : DB.ExpectedText
    on_capture_callback : list
    """
    Application needing to be run to capture the camera stream
    """
    def __init__(self, root, title="Capture Window", delay=15):
        """
        constructor
        :param root: Root TK frame we display into
        :param title: title the root frame
        :param delay: delay between the updates of new frame displayed
        """
        super().__init__(root, title, delay)
        self.expected_text = None
        self.config_filename = "./camConfig.json"
        self.on_capture_callback = []
        if save_to_db:
            self.on_capture_callback.append(self.save_to_db)

        # gui
        self._cvn_camera_viewfinder = tk.Canvas()
        self._cvn_camera_viewfinder.pack()

        self.meta_frame = tk.Frame(root)
        self.expected_frame = tk.Frame(self.meta_frame)
        self.repeats_frame = tk.Frame(self.meta_frame)
        self.lbl_expected_text = tk.Label(self.expected_frame, text="text")
        self.ent_expected_text = tk.Entry(self.expected_frame)
        self.lbl_x_repeats = tk.Label(self.repeats_frame, text="x")
        self.ent_x_repeats = tk.Entry(self.repeats_frame)
        self.lbl_y_repeats = tk.Label(self.repeats_frame, text="y")
        self.ent_y_repeats = tk.Entry(self.repeats_frame)
        # self.btn_confirm_expected = tk.Button(text="Confirm", command=self.update_text)

        self.meta_frame.pack()
        self.expected_frame.pack()
        self.repeats_frame.pack()
        self.lbl_expected_text.pack(side=tk.LEFT)
        self.ent_expected_text.pack(side=tk.LEFT)
        self.lbl_x_repeats.pack(side=tk.LEFT)
        self.ent_x_repeats.pack(side=tk.LEFT)
        self.lbl_y_repeats.pack(side=tk.LEFT)
        self.ent_y_repeats.pack(side=tk.LEFT)
        # self.btn_confirm_expected.pack()

        self.ent_expected_text.insert(0, "Default expected text")
        self.ent_x_repeats.insert(1, "0")
        self.ent_y_repeats.insert(1, "0")

        self.ent_expected_text.configure(state='readonly')

        self._root.bind('c', self.capture_image)

        # state machine
        self.__state = None
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
        self._root.after(100, self.change_state, States.INITIAL)  # enter the state once gui is setup
        super().exec()

    def change_state(self, new_state):
        """
        Iterates through the states, normally do not call this from outside
        :param new_state: The new state to enter
        :return:
        """
        if self.__state != new_state:
            self.__state = new_state
            # call the new state's entry method
            self.transitions[self.__state]()

    def on_entry_initial(self):
        """
        State entry method, fill the viewfinder, and check for default config, then exit
        :return:
        """
        self._cvn_camera_viewfinder.create_rectangle(
            0, 0,
            self._cvn_camera_viewfinder.winfo_width(),
            self._cvn_camera_viewfinder.winfo_height(),
            fill='gray'
        )

        if os.path.exists(self.config_filename):
            self.change_state(States.CAMERA_ACTIVATION)
        else:
            self.change_state(States.ENTER_FILE)

    def on_entry_enter_file(self):
        """
        state entry method, read the file from dialogue then exit
        :return:
        """
        self.config_filename = filedialog.askopenfilename(
            initialdir=".",
            title="Select config",
            filetypes=(("Camera config file", "*.json"),)
        )

        self.change_state(States.CAMERA_ACTIVATION)

    def on_entry_camera_activation(self):
        """
        state entry method, open the camera, then exit to the corresponding state depending on the result
        :return:
        """
        self._cam = Cam(self.config_filename)

        if self._cam.activate_camera():
            self.change_state(States.CAMERA_OPEN)
        else:
           self.change_state(States.ENTER_FILE)

    def on_entry_camera_open(self):
        """
        state entry method, show the camera, and activate the synchronised capture
        """
        self._cam.show_camera(
            (
                self._cvn_camera_viewfinder.winfo_width(),
                self._cvn_camera_viewfinder.winfo_height()
            )
        )

        self.activate_frame_updates()
        Opc.set_synchro(self.capture_image)
        self.update_text()

    def update_text(self):
        """
        Update expected text information given the latest parameters
        :return:
        """
        text = Opc.get_text()
        (x,y) = Opc.get_repetions()

        print(text)
        if self.expected_text is None or not (text == self.expected_text.text and
                x == self.expected_text.x_repeats and
                y == self.expected_text.y_repeats):
            self.expected_text = DB.ExpectedText(text, x, y)

            # update gui
            self.ent_expected_text.configure(state='normal')
            self.ent_expected_text.delete(0, tk.END)
            self.ent_expected_text.insert(0, text)
            self.ent_expected_text.configure(state='readonly')

            self.ent_x_repeats.configure(state='normal')
            self.ent_x_repeats.delete(0, tk.END)
            self.ent_x_repeats.insert(0, str(x))
            self.ent_x_repeats.configure(state='readonly')

            self.ent_y_repeats.configure(state='normal')
            self.ent_y_repeats.delete(0, tk.END)
            self.ent_y_repeats.insert(0, str(y))
            self.ent_y_repeats.configure(state='readonly')


    def capture_image(self, _event=None):
        """
        Capture image, and send it to the callback listeners
        :param _event: not used
        :return:
        """
        img, corrected = self._cam.get_image()
        self.update_text()
        new_image = DB.BaseImg(img, datetime.now(), self.expected_text)
        new_corrected = DB.CorrectedImg(corrected, new_image)
        for i in self.on_capture_callback:
            # callback have that argument or it doesnt work, disable ide inspection
            # noinspection PyArgumentList
            i(new_corrected)

    def save_to_db(self, corrected: DB.CorrectedImg):
        """
        Capture image callback that save the image to the Database and local file system
        :param corrected:
        :return:
        """
        with DB.DbConnector() as db:
            db.insert(corrected.base_img.expected_text)
            db.insert(corrected.base_img)
            db.insert(corrected)

    def on_close(self):
        """
        Kill all
        :return:
        """
        Opc.kill_synchro()
        super().on_close()


if __name__ == '__main__':
    app = CaptureApp(tk.Tk())
    app.exec()
