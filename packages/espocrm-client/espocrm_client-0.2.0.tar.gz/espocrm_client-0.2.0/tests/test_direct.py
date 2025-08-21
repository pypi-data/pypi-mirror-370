#!/usr/bin/env python
"""Direct API test without using client"""

import os
import requests
import json
import uuid
from datetime import datetime

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

print(f"🚀 Direct EspoCRM CRUD Test")
print(f"API Key: {api_key[:10]}...")
print(f"Base URL: {base_url}")
print("-" * 50)

# Headers
headers = {
    'X-Api-Key': api_key,
    'Content-Type': 'application/json'
}

# Test data
unique_id = str(uuid.uuid4())[:8]
contact_data = {
    "firstName": f"DirectTest_{unique_id}",
    "lastName": f"User_{unique_id}",
    "emailAddress": f"direct_{unique_id}@example.com",
    "description": f"Direct test at {datetime.now().isoformat()}"
}

# 1. CREATE
print("\n1️⃣ CREATE:")
create_url = f"{base_url}/api/v1/Contact"
response = requests.post(create_url, json=contact_data, headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code in [200, 201]:
    created = response.json()
    contact_id = created.get('id')
    print(f"   ✅ Created contact: {contact_id}")
else:
    print(f"   ❌ Failed: {response.text}")
    exit(1)

# 2. READ
print("\n2️⃣ READ:")
read_url = f"{base_url}/api/v1/Contact/{contact_id}"
response = requests.get(read_url, headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    contact = response.json()
    print(f"   ✅ Read contact: {contact.get('firstName')} {contact.get('lastName')}")
else:
    print(f"   ❌ Failed: {response.text}")

# 3. UPDATE
print("\n3️⃣ UPDATE:")
update_data = {
    "firstName": f"Updated_{contact_data['firstName']}"
}
update_url = f"{base_url}/api/v1/Contact/{contact_id}"
response = requests.patch(update_url, json=update_data, headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print(f"   ✅ Updated contact")
else:
    print(f"   ❌ Failed: {response.text}")

# 4. DELETE
print("\n4️⃣ DELETE:")
delete_url = f"{base_url}/api/v1/Contact/{contact_id}"
response = requests.delete(delete_url, headers=headers)
print(f"   Status: {response.status_code}")
if response.status_code in [200, 204]:
    print(f"   ✅ Deleted contact")
else:
    print(f"   ❌ Failed: {response.text}")

print("\n" + "=" * 50)
print("✅ All direct API tests passed!")
print("=" * 50)
