import OpenOPC

opc = OpenOPC.client()
opc.connect('Matrikon.OPC.Simulation')
print(opc['Square Waves.Real8'])
opc.close()