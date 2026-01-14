#!/usr/bin/env python3
"""
TsharkCapture.py - Network traffic capture using Tshark

This script captures network traffic on a specified interface for 5 minutes
using source and destination IP filters. Requires Wireshark's Tshark utility.
"""

import os
import sys
import subprocess
from datetime import datetime
import ipaddress
import platform

def is_admin():
    """Check if running as administrator/root"""
    try:
        if platform.system() == 'Windows':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.getuid() == 0
    except:
        return False

def validate_ip(ip_str):
    """Validate an IP address string"""
    if not ip_str:
        return True
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def main():
    # Configuration
    TSHARK_PATH = r"C:\Program Files\Wireshark\tshark.exe"
    INTERFACE = "Ethernet4"
    CAPTURE_DURATION = 300  # 5 minutes in seconds
    OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "TsharkCaptures")

    # Check admin privileges
    if not is_admin():
        print("\nThis script requires Administrator privileges. Please run as Administrator.", file=sys.stderr)
        sys.exit(1)

    # Verify Tshark exists
    if not os.path.exists(TSHARK_PATH):
        print(f"\nTshark not found at {TSHARK_PATH}", file=sys.stderr)
        print("Please install Wireshark to the default location or modify the script path.")
        print("Download from: https://www.wireshark.org/download.html")
        sys.exit(1)

    # List available interfaces
    print("\nListing available interfaces...")
    try:
        subprocess.run([TSHARK_PATH, "-D"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error listing interfaces: {e}", file=sys.stderr)
        sys.exit(1)

    # Get user input for IP addresses
    print("\nEnter IP addresses (leave blank for any)")
    src_ip = input("Source IP address: ").strip()
    dst_ip = input("Destination IP address: ").strip()

    # Validate IP addresses
    if not validate_ip(src_ip):
        print("Invalid source IP address format", file=sys.stderr)
        sys.exit(1)
    if not validate_ip(dst_ip):
        print("Invalid destination IP address format", file=sys.stderr)
        sys.exit(1)

    # Build capture filter
    capture_filter = []
    if src_ip:
        capture_filter.append(f"src host {src_ip}")
    if dst_ip:
        capture_filter.append(f"dst host {dst_ip}")

    final_filter = " and ".join(capture_filter) if capture_filter else "ip"
    print(f"\nUsing filter: {final_filter}")

    # Prepare output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"TsharkCapture_{timestamp}.pcapng")

    # Display capture settings
    print("\nCapture Settings:")
    print(f"Interface: {INTERFACE}")
    print(f"Duration: {CAPTURE_DURATION // 60} minutes")
    print(f"Output File: {output_file}")
    print("Press Ctrl+C to stop capture early")

    # Run Tshark capture
    try:
        print("\nStarting capture...")
        tshark_cmd = [
            TSHARK_PATH,
            "-i", INTERFACE,
            "-f", final_filter,
            "-a", f"duration:{CAPTURE_DURATION}",
            "-w", output_file
        ]

        subprocess.run(tshark_cmd, check=True)

        # Verify capture file
        if not os.path.exists(output_file):
            raise Exception("Capture file was not created")

        file_size = os.path.getsize(output_file) / (1024 * 1024)  # in MB
        print("\nCapture completed successfully!")
        print(f"File saved to: {output_file}")
        print(f"File size: {file_size:.2f} MB")

    except subprocess.CalledProcessError as e:
        print(f"\nError during capture (Exit code {e.returncode}):", file=sys.stderr)
        print(e, file=sys.stderr)
        if os.path.exists(output_file):
            os.remove(output_file)
            print("Removed incomplete capture file")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCapture stopped by user")
        if os.path.exists(output_file):
            os.remove(output_file)
            print("Removed incomplete capture file")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        if os.path.exists(output_file):
            os.remove(output_file)
            print("Removed incomplete capture file")
        sys.exit(1)

if __name__ == "__main__":
    main()
