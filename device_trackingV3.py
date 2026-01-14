#!/usr/bin/env python
from getpass import getpass
import time
from netmiko import ConnectHandler

username = input("Enter username: ")
password = getpass()

listname = "./LISTS/proxmox_routers.txt"

f = open (listname)

for line in f:
    host = line.strip()
    iosv_l2 = {
             'device_type':'cisco_ios',
             'ip':host,
             'username': username,
             'password': password,
           }

    net_connect = ConnectHandler(**iosv_l2)
    net_connect.send_command_timing('conf t\n')
        
    net_connect.send_command_timing(' no ntp server 132.163.96.5 source GigabitEthernet 1 prefer\n')
        
    net_connect.send_command_timing('end\n')
    net_connect.send_command_timing('wr mem\n')
    time.sleep(3)
    output0 = net_connect.send_command_timing('show run | inc hostname\n')
    time.sleep(5)
    print(" ")
    print("The device tracking configuration has been updated for device " + output0[8:20] + " " + host )
    print (" ")

print ("Update completed for all devices...")
time.sleep(1)
