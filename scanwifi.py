#!/usr/bin/env python

import os
import sys
import time
import curses
import signal
import pandas as pd
import nic_service as nics
from threading import Thread
from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11ProbeResp, Dot11Elt, Dot11AssoReq, Dot11AssoResp, Dot11ProbeReq, sniff

def keyboard_interrupt_handler(interrupt_signal, frame):
    ### Keyboard ctrl+c interrupt
    print("Keyboard Interrupt ID: {} {}".format(interrupt_signal, frame))
    curses.endwin()  # Restore terminal settings
    save_results()  # Save results before exiting
    exit(1)

def check_permissions():
    if os.geteuid() != 0:
        print("No permissions. Run as root!")
        exit()

wlan_list = pd.DataFrame(columns=["SSID", "channel", "crypto", "clients"])
wlan_list.index.name = "BSSID"

clients_list = {}
network_list = []

class NetworkItem:
    def __init__(self, bssid, ssid, channel, crypto):
        self._bssid = bssid
        self._ssid = ssid
        self._channel = channel
        self._crypto = crypto

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

        net_item = NetworkItem(bssid, ssid, channel, protocol)
        network_list.append(net_item)

    # Number of client in access Point
    elif packet.haslayer(Dot11AssoReq) or packet.haslayer(Dot11AssoResp) or packet.haslayer(Dot11ProbeReq):
        client_mac = packet[Dot11].addr2
        ap_mac = packet[Dot11].addr1

        if ap_mac in clients_list:
            clients_list[ap_mac].add(client_mac)
        else:
            clients_list[ap_mac] = {client_mac}

            if ap_mac in wlan_list.index:
                wlan_list.at[ap_mac, 'clients'] = len(clients_list[ap_mac])

def print_table(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    stdscr.bkgd(' ', curses.color_pair(1))
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, wlan_list.to_string())
        stdscr.refresh()
        time.sleep(0.5)

def save_results():
    # Save results to a text file
    with open("network_results.txt", "w") as file:
        file.write(wlan_list.to_string())

if __name__ == "__main__":
    signal.signal(signal.SIGINT, keyboard_interrupt_handler)
    check_permissions()

    wlan_nic = nics.list_interfaces()
    # os.system("sudo airmon-ng check kill 2 >> /dev/null")
    # nics.monitor_mode(wlan_nic[0])
    # os.system("sudo airmon-ng start wlp3s 2 >> /dev/null")

    try:
        printer_for_table = Thread(target=curses.wrapper, args=(print_table,))
        printer_for_table.daemon = True
        printer_for_table.start()

        print("WLAN Network Scanning...")
        os.system("clear")
        sys.stdout.write("\033[0?0f")
        sys.stdout.flush()

        channel_changer = Thread(target=lambda: nics.change_wifi_channel(wlan_nic[0]))
        channel_changer.daemon = True
        channel_changer.start()

        sniff(prn=eval_wifi_ap_packets, iface=wlan_nic[0])
    finally:
        curses.endwin()  # Ensure terminal settings are restored on exit
        save_results()  # Save results before exiting

    print("Results saved to 'network_results.txt'")
