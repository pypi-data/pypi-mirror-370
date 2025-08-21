#!/usr/bin/env python
"""
Basit EspoCRM CRUD Test Script
Gerçek sunucuya bağlanıp temel işlemleri test eder
"""

import os
import sys
import uuid
from datetime import datetime

# Parent dizini import et
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from espocrm.client import EspoCRMClient
from espocrm.auth import APIKeyAuth, BasicAuth
from espocrm.config import ClientConfig
from espocrm.exceptions import EspoCRMError, EspoCRMNotFoundError

# .env dosyasını yükle
def load_env():
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

# Test için client oluştur
def create_test_client():
    load_env()
    
    # Config
    base_url = os.getenv('ESPO_URL')
    if not base_url:
        raise ValueError("ESPO_URL environment variable is not set")
    
    # Auth
    api_key = os.getenv('ESPO_API_KEY')
    username = os.getenv('ESPO_USERNAME')
    password = os.getenv('ESPO_PASSWORD')
    
    # Config oluştur (authentication bilgileri ile)
    if api_key and api_key != 'your-api-key-here':
        config = ClientConfig(
            base_url=base_url,
            api_key=api_key,
            timeout=30,
            verify_ssl=True
        )
        auth = APIKeyAuth(api_key=api_key)
    elif username and password:
        config = ClientConfig(
            base_url=base_url,
            username=username,
            password=password,
            timeout=30,
            verify_ssl=True
        )
        auth = BasicAuth(username=username, password=password)
    else:
        raise ValueError("No valid authentication credentials found")
    
    # Client
    client = EspoCRMClient(
        base_url=base_url,
        auth=auth,
        config=config
    )
    
    return client

def main():
    print("🚀 EspoCRM CRUD Test Başlıyor...")
    print("-" * 50)
    
    try:
        # Client oluştur
        client = create_test_client()
        print(f"✅ EspoCRM'e bağlandı: {os.getenv('ESPO_URL')}")
        
        # Test verisi
        unique_id = str(uuid.uuid4())[:8]
        test_contact = {
            "firstName": f"Test_{unique_id}",
            "lastName": f"User_{unique_id}",
            "emailAddress": f"test_{unique_id}@example.com",
            "description": f"Test contact created at {datetime.now().isoformat()}"
        }
        
        print("\n1️⃣ CREATE TEST:")
        print(f"   Creating contact: {test_contact['firstName']} {test_contact['lastName']}")
        
        # CREATE
        created = client.crud.create("Contact", test_contact)
        contact_id = created.get_id() if hasattr(created, 'get_id') else created.get('id')
        print(f"   ✅ Contact created with ID: {contact_id}")
        
        print("\n2️⃣ READ TEST:")
        # READ
        fetched = client.crud.read("Contact", contact_id)
        fetched_data = fetched.data if hasattr(fetched, 'data') else fetched
        print(f"   ✅ Contact read: {fetched_data.get('firstName')} {fetched_data.get('lastName')}")
        
        print("\n3️⃣ UPDATE TEST:")
        # UPDATE
        update_data = {
            "firstName": f"Updated_{test_contact['firstName']}",
            "description": f"Updated at {datetime.now().isoformat()}"
        }
        updated = client.crud.update("Contact", contact_id, update_data)
        print(f"   ✅ Contact updated")
        
        # Verify update
        fetched_after_update = client.crud.read("Contact", contact_id)
        fetched_data = fetched_after_update.data if hasattr(fetched_after_update, 'data') else fetched_after_update
        assert fetched_data.get('firstName').startswith('Updated_'), "Update failed"
        print(f"   ✅ Update verified: {fetched_data.get('firstName')}")
        
        print("\n4️⃣ LIST TEST:")
        # LIST
        from espocrm.models.search import SearchParams
        search_params = SearchParams(maxSize=5)
        contacts_list = client.crud.list("Contact", search_params=search_params)
        list_data = contacts_list.list if hasattr(contacts_list, 'list') else contacts_list.get('list', [])
        print(f"   ✅ Found {len(list_data)} contacts")
        
        print("\n5️⃣ DELETE TEST:")
        # DELETE
        deleted = client.crud.delete("Contact", contact_id)
        print(f"   ✅ Contact deleted: {deleted}")
        
        # Verify deletion
        try:
            client.crud.read("Contact", contact_id)
            print("   ❌ Contact still exists after deletion!")
        except EspoCRMNotFoundError:
            print("   ✅ Deletion verified - contact not found")
        except EspoCRMError as e:
            if '404' in str(e) or 'not found' in str(e).lower():
                print("   ✅ Deletion verified - contact not found")
            else:
                raise
        
        print("\n" + "=" * 50)
        print("🎉 TÜM TESTLER BAŞARIYLA TAMAMLANDI!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ TEST BAŞARISIZ: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
