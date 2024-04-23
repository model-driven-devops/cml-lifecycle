import requests
import json
import os
import urllib3

# Retrieve environment variables
cml_url = os.getenv('CML_URL')
cml_username = os.getenv('CML_USERNAME')
cml_password = os.getenv('CML_PASSWORD')
git_api = os.getenv('GITLAB_URL')
git_token = os.getenv('GITLAB_TOKEN')
ci_project_id = os.getenv('CI_PROJECT_ID')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_api_token():
    url = f"{cml_url}/api/v0/authenticate"
    payload = {
        "username": cml_username,
        "password": cml_password
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=payload, headers=headers, verify=False)
    # Directly return the response text as the token
    if response.status_code == 200:
        return response.text.strip('"')  # Remove any surrounding quotes
    else:
        print("Failed to retrieve token, response code:", response.status_code)
        print("Response content:", response.text)
        return None

def set_gitlab_env_var(token):
    print("Using GITLAB_TOKEN:", os.getenv('GITLAB_TOKEN'))
    print("Using CI_PROJECT_ID:", os.getenv('CI_PROJECT_ID'))
    # Endpoint to update the environment variable in GitLab
    url = f"{git_api}/api/v4/projects/{ci_project_id}/variables/API_TOKEN"
    print("Accessing URL:", url)
    payload = {
        "key": "API_TOKEN",
        "value": token,
        "variable_type": "env_var",
        "protected": True,
        "masked": True
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {git_token}'
    }
    # Make the POST request with SSL verification disabled
    response = requests.put(url, json=payload, headers=headers, verify=False)
    if response.status_code != 200:
        print(f"Failed to set GitLab environment variable: HTTP {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text}")
    else:
        print("GitLab environment variable set successfully.")
    print(response.text)

if __name__ == "__main__":
    token = get_api_token()
    if token:
        set_gitlab_env_var(token)
    else:
        print("Failed to retrieve API token")