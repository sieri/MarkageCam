from Capture.CameraCalibration import CamCalib
import tkinter as tk





def textBased():
    print("=====Camera Calibration script====")

    string = str(input("enter camera address:"))

    print("attempting to open camera")
    calib.set_access(string)

    if not calib.activate_camera():
        print("Couldn't open camera")
        exit(-1)

    calib.show_camera()

    answer = str(input("Confirm correct camera [Y/N]:", ))

    if not answer.upper() == 'Y':
        print("wrong camera, start over")
        exit(0)

    input("Press to stop")
    calib.hide_camera()


if __name__ == '__main__':
    window = tk.Tk(screenName="Calibration Window")

    greeting = tk.Label(text="hello wold")

    greeting.pack()

    window.mainloop()



