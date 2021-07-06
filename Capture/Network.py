import os
import socket
import time
from threading import Thread

import environement


class TCP_server:

    def __init__(self, callback, host='127.0.0.1', port = 65433):
        self.socket = None
        self.host = host
        self.port = port
        self.callback = callback
        self.running = False

        self.thread = Thread(target=self.serverRun, args=())
        self.thread.setName("Network thread for capture")

    def start(self):
        self.running = True
        self.thread.start()
        return self

    def stop(self):
        self.running = False
        self.socket.close()

    def serverRun(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            self.socket = s
            s.bind((self.host, self.port))
            while self.running:
                try:
                    s.listen()
                    conn, addr = s.accept()
                    with conn:
                        print('Connected by', addr)
                        while self.running:
                            data = conn.recv(1)
                            if not data:
                                break
                            self.callback()
                except ConnectionError as e:
                    if environement.debug:
                        print(e)
                except OSError:
                    pass


if __name__ == '__main__':
    def test():
        print("called back")

    serv = TCP_server(test)

    serv.start()
    print("And threads")
    time.sleep(10)
    serv.stop()
    print("ended")
