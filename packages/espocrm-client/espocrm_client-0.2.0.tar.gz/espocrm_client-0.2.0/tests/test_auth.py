#!/usr/bin/env python
"""Test authentication"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from espocrm.auth import APIKeyAuth

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
print(f"API Key from env: {api_key}")

auth = APIKeyAuth(api_key=api_key)
headers = auth.get_headers("GET", "/")
print(f"Headers generated: {headers}")
print(f"X-API-Key header: {headers.get('X-API-Key')}")
