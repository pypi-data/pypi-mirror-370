# CRUD Operations Guide

This guide covers all CRUD (Create, Read, Update, Delete) operations available in the EspoCRM Python Client.

## Table of Contents

- [Basic Setup](#basic-setup)
- [Create Operations](#create-operations)
- [Read Operations](#read-operations)
- [Update Operations](#update-operations)
- [Delete Operations](#delete-operations)
- [List Operations](#list-operations)
- [Search Operations](#search-operations)
- [Error Handling](#error-handling)

## Basic Setup

Before performing CRUD operations, you need to initialize the client:

```python
from espocrm.client import EspoCRMClient
from espocrm.auth import APIKeyAuth
from espocrm.config import ClientConfig

# Setup configuration
config = ClientConfig(
    base_url="https://your-espocrm.com",
    api_key="your-api-key"
)

# Setup authentication
auth = APIKeyAuth(api_key="your-api-key")

# Create client
client = EspoCRMClient(
    base_url=config.base_url,
    auth=auth,
    config=config
)
```

## Create Operations

### Creating a Single Record

```python
# Create a Contact
contact_data = {
    "firstName": "John",
    "lastName": "Doe",
    "emailAddress": "john.doe@example.com",
    "phoneNumber": "+1 555 123 4567",
    "title": "Software Engineer"
}

response = client.crud.create("Contact", contact_data)
contact_id = response.get_id()
print(f"Created contact with ID: {contact_id}")
```

### Creating Different Entity Types

```python
# Create an Account
account = client.crud.create("Account", {
    "name": "Acme Corporation",
    "website": "https://acme.com",
    "type": "Customer",
    "industry": "Technology"
})

# Create a Lead
lead = client.crud.create("Lead", {
    "firstName": "Jane",
    "lastName": "Smith",
    "emailAddress": "jane.smith@example.com",
    "status": "New",
    "source": "Website"
})

# Create an Opportunity
opportunity = client.crud.create("Opportunity", {
    "name": "New Business Deal",
    "amount": 50000,
    "stage": "Prospecting",
    "probability": 25,
    "closeDate": "2024-12-31"
})
```

## Read Operations

### Reading a Single Record

```python
# Read a contact by ID
contact = client.crud.read("Contact", contact_id)

# Access data
print(f"Name: {contact.data.get('firstName')} {contact.data.get('lastName')}")
print(f"Email: {contact.data.get('emailAddress')}")
print(f"Phone: {contact.data.get('phoneNumber')}")
```

### Reading with Field Selection

```python
# Read only specific fields
contact = client.crud.read(
    "Contact",
    contact_id,
    select=["firstName", "lastName", "emailAddress"]
)
```

## Update Operations

### Updating a Record

```python
# Update contact information
updated = client.crud.update(
    "Contact",
    contact_id,
    {
        "title": "Senior Software Engineer",
        "phoneNumber": "+1 555 987 6543",
        "description": "Updated via API"
    }
)

if updated:
    print("Contact updated successfully")
```

### Partial vs Full Update

```python
# Partial update (PATCH) - default
client.crud.update("Contact", contact_id, {"title": "New Title"})

# Full update (PUT) - replaces entire record
full_data = {
    "firstName": "John",
    "lastName": "Doe",
    "emailAddress": "john.doe@example.com",
    # ... all required fields
}
client.crud.update("Contact", contact_id, full_data, partial=False)
```

## Delete Operations

### Deleting a Record

```python
# Delete a contact
success = client.crud.delete("Contact", contact_id)

if success:
    print("Contact deleted successfully")
else:
    print("Failed to delete contact")
```

### Safe Delete with Existence Check

```python
# Check if record exists before deleting
try:
    contact = client.crud.read("Contact", contact_id)
    if contact:
        client.crud.delete("Contact", contact_id)
        print("Contact deleted")
except Exception as e:
    print(f"Contact not found or already deleted: {e}")
```

## List Operations

### Basic Listing

```python
# List contacts with default pagination
contacts = client.crud.list("Contact")

print(f"Total contacts: {contacts.total}")
for contact in contacts.list:
    print(f"- {contact.get('firstName')} {contact.get('lastName')}")
```

### Listing with Parameters

```python
# List with pagination and sorting
contacts = client.crud.list(
    "Contact",
    offset=0,
    max_size=20,
    order_by="createdAt",
    order="desc"
)

# List with field selection
contacts = client.crud.list(
    "Contact",
    select=["id", "firstName", "lastName", "emailAddress"],
    max_size=50
)
```

## Search Operations

### Simple Search

```python
from espocrm.models.search import SearchParams

# Search for contacts with specific criteria
search_params = SearchParams()
search_params.where = [
    {
        "type": "contains",
        "attribute": "emailAddress",
        "value": "@example.com"
    }
]

results = client.crud.search("Contact", search_params)
print(f"Found {len(results.list)} contacts")
```

### Advanced Search

```python
# Complex search with multiple conditions
search_params = SearchParams()
search_params.where = [
    {
        "type": "and",
        "value": [
            {
                "type": "equals",
                "attribute": "type",
                "value": "Customer"
            },
            {
                "type": "greater",
                "attribute": "createdAt",
                "value": "2024-01-01"
            }
        ]
    }
]
search_params.order_by = "name"
search_params.order = "asc"
search_params.offset = 0
search_params.max_size = 100

accounts = client.crud.search("Account", search_params)
```

### Search Operators

Common search operators you can use:

- `equals` - Exact match
- `notEquals` - Not equal to
- `contains` - Contains substring
- `startsWith` - Starts with
- `endsWith` - Ends with
- `greater` - Greater than
- `less` - Less than
- `greaterOrEquals` - Greater than or equal
- `lessOrEquals` - Less than or equal
- `in` - In array
- `notIn` - Not in array
- `isNull` - Is null
- `isNotNull` - Is not null
- `isTrue` - Boolean true
- `isFalse` - Boolean false

## Error Handling

### Basic Error Handling

```python
from espocrm.exceptions import (
    EspoCRMError,
    EspoCRMNotFoundError,
    EspoCRMValidationError,
    EspoCRMAuthenticationError
)

try:
    contact = client.crud.read("Contact", "invalid-id")
except EspoCRMNotFoundError:
    print("Contact not found")
except EspoCRMAuthenticationError:
    print("Authentication failed - check your API key")
except EspoCRMValidationError as e:
    print(f"Validation error: {e.message}")
except EspoCRMError as e:
    print(f"General API error: {e}")
```

### Handling Validation Errors

```python
try:
    # Try to create contact without required fields
    contact = client.crud.create("Contact", {
        "firstName": "John"
        # Missing required fields
    })
except EspoCRMValidationError as e:
    print(f"Validation failed: {e.message}")
    if hasattr(e, 'validation_errors'):
        for field, error in e.validation_errors.items():
            print(f"  - {field}: {error}")
```

## Complete Example

Here's a complete example demonstrating all CRUD operations:

```python
from espocrm.client import EspoCRMClient
from espocrm.auth import APIKeyAuth
from espocrm.config import ClientConfig
from espocrm.models.search import SearchParams
from espocrm.exceptions import EspoCRMError

# Setup
config = ClientConfig(
    base_url="https://your-espocrm.com",
    api_key="your-api-key"
)
auth = APIKeyAuth(api_key="your-api-key")
client = EspoCRMClient(config.base_url, auth, config)

try:
    # CREATE
    print("Creating contact...")
    contact = client.crud.create("Contact", {
        "firstName": "John",
        "lastName": "Doe",
        "emailAddress": "john.doe@example.com",
        "phoneNumber": "+1 555 123 4567"
    })
    contact_id = contact.get_id()
    print(f"✓ Created contact: {contact_id}")
    
    # READ
    print("\nReading contact...")
    contact_data = client.crud.read("Contact", contact_id)
    print(f"✓ Contact: {contact_data.data.get('firstName')} {contact_data.data.get('lastName')}")
    
    # UPDATE
    print("\nUpdating contact...")
    client.crud.update("Contact", contact_id, {
        "title": "Senior Developer",
        "description": "Updated via API"
    })
    print("✓ Contact updated")
    
    # SEARCH
    print("\nSearching contacts...")
    search = SearchParams()
    search.where = [{"type": "contains", "attribute": "emailAddress", "value": "@example.com"}]
    results = client.crud.search("Contact", search)
    print(f"✓ Found {len(results.list)} contacts")
    
    # LIST
    print("\nListing contacts...")
    all_contacts = client.crud.list("Contact", max_size=10)
    print(f"✓ Total contacts: {all_contacts.total}")
    
    # DELETE
    print("\nDeleting contact...")
    client.crud.delete("Contact", contact_id)
    print("✓ Contact deleted")
    
except EspoCRMError as e:
    print(f"Error: {e}")
```

## Tips and Best Practices

1. **Always handle exceptions** - The API can return various errors that should be handled gracefully
2. **Use field selection** - When listing records, only request the fields you need to improve performance
3. **Implement pagination** - For large datasets, always use pagination to avoid memory issues
4. **Cache responses when appropriate** - If data doesn't change frequently, consider caching responses
5. **Use proper authentication** - Always use API keys instead of username/password when possible
6. **Log operations** - Keep logs of CRUD operations for debugging and auditing purposes

## Next Steps

- Review the main [README](../README.md) for installation and configuration details
- Check the [test examples](../tests/) for more usage patterns
- Refer to the [EspoCRM API documentation](https://docs.espocrm.com/development/api/) for advanced features
