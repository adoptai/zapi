"""
Simplest possible ZAPI usage - exactly as shown in documentation.
"""

from zapi import ZAPI


def main():
    # Create ZAPI instance with your client credentials
    z = ZAPI(client_id="YOUR_CLIENT_ID", secret="YOUR_SECRET")

    # Launch browser and navigate to URL
    session = z.launch_browser(url="https://app.example.com/dashboard")

    # Dump network logs to HAR file
    session.dump_logs("session.har")

    # Clean up
    session.close()

    print("✓ Network logs saved to session.har")


if __name__ == "__main__":
    main()
