"""
Models specific to REST API tool generation from OpenAPI specs.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import os
import json
from dotenv import load_dotenv
from opal_tools_sdk.models import Parameter, AuthRequirement, Function, ParameterType


@dataclass
class ParsedOperation:
    """Parsed operation from OpenAPI specification."""
    name: str
    description: str
    method: str
    path: str
    base_url: str
    parameters: List[Parameter]
    auth_requirements: Optional[List[AuthRequirement]] = None
    operation_id: Optional[str] = None
    request_body_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    omit_auth_from_discovery_metadata: bool = False 
    
    def to_function(self, endpoint_prefix: str = "/rest-tools") -> Function:
        """Convert to Function object for tool registration."""
        endpoint = f"{endpoint_prefix}/{self.name}"
        
        auth_reqs = None if self.omit_auth_from_discovery_metadata else self.auth_requirements
        
        return Function(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
            endpoint=endpoint,
            auth_requirements=auth_reqs,
            http_method="POST"  # All tools use POST to receive parameters
        )

def get_auth_value() -> Optional[str]:
    """Get auth value from environment mapping."""
    load_dotenv()
    return os.getenv("BEARER_AUTHENTICATION", "your-api-key")

def get_endpoint_prefix() -> str:
    """Get endpoint prefix from environment variable."""
    load_dotenv()
    return os.getenv("RESTAPI_ENDPOINT_PREFIX", "/rest-tools")

@dataclass
class OpenAPIConfig:
    """Configuration for OpenAPI spec parsing."""
    base_url: Optional[str] = None
    auth_config: Optional[Dict[str, Any]] = None #TODO
    filter_operations: Optional[List[str]] = None 
    exclude_operations: Optional[List[str]] = None
    omit_auth_from_discovery_metadata: bool = False  # NEW: Simplified auth approach
    endpoint_prefix: str = field(default_factory=get_endpoint_prefix)  # Configurable endpoint prefix from env
    exclude_from_discovery: bool = False 