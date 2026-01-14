from netmiko import ConnectHandler
from getpass import getpass
subname = datetime.now().strftime("%Y%m%d-%H%M%S")
print(subname)
host = input("Enter Host/IP: ")
#search_term = input("Enter search term:")

user_name = input("Enter username:")
password = getpass("Enter password: ")
iosv_l2 = {
             'device_type':'cisco_ios',
             'host':host,
             'username':user_name,
             'password':password,
             
}
net_connect = ConnectHandler(**iosv_l2)

output = net_connect.send_command('show log ')
print (output)
net_connect.send_command('end\n')
