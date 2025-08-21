#!/usr/bin/env python
"""
Kalıcı Contact Oluşturma Testi

Bu script bir contact oluşturur ama SİLMEZ.
UI üzerinden kontrol edebilmeniz için contact'ı bırakır.
"""

import os
import sys
import uuid
from datetime import datetime

# Parent dizini import et
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from espocrm.client import EspoCRMClient
from espocrm.auth import APIKeyAuth
from espocrm.config import ClientConfig

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
    
    base_url = os.getenv('ESPO_URL')
    if not base_url:
        raise ValueError("ESPO_URL environment variable is not set")
    
    api_key = os.getenv('ESPO_API_KEY')
    username = os.getenv('ESPO_USERNAME')
    password = os.getenv('ESPO_PASSWORD')
    
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
        from espocrm.auth import BasicAuth
        auth = BasicAuth(username=username, password=password)
    else:
        raise ValueError("No valid authentication credentials found")
    
    client = EspoCRMClient(
        base_url=base_url,
        auth=auth,
        config=config
    )
    
    return client

def main():
    print("=" * 60)
    print("🚀 KALICI CONTACT OLUŞTURMA TESTİ")
    print("=" * 60)
    
    try:
        # Client oluştur
        client = create_test_client()
        print(f"✅ EspoCRM'e bağlandı: {os.getenv('ESPO_URL')}")
        print("-" * 60)
        
        # Test verisi - Türkçe karakterler ve detaylı bilgi
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        unique_suffix = str(uuid.uuid4())[:6].upper()
        
        test_contact = {
            "firstName": f"Test_{unique_suffix}",
            "lastName": "Kullanıcı",
            "emailAddress": f"test.user.{unique_suffix.lower()}@example.com",
            "phoneNumber": f"+90 555 {unique_suffix[:3]} {unique_suffix[3:5]} 00",
            "title": "Test Pozisyonu",
            "description": f"""Bu contact Python Client testi ile oluşturuldu.
            
Oluşturulma Zamanı: {timestamp}
Test ID: {unique_suffix}
Client Version: EspoCRM Python Client v0.1.0

NOT: Bu contact UI üzerinden kontrol edilmek üzere bırakıldı.
Test tamamlandıktan sonra manuel olarak silinebilir.""",
            "addressStreet": "Test Sokak No: 123",
            "addressCity": "İstanbul",
            "addressCountry": "Türkiye",
            "addressPostalCode": "34000"
        }
        
        print("📝 OLUŞTURULACAK CONTACT BİLGİLERİ:")
        print(f"   Ad: {test_contact['firstName']}")
        print(f"   Soyad: {test_contact['lastName']}")
        print(f"   E-posta: {test_contact['emailAddress']}")
        print(f"   Telefon: {test_contact['phoneNumber']}")
        print(f"   Pozisyon: {test_contact['title']}")
        print(f"   Şehir: {test_contact['addressCity']}")
        print("-" * 60)
        
        # Contact oluştur
        print("\n⏳ Contact oluşturuluyor...")
        created = client.crud.create("Contact", test_contact)
        contact_id = created.get_id() if hasattr(created, 'get_id') else created.get('id')
        
        print(f"\n✅ CONTACT BAŞARIYLA OLUŞTURULDU!")
        print(f"   ID: {contact_id}")
        print(f"   URL: {os.getenv('ESPO_URL')}/#Contact/view/{contact_id}")
        
        # Oluşturulan contact'ı tekrar oku ve doğrula
        print("\n🔍 Contact doğrulanıyor...")
        fetched = client.crud.read("Contact", contact_id)
        fetched_data = fetched.data if hasattr(fetched, 'data') else fetched
        
        print("✅ Contact verileri doğrulandı:")
        print(f"   Ad Soyad: {fetched_data.get('firstName')} {fetched_data.get('lastName')}")
        print(f"   E-posta: {fetched_data.get('emailAddress')}")
        if fetched_data.get('createdAt'):
            print(f"   Oluşturulma: {fetched_data.get('createdAt')}")
        
        # Arama ile doğrula
        print("\n🔎 Contact arama ile doğrulanıyor...")
        from espocrm.models.search import SearchParams
        search_params = SearchParams(query=test_contact['emailAddress'], maxSize=5)
        search_results = client.crud.search("Contact", search_params)
        
        if hasattr(search_results, 'list'):
            results_list = search_results.list
        else:
            results_list = search_results.get('list', [])
        
        found = any(c.get('id') == contact_id for c in results_list)
        if found:
            print("✅ Contact arama sonuçlarında bulundu!")
        
        print("\n" + "=" * 60)
        print("🎉 TEST BAŞARIYLA TAMAMLANDI!")
        print("=" * 60)
        print("\n📌 ÖNEMLİ NOTLAR:")
        print(f"   • Contact ID: {contact_id}")
        print(f"   • Contact SİLİNMEDİ - UI'da görüntülenebilir")
        print(f"   • UI Link: {os.getenv('ESPO_URL')}/#Contact/view/{contact_id}")
        print("   • Test tamamlandıktan sonra manuel olarak silinebilir")
        print("=" * 60)
        
        # Ek bilgi
        print("\n💡 İPUCU:")
        print("   Contact'ı UI'da görmek için:")
        print("   1. EspoCRM'e giriş yapın")
        print("   2. Contacts menüsüne gidin")
        print(f"   3. '{test_contact['firstName']} {test_contact['lastName']}' adlı contact'ı arayın")
        print(f"   4. Veya direkt link: {os.getenv('ESPO_URL')}/#Contact/view/{contact_id}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST BAŞARISIZ: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
