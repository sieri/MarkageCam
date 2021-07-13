debug = True
test_setup = True
image_path = "./img/"
save_to_db = True

if not test_setup:
    default_opc_server = "OPC.SimaticHMI.CoRtHmiRTm"
else:
    default_opc_server = 'Matrikon.OPC.Simulation'

pulling_time_syncro = 0.100
