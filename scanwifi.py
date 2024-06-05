#!/usr/bin/env python

### Plan ###
# 1. Check permissions (root) ✅
# 2. Check avaiable WLAN NIC ✅
#       2.1 CLIUI for set WLAN NIC  
# 3. Set NIC
# 4. Set NIC in monitor mode
# 5. Start scanning with scappy or pywifi
# 6. Analize and show results
# 7. Close program
# 8. Add error handling

import signal
import os
import nic_service as nics
import sniffing_service as sniffs
import time
import pandas
from threading import Thread
from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11ProbeResp, Dot11ProbeReq, Dot11Elt, sniff, RadioTap

def keybord_interrupt_handler(interrupt_signal, frame):
    ### Keybord ctrl+c interrupt

    print("Keybord Interrupt ID: {} {}".format(interrupt_signal, frame))
    exit(1)

def check_permissions():
    ### Check permissions (root)

    if os.geteuid() != 0:
        print("No permissions. Run as root!")
        exit()

wlan_list = pandas.DataFrame(columns=["BSSID", "SSID", "channel", "crypto"])
wlan_list.set_index("BSSID", inplace=True)

def eval_wifi_ap_packets(packet):
    if packet.haslayer(Dot11Beacon) or packet.haslayer(Dot11ProbeResp):
        if packet.type == 0 and packet.subtype == 8:
            bssid = packet[Dot11].addr2
            ssid = packet[Dot11Elt].info.decode().strip()
            net_stats = packet[Dot11Beacon].network_stats()
            channel = net_stats.get("channel")
            protocol = net_stats.get("crypto")
        
            wlan_list.loc[bssid] = (ssid, channel, protocol)

def print_tabel():
    r = 0
    while True:

        os.system("clear")
        print(wlan_list)
        time.sleep(0.5)


def run_app():
    ### this run app
    return None
    

if __name__ == "__main__":
    signal.signal(signal.SIGINT, keybord_interrupt_handler)
    check_permissions()
    
    wlan_nic = nics.list_interfaces()
    os.system(f"sudo airmon-ng check kill")
    nics.monitor_mode(wlan_nic[0])
    
    printer_for_tabel = Thread(target=print_tabel)
    printer_for_tabel.daemon = True
    printer_for_tabel.start()
    
    channel_changer = Thread(target=lambda: nics.change_wifi_channel(wlan_nic[0]))
    channel_changer.daemon = True
    channel_changer.start()
    
    sniff(prn=eval_wifi_ap_packets, iface=wlan_nic[0])
    
    # os.system(f"sudo systemctl start NetworkManager.service")
    # nics.managed_mode(wlan_nic[0])