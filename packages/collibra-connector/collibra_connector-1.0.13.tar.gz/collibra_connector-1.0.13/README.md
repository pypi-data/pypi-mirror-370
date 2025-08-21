# Collibra Python Connector

An **UNOFFICIAL** comprehensive Python connector for the Collibra Data Governance Center API.

## Features

- 🚀 **Complete API Coverage**: Asset, Community, Domain, User, Responsibility, Workflow, Metadata, and Comment management
- 🔄 **Automatic Retry Logic**: Built-in retry mechanism for robust API calls
- ✅ **Input Validation**: Comprehensive parameter validation with clear error messages
- 🏗️ **Clean Architecture**: Well-structured, extensible codebase with separation of concerns
- 📝 **Type Hints**: Full type annotations for better IDE support
- 🛡️ **Error Handling**: Custom exception hierarchy for different error types
- 🔧 **Utility Functions**: Helper methods for complex operations and bulk operations

## Installation

```bash
pip install collibra-connector
```

## Quick Start

```python
from collibra_connector import CollibraConnector

# Initialize the connector
connector = CollibraConnector(
    api="https://your-collibra-instance.com",
    username="your-username",
    password="your-password",
    timeout=30
)

# Test connection
if connector.test_connection():
    print("Connected successfully!")

# Get all metadata
metadata = connector.metadata.get_collibra_metadata()
print(f"Found {len(metadata['AssetType'])} asset types")

# Find communities
communities = connector.community.find_communities()
for community in communities.get("results", []):
    print(f"Community: {community['name']}")
```

## API Reference

### Assets

```python
# Get an asset
asset = connector.asset.get_asset("asset-uuid")

# Create an asset
new_asset = connector.asset.add_asset(
    name="My New Asset",
    domain_id="domain-uuid",
    display_name="My Asset Display Name",
    type_id="asset-type-uuid"
)

# Find assets
assets = connector.asset.find_assets(
    community_id="community-uuid",
    asset_type_ids=["type-uuid-1", "type-uuid-2"]
)
```

### Communities

```python
# Get a community
community = connector.community.get_community("community-uuid")

# Find communities
communities = connector.community.find_communities()
```

### Domains

```python
# Get a domain
domain = connector.domain.get_domain("domain-uuid")

# Create a domain
new_domain = connector.domain.create_domain(
    name="My New Domain",
    community_id="community-uuid"
)
```

### Users

```python
# Get user by username
user_id = connector.user.get_user_by_username("username")

# Create a new user
new_user = connector.user.create_user(
    username="newuser",
    email_address="newuser@example.com"
)
```

### Complete Documentation

For comprehensive API documentation and examples, see the full README with all available methods for:
- Asset management (CRUD operations, attributes, activities)
- Community and Domain operations
- User management
- Responsibility assignments
- Workflow operations
- Comment management
- Metadata retrieval
- Utility functions for bulk operations

## Error Handling

```python
from collibra_connector.api.Exceptions import (
    CollibraAPIError,
    UnauthorizedError,
    NotFoundError
)

try:
    asset = connector.asset.get_asset("invalid-uuid")
except NotFoundError:
    print("Asset not found")
except CollibraAPIError as e:
    print(f"API error: {e}")
```

## Requirements

- Python 3.8+
- requests >= 2.20.0