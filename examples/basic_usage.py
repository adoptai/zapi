"""
Basic usage example for ZAPI.

This demonstrates the minimal API for launching a browser,
navigating to a URL, and capturing network logs in HAR format.
"""

from zapi import ZAPI


def main():
    # Example 1: Basic usage
    print("Example 1: Basic ZAPI usage")
    z = ZAPI(client_id="YOUR_CLIENT_ID", secret="YOUR_SECRET")
    session = z.launch_browser(url="https://app.example.com/dashboard")

    # The session is already on the dashboard page
    # You can interact with it if needed
    session.wait_for(timeout=2000)  # Wait 2 seconds

    # Dump network logs to HAR file
    session.dump_logs("example1_session.har")
    session.close()
    print("✓ HAR file saved to example1_session.har\n")

    # Example 2: Multi-page navigation with interactions
    print("Example 2: Multi-page navigation with interactions")
    z2 = ZAPI(client_id="YOUR_CLIENT_ID", secret="YOUR_SECRET")
    session2 = z2.launch_browser(url="https://app.example.com")

    # Navigate to different pages
    session2.navigate("/dashboard")
    session2.wait_for(timeout=1000)

    session2.navigate("/profile")
    session2.wait_for(timeout=1000)

    # Click on an element (example)
    # session2.click("#settings-button")

    # Fill a form (example)
    # session2.fill("#search-input", "test query")

    session2.dump_logs("example2_session.har")
    session2.close()
    print("✓ HAR file saved to example2_session.har\n")

    # Example 3: Using as context manager (auto-cleanup)
    print("Example 3: Using context manager for automatic cleanup")
    z3 = ZAPI(client_id="YOUR_CLIENT_ID", secret="YOUR_SECRET")
    session3 = z3.launch_browser(url="https://app.example.com")

    with session3:
        session3.navigate("/api-endpoint")
        session3.wait_for(timeout=2000)
        session3.dump_logs("example3_session.har")
    # Browser automatically closed when exiting context
    print("✓ HAR file saved to example3_session.har (auto-cleanup)\n")

    print("All examples completed! Check the generated .har files.")


if __name__ == "__main__":
    main()
