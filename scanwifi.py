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

def keybord_interrupt_handler(interrupt_signal, frame):
    ### Keybord ctrl+c interrupt

    print("Keybord Interrupt ID: {} {}".format(interrupt_signal, frame))
    exit(1)

def check_permissions():
    ### Check permissions (root)

    if os.geteuid() != 0:
        print("No permissions. Run as root!")
        exit()

def run_app():
    ### this run app

    check_permissions()

    wlan_nic = nics.list_interfaces()

    for nic in wlan_nic:
        print(nic)

    nics.managed_mode(wlan_nic[0])

if __name__ == "__main__":
    signal.signal(signal.SIGINT, keybord_interrupt_handler)
    run_app()