"""
EspoCRM CRUD Test Suite

Gerçek EspoCRM sunucusuna bağlanarak Contact entity üzerinde
Create, Read, Update, Delete işlemlerini test eder.
"""

import os
import sys
import uuid
import pytest
from datetime import datetime
from typing import Optional, Dict, Any

# Parent dizini Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from espocrm.client import EspoCRMClient
from espocrm.exceptions import (
    EspoCRMAPIError,
    EspoCRMNotFoundError,
    EspoCRMValidationError
)


class TestContactCRUD:
    """Contact entity için CRUD testleri"""
    
    @pytest.fixture(autouse=True)
    def setup(self, espo_client: EspoCRMClient):
        """Her test için setup"""
        self.client = espo_client
        self.test_contacts = []  # Temizlik için oluşturulan contact'ları takip et
        yield
        # Cleanup: Test sonrası oluşturulan contact'ları sil
        for contact_id in self.test_contacts:
            try:
                self.client.delete_entity("Contact", contact_id)
            except:
                pass  # Zaten silinmiş olabilir
    
    def create_test_contact_data(self) -> Dict[str, Any]:
        """Test için benzersiz contact verisi oluştur"""
        unique_id = str(uuid.uuid4())[:8]
        return {
            "firstName": f"Test_{unique_id}",
            "lastName": f"User_{unique_id}",
            "emailAddress": f"test_{unique_id}@example.com",
            "phoneNumber": f"+90 555 {unique_id[:3]} {unique_id[3:5]} {unique_id[5:7]}",
            "description": f"Test contact created at {datetime.now().isoformat()}"
        }
    
    def test_create_contact(self):
        """CREATE: Yeni bir contact oluştur"""
        # Test verisi hazırla
        contact_data = self.create_test_contact_data()
        
        # Contact oluştur
        response = self.client.create_entity("Contact", contact_data)
        
        # Response'u doğrula
        assert response is not None, "Create response boş olmamalı"
        assert "id" in response, "Response'da id bulunmalı"
        assert response.get("firstName") == contact_data["firstName"]
        assert response.get("lastName") == contact_data["lastName"]
        assert response.get("emailAddress") == contact_data["emailAddress"]
        
        # Temizlik için ID'yi kaydet
        self.test_contacts.append(response["id"])
        
        print(f"✅ Contact başarıyla oluşturuldu: {response['id']}")
        return response["id"]
    
    def test_read_contact(self):
        """READ: Var olan bir contact'ı oku"""
        # Önce bir contact oluştur
        contact_data = self.create_test_contact_data()
        created = self.client.create_entity("Contact", contact_data)
        contact_id = created["id"]
        self.test_contacts.append(contact_id)
        
        # Contact'ı oku
        contact = self.client.get_entity("Contact", contact_id)
        
        # Verileri doğrula
        assert contact is not None, "Contact bulunamadı"
        assert contact.get("id") == contact_id
        assert contact.get("firstName") == contact_data["firstName"]
        assert contact.get("lastName") == contact_data["lastName"]
        
        print(f"✅ Contact başarıyla okundu: {contact_id}")
    
    def test_update_contact(self):
        """UPDATE: Var olan bir contact'ı güncelle"""
        # Önce bir contact oluştur
        contact_data = self.create_test_contact_data()
        created = self.client.create_entity("Contact", contact_data)
        contact_id = created["id"]
        self.test_contacts.append(contact_id)
        
        # Güncelleme verisi
        update_data = {
            "firstName": f"Updated_{contact_data['firstName']}",
            "description": f"Updated at {datetime.now().isoformat()}"
        }
        
        # Contact'ı güncelle
        updated = self.client.update_entity("Contact", contact_id, update_data)
        
        # Güncellenmiş veriyi oku ve doğrula
        contact = self.client.get_entity("Contact", contact_id)
        assert contact.get("firstName") == update_data["firstName"]
        assert "Updated at" in contact.get("description", "")
        
        print(f"✅ Contact başarıyla güncellendi: {contact_id}")
    
    def test_delete_contact(self):
        """DELETE: Var olan bir contact'ı sil"""
        # Önce bir contact oluştur
        contact_data = self.create_test_contact_data()
        created = self.client.create_entity("Contact", contact_data)
        contact_id = created["id"]
        
        # Contact'ı sil
        result = self.client.delete_entity("Contact", contact_id)
        assert result is True, "Delete işlemi başarısız"
        
        # Silindiğini doğrula (okunamaz olmalı)
        with pytest.raises(EspoCRMNotFoundError):
            self.client.get_entity("Contact", contact_id)
        
        print(f"✅ Contact başarıyla silindi: {contact_id}")
    
    def test_list_contacts(self):
        """LIST: Contact'ları listele ve filtrele"""
        # Test için birkaç contact oluştur
        test_prefix = f"TestList_{str(uuid.uuid4())[:6]}"
        created_ids = []
        
        for i in range(3):
            contact_data = {
                "firstName": f"{test_prefix}_{i}",
                "lastName": f"User_{i}",
                "emailAddress": f"list_test_{i}@example.com"
            }
            created = self.client.create_entity("Contact", contact_data)
            created_ids.append(created["id"])
            self.test_contacts.append(created["id"])
        
        # Tüm contact'ları listele
        all_contacts = self.client.list_entities("Contact", max_size=100)
        assert "list" in all_contacts, "Response'da list bulunmalı"
        assert len(all_contacts["list"]) > 0, "En az bir contact bulunmalı"
        
        # Filtreleme ile listele
        filtered = self.client.list_entities(
            "Contact",
            where={
                "type": "contains",
                "attribute": "firstName",
                "value": test_prefix
            }
        )
        
        # Filtrelenmiş sonuçları doğrula
        assert "list" in filtered
        filtered_ids = [c["id"] for c in filtered["list"]]
        for created_id in created_ids:
            assert created_id in filtered_ids, f"Oluşturulan contact listede bulunmalı: {created_id}"
        
        print(f"✅ {len(created_ids)} contact başarıyla listelendi")
    
    def test_search_contacts(self):
        """SEARCH: Contact'ları ara"""
        # Test için benzersiz bir contact oluştur
        unique_term = f"UniqueSearch_{str(uuid.uuid4())[:8]}"
        contact_data = self.create_test_contact_data()
        contact_data["lastName"] = unique_term
        
        created = self.client.create_entity("Contact", contact_data)
        self.test_contacts.append(created["id"])
        
        # Arama yap
        from espocrm.models.search import SearchParams
        search_params = SearchParams(query=unique_term, maxSize=10)
        search_results = self.client.search_entities(
            "Contact",
            search_params
        )
        
        # Sonuçları doğrula
        assert "list" in search_results
        found_ids = [c["id"] for c in search_results["list"]]
        assert created["id"] in found_ids, "Oluşturulan contact arama sonuçlarında bulunmalı"
        
        print(f"✅ Contact başarıyla arandı ve bulundu: {unique_term}")
    
    def test_validation_error(self):
        """VALIDATION: Geçersiz veri ile hata kontrolü"""
        # Geçersiz email ile contact oluşturmayı dene
        invalid_data = {
            "firstName": "Test",
            "lastName": "User",
            "emailAddress": "invalid-email"  # Geçersiz email formatı
        }
        
        # Validation hatası bekleniyor
        with pytest.raises((EspoCRMValidationError, EspoCRMAPIError)):
            self.client.create_entity("Contact", invalid_data)
        
        print("✅ Validation hatası başarıyla yakalandı")
    
    def test_not_found_error(self):
        """NOT FOUND: Var olmayan kayıt için hata kontrolü"""
        fake_id = "non-existent-id-12345"
        
        # NotFound hatası bekleniyor
        with pytest.raises(EspoCRMNotFoundError):
            self.client.get_entity("Contact", fake_id)
        
        print("✅ NotFound hatası başarıyla yakalandı")
    
    def test_bulk_operations(self):
        """BULK: Toplu işlemler"""
        # Toplu oluşturma
        bulk_count = 5
        bulk_prefix = f"Bulk_{str(uuid.uuid4())[:6]}"
        created_contacts = []
        
        for i in range(bulk_count):
            contact_data = {
                "firstName": f"{bulk_prefix}_{i}",
                "lastName": f"User_{i}",
                "emailAddress": f"bulk_{i}_{bulk_prefix}@example.com"
            }
            created = self.client.create_entity("Contact", contact_data)
            created_contacts.append(created)
            self.test_contacts.append(created["id"])
        
        # Toplu okuma
        for contact in created_contacts:
            fetched = self.client.get_entity("Contact", contact["id"])
            assert fetched["id"] == contact["id"]
        
        # Toplu güncelleme
        for contact in created_contacts:
            update_data = {"description": f"Bulk updated at {datetime.now().isoformat()}"}
            self.client.update_entity("Contact", contact["id"], update_data)
        
        # Güncellemeleri doğrula
        for contact in created_contacts:
            fetched = self.client.get_entity("Contact", contact["id"])
            assert "Bulk updated" in fetched.get("description", "")
        
        print(f"✅ {bulk_count} contact için toplu işlemler başarıyla tamamlandı")


if __name__ == "__main__":
    # Testleri çalıştır
    pytest.main([__file__, "-v", "-s"])
