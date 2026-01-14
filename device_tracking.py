#!/usr/bin/env python
from netmiko import ConnectHandler
from getpass import getpass
#from netmiko import NetMikoTimeoutException
#from paramiko.ssh_exception import SSHException
#from netmiko import NetmikoAuthenticationException

username = input("Enter username: ")
password = getpass()
 
with open('/LISTS/REMOTE_DEVICE_TRACKING_1.txt') as f:
    devices_list = f.read().splitlines()

# Device connect parameters

for devices in devices_list:
    print ('Connecting to device ' + str(devices))
    ip_address_of_device = devices
    ios_device = {
        'device_type': 'cisco_ios',
        'ip': ip_address_of_device, 
        'username': username,
        'password': password,
        'port': 22,
    }

    #try:
    net_connect = ConnectHandler(**ios_device)
    #except (AuthenticationException):
    #    print ('Authentication failure: ' + str(ip_address_of_device))
    #    continue
    #except (NetMikoTimeoutException):
    #    print ('Timeout to device: ' + str(ip_address_of_device))
    #    continue
    #except (EOFError):
    #    print ("End of file while attempting device " + str(ip_address_of_device))
    ##    continue
    #except (SSHException):
    #    print ('SSH Issue. Are you sure SSH is enabled ? ' + str(ip_address_of_device))
    #    continue
    #except Exception as unknown_error:
    #    print ('Some other error: ' + str(unknown_error))
    #    continue
    output0 = net_connect.send_command_timing('enable')
    #print (output0)
    output1 = net_connect.send_command_timing('configure terminal ')
    #print (output1) 
    output2 = net_connect.send_command_timing('device-tracking binding stale-lifetime 10 down-lifetime 10')
    #print (output2)
    output3 = net_connect.send_command_timing('end')
    #print (output3)
    #output4 = net_connect.send_command_timing('show run | inc device binding')
    #print (output4)
              
    #print ("Configuration update complete...") 
    net_connect.send_command_timing('end')
