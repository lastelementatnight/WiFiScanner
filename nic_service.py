#!/usr/bin/env python

import subprocess
import os

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