"""
ZAPI Langchain Tool - Simple & Clean

Basic conversion of ZAPI documented APIs into Langchain tools.
"""

import requests
import json
import os
from typing import Dict, Any, List, Optional, Callable

from langchain_core.tools import tool

from ...core import ZAPI
from ...utils import load_security_headers


class ZAPILangchainTool:
    """
    Simple tool provider to convert ZAPI APIs into Langchain tools.
    
    Supports loading security headers from a JSON file for API authentication.
    The headers file should contain a 'headers' object with key-value pairs
    that will be added to all API requests.
    
    Example headers file (api-headers.json):
    {
        "headers": {
            "Authorization": "Bearer your-token",
            "X-API-Key": "your-api-key",
            "X-Client-ID": "your-client-id"
        }
    }
    """
    
    def __init__(self, zapi_instance: ZAPI, headers_file: Optional[str] = None):
        self.zapi = zapi_instance
        self.security_headers = load_security_headers(headers_file)
    
    def create_tools(self) -> List[Callable]:
        """Create Langchain tools from documented APIs."""
        # Get APIs from ZAPI
        response = self.zapi.get_documented_apis(page_size=50)
        apis = response.get('items', [])
        
        # Create tools
        tools = []
        for api_data in apis:
            try:
                tool_func = self._create_tool(api_data)
                tools.append(tool_func)
            except Exception as e:
                print(f"Error creating tool: {e}")
                continue  # Skip failed tools
        
        return tools
    
    def _create_tool(self, api_data: Dict[str, Any]) -> Callable:
        """Create a tool from API data."""
        api_id = api_data.get('id', '')
        api_name = api_data.get('title', f'api_{api_id}')
        description = api_data.get('description', f"{api_data.get('api_type', 'GET')} {api_data.get('path', '/')}")
        
        @tool(description=description)
        def api_tool(**kwargs) -> Dict[str, Any]:
            """Dynamically created ZAPI tool for API calls."""
            return self._call_api(api_id, api_data, kwargs)
        
        # Set the tool name (clean it for use as function name)
        clean_name = api_name.lower().replace(' ', '_').replace('-', '_').replace('/', '_')
        # Remove any non-alphanumeric characters except underscores
        clean_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in clean_name)
        # Ensure it starts with a letter or underscore
        if clean_name and not (clean_name[0].isalpha() or clean_name[0] == '_'):
            clean_name = f"api_{clean_name}"
        
        api_tool.name = clean_name or f"api_{api_id}"
        
        return api_tool
    
    def _call_api(self, api_id: str, api_data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Make the actual API call with comprehensive error handling."""
        import logging
        import os
        
        method = api_data.get('api_type', 'GET')  # Use 'api_type' instead of 'method'
        path = api_data.get('path', '/')
        base_url = api_data.get('base_url', '') or os.getenv('YOUR_API_BASE_URL', '')
        
        # Validate base_url
        if not base_url:
            return {
                'error': True,
                'error_type': 'configuration_error',
                'message': 'No base URL configured for API call',
                'details': 'Either set base_url in API configuration or YOUR_API_BASE_URL environment variable',
                'api_id': api_id,
                'path': path
            }
        
        # Build URL
        url = f"{base_url.rstrip('/')}{path}"
        
        # Replace path parameters
        for key, value in params.items():
            url = url.replace(f'{{{key}}}', str(value))
        
        # Prepare request
        headers = {}
        data = None
        
        # Add security headers from loaded configuration
        headers.update(self.security_headers)
        
        # Set data for POST/PUT
        if method.upper() in ['POST', 'PUT']:
            data = {k: v for k, v in params.items() if f'{{{k}}}' not in api_data.get('path', '')}
        
        # Log request details
        logging.info(f"API Call - {method.upper()} {url}")
        if data:
            logging.debug(f"Request data: {data}")
        
        # Make request
        response = None
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data if data else None,
                timeout=30
            )
            
            # Log response details
            logging.info(f"API Response - Status: {response.status_code}")
            
            # Handle successful responses (2xx)
            if 200 <= response.status_code < 300:
                try:
                    return response.json() if response.content else {'status': 'success'}
                except ValueError as e:
                    # JSON parsing failed but status was successful
                    logging.warning(f"JSON parsing failed for successful response: {str(e)}")
                    return {
                        'status': 'success',
                        'raw_response': response.text,
                        'content_type': response.headers.get('content-type', 'unknown'),
                        'warning': f'Response not valid JSON: {str(e)}'
                    }
            
            # Handle client errors (4xx) and server errors (5xx)
            else:
                error_response = {
                    'error': True,
                    'status_code': response.status_code,
                    'status_text': response.reason,
                    'url': url,
                    'method': method.upper()
                }
                
                # Try to get JSON error response
                try:
                    error_response['response'] = response.json()
                except ValueError:
                    # Not JSON, capture raw text
                    error_response['raw_response'] = response.text
                
                # Add response headers that might be useful
                useful_headers = ['content-type', 'www-authenticate', 'retry-after', 'x-ratelimit-remaining']
                response_headers = {k: v for k, v in response.headers.items() 
                                 if k.lower() in useful_headers}
                if response_headers:
                    error_response['headers'] = response_headers
                
                logging.error(f"API Error - {response.status_code}: {error_response}")
                return error_response
                
        except requests.exceptions.Timeout as e:
            error_response = {
                'error': True,
                'error_type': 'timeout',
                'message': f'Request timed out after 30 seconds',
                'url': url,
                'method': method.upper(),
                'details': str(e)
            }
            logging.error(f"API Timeout: {error_response}")
            return error_response
            
        except requests.exceptions.ConnectionError as e:
            error_response = {
                'error': True,
                'error_type': 'connection_error',
                'message': 'Failed to connect to the API endpoint',
                'url': url,
                'method': method.upper(),
                'details': str(e)
            }
            logging.error(f"API Connection Error: {error_response}")
            return error_response
            
        except requests.exceptions.HTTPError as e:
            error_response = {
                'error': True,
                'error_type': 'http_error',
                'message': 'HTTP error occurred',
                'url': url,
                'method': method.upper(),
                'details': str(e)
            }
            if response:
                error_response['status_code'] = response.status_code
                error_response['status_text'] = response.reason
            logging.error(f"API HTTP Error: {error_response}")
            return error_response
            
        except requests.exceptions.RequestException as e:
            error_response = {
                'error': True,
                'error_type': 'request_error',
                'message': 'Request failed',
                'url': url,
                'method': method.upper(),
                'details': str(e)
            }
            logging.error(f"API Request Error: {error_response}")
            return error_response
            
        except Exception as e:
            error_response = {
                'error': True,
                'error_type': 'unexpected_error',
                'message': 'An unexpected error occurred',
                'url': url,
                'method': method.upper(),
                'details': str(e),
                'exception_type': type(e).__name__
            }
            logging.error(f"API Unexpected Error: {error_response}")
            return error_response
