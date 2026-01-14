#!/usr/bin/env python3

import os
import subprocess

def change_hostname(new_hostname):
    try:
        # Step 1: Temporarily change the hostname
        subprocess.run(['hostnamectl', 'set-hostname', new_hostname], check=True)

        # Step 2: Update /etc/hostname
        with open('/etc/hostname', 'w') as hostname_file:
            hostname_file.write(new_hostname + '\n')

        # Step 3: Update /etc/hosts
        with open('/etc/hosts', 'r') as hosts_file:
            hosts_content = hosts_file.readlines()

        with open('/etc/hosts', 'w') as hosts_file:
            for line in hosts_content:
                if line.startswith('127.0.1.1'):
                    hosts_file.write(f'127.0.1.1    {new_hostname}\n')
                else:
                    hosts_file.write(line)

        print(f"Hostname successfully changed to '{new_hostname}'.")
        print("Please reboot your system to apply the changes.")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except PermissionError:
        print("This script must be run with sudo or as root.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Please run this script with sudo or as root.")
        exit(1)

    new_hostname = input("Enter the new hostname: ")
    change_hostname(new_hostname)
