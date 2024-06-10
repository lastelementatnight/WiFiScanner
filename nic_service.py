#!/usr/bin/env python

import subprocess
import os
from time import sleep

def list_interfaces():
    iwconfig_result = subprocess.run(['iwconfig'], capture_output=True, text=True)
    wireless_interfaces = []
    for l in iwconfig_result.stdout.split("\n"):
        if "IEEE 802.11" in l:
            interface = l.split()[0]
            wireless_interfaces.append(interface)
    
    return wireless_interfaces

def monitor_mode(interface):
    os.system(f"sudo ip link set {interface} down")
    print(f"Interface {interface} down")
    os.system(f"sudo iwconfig {interface} mode monitor")
    print(f"Interface {interface} set monitor mode")
    os.system(f"sudo ip link set {interface} up")
    print(f"Interface {interface} up")

def managed_mode(interface):
    os.system(f"sudo ip link set {interface} down")
    print(f"Interface {interface} down")
    os.system(f"sudo iwconfig {interface} mode managed")
    print(f"Interface {interface} set manged mode")
    os.system(f"sudo ip link set {interface} up")
    print(f"Interface {interface} up")
    
def change_wifi_channel(interface):

    _channel = 1
    
    while True:
<<<<<<< HEAD
        os.system(f"sudo airmon-ng check kill")
        # os.system(f"sudo iwconfig {interface} channel {_channel}")
        command = ["sudo", "iwconfig", f"{interface}", "channel", f"{_channel}"]
        with open("/dev/null", "w") as devnull:
            subprocess.run(command, stdout=devnull, stderr=devnull)
        _channel = _channel % 14+1
        sleep(0.5)
=======
        # os.system("sudo airmon-ng check kill 2 >> /dev/null")
        command = ["sudo", "iwconfig", f"{interface}", "channel", f"{_channel}"]
        with open("/dev/null", "w") as devnull:
            subprocess.run(command, stdout=devnull, stderr=devnull)
        _channel = _channel % 13+1
        sleep(1)
>>>>>>> Save-to-file-
        