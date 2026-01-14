import os

# Get the directory of the current script
#base_dir = os.path.dirname(os.path.abspath(__file__))
base_dir_list = "/home/mark/lists/"
base_dir_outputs = "/home/mark/lists"

# Prompt the user to enter the file name for the IP addresses and the output file name
ip_file_name = input("Enter the name of the file containing the IP addresses: ")
output_file_name = input("Enter the name of the output file: ")

# Construct the full file paths
ip_file_path = os.path.join(base_dir_list, ip_file_name)
output_file_path = os.path.join(base_dir_outputs, output_file_name)

# Read IP addresses from the file
try:
    with open(ip_file_path, 'r') as file:
        ip_addresses = file.readlines()
except FileNotFoundError:
    print(f"File not found: {ip_file_path}")
    exit(1)

# Strip whitespace characters like `\n` at the end of each line
ip_addresses = [ip.strip() for ip in ip_addresses]

# Ping each IP address and write the results to the output file
with open(output_file_path, 'w') as output_file:
    for ip in ip_addresses:
        response = os.system(f"ping -c 1 {ip}")  # Use -n 1 for Windows
        if response != 0:
            result = f"{ip} is down!\n"
            print(result.strip())  # Print to console
            output_file.write(result)  # Write to the output file

print(f"Results have been written to {output_file_path}")
