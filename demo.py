#!/usr/bin/env python
"""ZAPI Demo Script showing capture, analysis, and upload."""

from pathlib import Path
from typing import Optional

from zapi import (
    ZAPI,
    BrowserInitializationError,
    BrowserNavigationError,
    BrowserSessionError,
    HarProcessingError,
    ZAPIAuthenticationError,
    ZAPIError,
    ZAPINetworkError,
    ZAPIValidationError,
    analyze_har_file,
)

# ---------------------------------------------------------------------------
# Quick configuration – edit these defaults before running the script.
# ---------------------------------------------------------------------------
DEMO_URL = "<INSERT_URL_HERE>"
OUTPUT_FILE = Path("demo_session.har")
HEADLESS_BROWSER = False


def record_session(zapi_client: ZAPI, url: str, output_path: Path) -> None:
    """Record a HAR file by letting the user drive the browser."""
    print(f"🌐 Launching browser and navigating to: {url}")
    session = zapi_client.launch_browser(url=url, headless=HEADLESS_BROWSER)
    try:
        print("✅ Browser launched successfully!")
        input("📋 Use the browser freely, then press ENTER to save the HAR...")

        print("💾 Saving session logs...")
        session.dump_logs(str(output_path))
        print(f"✅ Session saved to: {output_path}")
    finally:
        session.close()
        print("🧹 Browser session closed.")


def analyze_har_file_with_filter(source_path: Path) -> Optional[Path]:
    """Analyze the HAR and produce a filtered file for API-only calls."""
    print("\n🔍 Analyzing HAR file...")
    try:
        stats, report, filtered_path = analyze_har_file(str(source_path), save_filtered=True)
    except HarProcessingError as exc:
        print(f"⚠️ HAR analysis failed: {exc}")
        print("   Continuing with the original HAR.")
        return None

    print("\n📊 HAR Analysis Results:")
    print(f"   ✅ API-relevant entries: {stats.valid_entries:,}")
    print(f"   💰 Estimated cost: ${stats.estimated_cost_usd:.2f}")
    print(f"   ⏱️  Estimated processing time: {round(stats.estimated_time_minutes)} minutes")
    if filtered_path:
        print(f"   🧹 Filtered HAR saved to: {filtered_path}")
    return Path(filtered_path).resolve() if filtered_path else None


def pick_upload_file(original_path: Path, filtered_path: Optional[Path]) -> Path:
    """Interactively choose whether to upload the original or filtered HAR."""
    if filtered_path:
        print("\nYou now have two files available:")
        print(f"  1. Original HAR : {original_path}")
        print(f"  2. Filtered HAR : {filtered_path}")
        choice = input("Upload filtered HAR? (Y/n): ").strip().lower()
        if choice in ("", "y", "yes"):
            print("📤 Using filtered HAR for upload.")
            return filtered_path
        print("📤 Using original HAR for upload.")
        return original_path

    print("\nFiltered HAR not available, defaulting to the original file.")
    return original_path


def main() -> int:
    print("🚀 Starting ZAPI demo...")
    url = DEMO_URL
    output_path = OUTPUT_FILE.expanduser().resolve()

    try:
        z = ZAPI()
        record_session(z, url, output_path)

        filtered_path = analyze_har_file_with_filter(output_path)
        upload_path = pick_upload_file(output_path, filtered_path)

        confirm = input("\n💡 Ready to upload. Press ENTER to continue or 'n' to cancel: ").strip().lower()
        if confirm in {"n", "no"}:
            print("⏹️ Upload cancelled by user.")
            return 0

        print("\n☁️ Uploading HAR file...")
        z.upload_har(str(upload_path))
        print("✅ HAR file uploaded successfully!")
        print("🎉 Demo completed successfully!")

    except ZAPIValidationError as e:
        print("❌ Configuration Validation Error:")
        print(f"   {str(e)}")
        print("💡 Please check your input values:")
        print(f"   - URL: '{url}' (should be like 'https://example.com')")
        print(f"   - Output file: '{output_path}' (should end with '.har')")
        print("   Make sure to replace placeholder values with actual ones.")
        return 1

    except ZAPIAuthenticationError as e:
        print("❌ Authentication Error:")
        print(f"   {str(e)}")
        print("💡 Please check your credentials:")
        print("   - Make sure your account is active and has proper permissions")
        return 1

    except ZAPINetworkError as e:
        print("❌ Network Error:")
        print(f"   {str(e)}")
        print("💡 This might be due to:")
        print("   - Internet connectivity issues")
        print("   - ZAPI service being temporarily unavailable")
        print("   - Firewall or proxy blocking the connection")
        print("   - DNS resolution problems")
        return 1

    except BrowserNavigationError as e:
        print("❌ Browser Navigation Error:")
        print(f"   {str(e)}")
        print("💡 Common solutions:")
        print(f"   - Check URL format: '{url}'")
        print("   - Ensure the website is accessible")
        print("   - Try a different URL for testing")
        print("   - Check your internet connection")
        return 1

    except BrowserInitializationError as e:
        print("❌ Browser Initialization Error:")
        print(f"   {str(e)}")
        print("💡 This might be due to:")
        print("   - Missing browser dependencies (try: playwright install)")
        print("   - System permissions issues")
        print("   - Insufficient system resources")
        return 1

    except BrowserSessionError as e:
        print("❌ Browser Session Error:")
        print(f"   {str(e)}")
        print("💡 Try the following:")
        print("   - Restart the script")
        print("   - Check if the browser window is responsive")
        print("   - Ensure sufficient disk space for HAR files")
        return 1

    except HarProcessingError as e:
        print("❌ HAR Processing Error:")
        print(f"   {str(e)}")
        print("💡 This error occurred during HAR file analysis:")
        print("   - Check if the HAR file was generated correctly")
        print("   - Ensure the file is not corrupted or empty")
        print("   - Try generating a new session")
        return 1

    except ZAPIError as e:
        print("❌ ZAPI Error:")
        print(f"   {str(e)}")
        print("💡 This is a general ZAPI error. Please check your configuration.")
        return 1

    except Exception as e:
        print("❌ Unexpected Error:")
        print(f"   {str(e)}")
        print("💡 This is an unexpected error. Please:")
        print("   - Check all your input values")
        print("   - Try running the script again")
        print("   - Contact support if the issue persists")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
