from Capture import Opc_Client
from Capture.Opc_Client import OpcClient, address_text,address_trigger, set_synchro, get_text, kill_synchro, get_repetions
from environement import default_opc_server, test_setup
import OpenOPC
import time 

def callback():
    print("Taking picture now")

if __name__ == '__main__':
    print("Trying to connect to server " + default_opc_server)
    print("\n ====================================\n")
    try:
        address_text = "." + address_text

        if test_setup:
            address_text = "." + address_text
            address_trigger = "." + address_trigger

        with OpcClient(default_opc_server) as opc:
            opc.opc[address_text] = 'test42'

        set_synchro(callback)

        for i in range(20):
            time.sleep(1)
            string = get_text()
            print('Reading the text', string)
            print('repeats:', get_repetions())

        kill_synchro()
        print("end test")
    except OpenOPC.OPCError as e:
        print('Error', e)

    input('press enter key to exit..')
