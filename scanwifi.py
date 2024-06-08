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
from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11ProbeResp, Dot11Elt, Dot11AssoReq, Dot11AssoResp,Dot11ProbeReq, sniff

def keyboard_interrupt_handler(interrupt_signal, frame):
    ### Keybord ctrl+c interrupt
    print("Keyboard Interrupt ID: {} {}".format(interrupt_signal, frame))
    exit(1)

def check_permissions():
    if os.geteuid() != 0:
        print("No permissions. Run as root!")
        exit()

wlan_list = pd.DataFrame(columns=["SSID", "channel", "crypto", "clients"])
wlan_list.index.name = "BSSID"

clients_list = {}
network_list = []

class network_item:
    _bssid = None
    _ssid = None
    _channel = None
    _crypto = None

def eval_wifi_ap_packets(packet):
        if packet.haslayer(Dot11Beacon) or packet.haslayer(Dot11ProbeResp):
            bssid = packet[Dot11].addr2
            if packet.haslayer(Dot11Elt):
                ssid = packet[Dot11Elt].info.decode().strip()
            # Filter empty packet
            if packet.haslayer(Dot11Beacon):
                net_stats = packet[Dot11Beacon].network_stats()
            elif packet.haslayer(Dot11ProbeResp):
                net_stats = packet[Dot11ProbeResp].network_stats()
            else:
                return

            channel = net_stats.get("channel")
            protocol = net_stats.get("crypto")
            wlan_list.loc[bssid] = (ssid, channel, protocol, clients_list.get(bssid, 0))
            
            net_item = network_item()
            net_item._bssid = bssid
            net_item._ssid = ssid
            net_item._channel = channel
            net_item._crypto = protocol
            network_list.append(net_item)
        
        # Number of client in access Point
        elif packet.haslayer(Dot11AssoReq) or packet.haslayer(Dot11AssoResp) or packet.haslayer  (Dot11ProbeReq):
            client_mac = packet[Dot11].addr2
            ap_mac = packet[Dot11].addr1
                
            if ap_mac in clients_list:
                clients_list[ap_mac].add(client_mac)
            else:
                clients_list[ap_mac] = {client_mac}    
                
                if ap_mac in wlan_list.index:
                    wlan_list.at[ap_mac, 'clients'] = len(clients_list[ap_mac])

def print_table():
    while True:
        os.system("clear")
        print(wlan_list.to_string())
        time.sleep(0.8)
        
if __name__ == "__main__":
    signal.signal(signal.SIGINT, keyboard_interrupt_handler)
    check_permissions()
    
    wlan_nic = nics.list_interfaces()
    # os.system("sudo airmon-ng check kill 2 >> /dev/null")
    # nics.monitor_mode(wlan_nic[0])
    # os.system("sudo airmon-ng start wlp3s 2 >> /dev/null")
    
    # printer_for_table = Thread(target=print_table)
    # printer_for_table.daemon = True
    # printer_for_table.start()
    
    print("WLAN Network Scanning...")
    
    channel_changer = Thread(target=lambda: nics.change_wifi_channel(wlan_nic[0]))
    channel_changer.daemon = True
    channel_changer.start()
    
    sniff(prn=eval_wifi_ap_packets, iface=wlan_nic[0], count=100)
    
    i = 0
    for x in network_list:
        print(network_list[i]._ssid)
        i+=1
    
    
    # os.system("sudo systemctl start NetworkManager.service")
    # nics.managed_mode(wlan_nic[0])
