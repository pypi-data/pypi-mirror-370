# EspoCRM Python Client Documentation

Simple and easy-to-use Python client for EspoCRM API with full CRUD support.

## Overview

EspoCRM Python Client is a lightweight library that provides a simple interface for interacting with EspoCRM's REST API. It supports all basic CRUD operations (Create, Read, Update, Delete) and includes proper authentication handling.

## Features

- ✅ Full CRUD operations support
- ✅ API Key authentication
- ✅ Request/Response interceptors
- ✅ Proper error handling
- ✅ Connection pooling
- ✅ Rate limiting support
- ✅ Type hints for better IDE support

## Quick Start

### Installation

```bash
pip install espocrm-client
```

### Basic Usage

```python
from espocrm.client import EspoCRMClient
from espocrm.auth import APIKeyAuth
from espocrm.config import ClientConfig

# Configure client
config = ClientConfig(
    base_url="https://your-espocrm.com",
    api_key="your-api-key"
)

auth = APIKeyAuth(api_key="your-api-key")

# Create client
client = EspoCRMClient(
    base_url=config.base_url,
    auth=auth,
    config=config
)

# Create a record
contact = client.crud.create("Contact", {
    "firstName": "John",
    "lastName": "Doe",
    "emailAddress": "john.doe@example.com"
})

print(f"Created contact with ID: {contact.get_id()}")
```

## Documentation

- [CRUD Operations](crud.md) - Complete guide to CRUD operations

## Support

- **GitHub Issues**: Report bugs and request features
- **EspoCRM Documentation**: [Official API docs](https://docs.espocrm.com/development/api/)

## License

This project is licensed under the MIT License.
