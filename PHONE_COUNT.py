#!/usr/bin/env python
import time
from netmiko import ConnectHandler
from getpass import getpass
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException
from datetime import datetime

username = input("Enter username: ")
password = getpass('Enter SSH password: ')

subname = datetime.now().strftime("%Y%m%d-%H%M%S")
LIST = input("Enter Floor:")
#REPORT = input("Enter Report Name:") Use if you want the option to create a on3 off report name
reportname = "/REPORTS/phone_count/count-" + subname + ".txt"
listname = "/LISTS/%s.txt" % LIST

print ("Writing output to REPORTS directory...")
time.sleep(3)

file = open(reportname , 'w')

f = open (listname)

for line in f:
    host = line.strip()
    iosv_l2 = {
             'device_type':'cisco_ios',
             'ip':host,
             'username':username,
             'password':password,
           }
    try:
	    net_connect = ConnectHandler(**iosv_l2)
    except (AuthenticationException):
        print ('Authentication failure: ' + HOST)
        continue
    except (NetMikoTimeoutException):
        print ('Timeout to device: ' + HOST)
        file.write('Timeout to device: ' + HOST)
        continue
    except (EOFError):
        print ('End of file while attempting device ' + HOST)
        continue
    except (SSHException):
        print ('SSH Issue. Are you sure SSH is enabled? ' + HOST)
        continue
    except Exception as unknown_error:
        print ('Some other error: ' + str(unknown_error) )
        continue
    net_connect = ConnectHandler(**iosv_l2)
    output0 = net_connect.send_command('show run | inc hostname')
    print (host + "\n")
    file.write(host + "\n")
    file.write( "\n")
    print (output0[9:32])
    file.write( "\n")
    file.write (output0[9:32])
    file.write( "\n")
    file.write(" ")
    file.write(" ")
    file.write( "\n")    
    net_connect = ConnectHandler(**iosv_l2)
    output1 = net_connect.send_command('show cdp nei | count SEP ')
    print ('PHONE COUNT' + output1[35:45])
    file.write( "\n")
    file.write ('PHONE COUNT' + output1[35:45])
    file.write( "\n")
    file.write(" ")
    file.write(" ")
    file.write( "\n")
    output2 = net_connect.send_command('show ver | inc uptime')
    print (output2)
    file.write( "\n")
    file.write (output2)
    file.write(" \n")
    file.write(" ")
    file.write(" \n")
    
file.close()

print ("Report saved to Reports directory...")
time.sleep(1)
