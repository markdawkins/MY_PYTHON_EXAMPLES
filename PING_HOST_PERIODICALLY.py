import socket
import sys
import os
import time 
import datetime

server_ip = input("Enter server IP:")

while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    rep = os.system( 'ping ' + server_ip)
    if rep == 0: 
	    print('Server is up: {:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()))
    else:
	    print('Server is down: {:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()))
    time.sleep(300)
    print ("   ")
