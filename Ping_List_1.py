import os
import subprocess

# Function to ping a host and check if it's reachable
def ping_host(host):
    """Pings a host and returns True if reachable, False otherwise."""
    try:
        # Run the ping command and capture output
        result = subprocess.run(["ping", "-n", "1", host], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error pinging {host}: {e}")
        return False

# Main function to read the list file and ping each host
def main():
    directory = r"C:\Users\mark\Desktop\Code\Python\lists"
    
    # Prompt user for the list file name
    file_name = input("Enter the name of the list file: ")
    file_path = os.path.join(directory, file_name)
    
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: The file {file_path} does not exist.")
        return
    
    # Read the file and extract hostnames/IPs
    with open(file_path, "r") as file:
        hosts = [line.strip() for line in file if line.strip()]
    
    # Check if the list is empty
    if not hosts:
        print("Error: The list is empty.")
        return
    
    # Ping each host and print the status
    for host in hosts:
        status = "Reachable" if ping_host(host) else "Unreachable"
        print(f"{host}: {status}")

# Run the script only if it's executed directly
if __name__ == "__main__":
    main()
