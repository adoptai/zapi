"""BrowserSession implementation with Playwright integration."""

import asyncio
from pathlib import Path
from typing import Optional, Union
from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Playwright,
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
)

from .auth import get_auth_handler


def _run_async(coro):
    """Helper to run async coroutines synchronously."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop.is_running():
        # If we're already in an async context, just return the coroutine
        return coro
    else:
        # Run synchronously
        return loop.run_until_complete(coro)


class BrowserSessionError(Exception):
    """Base exception for browser session errors."""
    pass


class BrowserNavigationError(BrowserSessionError):
    """Navigation-related browser errors."""
    pass


class BrowserInitializationError(BrowserSessionError):
    """Browser initialization errors."""
    pass


class BrowserSession:
    """
    Manages a Playwright browser session with HAR recording and network log capture.
    
    This class handles browser lifecycle, authentication injection, navigation,
    and HAR file export for API discovery.
    """
    
    def __init__(
        self,
        auth_token: str,
        headless: bool = True,
        **playwright_options
    ):
        """
        Initialize a browser session.
        
        Args:
            auth_token: Authentication token to inject via Authorization header
            headless: Whether to run browser in headless mode
            **playwright_options: Additional options for Playwright browser launch
        """
        self.auth_token = auth_token
        self.headless = headless
        self.playwright_options = playwright_options
        
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._har_path: Optional[Path] = None
        
    async def _initialize(self, initial_url: Optional[str] = None, wait_until: str = "load"):
        """
        Initialize Playwright browser, context, and page.
        
        Args:
            initial_url: Optional initial URL to navigate to
            wait_until: When to consider navigation complete (default: "load")
            
        Raises:
            BrowserInitializationError: If browser initialization fails
            BrowserNavigationError: If initial navigation fails
        """
        try:
            # Start Playwright
            self._playwright = await async_playwright().start()
            
            # Launch browser with enhanced error handling
            try:
                self._browser = await self._playwright.chromium.launch(
                    headless=self.headless,
                    **self.playwright_options
                )
            except Exception as e:
                raise BrowserInitializationError(
                    f"Failed to launch browser: {str(e)}. "
                    "This may be due to missing browser dependencies or system restrictions."
                )
            
            # Create temporary HAR file path
            import tempfile
            self._har_path = Path(tempfile.mktemp(suffix=".har"))
            
            # Create context with HAR recording
            try:
                self._context = await self._browser.new_context(
                    record_har_path=str(self._har_path),
                    record_har_mode="minimal",
                )
            except Exception as e:
                raise BrowserInitializationError(
                    f"Failed to create browser context: {str(e)}"
                )
            
            # Apply header-based authentication (Bearer token)
            try:
                auth_handler = get_auth_handler("header")
                await auth_handler(self._context, self.auth_token)
            except Exception as e:
                raise BrowserInitializationError(
                    f"Failed to apply authentication: {str(e)}"
                )
            
            # Create page
            try:
                self._page = await self._context.new_page()
            except Exception as e:
                raise BrowserInitializationError(
                    f"Failed to create browser page: {str(e)}"
                )
            
            # Navigate to initial URL if provided
            if initial_url:
                await self._navigate_async(initial_url, wait_until=wait_until)
                
        except (BrowserInitializationError, BrowserNavigationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Catch any other unexpected errors
            raise BrowserInitializationError(
                f"Unexpected error during browser initialization: {str(e)}"
            )
    
    async def _navigate_async(self, url: str, wait_until: str = "load") -> None:
        """
        Internal async navigate method with enhanced error handling.
        
        Args:
            url: URL to navigate to
            wait_until: When to consider navigation complete
                       ("load", "domcontentloaded", "networkidle")
                       
        Raises:
            BrowserNavigationError: If navigation fails
        """
        if not self._page:
            raise BrowserSessionError("Browser session not initialized. Call _initialize() first.")
        
        try:
            # Navigate with Authorization header already set
            await self._page.goto(url, wait_until=wait_until, timeout=30000)  # 30 second timeout
            
        except PlaywrightTimeoutError:
            raise BrowserNavigationError(
                f"Navigation timeout: '{url}' took too long to load. "
                "The website may be slow or unresponsive. Try again or use a different URL."
            )
        except PlaywrightError as e:
            error_message = str(e)
            
            if "Cannot navigate to invalid URL" in error_message:
                raise BrowserNavigationError(
                    f"Invalid URL format: '{url}'. "
                    "Please ensure the URL is properly formatted (e.g., 'https://example.com')."
                )
            elif "net::ERR_NAME_NOT_RESOLVED" in error_message:
                raise BrowserNavigationError(
                    f"Domain name could not be resolved: '{url}'. "
                    "Please check the URL spelling and your internet connection."
                )
            elif "net::ERR_CONNECTION_REFUSED" in error_message:
                raise BrowserNavigationError(
                    f"Connection refused: '{url}'. "
                    "The server may be down or the URL may be incorrect."
                )
            elif "net::ERR_CONNECTION_TIMED_OUT" in error_message:
                raise BrowserNavigationError(
                    f"Connection timed out: '{url}'. "
                    "The server took too long to respond. Please try again."
                )
            elif "net::ERR_INTERNET_DISCONNECTED" in error_message:
                raise BrowserNavigationError(
                    "No internet connection detected. Please check your network connection."
                )
            elif "net::ERR_CERT_AUTHORITY_INVALID" in error_message:
                raise BrowserNavigationError(
                    f"SSL certificate error for: '{url}'. "
                    "The website's security certificate is invalid or expired."
                )
            else:
                raise BrowserNavigationError(
                    f"Navigation failed for '{url}': {error_message}"
                )
        except Exception as e:
            raise BrowserNavigationError(
                f"Unexpected navigation error for '{url}': {str(e)}"
            )
    
    def navigate(self, url: str, wait_until: str = "load") -> None:
        """
        Navigate to a URL with authentication injection.
        
        Args:
            url: URL to navigate to
            wait_until: When to consider navigation complete
                       ("load", "domcontentloaded", "networkidle")
                       
        Raises:
            BrowserNavigationError: If navigation fails
        """
        _run_async(self._navigate_async(url, wait_until))
    
    async def _click_async(self, selector: str, **kwargs) -> None:
        """
        Internal async click method with error handling.
        
        Raises:
            BrowserSessionError: If click operation fails
        """
        if not self._page:
            raise BrowserSessionError("Browser session not initialized.")
        
        try:
            await self._page.click(selector, **kwargs)
        except PlaywrightTimeoutError:
            raise BrowserSessionError(
                f"Element not found or not clickable: '{selector}'. "
                "Please check the selector or wait for the page to load completely."
            )
        except PlaywrightError as e:
            raise BrowserSessionError(
                f"Click failed for selector '{selector}': {str(e)}"
            )
    
    def click(self, selector: str, **kwargs) -> None:
        """
        Click an element by selector.
        
        Args:
            selector: CSS selector for the element
            **kwargs: Additional options for Playwright click
        """
        _run_async(self._click_async(selector, **kwargs))
    
    async def _fill_async(self, selector: str, value: str, **kwargs) -> None:
        """
        Internal async fill method with error handling.
        
        Raises:
            BrowserSessionError: If fill operation fails
        """
        if not self._page:
            raise BrowserSessionError("Browser session not initialized.")
        
        try:
            await self._page.fill(selector, value, **kwargs)
        except PlaywrightTimeoutError:
            raise BrowserSessionError(
                f"Input element not found: '{selector}'. "
                "Please check the selector or wait for the page to load completely."
            )
        except PlaywrightError as e:
            raise BrowserSessionError(
                f"Fill failed for selector '{selector}': {str(e)}"
            )
    
    def fill(self, selector: str, value: str, **kwargs) -> None:
        """
        Fill a form field.
        
        Args:
            selector: CSS selector for the input element
            value: Value to fill
            **kwargs: Additional options for Playwright fill
        """
        _run_async(self._fill_async(selector, value, **kwargs))
    
    async def _wait_for_async(
        self, 
        selector: Optional[str] = None, 
        timeout: Optional[float] = None
    ) -> None:
        """
        Internal async wait_for method with error handling.
        
        Raises:
            BrowserSessionError: If wait operation fails
        """
        if not self._page:
            raise BrowserSessionError("Browser session not initialized.")
        
        if selector:
            try:
                await self._page.wait_for_selector(selector, timeout=timeout)
            except PlaywrightTimeoutError:
                raise BrowserSessionError(
                    f"Element not found within timeout: '{selector}'. "
                    "The element may not exist or may take longer to appear."
                )
            except PlaywrightError as e:
                raise BrowserSessionError(
                    f"Wait failed for selector '{selector}': {str(e)}"
                )
        elif timeout:
            try:
                await self._page.wait_for_timeout(timeout)
            except Exception as e:
                raise BrowserSessionError(
                    f"Wait timeout failed: {str(e)}"
                )
        else:
            raise BrowserSessionError("Must provide either selector or timeout")
    
    def wait_for(
        self, 
        selector: Optional[str] = None, 
        timeout: Optional[float] = None
    ) -> None:
        """
        Wait for a selector or timeout.
        
        Args:
            selector: CSS selector to wait for (if None, waits for timeout)
            timeout: Timeout in milliseconds
        """
        _run_async(self._wait_for_async(selector, timeout))
    
    async def _dump_logs_async(self, filepath: Union[str, Path]) -> None:
        """
        Internal async dump_logs method with error handling.
        
        Raises:
            BrowserSessionError: If log dumping fails
        """
        if not self._context:
            raise BrowserSessionError("Browser session not initialized.")
        
        try:
            # Close context to finalize HAR recording
            await self._context.close()
        except Exception as e:
            raise BrowserSessionError(
                f"Failed to close browser context: {str(e)}"
            )
        
        # Copy HAR file to destination with enhanced error handling
        try:
            if self._har_path and self._har_path.exists():
                import shutil
                
                # Ensure destination directory exists
                dest_path = Path(filepath)
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy(self._har_path, filepath)
                
                # Verify the copy was successful
                if not Path(filepath).exists():
                    raise BrowserSessionError(
                        f"Failed to create HAR file at: '{filepath}'"
                    )
                
                # Clean up temporary file
                self._har_path.unlink()
            else:
                raise BrowserSessionError(
                    "HAR file not found. Session may not have been properly initialized "
                    "or no network activity was recorded."
                )
        except PermissionError:
            raise BrowserSessionError(
                f"Permission denied writing to: '{filepath}'. "
                "Please check file permissions and directory access."
            )
        except FileNotFoundError:
            raise BrowserSessionError(
                f"Destination directory does not exist: '{Path(filepath).parent}'"
            )
        except Exception as e:
            raise BrowserSessionError(
                f"Failed to save HAR file to '{filepath}': {str(e)}"
            )
        
        # Mark context as closed
        self._context = None
        self._page = None
    
    def dump_logs(self, filepath: Union[str, Path]) -> None:
        """
        Export captured network logs to a HAR file.
        
        Args:
            filepath: Path where to save the HAR file
        """
        _run_async(self._dump_logs_async(filepath))
    
    async def _close_async(self) -> None:
        """Internal async close method."""
        if self._context:
            await self._context.close()
        
        if self._browser:
            await self._browser.close()
        
        if self._playwright:
            await self._playwright.stop()
        
        # Clean up temporary HAR file if it exists
        if self._har_path and self._har_path.exists():
            self._har_path.unlink()
        
        self._page = None
        self._context = None
        self._browser = None
        self._playwright = None
    
    def close(self) -> None:
        """
        Close the browser session and cleanup resources.
        """
        _run_async(self._close_async())
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_async()
        return False

