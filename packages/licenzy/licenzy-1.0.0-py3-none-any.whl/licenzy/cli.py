"""
🖥️ Licenzy CLI - Command-line interface for license management

Provides a clean, user-friendly CLI for managing licenses.
Built with Click for a great developer experience.
"""

import click
from .management import activate_license, deactivate_license, show_license_status
from .core import check_license


@click.group()
@click.version_option(version="1.0.0")
def main():
    """
    🔑 Licenzy - Simple license management for AI tools
    
    Licenzy provides easy license validation for your Python projects.
    Perfect for indie developers and small teams building AI tools.
    """
    pass


@main.command()
@click.argument('license_key')
def activate(license_key: str):
    """
    🔓 Activate a license key
    
    LICENSE_KEY: Your license key string
    
    Example:
        licenzy activate user123:pro:1735689600:abc123def456
    """
    success = activate_license(license_key)
    if not success:
        raise click.ClickException("License activation failed")


@main.command()
def deactivate():
    """
    🔒 Deactivate the current license
    
    Removes the stored license key from your system.
    """
    deactivate_license()


@main.command()
def status():
    """
    📊 Show current license status
    
    Displays detailed information about your license state.
    """
    show_license_status()


@main.command()
def check():
    """
    ✅ Quick license validation check
    
    Returns exit code 0 if valid, 1 if invalid.
    Perfect for scripts and automation.
    """
    if check_license():
        click.echo("✅ License is valid")
    else:
        click.echo("❌ License is invalid")
        raise click.ClickException("Invalid license")


@main.command()
def info():
    """
    ℹ️ Show Licenzy information and usage examples
    """
    click.echo("🔑 Licenzy - Simple license management for AI tools")
    click.echo()
    click.echo("📋 Quick Start:")
    click.echo("  licenzy activate your-license-key    # Activate license")
    click.echo("  licenzy status                       # Check status")
    click.echo("  licenzy check                        # Quick validation")
    click.echo()
    click.echo("🐍 Python Integration:")
    click.echo("  from licenzy import licensed, check_license")
    click.echo()
    click.echo("  @licensed")
    click.echo("  def premium_feature():")
    click.echo("      return 'This requires a license!'")
    click.echo()
    click.echo("  if check_license():")
    click.echo("      print('Access granted!')")
    click.echo()
    click.echo("🌐 Environment Variables:")
    click.echo("  LICENZY_LICENSE_KEY=your-key         # Set license via env")
    click.echo("  LICENZY_DEV_MODE=true               # Bypass for development")
    click.echo()
    click.echo("📁 License Storage Locations:")
    click.echo("  ~/.licenzy/license.key              # User-specific")
    click.echo("  .licenzy_license                    # Project-specific")


if __name__ == "__main__":
    main()
