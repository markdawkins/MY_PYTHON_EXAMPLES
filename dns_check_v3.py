"""
DNS Resolution Check Script

This script performs DNS resolution checks for a list of hostnames against two nameservers (ns1 and ns9).
It reads hostnames from an Excel file and writes the results to separate CSV files for each nameserver.

All file paths are relative to the directory where the script is running from.

Features:
- Reads hostnames from Excel file (first column)
- Performs DNS A record lookups against specified nameservers
- Handles various DNS resolution errors gracefully
- Writes results to CSV files with timestamps
- Shows real-time progress during execution

Requirements:
- Python 3.6+
- Packages: dnspython, openpyxl (install with: pip install dnspython openpyxl)
"""

import dns.resolver  # For DNS resolution
import openpyxl      # For reading Excel files
import csv           # For writing CSV files
from datetime import datetime  # For timestamping results
import sys           # For system exit and stderr
import os            # For path handling

def resolve_hostname(hostname, nameserver):
    """
    Resolve a hostname to its IP addresses using a specific nameserver
    
    Args:
        hostname (str): The hostname to resolve
        nameserver (str): IP address of the nameserver to query
    
    Returns:
        list: List of IP addresses or error messages
    """
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [nameserver]
    
    try:
        answers = resolver.resolve(hostname, 'A')
        return [str(answer) for answer in answers]
    except dns.resolver.NXDOMAIN:
        return ["NXDOMAIN (Non-existent domain)"]
    except dns.resolver.NoAnswer:
        return ["No A records found"]
    except dns.resolver.Timeout:
        return ["DNS query timed out"]
    except dns.resolver.NoNameservers:
        return ["No working nameservers"]
    except Exception as e:
        return [f"DNS resolution error: {str(e)}"]

def read_hostnames_from_excel(file_path):
    """
    Read hostnames from the first column of an Excel file
    
    Args:
        file_path (str): Path to the Excel file
    
    Returns:
        list: List of hostnames to check
    
    Raises:
        SystemExit: If the file cannot be read
    """
    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        hostnames = []
        
        for row in sheet.iter_rows(values_only=True):
            if row and row[0]:
                hostname = str(row[0]).strip()
                if hostname and not hostname.startswith('#'):
                    hostnames.append(hostname)
        
        return hostnames
    except Exception as e:
        print(f"ERROR: Failed to read Excel file: {str(e)}", file=sys.stderr)
        sys.exit(1)

def write_results_to_csv(file_path, results):
    """
    Write DNS resolution results to a CSV file
    
    Args:
        file_path (str): Path to the output CSV file
        results (dict): Dictionary of {hostname: [ip_addresses]}
    
    Raises:
        SystemExit: If the file cannot be written
    """
    try:
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Hostname', 'IP Addresses', 'Timestamp'])
            for hostname, ips in results.items():
                writer.writerow([
                    hostname, 
                    ', '.join(ips), 
                    datetime.now().isoformat()
                ])
    except Exception as e:
        print(f"ERROR: Failed to write CSV file: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main execution function for the script"""
    
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # ===== CONFIGURATION =====
    # Input and output files will be in the same directory as the script
    input_file = os.path.join(script_dir, "DNSCheckList082025.xlsx")
    output_ns1 = os.path.join(script_dir, "DNSCheckList082025-ns1results01.csv")
    output_ns9 = os.path.join(script_dir, "DNSCheckList082025-ns9results01.csv")
    
    # Nameservers to test against
    dns_servers = {
        'ns1': '10.212.6.64',
        'ns9': '10.211.134.47'
    }
    # ===== END CONFIGURATION =====

    print("\nDNS Resolution Check Script")
    print("=" * 50)
    print(f"Script running from: {script_dir}")
    print(f"Input file: {input_file}")
    print(f"Nameservers: {', '.join(dns_servers.keys())}\n")

    # STEP 1: Read hostnames from Excel
    print("[1/3] Reading hostnames from Excel file...")
    hostnames = read_hostnames_from_excel(input_file)
    if not hostnames:
        print("ERROR: No valid hostnames found in the input file.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(hostnames)} hostnames to check\n")

    # STEP 2: Perform DNS resolution against each nameserver
    for server_name, server_ip in dns_servers.items():
        print(f"[2/3] Checking against {server_name} ({server_ip})...")
        
        results = {}
        total = len(hostnames)
        
        for i, hostname in enumerate(hostnames, 1):
            progress = (i / total) * 100
            print(f"\r  {i}/{total} ({progress:.1f}%) - Resolving: {hostname.ljust(50)}", end='', flush=True)
            
            ips = resolve_hostname(hostname, server_ip)
            results[hostname] = ips
        
        # STEP 3: Write results to CSV
        output_file = output_ns1 if server_name == 'ns1' else output_ns9
        write_results_to_csv(output_file, results)
        print(f"\n  Results saved to: {output_file}\n")

    print("[3/3] Script completed successfully\n")

if __name__ == "__main__":
    main()
