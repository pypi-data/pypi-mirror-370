"""
RESTToolService - A service that automatically generates tools from OpenAPI specifications.
"""

# Standard library imports
import logging
from typing import Dict, Any, Union, Optional, List, Set, Callable
from pathlib import Path
from datetime import datetime

# Third-party imports
from fastapi import FastAPI, Request, HTTPException
import aiohttp

# Local imports
from opal_tools_sdk import ToolsService
from opal_tools_sdk.models import Parameter, AuthRequirement
from .rest_models import OpenAPIConfig, ParsedOperation
from .openapi_parser import OpenAPISpecParser
from .rest_handler import RESTHandler


logger = logging.getLogger(__name__)


class RESTToolRegistry:
    """Registry for managing REST operations and their metadata."""
    
    def __init__(self):
        self._operations: Dict[str, ParsedOperation] = {}
        self._tags: Dict[str, Set[str]] = {}
        self._spec_operations: Dict[str, Set[str]] = {}
    
    def register(self, operation: ParsedOperation, spec_name: Optional[str] = None) -> None:
        """Register an operation."""
        self._operations[operation.name] = operation
        
        # Register by tags
        for tag in operation.tags or []:
            if tag not in self._tags:
                self._tags[tag] = set()
            self._tags[tag].add(operation.name)
        
        # Register by spec name
        if spec_name:
            if spec_name not in self._spec_operations:
                self._spec_operations[spec_name] = set()
            self._spec_operations[spec_name].add(operation.name)
    
    def unregister(self, name: str) -> bool:
        """Unregister an operation."""
        if name not in self._operations:
            return False
        
        operation = self._operations[name]
        
        # Remove from tags
        for tag in operation.tags or []:
            if tag in self._tags:
                self._tags[tag].discard(name)
                if not self._tags[tag]:
                    del self._tags[tag]
        
        # Remove from specs
        for spec_name, operations in self._spec_operations.items():
            operations.discard(name)
        
        del self._operations[name]
        return True
    
    def get(self, name: str) -> Optional[ParsedOperation]:
        """Get operation by name."""
        return self._operations.get(name)
    
    def get_by_tag(self, tag: str) -> List[ParsedOperation]:
        """Get operations by tag."""
        operation_names = self._tags.get(tag, set())
        return [self._operations[name] for name in operation_names if name in self._operations]
    
    def get_by_spec(self, spec_name: str) -> List[ParsedOperation]:
        """Get operations by spec name."""
        operation_names = self._spec_operations.get(spec_name, set())
        return [self._operations[name] for name in operation_names if name in self._operations]
    
    def list_all(self) -> List[ParsedOperation]:
        """Get all registered operations."""
        return list(self._operations.values())
    
    def clear(self) -> None:
        """Clear all registered operations."""
        self._operations.clear()
        self._tags.clear()
        self._spec_operations.clear()
    
    def clear_spec(self, spec_name: str) -> List[str]:
        """Clear operations from a specific spec."""
        if spec_name not in self._spec_operations:
            return []
        
        operation_names = list(self._spec_operations[spec_name])
        for name in operation_names:
            self.unregister(name)
        
        return operation_names
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_operations": len(self._operations),
            "tags": list(self._tags.keys()),
            "specs": list(self._spec_operations.keys()),
            "operations_by_tag": {tag: len(ops) for tag, ops in self._tags.items()},
            "operations_by_spec": {spec: len(ops) for spec, ops in self._spec_operations.items()}
        }


class RESTToolService(ToolsService):
    """
    Extended ToolsService that can automatically generate tools from OpenAPI specifications.
    
    Features:
    - Auto-registration of OpenAPI operations as tools
    - Operation registry with tag-based filtering
    - Bulk operations for multiple specs
    - Health monitoring and metrics
    """
    
    def __init__(self, app: FastAPI, config: Optional[OpenAPIConfig] = None):
        """
        Initialize the REST tool service.
        
        Args:
            app: FastAPI application to attach routes to
            config: Configuration for OpenAPI parsing
        """
        super().__init__(app)
        self.config = config or OpenAPIConfig()
        self.parser = OpenAPISpecParser(self.config)
        self.rest_handler = RESTHandler()
        self.registry = RESTToolRegistry()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._specs_loaded: Dict[str, Dict[str, Any]] = {}
        self._startup_time: Optional[datetime] = None
        
        # Add middleware to handle empty JSON bodies
        self._add_json_body_middleware(app)
    
    # Core Registration Methods
    def register_openapi_spec(self, 
                            openapi_spec: Union[str, Dict[str, Any], Path], 
                            spec_name: Optional[str] = None) -> int:
        """
        Register all tools from an OpenAPI specification.
        
        Args:
            openapi_spec: OpenAPI spec as string (JSON/YAML), dict, or Path
            spec_name: Optional name for the spec (for tracking and filtering)
            
        Returns:
            Number of tools registered
        """
        spec_name = spec_name or f"spec_{len(self._specs_loaded) + 1}"
        self.logger.info(f"Parsing OpenAPI specification: {spec_name}")
        
        try:
            # Handle Path objects
            if isinstance(openapi_spec, Path):
                openapi_spec = openapi_spec.read_text()
            
            # Parse the OpenAPI spec
            operations = self.parser.parse(openapi_spec)
            self.logger.info(f"Found {len(operations)} operations in OpenAPI spec: {spec_name}")
            
            # Store spec metadata
            self._specs_loaded[spec_name] = {
                "loaded_at": datetime.now(),
                "operation_count": len(operations),
                "operations": [op.name for op in operations]
            }
            
            # Register each operation as a tool
            registered_count = 0
            for operation in operations:
                try:
                    handler = self._create_operation_handler(operation)
                    
                    if not self.config.exclude_from_discovery:
                        self._register_rest_operation(operation, handler)
                        
                    self.registry.register(operation, spec_name)
                    registered_count += 1
                    self.logger.info(f"Registered REST tool: {operation.name}")
                except Exception as e:
                    self.logger.error(f"Failed to register operation {operation.name}: {e}")
                    continue
            
            self.logger.info(f"Successfully registered {registered_count} REST tools from {spec_name}")
            return registered_count
            
        except Exception as e:
            self.logger.error(f"Error parsing OpenAPI spec {spec_name}: {e}")
            raise ValueError(f"Failed to parse OpenAPI specification {spec_name}: {e}")
    
    async def register_openapi_url(self, url: str, spec_name: Optional[str] = None) -> int:
        """
        Register tools from OpenAPI spec at URL.
        
        Args:
            url: URL to fetch OpenAPI spec from
            spec_name: Optional name for the spec
            
        Returns:
            Number of tools registered
        """
        spec_name = spec_name or f"url_{len(self._specs_loaded) + 1}"
        self.logger.info(f"Fetching OpenAPI spec from URL: {url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    if response.content_type == 'application/json':
                        openapi_spec = await response.json()
                    else:
                        openapi_spec = await response.text()
            
            return self.register_openapi_spec(openapi_spec, spec_name)
            
        except Exception as e:
            self.logger.error(f"Error fetching OpenAPI spec from {url}: {e}")
            raise ValueError(f"Failed to fetch OpenAPI specification from {url}: {e}")
    
    def register_multiple_specs(self, specs: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Register multiple OpenAPI specs in batch.
        
        Args:
            specs: List of spec configs with keys: 'spec', 'name' (optional), 'url' (optional)
            
        Returns:
            Dictionary mapping spec names to number of tools registered
        """
        results = {}
        
        for i, spec_config in enumerate(specs):
            try:
                spec_name = spec_config.get('name', f"batch_spec_{i + 1}")
                
                if 'url' in spec_config:
                    # Handle async URL registration synchronously
                    import asyncio
                    count = asyncio.run(self.register_openapi_url(spec_config['url'], spec_name))
                elif 'spec' in spec_config:
                    count = self.register_openapi_spec(spec_config['spec'], spec_name)
                else:
                    self.logger.error(f"Invalid spec config at index {i}: missing 'spec' or 'url'")
                    continue
                
                results[spec_name] = count
                
            except Exception as e:
                self.logger.error(f"Failed to register spec at index {i}: {e}")
                results[spec_config.get('name', f"batch_spec_{i + 1}")] = 0
        
        return results
    
    # Operation Management
    def get_operations(self, 
                      tag: Optional[str] = None, 
                      spec_name: Optional[str] = None) -> List[ParsedOperation]:
        """
        Get operations with optional filtering.
        
        Args:
            tag: Filter by tag
            spec_name: Filter by spec name
            
        Returns:
            List of matching operations
        """
        if tag:
            return self.registry.get_by_tag(tag)
        elif spec_name:
            return self.registry.get_by_spec(spec_name)
        else:
            return self.registry.list_all()
    
    def unregister_operation(self, name: str) -> bool:
        """
        Unregister a specific operation.
        
        Args:
            name: Operation name to unregister
            
        Returns:
            True if operation was found and removed
        """
        if self.registry.unregister(name):
            # Also need to unregister from parent ToolsService
            # This would require access to the parent's internal registry
            self.logger.info(f"Unregistered operation: {name}")
            return True
        return False
    
    def reload_spec(self, spec_name: str) -> int:
        """
        Reload a specific OpenAPI spec.
        
        Args:
            spec_name: Name of the spec to reload
            
        Returns:
            Number of tools registered from reloaded spec
        """
        if spec_name not in self._specs_loaded:
            raise ValueError(f"Spec '{spec_name}' not found")
        
        # Clear existing operations for this spec
        cleared_operations = self.registry.clear_spec(spec_name)
        self.logger.info(f"Cleared {len(cleared_operations)} operations from spec: {spec_name}")
        
        # Re-register the spec (this would need the original spec data to be stored)
        # For now, just return 0 as we don't store the original spec
        self.logger.warning(f"Reload not fully implemented - original spec data not stored")
        return 0
    
    # Health & Monitoring
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health and statistics."""
        registry_stats = self.registry.get_stats()
        
        return {
            "status": "healthy",
            "startup_time": self._startup_time.isoformat() if self._startup_time else None,
            "uptime_seconds": (datetime.now() - self._startup_time).total_seconds() if self._startup_time else 0,
            "specs_loaded": len(self._specs_loaded),
            "total_operations": registry_stats["total_operations"],
            "registry_stats": registry_stats,
            "specs": {
                name: {
                    "loaded_at": info["loaded_at"].isoformat(),
                    "operation_count": info["operation_count"],
                    "operations": info["operations"]
                }
                for name, info in self._specs_loaded.items()
            }
        }
    
    def validate_operations(self) -> Dict[str, List[str]]:
        """
        Validate all registered operations.
        
        Returns:
            Dictionary with 'valid' and 'invalid' operations and their issues
        """
        valid_operations = []
        invalid_operations = []
        
        for operation in self.registry.list_all():
            issues = self._validate_operation(operation)
            if issues:
                invalid_operations.append({
                    "name": operation.name,
                    "issues": issues
                })
            else:
                valid_operations.append(operation.name)
        
        return {
            "valid": valid_operations,
            "invalid": invalid_operations,
            "summary": {
                "total": len(valid_operations) + len(invalid_operations),
                "valid_count": len(valid_operations),
                "invalid_count": len(invalid_operations)
            }
        }
    
    # Private Implementation Methods
    def _register_rest_operation(self, operation: ParsedOperation, handler: Callable) -> None:
        """Register a single REST operation as a tool."""
       
        # Convert operation to Function and register
        function = operation.to_function(self.config.endpoint_prefix)
        
        # Register the tool using the parent class method
        self.register_tool(
            name=operation.name,
            description=operation.description,
            handler=handler,
            parameters=operation.parameters,
            endpoint=function.endpoint,
            auth_requirements=function.auth_requirements
        )
    
    def _create_operation_handler(self, operation: ParsedOperation):
        """Create async handler for REST operation.
       
        IMPORTANT: The handler signature accepts a plain dict of parameters instead of
        FastAPI's Request object. This keeps it compatible with the Opal SDK's
        tool wrapper which attempts to construct the first argument from the
        provided parameters. Using `dict` ensures the wrapper simply passes the
        parsed parameters through without trying to instantiate a Request.
        """
        async def rest_tool_handler(parameters: dict, auth_data: Optional[Dict[str, Any]] = None, environment: Optional[Dict[str, Any]] = None):
            try:
                self.logger.info(f"Executing REST operation: {operation.name}")
               
                # Execute the REST API call
                result = await self.rest_handler.execute_operation(
                    operation=operation,
                    parameters=parameters or {},
                    auth_data=auth_data,
                    environment=environment or {}
                )
               
                self.logger.info(f"REST tool {operation.name} returned: {result}")
                return result
               
            except Exception as e:
                import traceback
                self.logger.error(f"Error in REST tool {operation.name}: {str(e)}")
                self.logger.error(traceback.format_exc())
                raise HTTPException(status_code=500, detail=str(e))
       
        return rest_tool_handler
    
    def _add_json_body_middleware(self, app: FastAPI):
        """Add middleware to handle empty JSON bodies for REST tools."""
        endpoint_prefix = self.config.endpoint_prefix
        @app.middleware("http")
        async def json_body_middleware(request: Request, call_next):
            # Only apply to our REST tool endpoints
            if request.url.path.startswith(f"{endpoint_prefix}/"):
                # Check if the request has an empty body
                body = await request.body()
                if not body or body.strip() == b'':
                    # Create a new request with minimal valid JSON
                    import json
                    from starlette.requests import Request as StarletteRequest
                    
                    minimal_body = json.dumps({"parameters": {}}).encode()
                    
                    # Create new scope with the fixed body
                    new_scope = request.scope.copy()
                    new_scope["body"] = minimal_body
                    
                    # Create new request with the fixed body
                    new_request = StarletteRequest(scope=new_scope, receive=request.receive)
                    new_request._body = minimal_body
                    
                    return await call_next(new_request)
            
            # For all other endpoints, proceed normally
            return await call_next(request)
    
    def _validate_operation(self, operation: ParsedOperation) -> List[str]:
        """
        Validate a single operation.
        
        Args:
            operation: Operation to validate
            
        Returns:
            List of validation issues (empty if valid)
        """
        issues = []
        
        # Basic validation
        if not operation.name:
            issues.append("Missing operation name")
        
        if not operation.description:
            issues.append("Missing operation description")
        
        if not operation.method:
            issues.append("Missing HTTP method")
        
        if not operation.path:
            issues.append("Missing operation path")
        
        # Parameter validation
        for param in operation.parameters or []:
            if not param.name:
                issues.append(f"Parameter missing name: {param}")
        
        return issues
    
    # Lifecycle Management
    async def startup(self) -> None:
        """Initialize service resources."""
        self._startup_time = datetime.now()
        self.logger.info("RESTToolService starting up")
        
        # Initialize REST handler if needed
        if hasattr(self.rest_handler, 'startup'):
            await self.rest_handler.startup()
        
        self.logger.info("RESTToolService startup completed")
    
    async def shutdown(self) -> None:
        """Cleanup service resources."""
        self.logger.info("RESTToolService shutting down")
        
        # Clear registry
        self.registry.clear()
        
        # Close REST handler
        if self.rest_handler:
            await self.rest_handler.close()
        
        self.logger.info("RESTToolService shutdown completed")
    
    # Legacy compatibility methods
    def get_rest_operations(self) -> List[ParsedOperation]:
        """Get list of registered REST operations (legacy compatibility)."""
        return self.registry.list_all()
    
    def get_operation_by_name(self, name: str) -> Optional[ParsedOperation]:
        """Get a specific REST operation by name (legacy compatibility)."""
        return self.registry.get(name)
    
    async def close(self):
        """Close resources (legacy compatibility)."""
        await self.shutdown()


# Factory Functions
def create_rest_tool_service(app: FastAPI, 
                           openapi_spec: Union[str, Dict[str, Any]], 
                           config: Optional[OpenAPIConfig] = None) -> RESTToolService:
    """
    Create RESTToolService with single spec.
    
    Args:
        app: FastAPI application
        openapi_spec: OpenAPI specification
        config: Optional configuration
        
    Returns:
        Configured RESTToolService instance
    """
    service = RESTToolService(app, config)
    service.register_openapi_spec(openapi_spec)
    return service


def create_multi_spec_service(app: FastAPI,
                            specs: Dict[str, Union[str, Dict, Path]],
                            config: Optional[OpenAPIConfig] = None) -> RESTToolService:
    """
    Create RESTToolService with multiple named specs.
    
    Args:
        app: FastAPI application
        specs: Dictionary mapping spec names to spec data (string, dict, or Path)
        config: Optional configuration
        
    Returns:
        Configured RESTToolService instance with all specs loaded
    """
    service = RESTToolService(app, config)
    
    for spec_name, spec_data in specs.items():
        try:
            service.register_openapi_spec(spec_data, spec_name)
        except Exception as e:
            logger.error(f"Failed to load spec '{spec_name}': {e}")
            continue
    
    return service


async def create_service_from_urls(app: FastAPI,
                                 spec_urls: Dict[str, str],
                                 config: Optional[OpenAPIConfig] = None) -> RESTToolService:
    """
    Create RESTToolService by fetching specs from URLs.
    
    Args:
        app: FastAPI application
        spec_urls: Dictionary mapping spec names to URLs
        config: Optional configuration
        
    Returns:
        Configured RESTToolService instance with all specs loaded
    """
    service = RESTToolService(app, config)
    
    for spec_name, url in spec_urls.items():
        try:
            await service.register_openapi_url(url, spec_name)
        except Exception as e:
            logger.error(f"Failed to load spec '{spec_name}' from URL '{url}': {e}")
            continue
    
    return service