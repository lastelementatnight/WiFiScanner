#!/usr/bin/env python

### Plan ###
# 1. Check permissions (root) ✅
# 2. Check available WLAN NIC ✅
#       2.1 CLIUI for set WLAN NIC  
# 3. Set NIC ✅
# 4. Set NIC in monitor mode ✅
# 5. Start scanning with scapy or pywifi ✅
# 6. Analyze and show results 🔥🔥
# 7. Close program
# 8. Add error handling

import os
import time
import curses
import signal
import pandas as pd
import nic_service as nics
from threading import Thread
from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11ProbeResp, Dot11Elt, sniff

def keyboard_interrupt_handler(interrupt_signal, frame):
    ### Keybord ctrl+c interrupt
    print("Keyboard Interrupt ID: {} {}".format(interrupt_signal, frame))
    exit(1)

def check_permissions():
    if os.geteuid() != 0:
        print("No permissions. Run as root!")
        exit()

wlan_list = pd.DataFrame(columns=["SSID", "channel", "crypto"])
wlan_list.index.name = "BSSID"

def eval_wifi_ap_packets(packet):
    if packet.haslayer(Dot11Beacon) or packet.haslayer(Dot11ProbeResp):
        bssid = packet[Dot11].addr2
        if packet.haslayer(Dot11Elt):
            ssid = packet[Dot11Elt].info.decode().strip()
        else:
            ssid = "SSID - N/A"
        
        # Filter empty packet
        if packet.haslayer(Dot11Beacon):
            net_stats = packet[Dot11Beacon].network_stats()
        elif packet.haslayer(Dot11ProbeResp):
            net_stats = packet[Dot11ProbeResp].network_stats()
        else:
            return

        channel = net_stats.get("channel")
        protocol = net_stats.get("crypto")
        wlan_list.loc[bssid] = (ssid, channel, protocol)

def print_table(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)  # No blocked std screen?
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, wlan_list.to_string())
        stdscr.refresh()
        time.sleep(0.5)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, keyboard_interrupt_handler)
    check_permissions()
    
    wlan_nic = nics.list_interfaces()
    os.system("sudo airmon-ng check kill")
    nics.monitor_mode(wlan_nic[0])
    
    printer_for_table = Thread(target=lambda: curses.wrapper(print_table))
    printer_for_table.daemon = True
    printer_for_table.start()
    
    channel_changer = Thread(target=lambda: nics.change_wifi_channel(wlan_nic[0]))
    channel_changer.daemon = True
    channel_changer.start()
    
    sniff(prn=eval_wifi_ap_packets, iface=wlan_nic[0])
    
    # os.system("sudo systemctl start NetworkManager.service")
    # nics.managed_mode(wlan_nic[0])
