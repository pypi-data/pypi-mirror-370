# Listings DB API Client

A Python client library for the Finder property listings database API.

## Installation

```bash
pip install listings-db-api-client
```

## Usage

```python
from listings_db_api_client import ListingsDBAPIClient

# Initialize client
client = ListingsDBAPIClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Get listings
listings = client.get_listings(limit=10)

# Create a listing
# ... (see examples for more details)
```

## Features

- Full CRUD operations for listings
- Image management
- Estate agent management
- Authentication support
- Error handling and validation 