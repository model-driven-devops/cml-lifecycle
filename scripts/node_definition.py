import json
import os
import requests
import sys  # Needed for exiting the script early
from urllib3.exceptions import InsecureRequestWarning

# Disable warnings about insecure requests (for HTTPS with verify=False)
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Environment Variables Check
required_env_vars = ['CML_URL', 'API_TOKEN', 'NODE_DEFINITION']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    print(f"Missing required environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

# Retrieve environment variables
cml_url = os.getenv('CML_URL')
api_token = os.getenv('API_TOKEN')
node_definition = os.getenv('NODE_DEFINITION')

# Load and update the JSON payload
with open('definitions/node_definition.json', 'r') as file:
    payload = json.load(file)

# Update the node definition based on environment variable
payload['id'] = node_definition
payload['general']['description'] = node_definition
payload['ui']['label'] = node_definition
payload['ui']['label_prefix'] = f"{node_definition}-"

# Prepare headers and URL for the API request
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_token}'
}
api_endpoint = "/api/v0/node_definitions"
full_url = cml_url + api_endpoint

# Function to send API requests
def send_request(method, url, json_data):
    if method == 'POST':
        return requests.post(url, json=json_data, headers=headers, verify=False)
    elif method == 'PUT':
        return requests.put(url, json=json_data, headers=headers, verify=False)

# First try to POST the new node definition
response = send_request('POST', full_url, payload)

# Check response status code
if response.status_code == 400:  # Assuming 400 indicates the node already exists
    print("Node already exists. Attempting to update the existing node...")
    response = send_request('PUT', full_url, payload)
    if response.status_code in [200, 204]:  # Common success codes for PUT
        print("Node definition updated successfully.")
    else:
        print(f"Failed to update node definition: HTTP {response.status_code}")
elif response.status_code in [200, 201]:  # Common success codes for POST
    print("Node definition created successfully.")
else:
    print(f"Failed to create or update node definition: HTTP {response.status_code}, Response: {response.text}")

# Print the final response
print(response.text)
