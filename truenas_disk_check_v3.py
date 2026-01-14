####
#script to specifically filter the disk utilization output for only the Pool1/emby and Pool2/emby2 mount points. This can be changed later. 
#!/usr/bin/env python3
import paramiko
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import socket
import os

# Configuration
TRUENAS_SERVERS = [
    {'ip': '192.168.1.229', 'username': 'your_username', 'password': 'your_password'},
    {'ip': '192.168.1.239', 'username': 'your_username', 'password': 'your_password'}
]
LOG_FILE = '/path/to/your/truenas_disk_utilization.csv'
EMAIL_FROM = 'your_nagios_email@example.com'
EMAIL_TO = 'your_email@example.com'
EMAIL_SUBJECT = 'TrueNAS Disk Utilization Report'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'your_smtp_username'
SMTP_PASSWORD = 'your_smtp_password'

# Mount points to monitor
MONITOR_MOUNTS = ['Pool1/emby', 'Pool2/emby2']

def check_disk_utilization(server):
    """Connect to TrueNAS server and check specific disk utilization"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server['ip'], username=server['username'], password=server['password'])
        
        # Run df command to get disk usage
        stdin, stdout, stderr = ssh.exec_command('df -h')
        df_output = stdout.read().decode().strip()
        
        ssh.close()
        
        # Filter output for specific mounts
        filtered_output = []
        lines = df_output.split('\n')
        header = lines[0]  # Get the header line
        
        for line in lines[1:]:
            for mount in MONITOR_MOUNTS:
                if mount in line:
                    filtered_output.append(line)
                    break
        
        if filtered_output:
            final_output = header + '\n' + '\n'.join(filtered_output)
        else:
            final_output = f"No monitored mounts found in df output\nSearched for: {', '.join(MONITOR_MOUNTS)}"
        
        return {
            'ip': server['ip'],
            'status': 'success',
            'output': final_output,
            'error': None
        }
    except Exception as e:
        return {
            'ip': server['ip'],
            'status': 'error',
            'output': None,
            'error': str(e)
        }

def log_to_csv(results):
    """Log results to CSV file"""
    file_exists = os.path.isfile(LOG_FILE)
    
    with open(LOG_FILE, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'server_ip', 'status', 'output', 'error']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for result in results:
            writer.writerow({
                'timestamp': datetime.now().isoformat(),
                'server_ip': result['ip'],
                'status': result['status'],
                'output': result['output'],
                'error': result['error']
            })

def send_email(results):
    """Send email with disk utilization results"""
    try:
        # Create email content
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = EMAIL_SUBJECT
        
        # Build email body
        body = "TrueNAS Disk Utilization Report (Filtered)\n\n"
        body += f"Monitored mounts: {', '.join(MONITOR_MOUNTS)}\n"
        body += f"Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for result in results:
            body += f"=== Server: {result['ip']} ===\n"
            body += f"Status: {result['status']}\n"
            
            if result['status'] == 'success':
                body += f"Disk Utilization:\n{result['output']}\n\n"
            else:
                body += f"Error: {result['error']}\n\n"
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable TLS
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

def main():
    results = []
    
    for server in TRUENAS_SERVERS:
        print(f"Checking disk utilization on {server['ip']}...")
        result = check_disk_utilization(server)
        results.append(result)
        
        if result['status'] == 'success':
            print(f"Successfully retrieved disk info from {server['ip']}")
            print(result['output'])  # Print the filtered output
        else:
            print(f"Error connecting to {server['ip']}: {result['error']}")
    
    # Log results to CSV
    log_to_csv(results)
    
    # Send email with results
    send_email(results)

if __name__ == '__main__':
    main()
