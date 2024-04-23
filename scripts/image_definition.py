import json
import os
import requests
from urllib3.exceptions import InsecureRequestWarning

# Disable warnings about insecure requests (for HTTPS with verify=False)
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Retrieve environment variables
cml_url = os.getenv('CML_URL')  # Default value if not set
api_token = os.getenv('API_TOKEN')  # Default value for safety in non-production environments
image_name = os.getenv('IMAGE_NAME')  # Retrieve the IMAGE_NAME environment variable set in GitLab CI

# Read and modify the JSON payload
with open('definitions/image_definition.json', 'r') as file:
    payload = json.load(file)

# Update the JSON payload with the environment variables
if image_name:
    payload['id'] = image_name
    payload['description'] = image_name
    payload['label'] = image_name
    payload['disk_image'] = f"{image_name}.qcow2"
else:
    print("Error: IMAGE_NAME environment variable is not set.")
    exit(1)  # Exit if the required environment variable is not set

# Prepare headers and URL for the API request
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_token}'
}
api_endpoint = "/api/v0/image_definitions"
full_url = cml_url + api_endpoint

# Function to handle API request
def send_request(method, url, json_data):
    if method == 'POST':
        response = requests.post(url, json=json_data, headers=headers, verify=False)
    elif method == 'PUT':
        response = requests.put(url, json=json_data, headers=headers, verify=False)
    return response

# Try to POST the new image definition
response = send_request('POST', full_url, payload)

# Check response status code
if response.status_code == 400:  # Assuming 400 indicates the image already exists
    print("Image already exists. Updating existing definition...")
    response = send_request('PUT', full_url, payload)
    if response.status_code == 200:
        print("Image definition updated successfully.")
    else:
        print(f"Failed to update image definition: {response.status_code}")
elif response.status_code == 200 or response.status_code == 201:
    print("Image definition created successfully.")
else:
    print(f"Failed to create image definition: {response.status_code}, {response.text}")

# Print the response
print(response.text)