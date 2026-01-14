from netmiko import ConnectHandler

IP = raw_input("Enter device IP: ")
user_name = raw_input("Enter username: ")
passwd = raw_input("Enter password: ")
device_name = raw_input("Enter device name: ")
enable_pass = raw_input("Enter enable password: ")
#HOST = device_name + '.dcom.testsite.com'
HOST = IP 

iosv_l2 = {
    'device_type': 'cisco_ios',
    'ip':(HOST),
    'username':(user_name),
    'password':(passwd),
}


net_connect = ConnectHandler(**iosv_l2)
#net_connect.find_prompt()
output = net_connect.enable
output = net_connect.send_command(enable_pass)
output = net_connect.send_command('show run')

readoutput = (output)	
saveoutput = open("/home/mark/CONFIGS/" + device_name , "w")
saveoutput.write(readoutput)
saveoutput.close
     
net_connect.send_command('end\n')
