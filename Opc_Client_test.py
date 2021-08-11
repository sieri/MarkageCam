from Capture import Opc_Client
from Capture.Opc_Client import OpcClient, address_text,address_trigger
from environement import default_opc_server, test_setup
import OpenOPC

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
            with OpcClient('Matrikon.OPC.Simulation') as opc:
                opc.opc[address_text] = 'test'

        set_synchro(callback)

        for i in range(60):
            time.sleep(1)
            string = get_text()
            print('Reading the text', string)

        kill_synchro()
        print("end test")
    except OpenOPC.OPCError as e:
        print('Error', e)

    input('press enter key to exit..')
