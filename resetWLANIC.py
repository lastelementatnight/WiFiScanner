import os

def reset():
    os.system("sudo ip link set wlp3s0 down")
    os.system("sudo iw dev wlp3s0 set type managed")
    os.system("sudo ip link set wlp3s0 up")
    os.system("sudo systemctl restart NetworkManager.service")

reset()
