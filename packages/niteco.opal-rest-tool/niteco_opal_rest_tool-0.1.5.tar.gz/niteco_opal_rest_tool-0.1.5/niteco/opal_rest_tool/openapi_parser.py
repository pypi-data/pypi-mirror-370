"""
OpenAPI specification parser for generating tools from REST API specs.
"""
import json
import yaml
import re
from typing import Dict, Any, List, Optional, Union
from opal_tools_sdk.models import Parameter, ParameterType, AuthRequirement
from .rest_models import ParsedOperation, OpenAPIConfig


class OpenAPISpecParser:
    """Parser for OpenAPI 3.x specifications."""
    
    def __init__(self, config: Optional[OpenAPIConfig] = None):
        self.config = config or OpenAPIConfig()
    
    def parse(self, openapi_spec: Union[str, Dict[str, Any]]) -> List[ParsedOperation]:
        """
        Parse OpenAPI specification and return list of operations.
        
        Args:
            openapi_spec: OpenAPI spec as string (JSON/YAML) or dict
            
        Returns:
            List of ParsedOperation objects
        """
        if isinstance(openapi_spec, str):
            spec_dict = self._parse_spec_string(openapi_spec)
        else:
            spec_dict = openapi_spec
            
        # Resolve any $ref references
        spec_dict = self._resolve_references(spec_dict)
        
        # Collect operations from paths
        return self._collect_operations(spec_dict)
    
    def _parse_spec_string(self, spec_string: str) -> Dict[str, Any]:
        """Parse OpenAPI spec string (JSON or YAML)."""
        spec_string = spec_string.strip()
        
        try:
            # Try JSON first
            return json.loads(spec_string)
        except json.JSONDecodeError:
            try:
                # Try YAML
                return yaml.safe_load(spec_string)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid OpenAPI spec format: {e}")
    
    def _resolve_references(self, spec_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve $ref references in the spec."""
        # Simplified reference resolution - for production, use a proper resolver
        # For now, just return as-is
        return spec_dict
    
    def _collect_operations(self, spec_dict: Dict[str, Any]) -> List[ParsedOperation]:
        """Collect all operations from the OpenAPI spec."""
        operations = []
        
        # Get base URL
        base_url = self._extract_base_url(spec_dict)
        
        # Get global security schemes
        global_security = spec_dict.get("security", [])
        security_schemes = spec_dict.get("components", {}).get("securitySchemes", {})
        
        paths = spec_dict.get("paths", {})
        
        for path, path_item in paths.items():
            # Get path-level parameters
            path_parameters = path_item.get("parameters", [])
            
            # Process each HTTP method
            http_methods = ["get", "post", "put", "delete", "patch", "head", "options"]
            
            for method in http_methods:
                if method not in path_item:
                    continue
                    
                operation = path_item[method]
                operation_id = operation.get("operationId")
                
                # Generate operation name
                if operation_id:
                    name = self._to_snake_case(operation_id)
                else:
                    # Generate name from path and method
                    clean_path = re.sub(r'[{}]', '', path).strip('/')
                    name = f"{method}_{clean_path}".replace('/', '_').replace('-', '_')
                    name = re.sub(r'_+', '_', name).strip('_')
                
                # Apply filters if configured
                if self.config.filter_operations and name not in self.config.filter_operations:
                    continue
                if self.config.exclude_operations and name in self.config.exclude_operations:
                    continue
                
                # Extract parameters
                parameters = self._extract_parameters(operation, path_parameters)
                
                # Extract auth requirements
                auth_requirements = self._extract_auth_requirements(
                    operation, global_security, security_schemes
                )
                
                # Create parsed operation
                parsed_op = ParsedOperation(
                    name=name,
                    description=operation.get("description", operation.get("summary", f"{method.upper()} {path}")),
                    method=method.upper(),
                    path=path,
                    base_url=base_url,
                    parameters=parameters,
                    auth_requirements=auth_requirements,
                    operation_id=operation_id,
                    request_body_schema=operation.get("requestBody"),
                    response_schema=operation.get("responses"),
                    omit_auth_from_discovery_metadata=self.config.omit_auth_from_discovery_metadata  # HACK: implicit login with dotenv config
                )
                
                operations.append(parsed_op)
        
        return operations
    
    def _extract_base_url(self, spec_dict: Dict[str, Any]) -> str:
        """Extract base URL from servers section."""
        if self.config.base_url:
            return self.config.base_url
            
        servers = spec_dict.get("servers", [])
        if servers:
            return servers[0].get("url", "")
        
        return ""
    
    def _extract_parameters(self, operation: Dict[str, Any], path_parameters: List[Dict]) -> List[Parameter]:
        """Extract parameters from operation and path."""
        parameters = []
        
        # Combine operation and path parameters
        all_params = list(path_parameters)
        all_params.extend(operation.get("parameters", []))
        
        for param in all_params:
            # Skip parameters that don't have a name (invalid parameters)
            if "name" not in param:
                continue
                
            param_type = self._map_openapi_type_to_parameter_type(param.get("schema", {}))
            
            parameters.append(Parameter(
                name=param["name"],
                param_type=param_type,
                description=param.get("description", ""),
                required=param.get("required", False)
            ))
        
        # Handle request body as parameters
        request_body = operation.get("requestBody")
        if request_body:
            content = request_body.get("content", {})
            # Look for JSON content
            for content_type in ["application/json", "application/x-www-form-urlencoded"]:
                if content_type in content:
                    schema = content[content_type].get("schema", {})
                    body_params = self._extract_schema_parameters(schema, request_body.get("required", False))
                    parameters.extend(body_params)
                    break
        
        return parameters
    
    def _extract_schema_parameters(self, schema: Dict[str, Any], required: bool = False) -> List[Parameter]:
        """Extract parameters from a JSON schema."""
        parameters = []
        
        if schema.get("type") == "object":
            properties = schema.get("properties", {})
            required_fields = set(schema.get("required", []))
            
            for prop_name, prop_schema in properties.items():
                param_type = self._map_openapi_type_to_parameter_type(prop_schema)
                
                parameters.append(Parameter(
                    name=prop_name,
                    param_type=param_type,
                    description=prop_schema.get("description", ""),
                    required=prop_name in required_fields
                ))
        
        return parameters
    
    def _map_openapi_type_to_parameter_type(self, schema: Dict[str, Any]) -> ParameterType:
        """Map OpenAPI schema type to ParameterType."""
        schema_type = schema.get("type", "string")
        
        type_mapping = {
            "string": ParameterType.string,
            "integer": ParameterType.integer,
            "number": ParameterType.number,
            "boolean": ParameterType.boolean,
            "array": ParameterType.list,
            "object": ParameterType.dictionary
        }
        
        return type_mapping.get(schema_type, ParameterType.string)
    
    def _extract_auth_requirements(self, 
                                 operation: Dict[str, Any], 
                                 global_security: List[Dict],
                                 security_schemes: Dict[str, Any]) -> Optional[List[AuthRequirement]]:
        """Extract authentication requirements from operation."""
        # Get security requirements (operation-level overrides global)
        security = operation.get("security", global_security)
        
        if not security or not security_schemes:
            return None
        
        auth_requirements = []
        
        for security_req in security:
            for scheme_name, scopes in security_req.items():
                if scheme_name in security_schemes:
                    scheme = security_schemes[scheme_name]
                    
                    # Map different auth types to providers
                    auth_type = scheme.get("type")
                    provider = ""
                    scope_bundle = ""
                    
                    if auth_type == "oauth2":
                        provider = "oauth2"
                        scope_bundle = ",".join(scopes) if scopes else ""
                    elif auth_type == "apiKey":
                        provider = "api_key"
                        scope_bundle = scheme.get("name", "")
                    elif auth_type == "http":
                        provider = scheme.get("scheme", "bearer")
                    
                    auth_requirements.append(AuthRequirement(
                        provider=provider,
                        scope_bundle=scope_bundle,
                        required=True
                    ))
        
        return auth_requirements if auth_requirements else None
    
    def _to_snake_case(self, name: str) -> str:
        """Convert string to snake_case."""
        # Replace special characters with underscore
        name = re.sub(r'[^a-zA-Z0-9]', '_', name)
        # Convert camelCase to snake_case
        name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
        # Convert to lowercase and clean up underscores
        name = name.lower()
        name = re.sub(r'_+', '_', name)
        return name.strip('_')