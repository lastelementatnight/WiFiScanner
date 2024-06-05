import os

def setWLAN():
    os.system(f"sudo airmon-ng check kill")
    os.system("sudo ip link set wlp3s0 down")
    os.system("sudo iw dev wlp3s0 set type monitor")
    os.system("sudo ip link set wlp3s0 up")

setWLAN()
