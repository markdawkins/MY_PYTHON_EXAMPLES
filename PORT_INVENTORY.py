#!/usr/bin/env python
import time
from datetime import datetime
from getpass import getpass
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException

username = input('Enter your SSH username: ')
password = getpass()


subname = datetime.now().strftime("%Y%m%d-%H%M%S")

filename = "/PORT_INVENTORY" + subname + ".csv" 

print ("Writing output to directory...")
time.sleep(1)

file = open(filename , 'w')


with open('devices_file.txt') as f:
    devices_list = f.read().splitlines()

for devices in devices_list:
    print ('Connecting to device" ' + devices)
    ip_address_of_device = devices
    ios_device = {
        'device_type': 'cisco_ios',
        'ip': ip_address_of_device, 
        'username': username,
        'password': password
    }

    try:
        net_connect = ConnectHandler(**ios_device)
    except (AuthenticationException):
        print ('Authentication failure: ' + ip_address_of_device)
        continue
    except (NetMikoTimeoutException):
        print ('Timeout to device: ' + ip_address_of_device )
        continue
    except (EOFError):
        print ("End of file while attempting device " + ip_address_of_device)
        continue
    except (SSHException):
        print ('SSH Issue. Are you sure SSH is enabled? ' + ip_address_of_device)
        continue
    except Exception as unknown_error:
        print ('Some other error: ' + str(unknown_error))
        continue

    
    output1 = net_connect.send_command('show run | inc hostname')
    output2 = net_connect.send_command('show int status | count notconnect')
    output3 = net_connect.send_command('show int status | inc notconnect')
    print (output1)
    print (" ")
    print (output2)
    print (" ")
    print (output3)
    print (" ")
    file.write(output1)
    file.write(' \n')
    file.write(' \n')
    file.write(output2)
    file.write(' \n')
    file.write(' \n')
    file.write(output3)
    file.write(' \n')
    file.write(' \n')
    #file.write(output4)
    #file.write(' \n')
    #file.write(' \n')
    net_connect.send_command('end\n')
    print ("Report saved to Reports directory...")
