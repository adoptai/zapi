"""Authentication handlers for different auth modes."""

from typing import Literal
from playwright.async_api import Page, BrowserContext


AuthMode = Literal["localStorage", "cookie", "header"]


async def apply_localStorage_auth(page: Page, token: str, key: str = "authToken") -> None:
    """
    Inject authentication token into localStorage.
    
    Args:
        page: Playwright page instance
        token: Authentication token
        key: localStorage key name (default: "authToken")
    """
    await page.evaluate(f"localStorage.setItem('{key}', '{token}')")


async def apply_cookie_auth(
    page: Page, 
    token: str, 
    name: str = "authToken",
    domain: str = None
) -> None:
    """
    Set authentication token as a cookie.
    
    Args:
        page: Playwright page instance
        token: Authentication token
        name: Cookie name (default: "authToken")
        domain: Cookie domain (optional)
    """
    cookie = {
        "name": name,
        "value": token,
        "path": "/",
    }
    if domain:
        cookie["domain"] = domain
    
    await page.context.add_cookies([cookie])


async def apply_header_auth(context: BrowserContext, token: str) -> None:
    """
    Add Authorization header to all requests.
    
    Args:
        context: Playwright browser context
        token: Authentication token (will be added as "Bearer <token>")
    """
    await context.set_extra_http_headers({
        "Authorization": f"Bearer {token}"
    })


def get_auth_handler(auth_mode: AuthMode):
    """
    Factory function to get the appropriate auth handler.
    
    Args:
        auth_mode: Authentication mode ("localStorage", "cookie", or "header")
        
    Returns:
        Corresponding auth handler function
        
    Raises:
        ValueError: If auth_mode is not recognized
    """
    handlers = {
        "localStorage": apply_localStorage_auth,
        "cookie": apply_cookie_auth,
        "header": apply_header_auth,
    }
    
    if auth_mode not in handlers:
        raise ValueError(
            f"Invalid auth_mode: {auth_mode}. "
            f"Must be one of: {', '.join(handlers.keys())}"
        )
    
    return handlers[auth_mode]

