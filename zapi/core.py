"""Core ZAPI class implementation."""

import asyncio
import json
import requests
import httpx
from typing import Optional, Dict, Any, List, Callable
from .session import BrowserSession
from .providers import validate_llm_keys
from .encryption import LLMKeyEncryption
from .utils import load_zapi_credentials


class ZAPIError(Exception):
    """Base exception class for ZAPI errors."""
    pass


class ZAPIAuthenticationError(ZAPIError):
    """Authentication-related errors."""
    pass


class ZAPIValidationError(ZAPIError):
    """Input validation errors."""
    pass


class ZAPINetworkError(ZAPIError):
    """Network-related errors."""
    pass


class ZAPI:
    """
    Zero-Config API Intelligence main class.
    
    This class provides a simple interface to launch browser sessions,
    capture network traffic, and export HAR files for API discovery.
    """
    
    def __init__(
        self, 
        client_id: Optional[str] = None,
        secret: Optional[str] = None,
        llm_provider: Optional[str] = None,
        llm_model_name: Optional[str] = None,
        llm_api_key: Optional[str] = None
    ):
        """
        Initialize ZAPI instance.
        
        Args:
            client_id: Client ID for authentication. If None, loads from ADOPT_CLIENT_ID env var.
            secret: Secret key for authentication. If None, loads from ADOPT_SECRET_KEY env var.
            llm_provider: LLM provider name (e.g., "anthropic"). If None, loads from LLM_PROVIDER env var.
            llm_model_name: LLM model name (e.g., "claude-3-5-sonnet-20241022"). If None, loads from LLM_MODEL_NAME env var.
            llm_api_key: LLM API key for the specified provider. If None, loads from LLM_API_KEY env var.
            
        Raises:
            ValueError: If client_id or secret is empty, or LLM key format is invalid
            RuntimeError: If token fetch fails
        """
        # Auto-load credentials from environment if not provided
        if client_id is None or secret is None or llm_provider is None or llm_model_name is None or llm_api_key is None:
            env_client_id, env_secret, env_llm_provider, env_llm_model_name, env_llm_api_key = load_zapi_credentials()
            
            # Use provided values or fallback to environment values
            client_id = client_id or env_client_id
            secret = secret or env_secret
            llm_provider = llm_provider or env_llm_provider
            llm_model_name = llm_model_name or env_llm_model_name
            llm_api_key = llm_api_key or env_llm_api_key
        
        if not client_id or not client_id.strip():
            raise ZAPIValidationError("client_id cannot be empty")
        if not secret or not secret.strip():
            raise ZAPIValidationError("secret cannot be empty")
        
        self.client_id = client_id
        self.secret = secret
        
        # Fetch auth token and extract org_id
        self.auth_token, self.org_id, self.email = self._fetch_auth_token()
        
        # Initialize encryption handler
        self._key_encryptor = LLMKeyEncryption(self.org_id)
        
        # Validate and encrypt LLM key if provided
        self._encrypted_llm_key: str = ""
        self._llm_provider: str = llm_provider
        self._llm_model_name: str = llm_model_name
        self.set_llm_key(llm_provider, llm_api_key, llm_model_name)
        
        # Automatically set LLM API key in environment for LangChain compatibility
        if self._llm_provider and self._encrypted_llm_key:
            from .utils import set_llm_api_key_env
            try:
                set_llm_api_key_env(self._llm_provider, self.get_decrypted_llm_key())
            except Exception:
                # Silently fail if LangChain integration is not available
                pass
            
    def _fetch_auth_token(self) -> tuple[str, str]:
        """
        Fetch authentication token from adopt.ai API and extract org_id.
        
        Returns:
            Tuple of (authentication_token, org_id)
            
        Raises:
            RuntimeError: If token fetch fails or org_id extraction fails
        """
        url = "https://connect.adopt.ai/v1/auth/token"
        payload = {
            "clientId": self.client_id,
            "secret": self.secret
        }
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Extract token from response
            if "token" in data:
                token = data["token"]
            elif "access_token" in data:
                token = data["access_token"]
            else:
                raise RuntimeError(f"Unexpected response format: {data}")
            
            # Validate token and extract org_id via backend API
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            org_id, email = loop.run_until_complete(self._validate_token_and_extract_org_id(token))
            
            return token, org_id, email
                
        except requests.exceptions.Timeout:
            raise ZAPINetworkError("Authentication request timed out. Please check your internet connection.")
        except requests.exceptions.ConnectionError:
            raise ZAPINetworkError("Cannot connect to adopt.ai authentication service. Please check your internet connection.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ZAPIAuthenticationError("Invalid client_id or secret. Please check your credentials.")
            elif e.response.status_code == 403:
                raise ZAPIAuthenticationError("Access forbidden. Please check your account permissions.")
            else:
                raise ZAPIAuthenticationError(f"Authentication failed: HTTP {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ZAPINetworkError(f"Failed to fetch authentication token: {e}")
    
    async def _validate_token_and_extract_org_id(self, token: str) -> str:
        """
        Validate JWT token via backend API and extract org_id.
        
        Args:
            token: JWT token string
            
        Returns:
            Organization ID extracted from validated token
            
        Raises:
            RuntimeError: If token validation fails or org_id extraction fails
        """
        # Use adopt.ai backend API for token validation
        backend_url = "https://connect.adopt.ai"  # Adjust if different
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{backend_url}/v1/auth/validate-token",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                )
                response.raise_for_status()
                
                validation_result = response.json()
                
                # API returns org_id and user_email directly on success
                org_id = validation_result.get('org_id')
                email = validation_result.get('user_email', "")
                if not org_id or not isinstance(org_id, str):
                    raise RuntimeError("Invalid org_id in validation response")

                print(f"Org ID: {org_id}")
                print(f"Email: {email}")
                
                return org_id, email
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise ZAPIAuthenticationError("Token validation failed: Invalid or expired token")
                elif e.response.status_code == 403:
                    raise ZAPIAuthenticationError("Token validation failed: Access forbidden")
                else:
                    raise ZAPINetworkError(f"Backend token validation failed: HTTP {e.response.status_code}")
            except httpx.ConnectTimeout:
                raise ZAPINetworkError("Token validation timed out. Please check your internet connection.")
            except httpx.RequestError as e:
                raise ZAPINetworkError(f"Token validation request failed: {e}")
            except Exception as e:
                raise ZAPIError(f"Token validation error: {e}")
    
    def set_llm_key(self, provider: str, api_key: str, model_name: str) -> None:
        """
        Set LLM API key for a specific provider.
        
        Args:
            provider: Provider name (e.g., "anthropic")
            api_key: API key for the specified provider
            
        Raises:
            ValueError: If provider or api_key format is invalid
            RuntimeError: If encryption fails
        """
        if not provider or not api_key:
            self._encrypted_llm_key = None
            self._llm_provider = None
            self._llm_model_name = None
            return
        
        # Validate key format for the provider
        try:
            validated_keys = validate_llm_keys({provider: api_key})
            validated_provider = list(validated_keys.keys())[0]
            validated_key = list(validated_keys.values())[0]
        except ValueError as e:
            raise ZAPIValidationError(f"LLM key validation failed: {e}")
        
        # Encrypt only the API key using org_id (provider stored separately)
        try:
            self._encrypted_llm_key = self._key_encryptor.encrypt_key(validated_key)
            self._llm_provider = validated_provider
            self._llm_model_name = model_name
        except Exception as e:
            raise ZAPIError(f"Failed to encrypt LLM key: {e}")
    
    def get_llm_provider(self) -> Optional[str]:
        """
        Get the configured LLM provider.
        
        Returns:
            Provider name if configured, None otherwise
        """
        return self._llm_provider

    def get_llm_model_name(self) -> Optional[str]:
        """
        Get the configured LLM model name.
        
        Returns:
            Model name if configured, None otherwise
        """
        return self._llm_model_name
    
    def get_encrypted_llm_key(self) -> Optional[str]:
        """
        Get the encrypted LLM API key.
        
        Returns:
            Encrypted API key if configured, None otherwise
        """
        return self._encrypted_llm_key

    def get_decrypted_llm_key(self) -> Optional[str]:
        """
        Get the decrypted LLM API key.
        
        Returns:
            Decrypted API key if configured, None otherwise
        """
        try:
            if not self._encrypted_llm_key:
                return None
            return self._key_encryptor.decrypt_key(self._encrypted_llm_key)
        except Exception as e:
            print(f"Failed to decrypt LLM key: {e}")
            return None
    
    def has_llm_key(self) -> bool:
        """
        Check if LLM key is configured.
        
        Returns:
            True if LLM key is set, False otherwise
        """
        return self._encrypted_llm_key is not None
    
    
    def get_zapi_tools(self) -> List[Callable]:
        """
        Get LangChain tools from ZAPI (created on-demand).
        
        Returns:
            List of LangChain tool functions
        """
        try:
            from .integrations.langchain.tool import ZAPILangchainTool
            tool_creator = ZAPILangchainTool(self)
            return tool_creator.create_tools()
        except ImportError:
            raise ImportError("LangChain integration not available. Install langchain to use this feature.")
    
    def launch_browser(
        self,
        url: str,
        headless: bool = True,
        wait_until: str = "load",
        **playwright_options
    ) -> BrowserSession:
        """
        Launch a browser session with network logging.
        
        Args:
            url: Initial URL to navigate to
            headless: Whether to run browser in headless mode (default: True)
            wait_until: When to consider navigation complete (default: "load")
                       Options: "load", "domcontentloaded", "networkidle"
            **playwright_options: Additional Playwright browser launch options
            
        Returns:
            BrowserSession instance ready for navigation and interaction
            
        Raises:
            ZAPIValidationError: If URL format is invalid
            ZAPIError: If browser launch fails
            
        Example:
            >>> z = ZAPI(client_id="YOUR_CLIENT_ID", secret="YOUR_SECRET")
            >>> session = z.launch_browser(url="https://app.example.com")
            >>> session.dump_logs("session.har")
            >>> session.close()
        """
        session = BrowserSession(
            auth_token=self.auth_token,
            headless=headless,
            **playwright_options
        )
        
        # Initialize the session synchronously with enhanced error handling
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(session._initialize(initial_url=url, wait_until=wait_until))
        except Exception as e:
            # Close session if initialization failed
            try:
                session.close()
            except Exception:
                # Ignore cleanup errors, focus on the original error
                pass
            
            error_message = str(e)
            
            # Provide specific error messages for common browser issues
            if "Cannot navigate to invalid URL" in error_message:
                raise ZAPIValidationError(
                    f"Browser cannot navigate to URL: '{url}'. "
                    "Please check the URL format and ensure it's accessible."
                )
            elif "net::ERR_NAME_NOT_RESOLVED" in error_message:
                raise ZAPINetworkError(
                    f"Domain name could not be resolved: '{url}'. "
                    "Please check the URL spelling and your internet connection."
                )
            elif "net::ERR_CONNECTION_REFUSED" in error_message:
                raise ZAPINetworkError(
                    f"Connection refused to: '{url}'. "
                    "The server may be down or the URL may be incorrect."
                )
            elif "Timeout" in error_message:
                raise ZAPINetworkError(
                    f"Timeout while loading: '{url}'. "
                    "The website took too long to respond. Please try again or use a different URL."
                )
            else:
                raise ZAPIError(f"Failed to launch browser session: {error_message}")
        
        return session

    def upload_har(self, har_file: str):
        """
        Upload a HAR file to the ZAPI API with optional encrypted LLM keys.
        
        Args:
            har_file: Path to the HAR file to upload
        
        Returns:
            Response JSON from the API
        
        Raises:
            ZAPIValidationError: If file validation fails
            ZAPINetworkError: If upload fails due to network issues
            ZAPIAuthenticationError: If authentication fails
        """
        url = "https://connect.adopt.ai/v1/api-discovery/upload-file"
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        # Prepare metadata if LLM key is configured
        metadata = {}
        if self.has_llm_key():
            metadata = {
                "byok_encrypted_llm_key": self._encrypted_llm_key,
                "byok_llm_provider": self._llm_provider,  # Provider sent in plaintext
                "byok_llm_model": self._llm_model_name,
                "byok_enabled": True,
                "is_trial_user": True,
            }

            if self.email:
                metadata["user_email"] = self.email
        else:
            metadata = {
                "byok_enabled": False,
                "is_trial_user": True,
            }

            if self.email:
                metadata["user_email"] = self.email
        
        # Prepare multipart form data with enhanced error handling
        try:
            with open(har_file, 'rb') as f:
                files = {
                    'file': (har_file, f, 'application/json')
                }
                
                # Add metadata as form data
                data = {
                    'metadata': json.dumps(metadata)
                }
                
                response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
        
        except FileNotFoundError:
            raise ZAPIValidationError(f"HAR file not found: '{har_file}'")
        except PermissionError:
            raise ZAPIValidationError(f"Permission denied reading HAR file: '{har_file}'")
        except requests.exceptions.Timeout:
            raise ZAPINetworkError("Upload request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            raise ZAPINetworkError("Cannot connect to ZAPI upload service. Please check your internet connection.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ZAPIAuthenticationError("Upload failed: Invalid or expired authentication token")
            elif e.response.status_code == 413:
                raise ZAPIValidationError("HAR file is too large. Please try with a smaller session.")
            elif e.response.status_code == 400:
                raise ZAPIValidationError("Invalid HAR file format. Please ensure the file was generated correctly.")
            else:
                raise ZAPINetworkError(f"Upload failed: HTTP {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ZAPINetworkError(f"Upload request failed: {e}")
        
        try:
            response.raise_for_status()
            print("file uploaded successfully")
            if self.has_llm_key():
                print(f"Included encrypted key for provider: {self.get_llm_provider()}")
            return response.json()
        except requests.exceptions.HTTPError:
            # This should be caught above, but just in case
            raise ZAPINetworkError(f"Upload failed with status code: {response.status_code}")
        except json.JSONDecodeError:
            raise ZAPIError("Invalid response format from upload service")


    def get_documented_apis(self, page: int = 1, page_size: int = 10):
        """
        Fetch the list of documented APIs with pagination support.
        
        Args:
            page: Page number to fetch (default: 1)
            page_size: Number of items per page (default: 10)
        
        Returns:
            Response JSON containing the list of documented APIs
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = "https://connect.adopt.ai/v1/tools/apis"
        headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }
        params = {
            "page": page,
            "page_size": page_size
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()