"""
Pytest Configuration and Fixtures

Test ortamını yapılandırır ve paylaşılan fixture'ları sağlar.
"""

import os
import sys
import pytest
from pathlib import Path
from typing import Generator

# Parent dizini Python path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from espocrm.client import EspoCRMClient


def pytest_configure(config):
    """Pytest yapılandırması"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )


def load_env_file():
    """
    .env dosyasından environment variable'ları yükle
    """
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        raise FileNotFoundError(
            f".env dosyası bulunamadı: {env_file}\n"
            "Lütfen tests/.env dosyasını oluşturun ve EspoCRM bağlantı bilgilerini girin."
        )
    
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


# .env dosyasını yükle
load_env_file()


@pytest.fixture(scope="session")
def espo_config():
    """
    EspoCRM bağlantı konfigürasyonu
    """
    # Gerekli environment variable'ları kontrol et
    required_vars = ["ESPO_URL"]
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Gerekli environment variable eksik: {var}")
    
    # API Key veya Username/Password kontrolü
    has_api_key = bool(os.getenv("ESPO_API_KEY"))
    has_basic_auth = bool(os.getenv("ESPO_USERNAME")) and bool(os.getenv("ESPO_PASSWORD"))
    
    if not has_api_key and not has_basic_auth:
        raise ValueError(
            "Kimlik doğrulama bilgileri eksik. "
            "ESPO_API_KEY veya ESPO_USERNAME/ESPO_PASSWORD ayarlanmalı."
        )
    
    config = {
        "url": os.getenv("ESPO_URL"),
        "timeout": int(os.getenv("TEST_TIMEOUT", "30")),
        "debug": os.getenv("DEBUG", "false").lower() == "true"
    }
    
    # API Key varsa kullan
    if has_api_key:
        config["api_key"] = os.getenv("ESPO_API_KEY")
    else:
        config["username"] = os.getenv("ESPO_USERNAME")
        config["password"] = os.getenv("ESPO_PASSWORD")
    
    return config


@pytest.fixture(scope="session")
def espo_client(espo_config) -> Generator[EspoCRMClient, None, None]:
    """
    Test session'ı boyunca kullanılacak EspoCRM client instance'ı
    """
    # Client'ı oluştur
    from espocrm.auth import APIKeyAuth, BasicAuth
    from espocrm.config import ClientConfig
    
    # Config oluştur
    config = ClientConfig(
        base_url=espo_config["url"],
        timeout=espo_config["timeout"],
        verify_ssl=True
    )
    
    # Authentication oluştur
    if "api_key" in espo_config:
        auth = APIKeyAuth(api_key=espo_config["api_key"])
    else:
        auth = BasicAuth(
            username=espo_config["username"],
            password=espo_config["password"]
        )
    
    # Client oluştur
    client = EspoCRMClient(
        base_url=espo_config["url"],
        auth=auth,
        config=config
    )
    
    # Debug modunu ayarla
    if espo_config["debug"]:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Bağlantıyı test et
    try:
        # Basit bir API çağrısı ile bağlantıyı doğrula
        client.list("Contact", max_size=1)
        print(f"✅ EspoCRM'e başarıyla bağlanıldı: {espo_config['url']}")
    except Exception as e:
        pytest.fail(f"EspoCRM'e bağlanılamadı: {e}")
    
    yield client
    
    # Cleanup (gerekirse)
    # Client kapatma işlemleri varsa burada yapılabilir


@pytest.fixture
def test_data_prefix():
    """
    Test verileri için kullanılacak prefix
    """
    return os.getenv("TEST_DATA_PREFIX", "TEST_")


@pytest.fixture
def clean_test_data(espo_client: EspoCRMClient, test_data_prefix: str):
    """
    Test sonrası test verilerini temizle
    """
    created_entities = []
    
    def track_entity(entity_type: str, entity_id: str):
        """Temizlenecek entity'yi takip et"""
        created_entities.append((entity_type, entity_id))
    
    yield track_entity
    
    # Test sonrası temizlik
    for entity_type, entity_id in created_entities:
        try:
            espo_client.delete(entity_type, entity_id)
            print(f"🧹 Temizlendi: {entity_type}/{entity_id}")
        except Exception as e:
            print(f"⚠️ Temizlenemedi: {entity_type}/{entity_id} - {e}")


@pytest.fixture
def sample_contact_data(test_data_prefix: str):
    """
    Test için örnek contact verisi
    """
    import uuid
    from datetime import datetime
    
    unique_id = str(uuid.uuid4())[:8]
    return {
        "firstName": f"{test_data_prefix}John_{unique_id}",
        "lastName": f"Doe_{unique_id}",
        "emailAddress": f"john.doe.{unique_id}@test.example.com",
        "phoneNumber": "+1 555 123 4567",
        "description": f"Test contact created at {datetime.now().isoformat()}"
    }


@pytest.fixture
def sample_account_data(test_data_prefix: str):
    """
    Test için örnek account verisi
    """
    import uuid
    from datetime import datetime
    
    unique_id = str(uuid.uuid4())[:8]
    return {
        "name": f"{test_data_prefix}Company_{unique_id}",
        "emailAddress": f"info@company-{unique_id}.example.com",
        "phoneNumber": "+1 555 987 6543",
        "website": f"https://company-{unique_id}.example.com",
        "description": f"Test account created at {datetime.now().isoformat()}"
    }


# Test sonuçları için hook'lar
def pytest_runtest_makereport(item, call):
    """Test sonuçlarını özelleştir"""
    if call.when == "call":
        if hasattr(item, "rep_call"):
            del item.rep_call
        item.rep_call = call


def pytest_runtest_teardown(item, nextitem):
    """Test teardown işlemleri"""
    if hasattr(item, "rep_call"):
        if item.rep_call.failed:
            print(f"\n❌ Test başarısız: {item.name}")
        elif item.rep_call.passed:
            print(f"\n✅ Test başarılı: {item.name}")
