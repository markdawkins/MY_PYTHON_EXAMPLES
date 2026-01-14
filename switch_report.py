from netmiko import ConnectHandler
import time
from getpass import getpass
from datetime import datetime
subname = datetime.now().strftime("%Y%m%d-%H%M%S")
logdate = datetime.now().strftime("%b")

host = input("Enter Host/IP: ")
commands = ['term length 0', 'show int status | inc connected' , 'show int status | count  connected' , 'show mac address-table  | inc DYNAMIC'
,'show mac address-table  | count DYNAMIC' , 'show cdp nei | inc AP|ap' , 'show ip int brie | exc unassigned'  ,'show inventory' , 'show ver | inc Version' , 'show run' , 'show log | inc ' + logdate ]

outputFileName = host +'_'+ subname +'_output.txt'

user_name = input("Enter username:")
password = getpass("Enter password: ")
iosv_l2 = {
             'device_type':'cisco_ios',
             'host':host,
             'username':user_name,
             'password':password,
             
}

net_connect = ConnectHandler(**iosv_l2)
with open("/Users/014mdawkins/Documents/SWITCH_REPORTS/"+  outputFileName, 'w') as f:
    for command in commands:
                net_connect.send_command(command)
                output = net_connect.send_command(command)
                f.write("\n")
                f.write("\n")
                f.write("\n")
                f.write(output)
             
net_connect.send_command('end\n')
time.sleep(2)
