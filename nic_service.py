#!/usr/bin/env python

import subprocess

def list_interfaces():
    iwconfig_result = subprocess.run(['iwconfig'], capture_output=True, text=True)
    wireless_interfaces = []
    for l in iwconfig_result.stdout.split("\n"):
        if "IEEE 802.11" in l:
            interface = l.split()[0]
            wireless_interfaces.append(interface)
    
    return interface

def monitor_mode(interface):
    return None

def managed_mode(interface):
    return None