# PyGard - Modern Async Python Client for Gard Data Service

PyGard is a modern, asynchronous Python client for the Gard data service. It provides a comprehensive interface for interacting with Gard data, featuring async support, OOP design, and excellent extensibility.

## Features

- **🔄 Async Support**: Built with `asyncio` and `aiohttp` for high-performance async operations
- **🏗️ OOP Design**: Clean, object-oriented architecture with clear separation of concerns
- **📊 Layered Architecture**: Application, service, configuration, connection, and model layers
- **🔧 Modern Syntax**: Uses Python 3.8+ features and modern coding practices
- **📝 Structured Logging**: Comprehensive logging with `structlog`
- **⚙️ Configuration Management**: Flexible configuration with `pydantic-settings` V2
- **🛡️ Error Handling**: Comprehensive exception handling with specific error types
- **🔌 Connection Pooling**: Efficient HTTP connection management
- **📦 Type Safety**: Full type hints and validation with Pydantic V2
- **🌍 Environment Support**: Environment variable and .env file configuration

## Installation

```bash
# Install from source
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
import asyncio
from pygard import GardClient, Gard

async def main():
    # Create client
    async with GardClient(base_url="http://localhost:8083") as client:
        # Create a new Gard record
        new_gard = Gard(
            name="Example Data",
            description="Sample dataset",
            tags=["geology", "sample"],
            type="GEOMETRY"
        )
        
        created_gard = await client.create_gard(new_gard)
        print(f"Created Gard with ID: {created_gard.did}")
        
        # Get Gard record
        gard = await client.get_gard(created_gard.did)
        print(f"Retrieved: {gard.name}")
        
        # List Gard records
        page = await client.list_gards(page=1, size=10)
        print(f"Found {page.total} records")

if __name__ == "__main__":
    asyncio.run(main())
```

### Configuration

#### Environment Variables

```bash
# Copy the example file
cp env.example .env

# Edit .env file with your settings
PYGARD_BASE_URL=http://localhost:8083
PYGARD_API_KEY=your_api_key_here
PYGARD_LOG_LEVEL=INFO
```

#### Code Configuration

```python
from pygard.config import GardConfig

# Create configuration
config = GardConfig(
    base_url="https://api.example.com",
    api_key="your_api_key",
    timeout=60,
    log_level="DEBUG"
)

# Use with client
async with GardClient(config) as client:
    # Use client
```

## Architecture

PyGard follows a layered architecture pattern:

### 1. Application Layer (`pygard/client/`)
- **GardClient**: Main client class providing high-level interface
- Handles client lifecycle and service coordination

### 2. Service Layer (`pygard/services/`)
- **GardService**: Business logic for Gard operations
- Extends BaseService for common functionality
- Implements specific API operations

### 3. Configuration Layer (`pygard/config/`)
- **GardConfig**: Configuration management with Pydantic V2
- Environment variable support with `pydantic-settings`
- Validation and defaults

### 4. Connection Layer (`pygard/core/`)
- **ConnectionManager**: HTTP connection and session management
- Connection pooling and retry logic
- Request/response handling

### 5. Model Layer (`pygard/models/`)
- **Gard**: Main data model with Pydantic V2
- **GardFilter**: Search filter model
- **GardPage**: Pagination model
- Common models for shared data structures

## Configuration

### Environment Variables

```bash
# API Configuration
PYGARD_BASE_URL=http://localhost:8083
PYGARD_API_VERSION=v1
PYGARD_TIMEOUT=30
PYGARD_MAX_RETRIES=3

# Authentication
PYGARD_API_KEY=your_api_key_here

# Logging
PYGARD_LOG_LEVEL=INFO
PYGARD_LOG_FORMAT=json

# Connection
PYGARD_CONNECTION_POOL_SIZE=10
PYGARD_KEEPALIVE_TIMEOUT=30
```

### Configuration File

```python
from pygard.config import GardConfig

config = GardConfig(
    base_url="http://localhost:8083",
    api_version="v1",
    timeout=30,
    log_level="INFO",
    connection_pool_size=10
)
```

## Usage Examples

### Basic Operations

```python
import asyncio
from pygard import GardClient, Gard, GardFilter

async def basic_operations():
    async with GardClient() as client:
        # Create
        gard = Gard(name="Test Data", description="Test description")
        created = await client.create_gard(gard)
        
        # Read
        retrieved = await client.get_gard(created.did)
        
        # Update
        retrieved.description = "Updated description"
        updated = await client.update_gard(retrieved.did, retrieved)
        
        # Delete
        await client.delete_gard(created.did)
```

### Search Operations

```python
async def search_operations():
    async with GardClient() as client:
        # Search by tags
        results = await client.search_by_tags(["geology", "paleontology"])
        
        # Search by keywords
        results = await client.search_by_keywords(["fossil", "strata"])
        
        # Advanced search
        filter_obj = GardFilter(
            tags=["geology"],
            keywords=["sedimentary"]
        )
        results = await client.search_gards(filter_obj, page=1, size=20)
```

### Pagination

```python
async def pagination_example():
    async with GardClient() as client:
        page = 1
        while True:
            results = await client.list_gards(page=page, size=50)
            
            for gard in results.records:
                print(f"Processing: {gard.name}")
            
            if not results.has_next:
                break
                
            page += 1
```

### Error Handling

```python
from pygard.utils.exceptions import GardNotFoundError, GardConnectionError


async def error_handling():
    async with GardClient() as client:
        try:
            gard = await client.get_gard(99999)  # Non-existent ID
        except GardNotFoundError:
            print("Gard record not found")
        except GardConnectionError:
            print("Connection error occurred")
        except Exception as e:
            print(f"Unexpected error: {e}")
```

## Pydantic V2 Features

### Model Validation

```python
from pygard import Gard
from pydantic import ValidationError

# Automatic validation
try:
    gard = Gard(
        name="Test Data",
        description="Test description",
        tags=["test", "sample"]
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

### Model Operations

```python
# Create from dictionary
gard_data = {"name": "From Dict", "description": "Test"}
gard = Gard.model_validate(gard_data)

# Update model
updated_gard = gard.model_copy(update={"description": "Updated"})

# Serialize
dict_data = gard.model_dump()
json_data = gard.model_dump_json()
```

### Custom Validation

```python
from pydantic import BaseModel, Field, field_validator

class CustomGard(Gard):
    tags_count: int = Field(..., description="Number of tags")
    
    @field_validator("tags_count")
    @classmethod
    def validate_tags_count(cls, v):
        if v < 0:
            raise ValueError("Tags count cannot be negative")
        return v
```

## Extending PyGard

### Adding New Services

```python
from pygard.core.base_service import BaseService
from pygard.models import YourModel

class YourService(BaseService[YourModel]):
    def __init__(self, connection_manager, config):
        super().__init__(connection_manager, config)
    
    async def your_operation(self, param):
        return await self.get("your/endpoint", YourModel, params={"param": param})
```

### Adding New Models

```python
from pydantic import BaseModel, Field

class YourModel(BaseModel):
    id: int = Field(..., description="Model ID")
    name: str = Field(..., description="Model name")
    description: str = Field(None, description="Model description")
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd data-service-sdk-python

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment file
cp env.example .env
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pygard

# Run specific test file
pytest tests/test_gard_service.py
```

### Code Quality

```bash
# Format code
black pygard/

# Sort imports
isort pygard/

# Type checking
mypy pygard/

# Linting
ruff check pygard/
```

## API Reference

### GardClient

Main client class for interacting with the Gard service.

#### Methods

- `create_gard(gard: Gard) -> Gard`: Create a new Gard record
- `get_gard(did: int) -> Gard`: Get Gard record by ID
- `update_gard(did: int, gard: Gard) -> Gard`: Update Gard record
- `delete_gard(did: int) -> bool`: Delete Gard record
- `list_gards(page: int = 1, size: int = 10) -> GardPage`: List Gard records
- `search_gards(filter_obj: GardFilter, page: int = 1, size: int = 10) -> GardPage`: Search Gard records
- `search_by_tags(tags: List[str], page: int = 1, size: int = 10) -> GardPage`: Search by tags
- `search_by_keywords(keywords: List[str], page: int = 1, size: int = 10) -> GardPage`: Search by keywords

### Gard Model

Main data model for Gard records.

#### Fields

- `did: Optional[int]`: Data ID
- `name: str`: Name of the data
- `description: Optional[str]`: Description
- `tags: Optional[List[str]]`: Tags
- `type: Optional[str]`: Data type
- `is_spatial: Optional[bool]`: Is spatial data
- `is_temporal: Optional[bool]`: Is temporal data
- And many more fields for spatial, temporal, and metadata information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on the GitHub repository.
