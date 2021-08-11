"""
File setting up global variables for the system, describe the running condition
"""

debug = True  # if true more printouts in the code
test_setup = False  # if true indicates we are in a test setup and call the simulators for external hardware or software
save_to_db = True  # if true the images are saved to the database and local file system, if false they aren't
image_path = "./img/"  # path from current folder where images are stored


pulling_time_syncro = 0.100  # time between read of the synchronisation value
display_fps = 24  # number of framed pulled per second


# set the correct opc server in test
if not test_setup:
    default_opc_server = "OPC.SimaticHMI.CoRtHmiRTm"
else:
    default_opc_server = 'Matrikon.OPC.Simulation'
