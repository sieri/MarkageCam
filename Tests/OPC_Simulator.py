import os
import socket
import subprocess
import time
from threading import Thread

from environement import default_opc_server, pulling_time_syncro, test_setup, debug

# noinspection DuplicatedCode
synchro = None


def get_text(server_name=default_opc_server):
    return "Text wanted"


def set_synchro(callback, server_name=default_opc_server):
    global synchro
    if synchro is not None:
        synchro.callback = callback
    else:
        synchro = TCP_server(callback)
        synchro.start()
        subprocess.Popen('python ./tests/AutomateSimulator.py')


def kill_synchro():
    global synchro
    # noinspection PyUnresolvedReferences
    synchro.stop()


class TCP_server:

    def __init__(self, callback, host='127.0.0.1', port=65433):
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
                    if debug:
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
