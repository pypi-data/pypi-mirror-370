# EspoCRM Python Client

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![EspoCRM](https://img.shields.io/badge/EspoCRM-7.0%2B-orange)](https://www.espocrm.com)

**Modern, Type-Safe, Production-Ready Python Client for EspoCRM API**

[Installation](#installation) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Examples](#examples) • [API Reference](#api-reference)

</div>

---

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [CRUD Operations](#crud-operations)
- [Advanced Features](#advanced-features)
- [Error Handling](#error-handling)
- [Configuration](#configuration)
- [Testing](#testing)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### Core Features
- 🔐 **Multiple Authentication Methods**: API Key, HMAC, Basic Auth
- 📝 **Full CRUD Operations**: Create, Read, Update, Delete, List, Search
- 🔄 **Automatic Retry Logic**: With exponential backoff
- 🎯 **Type Safety**: Full type hints and Pydantic models
- 🚀 **Async Support**: Coming soon
- 📊 **Bulk Operations**: Efficient batch processing
- 🔍 **Advanced Search**: Complex queries with SearchParams
- ⚡ **Connection Pooling**: Optimized HTTP connections
- 🛡️ **Comprehensive Error Handling**: Detailed exceptions
- 📈 **Rate Limiting**: Built-in rate limit management
- 🧪 **Well Tested**: Extensive test coverage

### Architecture
- **Modular Design**: Separate modules for auth, models, utils
- **Interceptor Pattern**: Request/Response interceptors
- **Factory Pattern**: Entity factories
- **Builder Pattern**: Query builders
- **Strategy Pattern**: Authentication strategies

---

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install espocrm-python-client
```

### From Source
```bash
git clone https://github.com/yourusername/espocrm-client.git
cd espocrm-client
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/yourusername/espocrm-client.git
cd espocrm-client
pip install -e ".[dev]"
```

### Requirements
- Python 3.8+
- requests >= 2.31.0
- pydantic >= 2.5.0
- structlog >= 23.2.0
- typing-extensions >= 4.8.0

---

## 🚀 Quick Start

### Basic Usage

```python
from espocrm import EspoCRMClient
from espocrm.auth import APIKeyAuth
from espocrm.config import ClientConfig

# Configure authentication
auth = APIKeyAuth(api_key="your-api-key")

# Configure client
config = ClientConfig(
    base_url="https://your-espocrm.com",
    api_key="your-api-key",
    timeout=30,
    verify_ssl=True
)

# Create client
client = EspoCRMClient(
    base_url="https://your-espocrm.com",
    auth=auth,
    config=config
)

# Create a contact
contact = client.crud.create("Contact", {
    "firstName": "John",
    "lastName": "Doe",
    "emailAddress": "john.doe@example.com"
})

print(f"Created contact with ID: {contact.get_id()}")
```

### Using Context Manager

```python
from espocrm import EspoCRMClient
from espocrm.auth import APIKeyAuth
from espocrm.config import ClientConfig

config = ClientConfig(
    base_url="https://your-espocrm.com",
    api_key="your-api-key"
)

auth = APIKeyAuth(api_key="your-api-key")

with EspoCRMClient(config.base_url, auth, config) as client:
    # Client will be automatically closed after the block
    contacts = client.crud.list("Contact", max_size=10)
    for contact in contacts.list:
        print(f"{contact.firstName} {contact.lastName}")
```

---

## 🔐 Authentication

### API Key Authentication (Recommended)

```python
from espocrm.auth import APIKeyAuth

# Create API User in EspoCRM Admin Panel
auth = APIKeyAuth(api_key="your-api-key-from-espocrm")
```

### HMAC Authentication (Most Secure)

```python
from espocrm.auth import HMACAuth

auth = HMACAuth(
    api_key="your-api-key",
    secret_key="your-secret-key"
)
```

### Basic Authentication

```python
from espocrm.auth import BasicAuth

# Using password
auth = BasicAuth(
    username="admin",
    password="your-password"
)

# Using token (recommended over password)
auth = BasicAuth(
    username="admin",
    token="your-auth-token"
)
```

### Custom Authentication

```python
from espocrm.auth.base import AuthenticationBase

class CustomAuth(AuthenticationBase):
    def get_headers(self, method: str, uri: str) -> Dict[str, str]:
        return {
            "X-Custom-Auth": "your-custom-token"
        }
```

---

## 📝 CRUD Operations

### Create

```python
# Simple create
contact = client.crud.create("Contact", {
    "firstName": "Jane",
    "lastName": "Smith",
    "emailAddress": "jane.smith@example.com",
    "phoneNumber": "+1 555 123 4567",
    "title": "Sales Manager",
    "description": "VIP Customer"
})

# Using models
from espocrm.models.entities import Contact

contact_model = Contact(
    firstName="Jane",
    lastName="Smith",
    emailAddress="jane.smith@example.com"
)

contact = client.crud.create("Contact", contact_model)
```

### Read

```python
# Get by ID
contact = client.crud.read("Contact", "contact-id-here")

# Get specific fields only
contact = client.crud.read(
    "Contact", 
    "contact-id-here",
    select=["firstName", "lastName", "emailAddress"]
)

# Access data
print(contact.data.firstName)
print(contact.data.emailAddress)
```

### Update

```python
# Update specific fields
updated = client.crud.update(
    "Contact",
    "contact-id-here",
    {
        "title": "Senior Sales Manager",
        "phoneNumber": "+1 555 987 6543"
    }
)

# Full update (PUT)
updated = client.crud.update(
    "Contact",
    "contact-id-here",
    full_contact_data,
    partial=False  # Use PUT instead of PATCH
)
```

### Delete

```python
# Delete by ID
success = client.crud.delete("Contact", "contact-id-here")

if success:
    print("Contact deleted successfully")
```

### List

```python
# Simple list
contacts = client.crud.list("Contact", max_size=50)

for contact in contacts.list:
    print(f"{contact.firstName} {contact.lastName}")

# With pagination
contacts = client.crud.list(
    "Contact",
    offset=0,
    max_size=20,
    order_by="createdAt",
    order="desc"
)

print(f"Total contacts: {contacts.total}")
print(f"Current page: {len(contacts.list)}")
```

### Search

```python
from espocrm.models.search import SearchParams

# Simple search
search_params = SearchParams(
    query="john",
    maxSize=10
)

results = client.crud.search("Contact", search_params)

# Advanced search with filters
search_params = SearchParams()
search_params.add_equals("type", "Customer")
search_params.add_contains("name", "Corp")
search_params.add_greater_than("createdAt", "2024-01-01")
search_params.set_order("createdAt", "desc")
search_params.set_pagination(0, 50)

results = client.crud.search("Account", search_params)

# Using where clauses
from espocrm.models.search import equals, contains, in_array

search_params = SearchParams()
search_params.add_where_clause(equals("status", "Active"))
search_params.add_where_clause(contains("email", "@company.com"))
search_params.add_where_clause(in_array("type", ["Customer", "Partner"]))

results = client.crud.search("Contact", search_params)
```

---

## 🔧 Advanced Features

### Bulk Operations

```python
# Bulk create
contacts_data = [
    {"firstName": "Alice", "lastName": "Johnson"},
    {"firstName": "Bob", "lastName": "Williams"},
    {"firstName": "Charlie", "lastName": "Brown"}
]

result = client.crud.bulk_create("Contact", contacts_data)
print(f"Created: {result.successful}/{result.total}")

# Bulk update
updates = [
    {"id": "id1", "status": "Active"},
    {"id": "id2", "status": "Active"},
    {"id": "id3", "status": "Inactive"}
]

result = client.crud.bulk_update("Contact", updates)

# Bulk delete
ids = ["id1", "id2", "id3"]
result = client.crud.bulk_delete("Contact", ids)

# Check results
for item in result.results:
    if item["success"]:
        print(f"✓ Processed: {item['id']}")
    else:
        print(f"✗ Failed: {item['id']} - {item.get('error')}")
```

### Related Records

```python
# Get account with contacts
account = client.crud.read("Account", "account-id")

# Get related contacts
contacts = client.crud.list(
    "Contact",
    where=[{
        "type": "equals",
        "attribute": "accountId",
        "value": "account-id"
    }]
)

# Link records
client.request(
    "POST",
    f"Account/{account_id}/contacts",
    json={"id": contact_id}
)

# Unlink records
client.request(
    "DELETE",
    f"Account/{account_id}/contacts/{contact_id}"
)
```

### Custom Entities

```python
# Work with custom entities
custom_record = client.crud.create("CustomEntity", {
    "name": "Custom Record",
    "customField1": "Value 1",
    "customField2": 123
})

# List custom entity records
records = client.crud.list("CustomEntity", max_size=100)
```

### Stream (Activity Feed)

```python
# Get stream
stream = client.request("GET", "Stream")

# Post to stream
client.request("POST", "Note", json={
    "post": "This is a note",
    "type": "Post",
    "parentType": "Account",
    "parentId": "account-id"
})
```

### File Attachments

```python
import base64

# Upload attachment
with open("document.pdf", "rb") as f:
    file_content = base64.b64encode(f.read()).decode()

attachment = client.request("POST", "Attachment", json={
    "name": "document.pdf",
    "type": "application/pdf",
    "file": file_content,
    "parentType": "Contact",
    "parentId": "contact-id"
})

# Download attachment
attachment_data = client.request("GET", f"Attachment/{attachment_id}")
file_content = base64.b64decode(attachment_data["file"])
```

### Request Interceptors

```python
# Add custom headers to all requests
def add_custom_header(request):
    request.headers["X-Custom-Header"] = "custom-value"
    return request

client.http_client.add_request_interceptor(add_custom_header)

# Log all responses
def log_response(response):
    print(f"Response: {response.status_code}")
    return response

client.http_client.add_response_interceptor(log_response)
```

### Rate Limiting

```python
# Configure rate limiting
config = ClientConfig(
    base_url="https://your-espocrm.com",
    api_key="your-api-key",
    rate_limit_per_minute=60  # Max 60 requests per minute
)

# Handle rate limit errors
from espocrm.exceptions import EspoCRMRateLimitError

try:
    contacts = client.crud.list("Contact")
except EspoCRMRateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after} seconds")
    time.sleep(e.retry_after)
    contacts = client.crud.list("Contact")
```

---

## ⚠️ Error Handling

### Exception Hierarchy

```python
from espocrm.exceptions import (
    EspoCRMError,           # Base exception
    EspoCRMAPIError,        # API errors
    EspoCRMAuthenticationError,  # 401 errors
    EspoCRMForbiddenError,  # 403 errors
    EspoCRMNotFoundError,   # 404 errors
    EspoCRMValidationError, # 400 validation errors
    EspoCRMRateLimitError,  # 429 rate limit errors
    EspoCRMServerError,     # 5xx server errors
    EspoCRMConnectionError  # Connection errors
)
```

### Error Handling Examples

```python
from espocrm.exceptions import *

try:
    contact = client.crud.read("Contact", "invalid-id")
except EspoCRMNotFoundError:
    print("Contact not found")
except EspoCRMAuthenticationError:
    print("Authentication failed - check your API key")
except EspoCRMValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Fields: {e.validation_errors}")
except EspoCRMServerError as e:
    print(f"Server error: {e.status_code} - {e.message}")
except EspoCRMConnectionError:
    print("Connection failed - check network")
except EspoCRMError as e:
    print(f"General error: {e}")
```

### Retry on Errors

```python
from espocrm.utils.retry import retry_on_error

@retry_on_error(max_retries=3, delay=1.0)
def create_contact(client, data):
    return client.crud.create("Contact", data)

# Or use built-in retry
config = ClientConfig(
    base_url="https://your-espocrm.com",
    api_key="your-api-key",
    max_retries=3,
    retry_delay=1.0
)
```

---

## ⚙️ Configuration

### Client Configuration

```python
from espocrm.config import ClientConfig

config = ClientConfig(
    # Required
    base_url="https://your-espocrm.com",
    
    # Authentication (one of these)
    api_key="your-api-key",
    # OR
    username="admin",
    password="password",
    
    # Optional settings
    timeout=30,                    # Request timeout in seconds
    verify_ssl=True,               # SSL certificate verification
    max_retries=3,                 # Maximum retry attempts
    retry_delay=1.0,              # Delay between retries
    rate_limit_per_minute=None,   # Rate limiting
    user_agent="MyApp/1.0",       # Custom user agent
    extra_headers={                # Additional headers
        "X-Custom": "value"
    },
    pool_connections=10,           # Connection pool size
    pool_maxsize=10,              # Max pool size
    
    # Logging
    log_level="INFO",             # Logging level
    log_requests=False,           # Log all requests
    log_responses=False,          # Log all responses
)
```

### Environment Variables

```bash
# .env file
ESPO_URL=https://your-espocrm.com
ESPO_API_KEY=your-api-key
# OR
ESPO_USERNAME=admin
ESPO_PASSWORD=your-password

# Optional
ESPO_TIMEOUT=30
ESPO_VERIFY_SSL=true
ESPO_MAX_RETRIES=3
```

```python
import os
from dotenv import load_dotenv

load_dotenv()

config = ClientConfig(
    base_url=os.getenv("ESPO_URL"),
    api_key=os.getenv("ESPO_API_KEY")
)
```

### Logging Configuration

```python
import logging
import structlog

# Standard logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Structured logging with structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
```

---

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=espocrm --cov-report=html

# Run specific test
pytest tests/test_crud.py::TestContactCRUD::test_create_contact

# Run with verbose output
pytest -v -s
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch
from espocrm import EspoCRMClient

@pytest.fixture
def mock_client():
    """Create a mock client for testing"""
    with patch('espocrm.client.EspoCRMClient') as mock:
        client = mock.return_value
        client.crud.create.return_value = {"id": "test-id"}
        yield client

def test_create_contact(mock_client):
    """Test contact creation"""
    result = mock_client.crud.create("Contact", {
        "firstName": "Test"
    })
    
    assert result["id"] == "test-id"
    mock_client.crud.create.assert_called_once()
```

### Integration Tests

```python
# tests/integration/test_real_api.py
import os
import pytest
from espocrm import EspoCRMClient
from espocrm.auth import APIKeyAuth
from espocrm.config import ClientConfig

@pytest.mark.integration
def test_real_api_connection():
    """Test real API connection"""
    config = ClientConfig(
        base_url=os.getenv("ESPO_TEST_URL"),
        api_key=os.getenv("ESPO_TEST_API_KEY")
    )
    
    auth = APIKeyAuth(api_key=os.getenv("ESPO_TEST_API_KEY"))
    
    with EspoCRMClient(config.base_url, auth, config) as client:
        # Test connection
        result = client.test_connection()
        assert result is True
        
        # Test CRUD
        contact = client.crud.create("Contact", {
            "firstName": "Test",
            "lastName": "User"
        })
        assert contact.get_id() is not None
        
        # Cleanup
        client.crud.delete("Contact", contact.get_id())
```

---

## 📚 API Reference

### Main Classes

#### EspoCRMClient
Main client class for interacting with EspoCRM API.

```python
class EspoCRMClient:
    def __init__(self, base_url: str, auth: AuthenticationBase, config: ClientConfig = None)
    def test_connection(self) -> bool
    def get_server_info(self) -> Dict[str, Any]
    def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]
    def close(self)
```

#### CrudClient
CRUD operations client.

```python
class CrudClient:
    def create(self, entity_type: str, data: Union[Dict, EntityRecord]) -> EntityResponse
    def read(self, entity_type: str, entity_id: str, select: List[str] = None) -> EntityResponse
    def update(self, entity_type: str, entity_id: str, data: Union[Dict, EntityRecord], partial: bool = True) -> EntityResponse
    def delete(self, entity_type: str, entity_id: str) -> bool
    def list(self, entity_type: str, search_params: SearchParams = None, **kwargs) -> ListResponse
    def search(self, entity_type: str, search_params: SearchParams) -> ListResponse
    def bulk_create(self, entity_type: str, entities: List[Union[Dict, EntityRecord]]) -> BulkOperationResult
    def bulk_update(self, entity_type: str, updates: List[Dict], partial: bool = True) -> BulkOperationResult
    def bulk_delete(self, entity_type: str, entity_ids: List[str]) -> BulkOperationResult
    def count(self, entity_type: str, where: List[Dict] = None) -> int
    def exists(self, entity_type: str, entity_id: str) -> bool
```

#### SearchParams
Search parameters builder.

```python
class SearchParams:
    def __init__(self, query: str = None, maxSize: int = None, offset: int = None)
    def add_where_clause(self, clause: WhereClause)
    def add_equals(self, field: str, value: Any)
    def add_not_equals(self, field: str, value: Any)
    def add_contains(self, field: str, value: str)
    def add_starts_with(self, field: str, value: str)
    def add_ends_with(self, field: str, value: str)
    def add_greater_than(self, field: str, value: Any)
    def add_less_than(self, field: str, value: Any)
    def add_in_array(self, field: str, values: List[Any])
    def add_not_in_array(self, field: str, values: List[Any])
    def add_is_null(self, field: str)
    def add_is_not_null(self, field: str)
    def set_order(self, field: str, direction: str = "asc")
    def set_pagination(self, offset: int, limit: int)
    def to_query_params(self) -> Dict[str, Any]
```

### Models

#### EntityResponse
Response wrapper for single entity operations.

```python
class EntityResponse:
    data: Dict[str, Any]
    entity_type: str
    
    def get_id(self) -> str
    def get_field(self, field: str) -> Any
    def to_dict(self) -> Dict[str, Any]
```

#### ListResponse
Response wrapper for list operations.

```python
class ListResponse:
    list: List[Dict[str, Any]]
    total: int
    entity_type: str
    
    def get_entities(self) -> List[EntityRecord]
    def get_ids(self) -> List[str]
    def is_empty(self) -> bool
```

#### BulkOperationResult
Result of bulk operations.

```python
class BulkOperationResult:
    success: bool
    total: int
    successful: int
    failed: int
    results: List[Dict[str, Any]]
    errors: List[Dict[str, Any]] = None
```

### Authentication Classes

```python
# API Key Authentication
class APIKeyAuth(AuthenticationBase):
    def __init__(self, api_key: str)

# HMAC Authentication
class HMACAuth(AuthenticationBase):
    def __init__(self, api_key: str, secret_key: str)

# Basic Authentication
class BasicAuth(AuthenticationBase):
    def __init__(self, username: str, password: str = None, token: str = None)
```

### Exception Classes

```python
class EspoCRMError(Exception): ...
class EspoCRMAPIError(EspoCRMError): ...
class EspoCRMAuthenticationError(EspoCRMAPIError): ...  # 401
class EspoCRMForbiddenError(EspoCRMAPIError): ...       # 403
class EspoCRMNotFoundError(EspoCRMAPIError): ...        # 404
class EspoCRMValidationError(EspoCRMAPIError): ...      # 400
class EspoCRMRateLimitError(EspoCRMAPIError): ...       # 429
class EspoCRMServerError(EspoCRMAPIError): ...          # 5xx
class EspoCRMConnectionError(EspoCRMError): ...
```

---

## 📘 Examples

### Complete CRUD Example

```python
from espocrm import EspoCRMClient
from espocrm.auth import APIKeyAuth
from espocrm.config import ClientConfig
from espocrm.models.search import SearchParams
from espocrm.exceptions import EspoCRMNotFoundError

# Setup
config = ClientConfig(
    base_url="https://your-espocrm.com",
    api_key="your-api-key"
)
auth = APIKeyAuth(api_key="your-api-key")

with EspoCRMClient(config.base_url, auth, config) as client:
    # CREATE
    print("Creating contact...")
    contact = client.crud.create("Contact", {
        "firstName": "John",
        "lastName": "Doe",
        "emailAddress": "john.doe@example.com",
        "phoneNumber": "+1 555 123 4567",
        "title": "CEO",
        "addressStreet": "123 Main St",
        "addressCity": "New York",
        "addressCountry": "USA"
    })
    contact_id = contact.get_id()
    print(f"✓ Created contact: {contact_id}")
    
    # READ
    print("\nReading contact...")
    fetched = client.crud.read("Contact", contact_id)
    print(f"✓ Contact name: {fetched.data.firstName} {fetched.data.lastName}")
    
    # UPDATE
    print("\nUpdating contact...")
    updated = client.crud.update("Contact", contact_id, {
        "title": "CTO",
        "description": "Updated via API"
    })
    print(f"✓ Updated title to: {updated.data.title}")
    
    # SEARCH
    print("\nSearching contacts...")
    search = SearchParams(query="john", maxSize=5)
    results = client.crud.search("Contact", search)
    print(f"✓ Found {len(results.list)} contacts")
    
    # LIST
    print("\nListing all contacts...")
    all_contacts = client.crud.list("Contact", max_size=10)
    print(f"✓ Total contacts: {all_contacts.total}")
    
    # DELETE
    print("\nDeleting contact...")
    deleted = client.crud.delete("Contact", contact_id)
    print(f"✓ Contact deleted: {deleted}")
    
    # VERIFY DELETION
    print("\nVerifying deletion...")
    try:
        client.crud.read("Contact", contact_id)
        print("✗ Contact still exists!")
    except EspoCRMNotFoundError:
        print("✓ Contact successfully deleted")
```

### Account with Contacts Example

```python
# Create account
account = client.crud.create("Account", {
    "name": "Acme Corporation",
    "website": "https://acme.com",
    "type": "Customer",
    "industry": "Technology"
})

# Create contacts for the account
contacts = []
for i in range(3):
    contact = client.crud.create("Contact", {
        "firstName": f"Employee {i+1}",
        "lastName": "Smith",
        "accountId": account.get_id(),
        "emailAddress": f"employee{i+1}@acme.com"
    })
    contacts.append(contact)

# Get account with related contacts
account_data = client.crud.read("Account", account.get_id())
related_contacts = client.crud.list(
    "Contact",
    where=[{
        "type": "equals",
        "attribute": "accountId",
        "value": account.get_id()
    }]
)

print(f"Account: {account_data.data.name}")
print(f"Contacts: {related_contacts.total}")
for contact in related_contacts.list:
    print(f"  - {contact.firstName} {contact.lastName}")
```

### Lead Conversion Example

```python
# Create a lead
lead = client.crud.create("Lead", {
    "firstName": "Jane",
    "lastName": "Prospect",
    "emailAddress": "jane@prospect.com",
    "companyName": "Prospect Inc",
    "title": "CEO",
    "status": "New"
})

# Update lead status
client.crud.update("Lead", lead.get_id(), {
    "status": "Assigned",
    "assignedUserId": "user-id"
})

# Convert lead to contact and account
conversion_result = client.request(
    "POST",
    f"Lead/{lead.get_id()}/convert",
    json={
        "createAccount": True,
        "createContact": True,
        "accountName": "Prospect Inc",
        "opportunityName": "New Opportunity"
    }
)

print(f"Lead converted:")
print(f"  Account ID: {conversion_result.get('accountId')}")
print(f"  Contact ID: {conversion_result.get('contactId')}")
print(f"  Opportunity ID: {conversion_result.get('opportunityId')}")
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/espocrm-client.git
cd espocrm-client

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 espocrm
mypy espocrm

# Format code
black espocrm
isort espocrm
```

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- EspoCRM Team for the excellent CRM platform
- All contributors who have helped improve this library
- Python community for the amazing ecosystem

---

## 📞 Support

- **Documentation**: [Full Documentation](https://espocrm-python-client.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/yourusername/espocrm-client/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/espocrm-client/discussions)
- **Email**: support@example.com

---

<div align="center">

**Made with ❤️ by the Open Source Community**

[⬆ Back to Top](#espocrm-python-client)

</div>
