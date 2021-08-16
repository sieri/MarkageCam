# used library only work with 32 bits interpreters raise error if not the case
import struct


n_bit = struct.calcsize("P") * 8
if n_bit == 64:
    raise NotImplementedError

import time
from threading import Thread
import OpenOPC
# noinspection PyUnresolvedReferences
import win32timezone  # import purely for pyinstaller

from environement import default_opc_server, pulling_time_syncro, test_setup

synchro = None

address_text = 'R_EBS_Texte'
address_x_repeats = 'R_EBS_Repetition'
address_y_repeats = 'R_EBS_Nbr_Ligne'
address_trigger = 'M_Trigger_Camera'


def get_text(server_name=default_opc_server):
    with OpcClient(server_name) as opc:
        return opc.opc[address_text]


def set_synchro(callback, server_name=default_opc_server):
    global synchro
    if synchro is not None:
        synchro.callback = callback
    else:
        synchro = Synchro(callback, server_name)
        synchro.start()


def get_repetions(server_name=default_opc_server):
    with OpcClient(server_name) as opc:
        return (opc.opc[address_x_repeats], opc.opc[address_y_repeats])

def kill_synchro():
    global synchro
    # noinspection PyUnresolvedReferences
    synchro.stop()


class Synchro:
    def __init__(self, callback, server_name):
        self.callback = callback
        self.running = False
        self.server_name = server_name
        self.thread = Thread(target=self.run, args=())
        self.thread.setName("synchro thread for capture")

    def start(self):
        self.running = True
        self.thread.start()
        return self

    def stop(self):
        self.running = False

    def run(self):
        trigger = False
        with OpcClient(self.server_name) as opc:
            while self.running:
                if opc.opc[address_trigger]:
                    if not trigger:
                        self.callback()
                        trigger = True
                        print(opc.opc[address_text])
                elif trigger:
                    trigger = False

                time.sleep(pulling_time_syncro)


class OpcClient:
    def __init__(self, server_name=default_opc_server):
        self.opc = OpenOPC.client()
        self.server_name = server_name

    def __enter__(self):
        self.opc.connect(self.server_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.opc.close()



