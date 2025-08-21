"""
EspoCRM Main Client Module

Bu modül EspoCRM API istemcisinin ana sınıfını sağlar.
Authentication, logging, HTTP operations ve modüler client'ları yönetir.
"""

import threading
from typing import Any, Dict, Optional, Union
from contextlib import contextmanager
import logging

from .config import ClientConfig
from .auth.base import AuthenticationBase
from .utils.http import HTTPClient
from .utils.serializers import DataSerializer, parse_espocrm_response
from .utils.validators import validate_url, ValidationError
from .utils.helpers import generate_request_id, timing_decorator
from .exceptions import (
    EspoCRMError,
    EspoCRMConnectionError,
    EspoCRMAuthenticationError,
    create_exception_from_status_code
)

logger = logging.getLogger(__name__)


class EspoCRMClient:
    """
    EspoCRM API istemcisinin ana sınıfı.
    
    Authentication, HTTP operations, logging ve modüler client'ları yönetir.
    Context manager pattern'ı destekler ve thread-safe operations sağlar.
    
    Example:
        >>> from espocrm import EspoCRMClient, ClientConfig
        >>> from espocrm.auth import APIKeyAuth
        >>> 
        >>> config = ClientConfig(
        ...     base_url="https://your-espocrm.com",
        ...     api_key="your-api-key"
        ... )
        >>> auth = APIKeyAuth(api_key="your-api-key")
        >>> 
        >>> with EspoCRMClient(config.base_url, auth, config) as client:
        ...     # Use client
        ...     pass
    """
    
    def __init__(
        self,
        base_url: str,
        auth: AuthenticationBase,
        config: Optional[ClientConfig] = None
    ):
        """
        EspoCRM client'ını başlatır.
        
        Args:
            base_url: EspoCRM server'ın base URL'i
            auth: Authentication instance'ı
            config: Client konfigürasyonu (opsiyonel)
            
        Raises:
            ValidationError: Geçersiz URL
            EspoCRMAuthenticationError: Authentication hatası
        """
        # URL validation
        try:
            validate_url(base_url, require_https=False)
        except ValidationError as e:
            raise ValidationError(f"Invalid base URL: {e}")
        
        self.base_url = base_url.rstrip('/')
        self.auth = auth
        self.config = config or ClientConfig(base_url=base_url)
        
        # Logger setup
        self.logger = logging.getLogger('espocrm.client')
        
        # Thread safety
        self._lock = threading.RLock()
        self._closed = False
        
        # Request context
        self._request_context = threading.local()
        
        # Components initialization
        self._initialize_components()
        
        # Modüler client'lar (placeholder - gerçek implementasyonlar sonra eklenecek)
        self._initialize_clients()
        
        self.logger.info(
            f"EspoCRM client initialized - base_url: {self.base_url}, auth_type: {self.auth.get_auth_type()}"
        )
    
    def _initialize_components(self):
        """Core component'ları başlatır."""
        # HTTP client
        self.http_client = HTTPClient(
            base_url=f"{self.base_url}/api/v1",
            timeout=self.config.timeout,
            verify_ssl=self.config.verify_ssl,
            max_retries=self.config.max_retries,
            retry_delay=self.config.retry_delay,
            rate_limit_per_minute=self.config.rate_limit_per_minute,
            user_agent=self.config.user_agent,
            extra_headers=self.config.extra_headers
        )
        
        # Data serializer
        self.serializer = DataSerializer()
        
        # Request/response interceptors
        self._setup_interceptors()
    
    def _setup_interceptors(self):
        """HTTP request/response interceptor'larını ayarlar."""
        # Request interceptor - authentication headers ekle
        def auth_interceptor(prepared_request):
            # Authentication headers al
            auth_headers = self.auth.get_headers(
                method=prepared_request.method,
                uri=prepared_request.path_url or '/'
            )
            
            # Headers'ı güncelle
            if auth_headers:
                prepared_request.headers.update(auth_headers)
            
            # Request ID ekle
            request_id = self._get_request_id()
            if request_id:
                prepared_request.headers['X-Request-ID'] = request_id
            
            return prepared_request
        
        # Response interceptor - logging ve error handling
        def response_interceptor(response):
            # Response'u logla
            self.logger.debug(
                f"API response received - method: {response.request.method}, "
                f"url: {response.request.url}, status_code: {response.status_code}, "
                f"response_time_ms: {response.elapsed.total_seconds() * 1000:.2f}"
            )
            
            return response
        
        # Interceptor'ları ekle
        self.http_client.add_request_interceptor(auth_interceptor)
        self.http_client.add_response_interceptor(response_interceptor)
    
    def _initialize_clients(self):
        """Modüler client'ları başlatır."""
        # CRUD client'ı başlat
        from .clients.crud import CrudClient
        self.crud = CrudClient(self)
    
    def _get_request_id(self) -> Optional[str]:
        """Current request ID'sini döndürür."""
        return getattr(self._request_context, 'request_id', None)
    
    def _set_request_id(self, request_id: str):
        """Request ID'sini ayarlar."""
        self._request_context.request_id = request_id
    
    @contextmanager
    def request_context(self, request_id: Optional[str] = None):
        """
        Request context manager.
        
        Args:
            request_id: Request ID (opsiyonel, otomatik generate edilir)
            
        Example:
            >>> with client.request_context() as ctx:
            ...     # Request operations
            ...     pass
        """
        if request_id is None:
            request_id = generate_request_id()
        
        old_request_id = self._get_request_id()
        self._set_request_id(request_id)
        
        try:
            yield request_id
        finally:
            # Eski request ID'yi restore et
            if old_request_id:
                self._set_request_id(old_request_id)
            else:
                self._request_context.request_id = None
    
    @timing_decorator
    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        HTTP request gönderir ve response'u parse eder.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            headers: Ek HTTP headers
            **kwargs: Ek request parametreleri
            
        Returns:
            Parse edilmiş response data
            
        Raises:
            EspoCRMError: API hatası
            EspoCRMConnectionError: Bağlantı hatası
        """
        with self._lock:
            if self._closed:
                raise EspoCRMError("Client is closed")
        
        # Request context oluştur
        with self.request_context() as request_id:
            try:
                # Request'i logla
                self.logger.info(
                    f"API request started - method: {method}, endpoint: {endpoint}, request_id: {request_id}"
                )
                
                # Data serialization
                json_data = None
                if data:
                    json_data = self.serializer.transform_for_espocrm(data)
                
                # HTTP request gönder
                response = self.http_client.request(
                    method=method,
                    endpoint=endpoint,
                    params=params,
                    json=json_data,
                    headers=headers,
                    **kwargs
                )
                
                # Response parse et
                try:
                    response_data = response.json()
                except ValueError:
                    # JSON parse edilemezse raw text döndür
                    response_data = {'raw_response': response.text}
                
                # EspoCRM response format'ına çevir
                parsed_data = parse_espocrm_response(response_data)
                
                # Success log
                self.logger.info(
                    f"API request completed - method: {method}, endpoint: {endpoint}, "
                    f"status_code: {response.status_code}, request_id: {request_id}"
                )
                
                return parsed_data
                
            except Exception as e:
                # Error log
                self.logger.error(
                    f"API request failed - method: {method}, endpoint: {endpoint}, "
                    f"error: {str(e)}, request_id: {request_id}"
                )
                raise
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """GET request gönderir."""
        return self.request('GET', endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """POST request gönderir."""
        return self.request('POST', endpoint, data=data, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """PUT request gönderir."""
        return self.request('PUT', endpoint, data=data, **kwargs)
    
    def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """PATCH request gönderir."""
        return self.request('PATCH', endpoint, data=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE request gönderir."""
        return self.request('DELETE', endpoint, **kwargs)
    
    def test_connection(self) -> bool:
        """
        EspoCRM server'a bağlantıyı test eder.
        
        Returns:
            Bağlantı başarılı mı
            
        Raises:
            EspoCRMConnectionError: Bağlantı hatası
            EspoCRMAuthenticationError: Authentication hatası
        """
        try:
            # Basit bir endpoint'e request gönder
            response = self.get('App/user')
            return response.get('success', True)
            
        except EspoCRMAuthenticationError:
            self.logger.error("Authentication failed during connection test")
            raise
        except EspoCRMConnectionError:
            self.logger.error("Connection failed during connection test")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during connection test: {e}")
            raise EspoCRMConnectionError(f"Connection test failed: {e}")
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        EspoCRM server bilgilerini alır.
        
        Returns:
            Server bilgileri
        """
        try:
            return self.get('App/about')
        except Exception as e:
            self.logger.warning(f"Could not retrieve server info: {e}")
            return {}
    
    def close(self):
        """Client'ı kapatır ve kaynakları temizler."""
        with self._lock:
            if self._closed:
                return
            
            self._closed = True
            
            # HTTP client'ı kapat
            if hasattr(self, 'http_client'):
                self.http_client.close()
            
            self.logger.info("EspoCRM client closed")
    
    def is_closed(self) -> bool:
        """Client'ın kapalı olup olmadığını kontrol eder."""
        with self._lock:
            return self._closed
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"EspoCRMClient("
            f"base_url={self.base_url!r}, "
            f"auth_type={self.auth.get_auth_type()!r}, "
            f"closed={self._closed})"
        )


    # CRUD convenience methods
    def create_entity(self, entity_type: str, data, **kwargs):
        """Entity oluşturur (CRUD client'a delegate eder)."""
        return self.crud.create(entity_type, data, **kwargs)
    
    def get_entity(self, entity_type: str, entity_id: str, **kwargs):
        """Entity getirir (CRUD client'a delegate eder)."""
        return self.crud.read(entity_type, entity_id, **kwargs)
    
    def update_entity(self, entity_type: str, entity_id: str, data, **kwargs):
        """Entity günceller (CRUD client'a delegate eder)."""
        return self.crud.update(entity_type, entity_id, data, **kwargs)
    
    def delete_entity(self, entity_type: str, entity_id: str, **kwargs):
        """Entity siler (CRUD client'a delegate eder)."""
        return self.crud.delete(entity_type, entity_id, **kwargs)
    
    def list_entities(self, entity_type: str, search_params=None, **kwargs):
        """Entity listesi getirir (CRUD client'a delegate eder)."""
        return self.crud.list(entity_type, search_params=search_params, **kwargs)
    
    def search_entities(self, entity_type: str, search_params, **kwargs):
        """Entity arama yapar (CRUD client'a delegate eder)."""
        return self.crud.search(entity_type, search_params, **kwargs)
    
    def count_entities(self, entity_type: str, where=None, **kwargs):
        """Entity sayısını döndürür (CRUD client'a delegate eder)."""
        return self.crud.count(entity_type, where=where, **kwargs)
    
    def entity_exists(self, entity_type: str, entity_id: str, **kwargs):
        """Entity'nin var olup olmadığını kontrol eder (CRUD client'a delegate eder)."""
        return self.crud.exists(entity_type, entity_id, **kwargs)


def create_client(
    base_url: str,
    auth: AuthenticationBase,
    config: Optional[ClientConfig] = None,
    **kwargs
) -> EspoCRMClient:
    """
    EspoCRM client oluşturur.
    
    Args:
        base_url: EspoCRM server'ın base URL'i
        auth: Authentication instance'ı
        config: Client konfigürasyonu
        **kwargs: Ek parametreler
        
    Returns:
        EspoCRMClient instance'ı
        
    Example:
        >>> from espocrm.auth import APIKeyAuth
        >>> auth = APIKeyAuth(api_key="your-api-key")
        >>> client = create_client("https://your-espocrm.com", auth)
    """
    return EspoCRMClient(base_url, auth, config, **kwargs)


# Export edilecek sınıf ve fonksiyonlar
__all__ = [
    "EspoCRMClient",
    "create_client",
]