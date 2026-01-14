#! /usr/bin/env python
from getpass import getpass
from netmiko import ConnectHandler


username = input("Enter username:")
password = getpass("Enter password: ")
host = input ("Enter Host ip or dns name: ")

# Device connect parameters
device = {
    'device_type': 'cisco_ios',
    'host': host,
    'username': username,
    'password': password,
    'port': 22,
}

net_connect = ConnectHandler(**device)

print("enable")
output1 = net_connect.send_command_timing("enable")
print(output1)
print("config t")
output2 = net_connect.send_command_timing("configure terminal")
print(output2)
print(" no crypto pki trustpoing DNAC-CA")
output3 = net_connect.send_command_timing("no crypto pki trustpoint DNAC-CA")
print(output3)
print("yes")
output4 = net_connect.send_command_timing("yes")
print(output4)
output5 = net_connect.send_command_timing("end")
print("end")
print(output5)
print (" ")
print ( " DNAC cert has been removed ")
