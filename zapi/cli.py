"""Command-line interface for ZAPI."""

import time
from pathlib import Path

import click

from .core import ZAPI
from .har_processing import analyze_har_file


@click.group()
def cli():
    """ZAPI command-line tool."""
    pass


@cli.command()
@click.argument('url')
@click.option('--output', default='session.har', help='Output HAR file path.')
@click.option('--headless/--no-headless', default=False, help='Run browser in headless mode.')
def capture(url, output, headless):
    """Capture a browser session to a HAR file."""
    zapi_client = ZAPI()
    output_path = Path(output)

    click.echo(f"🌐 Launching browser to capture: {url}")
    session = zapi_client.launch_browser(url=url, headless=headless)

    try:
        if not headless:
            click.echo("📋 Use the browser freely, then press ENTER to save the HAR...")
            input()
        else:
            click.echo("Running in headless mode. The script will automatically close the session.")
            # In a real-world headless scenario, you might add some automated actions here.
            # For now, we'll just wait for a moment.
            time.sleep(10) # Wait 10 seconds

        click.echo("💾 Saving session logs...")
        session.dump_logs(str(output_path))
        click.echo(f"✅ Session saved to: {output_path}")
    finally:
        session.close()
        click.echo("🧹 Browser session closed.")


@cli.command()
@click.argument('har_file', type=click.Path(exists=True))
def analyze(har_file):
    """Analyze a HAR file."""
    click.echo(f"🔍 Analyzing HAR file: {har_file}")
    stats, report, filtered_path = analyze_har_file(har_file, save_filtered=True)

    click.echo("\n📊 HAR Analysis Results:")
    click.echo(f"   ✅ API-relevant entries: {stats.valid_entries:,}")
    click.echo(f"   💰 Estimated cost: ${stats.estimated_cost_usd:.2f}")
    click.echo(f"   ⏱️  Estimated processing time: {round(stats.estimated_time_minutes)} minutes")
    if filtered_path:
        click.echo(f"   🧹 Filtered HAR saved to: {filtered_path}")


@cli.command()
@click.argument('har_file', type=click.Path(exists=True))
def upload(har_file):
    """Upload a HAR file to ZAPI."""
    zapi_client = ZAPI()
    click.echo(f"☁️ Uploading HAR file: {har_file}")
    zapi_client.upload_har(har_file)
    click.echo("✅ HAR file uploaded successfully!")


if __name__ == '__main__':
    cli()
