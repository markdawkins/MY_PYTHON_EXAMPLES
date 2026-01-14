#!/usr/bin/env python
import socket
import sys
import os
import time
from datetime import datetime
subname = datetime.now().strftime("%Y%m%d-%H%M%S")
filename = "/REPORTS/PING_REPORT"+ subname + ".csv"

file = open(filename , 'w')

LIST = input("Enter List Name:")

listname = "/LISTS/%s.txt"  % LIST

f = open (listname)

import datetime
for line in f:
    host = line 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    rep = os.system( 'ping ' + host)
    if rep == 0: 
	    output=('Server is up: {:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()))
	    
    else:
	    output=('Server is down: {:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()))
	    
    time.sleep(2)
    print ("   ")
    print (host)
    file.write(host)
    file.write(output + '\n')
    print ("   ")
    print ("   ")
    print (output)
