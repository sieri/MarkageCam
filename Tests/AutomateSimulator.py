from GUI.Base import BaseApp
import tkinter as tk
import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65433  # The port used by the server

class AutomateSim(BaseApp):
    def __init__(self, root):
        super().__init__(root)
        self.btn = tk.Button(text="take picture", command=self.on_btn)
        self.btn.pack()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))

    def on_btn(self):
        self.socket.sendall(b'1')



if __name__ == '__main__':
    app = AutomateSim(root=tk.Tk())
    app.exec()