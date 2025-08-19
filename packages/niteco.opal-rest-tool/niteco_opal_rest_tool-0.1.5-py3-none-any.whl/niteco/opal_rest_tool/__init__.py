"""
Niteco OPAL REST Tool Service

Automatically generates tools from OpenAPI 3.x specifications for use with OPAL.
Instead of manually writing wrapper functions for each API endpoint, provide an
OpenAPI spec and get all operations as callable tools.
"""

from .rest_tool_service import (
    RESTToolService,
    RESTToolRegistry,
    create_rest_tool_service,
    create_multi_spec_service,
    create_service_from_urls,
)
from .rest_models import ParsedOperation, OpenAPIConfig
from .openapi_parser import OpenAPISpecParser
from .rest_handler import RESTHandler

__version__ = "0.1.3"

__all__ = [
    "RESTToolService",
    "RESTToolRegistry", 
    "create_rest_tool_service",
    "create_multi_spec_service",
    "create_service_from_urls",
    "ParsedOperation",
    "OpenAPIConfig",
    "OpenAPISpecParser",
    "RESTHandler",
]