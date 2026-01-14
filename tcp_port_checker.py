import socket
import csv
import os
import time

def check_tcp_connection(host, port, timeout=3):
    """Attempts to connect to the specified host and port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return "Connected"
        except (socket.timeout, socket.error):
            return "Not Connected"

def main():
    # Get user input
    port = int(input("Enter the TCP port to check: "))
    filename = input("Enter the filename containing IPs/hostnames: ")
    file_path = f"C://lists/{filename}"
    
    # Validate file existence
    if not os.path.isfile(file_path):
        print("Error: File not found.")
        return
    
    # Output CSV file with timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"C://reports/connection_results_{timestamp}.csv"
    
    with open(file_path, "r") as infile, open(output_file, "w", newline="") as outfile:
        reader = infile.readlines()
        writer = csv.writer(outfile)
        writer.writerow(["Host", "Port", "Status"])
        
        for line in reader:
            host = line.strip()
            if host:
                status = check_tcp_connection(host, port)
                writer.writerow([host, port, status])
                print(f"{host}: {status}")
    
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()
