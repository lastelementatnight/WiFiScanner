#!/usr/bin/env python

from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11ProbeResp, Dot11ProbeReq, Dot11Elt, sniff, RadioTap

def eval_wifi_ap_packets(packet):
    if packet.haslayer(Dot11Beacon) or packet.haslayer(Dot11ProbeResp):
        if packet.type == 0 and packet.subtype == 8:
            print("Start sniffing...")
            bssid = packet[Dot11].addr2
            ssid = packet[Dot11Elt].info.decode().strip()
            net_stats = packet[Dot11Beacon].network_stats()
            channel = net_stats.get("channel")
            protocol = net_stats.get("crypto")
            enco = next(iter(protocol))
            
            print(bssid, ssid, channel, enco)