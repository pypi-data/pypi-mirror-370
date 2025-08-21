"""
Generic REST API handler for executing HTTP calls from parsed OpenAPI operations.
"""
import httpx
import logging
from typing import Dict, Any, Optional, List
from .rest_models import ParsedOperation, get_auth_value


logger = logging.getLogger(__name__)


class RESTHandler:
    """Generic handler for executing REST API calls."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def execute_operation(self, 
                              operation: ParsedOperation, 
                              parameters: Dict[str, Any],
                              auth_data: Optional[Dict[str, Any]] = None,
                              environment: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a REST API operation with the provided parameters.
        
        Args:
            operation: Parsed operation to execute
            parameters: Parameters for the API call
            auth_data: Authentication data
            environment: Environment variables
            
        Returns:
            Response from the API call
        """
        try:
            # Build the full URL
            url = self._build_url(operation, parameters)
            
            if operation.auth_requirements and any(auth_req.provider == "bearer" for auth_req in operation.auth_requirements):
                auth_value = get_auth_value()
                if auth_value:
                    auth_data = {"Authorization": "Bearer " + auth_value}
            
            # Prepare headers
            headers = self._build_headers(operation, auth_data, environment)
            
            # Prepare request data
            query_params, body_data = self._prepare_request_data(operation, parameters)
            
            logger.info(f"Executing {operation.method} {url}")
            logger.info(f"Query params: {query_params}")
            logger.info(f"Body data: {body_data}")
            
            # Make the HTTP request
            response = await self.client.request(
                method=operation.method,
                url=url,
                params=query_params,
                json=body_data if body_data else None,
                headers=headers
            )
            
            # Handle response
            return self._handle_response(response)
            
        except Exception as e:
            logger.error(f"Error executing operation {operation.name}: {str(e)}")
            raise
    
    def _build_url(self, operation: ParsedOperation, parameters: Dict[str, Any]) -> str:
        """Build the full URL with path parameters substituted."""
        base_url = operation.base_url.rstrip('/')
        path = operation.path
        
        # Substitute path parameters
        for param in operation.parameters:
            if f"{{{param.name}}}" in path:
                if param.name in parameters:
                    path = path.replace(f"{{{param.name}}}", str(parameters[param.name]))
                else:
                    logger.warning(f"Path parameter {param.name} not provided")
        
        return f"{base_url}{path}"
    
    def _build_headers(self, 
                      operation: ParsedOperation,
                      auth_data: Optional[Dict[str, Any]] = None,
                      environment: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Build request headers including authentication."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Opal-REST-Tools/1.0"
        }
        
        # Add authentication headers
        if auth_data:
            # First, check for direct header values (e.g., {"Authorization": "Bearer token"})
            for key, value in auth_data.items():
                if key.lower() in ["authorization", "x-api-key", "api-key"]:
                    headers[key] = value
            
            # Then handle structured auth based on requirements
            if operation.auth_requirements:
                for auth_req in operation.auth_requirements:
                    if auth_req.provider == "api_key":
                        # API Key authentication
                        if "api_key" in auth_data:
                            # Common patterns for API key headers
                            if auth_req.scope_bundle.lower() in ["authorization", "auth"]:
                                headers["Authorization"] = f"Bearer {auth_data['api_key']}"
                            elif auth_req.scope_bundle.lower() == "x-api-key":
                                headers["X-API-Key"] = auth_data["api_key"]
                            else:
                                headers[auth_req.scope_bundle] = auth_data["api_key"]
                    
                    elif auth_req.provider == "bearer":
                        # Bearer token authentication
                        if "token" in auth_data:
                            headers["Authorization"] = f"Bearer {auth_data['token']}"
                    
                    elif auth_req.provider == "oauth2":
                        # OAuth2 authentication
                        if "access_token" in auth_data:
                            headers["Authorization"] = f"Bearer {auth_data['access_token']}"
        
        # Add any custom headers from environment
        if environment and "headers" in environment:
            headers.update(environment["headers"])
        
        return headers
    
    def _prepare_request_data(self, 
                            operation: ParsedOperation, 
                            parameters: Dict[str, Any]) -> tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """Separate parameters into query params and request body."""
        query_params = {}
        body_data = {}
        path_params = set()
        
        # Identify path parameters
        for param in operation.parameters:
            if f"{{{param.name}}}" in operation.path:
                path_params.add(param.name)
        
        # Categorize parameters
        for param in operation.parameters:
            if param.name not in parameters:
                if param.required:
                    logger.warning(f"Required parameter {param.name} not provided")
                continue
            
            value = parameters[param.name]
            
            # HACK: Skip api_key parameter (handled in auth, not request data)
            if param.name == "api_key" and operation.use_api_key_param:
                continue
            
            # Skip path parameters (already handled in URL building)
            if param.name in path_params:
                continue
            
            # For GET requests, all parameters go to query string
            if operation.method == "GET":
                query_params[param.name] = value
            else:
                # For POST/PUT/PATCH, body parameters go to request body
                # Query parameters typically have specific indicators
                if self._is_query_parameter(param.name):
                    query_params[param.name] = value
                else:
                    body_data[param.name] = value
        
        return query_params, body_data if body_data else None
    
    def _is_query_parameter(self, param_name: str) -> bool:
        """Determine if a parameter should be sent as query parameter."""
        # Common query parameter patterns
        query_indicators = [
            "limit", "offset", "page", "size", "sort", "order", "filter",
            "search", "q", "query", "format", "fields", "include", "expand"
        ]
        
        return param_name.lower() in query_indicators
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle and format the HTTP response."""
        result = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
        }
        
        # Handle different content types
        content_type = response.headers.get("content-type", "").lower()
        
        try:
            if "application/json" in content_type:
                result["data"] = response.json()
            elif "text/" in content_type:
                result["data"] = response.text
            else:
                result["data"] = response.content
        except Exception as e:
            logger.warning(f"Error parsing response: {e}")
            result["data"] = response.text
        
        # Check for errors
        if response.status_code >= 400:
            error_msg = f"HTTP {response.status_code}: {response.reason_phrase}"
            if isinstance(result.get("data"), dict) and "message" in result["data"]:
                error_msg += f" - {result['data']['message']}"
            
            result["error"] = error_msg
            logger.error(error_msg)
        
        return result
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()