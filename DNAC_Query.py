### Script below was created  to provide a simple tool to allow users to automate the process of querying a Cisco DNAC Inventory database for a list of devices. The  results are then output to a CSV file. 
import requests
import csv
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

dnac = {
    "host": "10.14.16.5",
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD",
    "version": "v1"
}

def get_dnac_token(dnac):
    url = f"https://{dnac['host']}/dna/system/api/{dnac['version']}/auth/token"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    print(f"Attempting to authenticate with URL: {url}")
    response = requests.post(url, auth=(dnac['username'], dnac['password']), headers=headers, verify=False)
    print(f"Response Status Code: {response.status_code}")
    response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
    return response.json().get('Token')

def export_inventory_report(dnac, token):
    url = f"https://{dnac['host']}/api/{dnac['version']}/network-device"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Auth-Token': token
    }
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
    return response.json()

def save_report_to_csv(report, file_path):
    # Filter the devices to only include network switches
    network_switches = [device for device in report['response'] if device.get('family') == 'Switches and Hubs']
    
    if not network_switches:
        print("No network switches found in the inventory.")
        return
    
    # Define the header based on the keys of the first network switch
    header = network_switches[0].keys()
    
    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        for device in network_switches:
            writer.writerow(device)

try:
    # Get the token
    token = get_dnac_token(dnac)

    # Export the report
    report = export_inventory_report(dnac, token)

    # Save the report to a CSV file
    csv_file_path = "/path/to/save/inventory_report.csv"          #### Save to a local CSV file on  your machine 
    save_report_to_csv(report, csv_file_path)

    print(f"Inventory report exported successfully to {csv_file_path}!")
except requests.exceptions.HTTPError as err:
    print(f"HTTP error occurred: {err}")
except Exception as err:
    print(f"An error occurred: {err}")
