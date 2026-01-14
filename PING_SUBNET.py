import subprocess
import ipaddress

def ping_subnet(subnet):
    try:
        # Create an IPv4 network object from the given subnet
        network = ipaddress.IPv4Network(subnet, strict=False)

        # Iterate over all hosts in the subnet and ping each one
        for host in network.hosts():
            host = str(host)
            # Run the ping command and capture the output
            result = subprocess.run(['ping', '-c', '1', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Check the return code to see if the ping was successful
            if result.returncode == 0:
                print(f"{host} is reachable.")
            else:
                print(f"{host} is unreachable.")
    except ipaddress.AddressValueError as e:
        print(f"Error: {e}")

# Prompt the user for a subnet
subnet = input("Enter the subnet (e.g., 192.168.1.0/24): ")

# Call the ping_subnet function with the user-provided subnet
ping_subnet(subnet)
