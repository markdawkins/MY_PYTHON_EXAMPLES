import subprocess

def modify_netplan_config(interface, ip_address, netmask, gateway):
    netplan_config = f"""
network:
  version: 2
  renderer: networkd
  ethernets:
    {interface}:
      dhcp4: no
      addresses:
        - {ip_address}/{netmask}
      gateway4: {gateway}
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
    """

    # Write the netplan configuration to the appropriate file
    netplan_file = f"/etc/netplan/01-{interface}-static.yaml"
    with open(netplan_file, 'w') as file:
        file.write(netplan_config)
    
    # Apply the netplan configuration
    subprocess.run(['sudo', 'netplan', 'apply'], check=True)
    
    print(f"Netplan configuration for {interface} has been updated with static IP {ip_address}/{netmask}.")
    print(f"Default gateway set to {gateway}. Configuration is now persistent across reboots.")

if __name__ == "__main__":
    interface = input("Enter the network interface (e.g., eth0, enp0s3, wlan0): ")
    ip_address = input("Enter the IP address (e.g., 192.168.1.122): ")
    netmask = input("Enter the netmask (e.g., 24): ")
    gateway = input("Enter the default gateway (e.g., 192.168.1.1): ")
    
    modify_netplan_config(interface, ip_address, netmask, gateway)
