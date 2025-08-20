# ContentGrid Application Client

This ContentGrid Client is a Python library designed to interact with ContentGrid API endpoints, specifically in the HAL response type. For ContentGrid Applications, it provides a convenient interface for performing various operations such as fetching profiles, creating entities, fetching related entities, handling content attributes, and more.

## Features

- **Profile Handling**: Fetch profiles to retrieve HAL-forms specification about available entities and their attributes.
- **Entity Operations**: Create, fetch, update, and delete entities using a simple functions without needing to worry about headers and authentication.
- **Content Handling**: Upload and download content on content-attributes of entities.
- **Error Handling**: Provides basic error handling for network requests.
- **Attribute validation**: Provides attribute type checks for creating and updating entities. Checks wether attributes have the correct type and if all required attributes are present.

## Installation

To install the ContentGrid API Client, you can use pip:

```bash
pip install contentgrid-application-client
```

## Usage

### ContentGridApplicationClient
```python
from contentgrid-application-client import ContentGridApplicationClient

# Initialize the client with service account
client = ContentGridApplicationClient(
    client_endpoint="https://b93ccecf-3466-44c0-995e-2620a8c66ac3.eu-west-1.contentgrid.cloud",
    auth_uri="https://auth.eu-west-1.contentgrid.cloud/realms/cg-eade54da-3903-4554-aa5e-2982cd4126f1/protocol/openid-connect/token",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Initialize the client with token
client = ContentGridApplicationClient(
    client_endpoint="https://b93ccecf-3466-44c0-995e-2620a8c66ac3.eu-west-1.contentgrid.cloud",
    token="your_token"
)

# Fetch profile
profile = client.get_profile()

# Create entity
attributes = {
    "name": "Example Entity",
    "description": "This is an example entity"
}
entity = client.create_entity("entity-name", attributes)
```

## Testing
Installing requirements:
```bash
    pip install -r requirements.txt
```

Running tests: 

```bash
    python -m pytest
```

Running tests with coverage:

```bash
    coverage run -m pytest && coverage report -m
```

