### This quick script pings 3 IPS by default ang logs the results####
import subprocess
import platform
from datetime import datetime

# Get input for up to 3 devices
hosts = []
for i in range(3):
    host = input(f"Enter IP or hostname #{i+1} (or press Enter to skip): ").strip()
    if host:
        hosts.append(host)

# Ping each host and log results
with open("PING_LOG.txt", "a") as log_file:
    for host in hosts:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", host]
        
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=5)
            status = "SUCCESS" if result.returncode == 0 else "FAILED"
        except subprocess.TimeoutExpired:
            status = "TIMEOUT"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output = f"[{timestamp}] {host}: {status}"
        
        print(output)
        log_file.write(output + "\n")
