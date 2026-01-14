import requests
from requests.auth import HTTPBasicAuth
import getpass

# ServiceNow instance details
instance = 'companyprod'  # Replace with your ServiceNow instance

# Prompt for username and password
username = input("Enter your ServiceNow username: ")
password = getpass.getpass("Enter your ServiceNow password: ")

# Endpoint URL
url = f'https://{instance}.service-now.com/api/now/table/incident'

# Query parameters to filter incidents assigned to the specific user, sorted by creation date descending
params = {
    'sysparm_query': f'assigned_to.user_name={username}^ORDERBYDESCsys_created_on',
    'sysparm_fields': 'number,short_description,sys_created_on,assigned_to',
    'sysparm_limit': '20'  # Retrieve 20 most recent incidents
}

# Headers
headers = {
    'Accept': 'application/json'
}

# Make the request
response = requests.get(url, auth=HTTPBasicAuth(username, password), headers=headers, params=params)

# Check the response status
if response.status_code == 200:
    # Parse the JSON response
    incidents = response.json().get('result', [])
    for incident in incidents:
        print(f"Number: {incident['number']}, Short Description: {incident['short_description']}, Created On: {incident['sys_created_on']}")
else:
    print(f"Failed to retrieve incidents. Status code: {response.status_code}, Response: {response.text}")
