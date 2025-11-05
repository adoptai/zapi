"""Core ZAPI class implementation."""

import asyncio
import requests
from .session import BrowserSession


class ZAPI:
    """
    Zero-Config API Intelligence main class.
    
    This class provides a simple interface to launch browser sessions,
    capture network traffic, and export HAR files for API discovery.
    """
    
    def __init__(
        self, 
        client_id: str,
        secret: str
    ):
        """
        Initialize ZAPI instance.
        
        Args:
            client_id: Client ID for authentication
            secret: Secret key for authentication
            
        Raises:
            ValueError: If client_id or secret is empty
            RuntimeError: If token fetch fails
        """
        if not client_id or not client_id.strip():
            raise ValueError("client_id cannot be empty")
        if not secret or not secret.strip():
            raise ValueError("secret cannot be empty")
        
        self.client_id = client_id
        self.secret = secret
        self.auth_token = self._fetch_auth_token()
    
    def _fetch_auth_token(self) -> str:
        """
        Fetch authentication token from adopt.ai API.
        
        Returns:
            Authentication token string
            
        Raises:
            RuntimeError: If token fetch fails
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
                return data["token"]
            elif "access_token" in data:
                return data["access_token"]
            else:
                raise RuntimeError(f"Unexpected response format: {data}")
                
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to fetch authentication token: {e}")
    
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
            
        Example:
            >>> z = ZAPI(client_id="YOUR_CLIENT_ID", secret="YOUR_SECRET")
            >>> session = z.launch_browser(url="https://app.example.com")
            >>> session.dump_logs("session.har")
            >>> session.close()
        """
        print(f"Launching browser with auth token: {self.auth_token}")
        session = BrowserSession(
            auth_token=self.auth_token,
            headless=headless,
            **playwright_options
        )
        
        # Initialize the session synchronously
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(session._initialize(initial_url=url, wait_until=wait_until))
        
        return session

    def upload_har(self, har_file: str):
        """
        Upload a HAR file to the ZAPI API.
        
        Args:
            har_file: Path to the HAR file to upload
        
        Returns:
            Response JSON from the API
        
        Raises:
            requests.exceptions.RequestException: If the upload fails
        """
        url = "https://api.adopt.ai/v1/manual-api-file/upload"
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        # Prepare file for upload
        with open(har_file, 'rb') as f:
            files = {
                'file': (har_file, f, 'application/json')
            }
            response = requests.post(url, headers=headers, files=files)
        
        print("file uploaded successfully")
        response.raise_for_status()
        return response.json()


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