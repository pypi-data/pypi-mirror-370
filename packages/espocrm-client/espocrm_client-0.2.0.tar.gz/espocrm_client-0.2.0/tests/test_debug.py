#!/usr/bin/env python
"""Debug authentication and headers"""

import os
import sys
import requests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env
env_file = '.env'
with open(env_file, 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            if '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

api_key = os.getenv('ESPO_API_KEY')
base_url = os.getenv('ESPO_URL')

print(f"API Key: {api_key}")
print(f"Base URL: {base_url}")

# Test direct request
headers = {
    'X-Api-Key': api_key,
    'Content-Type': 'application/json'
}

url = f"{base_url}/api/v1/Contact"
print(f"\nTrying GET request to: {url}")
print(f"Headers: {headers}")

response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("✅ Authentication successful!")
    data = response.json()
    print(f"Response has {len(data.get('list', []))} contacts")
else:
    print(f"❌ Authentication failed: {response.text}")
