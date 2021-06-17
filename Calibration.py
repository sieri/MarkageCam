from Capture.CameraCalibration import CamCalib
import tkinter as tk

calib = CamCalib()

def textBased():
    print("=====Camera Calibration script====")

    string = str(input("enter camera address:"))


    answer = str(input("Confirm correct camera [Y/N]:", ))

    if not answer.upper() == 'Y':
        print("wrong camera, start over")
        exit(0)

    input("Press to stop")
    calib.hide_camera()


def event_btn_confirm(event):

    print("attempting to open camera")
    calib.set_access(ent_camera_ip.get())

    if not calib.activate_camera():
        print("Couldn't open camera")
        exit(-1)

    calib.show_camera()


if __name__ == '__main__':
    window = tk.Tk(screenName="Calibration Window")

    # create widgets
    lbl_camera_IP = tk.Label(text="Enter camera address:")
    ent_camera_ip = tk.Entry()
    btn_camera_ip = tk.Button(text="Confirm")

    # place on the window
    lbl_camera_IP.pack()
    ent_camera_ip.pack()
    btn_camera_ip.pack()

    # bind functionalities
    btn_camera_ip.bind("<Button-1>", event_btn_confirm)

    window.mainloop()



