#!/usr/bin/env python
"""ZAPI Demo Script - Simplified"""

from zapi import ZAPI


def main():
    client_id = "CLIENT_ID"
    secret = "SECRET_KEY"
    url = "URL"
    output_file = "OUTPUT_FILE.har"
    
    try:
        # Initialize and run ZAPI
        z = ZAPI(client_id=client_id, secret=secret)
        session = z.launch_browser(url=url, headless=False)
        input("Press ENTER when done navigating...")
        session.dump_logs(output_file)
        z.upload_har(output_file)
        session.close()
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())