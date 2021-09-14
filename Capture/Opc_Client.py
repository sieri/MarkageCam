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
address_x_repeats = 'R_EBS_Rep'
address_y_repeats = 'R_EBS_Nbr_Ligne'
address_trigger = 'M_Trigger_Camera'


def get_text(server_name=default_opc_server):
    with OpcClient(server_name) as opc:
        return opc.opc.read(address_text, source='device')[0]


def set_synchro(callback, server_name=default_opc_server):
    global synchro
    if synchro is not None:
        synchro._callback = callback
    else:
        synchro = Synchro(callback, server_name)
        synchro.start()


def get_repetions(server_name=default_opc_server):
    with OpcClient(server_name) as opc:
        return opc.opc.read(address_x_repeats, source='device')[0], opc.opc.read(address_y_repeats, source='device')[0]

def kill_synchro():
    global synchro
    # noinspection PyUnresolvedReferences
    synchro.stop()


class Synchro:
    _callback : function
    _running : bool
    _server_name : str
    _thread : Thread

    def __init__(self, callback:function, server_name: str):
        self._callback = callback
        self._running = False
        self._server_name = server_name
        self._thread = Thread(target=self.run, args=())
        self._thread.setName("synchro thread for capture")

    def start(self):
        self._running = True
        self._thread.start()
        return self

    def stop(self):
        self._running = False

    def run(self):
        trigger = False
        with OpcClient(self._server_name) as opc:
            while self._running:
                if read(address_trigger, source='device')[0]:
                    if not trigger:
                        self._callback()
                        trigger = True
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



