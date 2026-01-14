import subprocess
import ipaddress

def ping_ip(ip_address):
    try:
        result = subprocess.run(['ping', '-c', '4', str(ip_address)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr

def main():
    # Get the IP subnet from user input
    subnet_input = input("Enter the IP subnet (e.g., 192.168.1.0/24): ")

    # Validate and create a list of IP addresses in the subnet
    try:
        subnet = ipaddress.ip_network(subnet_input, strict=False)
        ip_addresses = list(subnet.hosts())
    except ValueError as e:
        print(f"Error: Invalid subnet '{subnet_input}'. {e}")
        return

    # Initialize list for IP addresses that do not respond
    not_responding_ips = []

    # Ping each IP address
    for ip_address in ip_addresses:
        print(f"Pinging {ip_address}...")
        response = ping_ip(ip_address)
        print(response)
        print("="*30)

        # Check if the response is empty (no response)
        if "100% packet loss" in response or "Destination Host Unreachable" in response:
            not_responding_ips.append(ip_address)

    # Print IP addresses that did not respond
    if not_responding_ips:
        print("\nIP addresses that did not respond:")
        for not_responding_ip in not_responding_ips:
            print(not_responding_ip)
    else:
        print("\nAll IP addresses responded.")

if __name__ == "__main__":
    main()
