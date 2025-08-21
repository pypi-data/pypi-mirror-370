# OPAL REST Tool Service

A robust implementation of REST API tools for the OPAL SDK that automatically generates tools from OpenAPI specifications.

## Overview

The RESTToolService extends the standard OPAL ToolsService to support automatic tool generation from OpenAPI 3.x specifications. Instead of manually writing wrapper functions for each API endpoint, you can simply provide an OpenAPI spec and get all operations as callable tools.

## Features

- ✅ **Zero-code tool generation** - REST APIs become tools automatically
- ✅ **OpenAPI 3.x support** - Parse JSON or YAML specifications  
- ✅ **Flexible authentication** - Support for API keys, OAuth2, Bearer tokens
- ✅ **Parameter mapping** - Convert OpenAPI parameters to OPAL Parameter types
- ✅ **HTTP client integration** - Built-in async HTTP client for API calls
- ✅ **Error handling** - Proper status code and error response handling
- ✅ **Backward compatibility** - Works alongside traditional @tool decorators
- ✅ **Configuration options** - Filter operations, custom base URLs, auth config

## REST Tool Flow

The OPAL REST Tool Service follows a clear pipeline that transforms OpenAPI specifications into executable tools:

### 1. Data Flow Architecture

```
┌─────────────────┐    ┌────────────────────┐    ┌─────────────────┐
│   OpenAPI       │───▶│  OpenAPISpecParser │───▶│ ParsedOperation │
│   Specification │    │                    │    │     List        │
│   (JSON/YAML)   │    │                    │    │                 │
└─────────────────┘    └────────────────────┘    └─────────────────┘
                                                            │
                                                            ▼
┌─────────────────┐    ┌────────────────────┐    ┌─────────────────┐
│   HTTP Client   │◀───│   RESTHandler      │◀───│ RESTToolService │
│   (httpx)       │    │                    │    │                 │
└─────────────────┘    └────────────────────┘    └─────────────────┘
                                                            │
                                                            ▼
┌─────────────────┐    ┌────────────────────┐    ┌─────────────────┐
│   FastAPI       │◀───│ RESTToolRegistry   │◀───│   Tool Handler  │
│   Endpoints     │    │                    │    │   Functions     │
└─────────────────┘    └────────────────────┘    └─────────────────┘
```

### 2. Processing Steps

1. **OpenAPI Parsing**: `OpenAPISpecParser` reads the specification and extracts operations
2. **Operation Registration**: Each operation becomes a `ParsedOperation` with parameters and metadata
3. **Tool Creation**: Operations are registered as FastAPI endpoints through `RESTToolService`
4. **Registry Management**: `RESTToolRegistry` tracks all operations with filtering and statistics
5. **Request Execution**: `RESTHandler` executes HTTP calls to target APIs
6. **Response Handling**: Results are formatted and returned to the client

### 3. Component Interaction

```
Request → FastAPI Endpoint → Tool Handler → RESTHandler → Target API
                                                 ↓
Response ← Tool Handler ← RESTHandler ← Target API Response
```

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables (optional):
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys and configuration
# BEARER_AUTHENTICATION=your-api-key-here
```

## Quick Start

Get started with REST tools in 3 simple steps:

### 1. Run the Example
```bash
# Run the Optimizely API example
python -m rest_tools_example
```

## How to Add New Tools

There are multiple ways to add new REST tools to the OPAL system, depending on your use case:

### Method 1: From OpenAPI Specification URL

The easiest way to add tools from a publicly accessible OpenAPI spec:

```python
from fastapi import FastAPI
from core.rest_tool_service import create_service_from_urls
from core.rest_models import OpenAPIConfig

app = FastAPI(title="My REST Tools Service")

# Configure which operations to include
config = OpenAPIConfig(
    base_url="https://api.example.com/v1",  # Override spec base URL if needed
    filter_operations=["list_users", "get_user"],  # Only include these operations
    # exclude_operations=["delete_all"]  # Or exclude specific operations
)

# Create service from URL
service = await create_service_from_urls(
    app, 
    {"my-api": "https://api.example.com/openapi.json"},  # spec_name: url
    config
)

await service.startup()
```

### Method 2: From Local OpenAPI Specification File

When you have the OpenAPI spec as a local file:

```python
from pathlib import Path
from core.rest_tool_service import create_rest_tool_service

# Load from file path
spec_path = Path("my-api-spec.json")  # or .yaml
service = create_rest_tool_service(app, spec_path, config)

# Or load and filter the spec first
import json
with open("full-api-spec.json") as f:
    full_spec = json.load(f)

# Filter to specific paths
filtered_spec = {
    **full_spec,
    "paths": {path: methods for path, methods in full_spec["paths"].items() 
              if path.startswith("/users")}  # Only /users endpoints
}

service = create_rest_tool_service(app, filtered_spec, config)
```

### Method 3: Multiple API Specifications

When you need to combine multiple APIs into one service:

```python
from core.rest_tool_service import create_multi_spec_service

# Multiple specs with names
specs = {
    "github-api": github_openapi_spec,
    "slack-api": slack_openapi_spec,
    "custom-api": Path("custom-api.yaml")
}

service = create_multi_spec_service(app, specs, config)
await service.startup()

# Access operations by spec
github_ops = service.get_operations(spec_name="github-api")
slack_ops = service.get_operations(spec_name="slack-api")
```

### Method 4: Dynamic Registration

Add specs dynamically to a running service:

```python
# Start with empty service
service = RESTToolService(app, config)
await service.startup()

# Add specs as needed
count1 = service.register_openapi_spec(api_spec_1, "api-v1")
count2 = await service.register_openapi_url("https://api.example.com/spec", "api-v2")

# Bulk registration
batch_specs = [
    {"spec": spec_1, "name": "spec1"},
    {"url": "https://api.example.com/spec2", "name": "spec2"}
]
results = service.register_multiple_specs(batch_specs)
```

### Configuration Options

Control which operations become tools using `OpenAPIConfig`:

```python
config = OpenAPIConfig(
    base_url="https://custom-base.com",           # Override API base URL
    filter_operations=["op1", "op2"],            # Only include these operations
    exclude_operations=["dangerous_op"],          # Exclude specific operations
    endpoint_prefix="/custom/api/path",           # Custom endpoint prefix
)
```

### Authentication Setup

Configure authentication for API calls:

```python
# In your tool calls, provide auth data:
auth_data = {
    # Direct headers
    "Authorization": "Bearer your-token",
    "X-API-Key": "your-api-key",
    
    # Or structured auth (matches OpenAPI security schemes)
    "api_key": "your-key",
    "token": "bearer-token",
    "access_token": "oauth-token"
}

# The RESTHandler will automatically apply the appropriate headers
result = await service.rest_handler.execute_operation(
    operation=my_operation,
    parameters={"param1": "value1"},
    auth_data=auth_data
)
```

#### Environment Variables

The system supports configuration via environment variables:

```bash
# Set in your .env file or environment

# Authentication
BEARER_AUTHENTICATION=your-api-key-here

# REST API Configuration
RESTAPI_ENDPOINT_PREFIX=/rest-tools  # Default endpoint prefix for tools
```

Configuration details:
- `BEARER_AUTHENTICATION`: API authentication token (loaded by `get_auth_value()`)
- `RESTAPI_ENDPOINT_PREFIX`: Configurable endpoint prefix for REST tools (default: `/rest-tools`)

#### Configurable Endpoint Prefix

You can customize the endpoint prefix for REST tools using the `RESTAPI_ENDPOINT_PREFIX` environment variable:

```bash
# Examples:
RESTAPI_ENDPOINT_PREFIX=/rest-tools           # Default
RESTAPI_ENDPOINT_PREFIX=/experimental/rest-tools
RESTAPI_ENDPOINT_PREFIX=/api/v2/tools
```

This affects all tool endpoints. For example, with `/experimental/rest-tools`:
- `list_projects` becomes `/experimental/rest-tools/list_projects`
- `get_user` becomes `/experimental/rest-tools/get_user`

You can also override in code:

```python
config = OpenAPIConfig(
    endpoint_prefix="/custom/api/path"  # Overrides environment variable
)
```

## Core Components

The system consists of several key components that work together to transform OpenAPI specs into executable tools:

### 1. OpenAPISpecParser (`niteco/opal_rest_tool/openapi_parser.py:12`)
Parses OpenAPI 3.x specifications and extracts operations into `ParsedOperation` objects:

**Key Features:**
- Supports JSON and YAML OpenAPI specs
- Extracts parameters from paths, query strings, and request bodies
- Maps OpenAPI security schemes to authentication requirements, can omit this (for Opal Hackathon)
- Applies operation filtering based on configuration

```python
from core.openapi_parser import OpenAPISpecParser
from core.rest_models import OpenAPIConfig

config = OpenAPIConfig(filter_operations=["list_users", "get_user"])
parser = OpenAPISpecParser(config)
operations = parser.parse(openapi_spec)  # Returns List[ParsedOperation]
```

### 2. RESTHandler (`niteco/opal_rest_tool/rest_handler.py:13`)
Executes HTTP requests for parsed operations using the httpx client:

**Key Features:**
- Builds URLs with path parameter substitution
- Handles bearer authentication
- Separates parameters into query params and request body
- Formats responses with error handling

```python
from core.rest_handler import RESTHandler

handler = RESTHandler(timeout=30)
result = await handler.execute_operation(
    operation=parsed_operation,
    parameters={"user_id": 123, "include_details": True},
    auth_data={"Authorization": "Bearer token"}
)
```

### 3. ParsedOperation (`niteco/opal_rest_tool/rest_models.py:10`)
Data model representing a parsed API operation with all necessary metadata:

```python
@dataclass
class ParsedOperation:
    name: str                                    # Generated tool name (snake_case)
    description: str                             # Operation description
    method: str                                  # HTTP method (GET, POST, etc.)
    path: str                                    # API path with parameters
    base_url: str                                # Base URL for API calls
    parameters: List[Parameter]                  # Extracted parameters
    auth_requirements: Optional[List[AuthRequirement]]  # Auth requirements
    operation_id: Optional[str]                  # Original OpenAPI operationId
    request_body_schema: Optional[Dict[str, Any]]  # Request body schema
    response_schema: Optional[Dict[str, Any]]    # Response schema
    tags: Optional[List[str]]                    # OpenAPI tags
```

### 4. RESTToolService (`niteco/opal_rest_tool/rest_tool_service.py:117`)
Main service class that extends the OPAL ToolsService to support REST API integration:

**Key Features:**
- Auto-registration of OpenAPI operations as FastAPI endpoints
- Operation registry with filtering and management
- Health monitoring and validation
- Multi-spec support with bulk operations
- Lifecycle management (startup/shutdown)

```python
from core.rest_tool_service import RESTToolService
from core.rest_models import OpenAPIConfig

app = FastAPI()
config = OpenAPIConfig(base_url="https://api.example.com")
service = RESTToolService(app, config)

# Register specs
count = service.register_openapi_spec(openapi_spec, "my-api")
count = await service.register_openapi_url("https://api.example.com/spec", "api-v2")

# Manage operations
operations = service.get_operations(spec_name="my-api")
service.unregister_operation("unwanted_tool")
```

### 5. RESTToolRegistry (`niteco/opal_rest_tool/rest_tool_service.py:26`)
Internal registry that manages REST operations with metadata tracking:

**Key Features:**
- Operation storage with name-based lookup
- Tag-based and spec-based filtering
- Statistics and health monitoring
- Bulk operations (clear, unregister)

```python
# Accessed through RESTToolService
stats = service.registry.get_stats()
operations_by_tag = service.registry.get_by_tag("users")
operations_by_spec = service.registry.get_by_spec("github-api")
```

### 6. OpenAPIConfig (`niteco/opal_rest_tool/rest_models.py:38`)
Configuration object for customizing OpenAPI parsing and tool generation:

```python
@dataclass
class OpenAPIConfig:
    base_url: Optional[str] = None                # Override API base URL
    auth_config: Optional[Dict[str, Any]] = None  # Auth configuration
    filter_operations: Optional[List[str]] = None # Include only these operations
    exclude_operations: Optional[List[str]] = None # Exclude these operations
```

## Testing

Run the test suite to see the RESTToolService in action:

```bash
# Test the parser only
python test_rest_service.py
# Choose option 1

# Test the full service with HTTP calls
python test_rest_service.py  
# Choose option 2
```

The test uses the JSONPlaceholder API (https://jsonplaceholder.typicode.com) to demonstrate:
- GET requests with query parameters
- POST requests with request body
- Path parameter substitution
- Response handling

## Authentication Support

The RESTToolService supports bearer authentication method for now.

## Error Handling

- HTTP errors (4xx, 5xx) are captured and included in responses
- Network errors are logged and re-raised as HTTPException
- Invalid OpenAPI specs raise ValueError with details
- Missing required parameters are logged as warnings

## Discovery Endpoint

All generated tools are automatically discoverable via the `/discovery` endpoint:

```json
{
  "functions": [
    {
      "name": "get_users",
      "description": "Get all users",
      "parameters": [...],
      "endpoint": "/rest-tools/get_users",
      "http_method": "POST"
    }
  ]
}
```

## Limitations

- Currently supports OpenAPI 3.x (not 2.x/Swagger)
- Reference resolution is simplified (no external refs)
- Authentication mapping may need customization for complex schemes
- Response schemas are captured but not validated

## Future Enhancements

- Full $ref reference resolution
- OpenAPI 2.x support
- Response validation against schemas
- Request/response transformation middleware
- Rate limiting and retry logic
- Caching for API responses

## Project Structure

### PyPI Package Structure (niteco.opal-rest-tool)
```
niteco/opal_rest_tool/                      # Core system components (included in PyPI)
├── __init__.py                             # Package initialization
├── rest_models.py                          # Data models (ParsedOperation, OpenAPIConfig)
├── openapi_parser.py                       # OpenAPI 3.x specification parser
├── rest_handler.py                         # HTTP client for REST API execution
└── rest_tool_service.py                    # Main service (RESTToolService, Registry)
```

### Development Repository Structure
```
Niteco.Opal-REST-tool/
├── niteco/opal_rest_tool/                  # Core system components (PyPI package)
│   ├── __init__.py                         # Package initialization
│   ├── rest_models.py                      # Data models (ParsedOperation, OpenAPIConfig)
│   ├── openapi_parser.py                   # OpenAPI 3.x specification parser
│   ├── rest_handler.py                     # HTTP client for REST API execution
│   └── rest_tool_service.py               # Main service (RESTToolService, Registry)
├── rest_tools_example/                     # Example implementations (dev only)
│   ├── __init__.py                         # Package initialization
│   ├── __main__.py                         # Example entry point
│   ├── optimizely_web_experimentation.py   # Optimizely API integration example
│   └── opal tool.postman_collection.json  # Postman collection for testing
├── test/                                   # Test files and specifications (dev only)
│   ├── Optimizely API - v1.0.json         # Sample OpenAPI specification
│   └── test_rest.py                        # Comprehensive test suite
├── .env.example                            # Environment configuration template
├── pyproject.toml                          # Package configuration and PyPI metadata
├── requirements.txt                        # Python dependencies
└── README.md                              # This documentation
```

### Core Files Description

- **`niteco/opal_rest_tool/rest_models.py`** - Data classes including `ParsedOperation` (line 10) and `OpenAPIConfig` (line 38)
- **`niteco/opal_rest_tool/openapi_parser.py`** - OpenAPI spec parser with `OpenAPISpecParser` class (line 12) 
- **`niteco/opal_rest_tool/rest_handler.py`** - HTTP execution engine with `RESTHandler` class (line 13)
- **`niteco/opal_rest_tool/rest_tool_service.py`** - Main service classes:
  - `RESTToolRegistry` (line 26) - Operation registry management
  - `RESTToolService` (line 117) - Main service extending OPAL ToolsService
  - Factory functions (lines 503-571) - Convenience service creators
- **`test/test_rest.py`** - Complete test suite demonstrating all features
- **`rest_tools_example/optimizely_web_experimentation.py`** - Real-world example using Optimizely API

## License

This implementation is part of the OPAL project.