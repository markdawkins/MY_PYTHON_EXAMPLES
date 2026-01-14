#!/usr/bin/env python
from netmiko import ConnectHandler
from getpass import getpass

sitename = input("Enter switch hostname or IP : ")
ha = input("Enter complete or partial mac address: ")
username = input("Enter username: ")
password = getpass()
#FOR LOOP TO CHECK BOTH SWITCH 1 AN SWITCH 2
for a in range (1,3):
	HOST = (sitename + "-"+ str(a) + ".mycompany.com")

	iosv_l2 = {
		'device_type': 'cisco_ios',
		'ip':(HOST),
		'username': username,
		'password':password,
	}
#COMMANDS THAT YOU ARE RUNNING AGAINST THE SWITCH ha is the input entered for mac address
	net_connect = ConnectHandler(**iosv_l2)
	output0 = net_connect.send_command('show run  | include hostname')
	output1 = net_connect.send_command('show interfaces status | i notconnect')
	output2 = net_connect.send_command('show mac address-table | inc ' + ha)
	output3 = net_connect.send_command('show log | inc ' + ha) 
	print (' \n')
	print (' \n')
	print (output0[9:20]) 
	print (' \n')
	print (output1) 
	print (' \n')
	print (output2)      
	print (' \n')
	print (output3)
    #net_connect.send_command('end\n')
