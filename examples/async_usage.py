"""
Advanced async usage example for ZAPI.

This demonstrates how to use the async API directly for concurrent
operations or integration with async frameworks.
"""

import asyncio
from zapi.session import BrowserSession


async def main():
    print("Advanced async usage example\n")
    
    # Example 1: Using async methods directly
    print("Example 1: Direct async API usage")
    session = BrowserSession(
        auth_token="YOUR_TOKEN",
        headless=True
    )
    
    await session._initialize(initial_url="https://app.example.com")
    await session._wait_for_async(timeout=2000)
    await session._dump_logs_async("async_example1.har")
    await session._close_async()
    print("✓ HAR file saved to async_example1.har\n")
    
    
    # Example 2: Concurrent sessions (multiple browsers at once)
    print("Example 2: Running multiple sessions concurrently")
    
    async def capture_session(url, output_file):
        """Helper to capture a session."""
        session = BrowserSession(
            auth_token="YOUR_TOKEN",
            headless=True
        )
        await session._initialize(initial_url=url)
        await session._wait_for_async(timeout=1000)
        await session._dump_logs_async(output_file)
        await session._close_async()
        print(f"✓ Captured {url} -> {output_file}")
    
    # Run multiple sessions concurrently
    await asyncio.gather(
        capture_session("https://api.example.com/v1/users", "async_users.har"),
        capture_session("https://api.example.com/v1/products", "async_products.har"),
        capture_session("https://api.example.com/v1/orders", "async_orders.har"),
    )
    print("\n✓ All concurrent sessions completed\n")
    
    
    # Example 3: Async context manager
    print("Example 3: Using async context manager")
    session = BrowserSession(
        auth_token="YOUR_TOKEN",
        headless=True
    )
    await session._initialize(initial_url="https://app.example.com")
    
    async with session:
        await session._navigate_async("/dashboard")
        await session._wait_for_async(timeout=2000)
        await session._dump_logs_async("async_context.har")
    print("✓ HAR file saved to async_context.har (auto-cleanup)\n")
    
    print("All async examples completed!")


if __name__ == "__main__":
    asyncio.run(main())

