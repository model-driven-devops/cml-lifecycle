import json
import os
import requests
import time
from urllib3.exceptions import InsecureRequestWarning

# Disable warnings about insecure requests (for HTTPS with verify=False)
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Retrieve environment variables
cml_url = os.getenv('CML_URL')
api_token = os.getenv('API_TOKEN')
lab_title = os.getenv('CML_LAB')
node_definition_filter = os.getenv('NODE_DEFINITION')
image_name = os.getenv('IMAGE_NAME')  # This is the new image definition to apply

if not all([cml_url, api_token, lab_title, node_definition_filter, image_name]):
    print("Missing required environment variables. Please check your setup.")
    exit(1)

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_token}'
}
api_endpoint = "/api/v0/populate_lab_tiles"
full_url = f"{cml_url}{api_endpoint}"

def get_lab_id(url, headers, lab_title):
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        labs = response.json().get('lab_tiles', {})
        for lab_id, details in labs.items():
            if details.get('lab_title') == lab_title:
                print(f"Lab found: {lab_title} with ID: {lab_id}")
                return lab_id
        print(f"No lab found with title '{lab_title}'")
        return None
    except requests.RequestException as e:
        print(f"Failed to fetch labs: {e}")
        return None

def get_nodes_in_lab(cml_url, lab_id, headers, node_definition_filter):
    node_details_url = f"{cml_url}/api/v0/labs/{lab_id}/nodes?data=true&operational=true"
    try:
        response = requests.get(node_details_url, headers=headers, verify=False)
        response.raise_for_status()
        nodes = response.json()
        return [node for node in nodes if node.get('node_definition') == node_definition_filter]
    except requests.RequestException as e:
        print(f"Failed to fetch node details for lab ID {lab_id}: {e}")
        return []

def stop_node(cml_url, lab_id, node_id, headers):
    stop_url = f"{cml_url}/api/v0/labs/{lab_id}/nodes/{node_id}/state/stop"
    try:
        response = requests.put(stop_url, headers=headers, verify=False)
        print(f"Node ID {node_id}: Stop command sent, status {response.status_code}")
        return response.status_code == 204 or response.status_code == 200
    except requests.RequestException as e:
        print(f"Error stopping node ID {node_id}: {e}")
        return False

def wipe_disks(cml_url, lab_id, node_id, headers):
    wipe_url = f"{cml_url}/api/v0/labs/{lab_id}/nodes/{node_id}/wipe_disks"
    try:
        response = requests.put(wipe_url, headers=headers, verify=False)
        print(f"Node ID {node_id}: Disk wipe command sent, status {response.status_code}")
    except requests.RequestException as e:
        print(f"Error wiping disks for node ID {node_id}: {e}")

def update_image_definition(cml_url, lab_id, node_id, headers, image_name):
    update_url = f"{cml_url}/api/v0/labs/{lab_id}/nodes/{node_id}"
    payload = {"image_definition": image_name}
    try:
        response = requests.patch(update_url, json=payload, headers=headers, verify=False)
        print(f"Node ID {node_id}: Image definition updated to {image_name}, status {response.status_code}")
    except requests.RequestException as e:
        print(f"Error updating image definition for node ID {node_id}: {e}")

def start_node(cml_url, lab_id, node_id, headers):
    start_url = f"{cml_url}/api/v0/labs/{lab_id}/nodes/{node_id}/state/start"
    try:
        response = requests.put(start_url, headers=headers, verify=False)
        print(f"Node ID {node_id}: Start command sent, status {response.status_code}")
    except requests.RequestException as e:
        print(f"Error starting node ID {node_id}: {e}")

def monitor_nodes_and_finalize(cml_url, lab_id, headers, node_definition_filter, image_name):
    nodes = get_nodes_in_lab(cml_url, lab_id, headers, node_definition_filter)
    # Stop nodes if booted, wipe disks, update image definitions, and start nodes
    for node in nodes:
        if node['state'] == 'BOOTED':
            if stop_node(cml_url, lab_id, node['id'], headers):
                time.sleep(2)  # Short delay to ensure the node stops before wiping disks
        wipe_disks(cml_url, lab_id, node['id'], headers)
        update_image_definition(cml_url, lab_id, node['id'], headers, image_name)
        start_node(cml_url, lab_id, node['id'], headers)
    print("All targeted nodes have been processed with new image definitions and started.")


# Fetch lab ID
lab_id = get_lab_id(full_url, headers, lab_title)

if lab_id:
    print(f"Lab ID {lab_id} will be used for further API calls.")
    monitor_nodes_and_finalize(cml_url, lab_id, headers, node_definition_filter, image_name)
else:
    print("Unable to find or fetch the lab ID.")
