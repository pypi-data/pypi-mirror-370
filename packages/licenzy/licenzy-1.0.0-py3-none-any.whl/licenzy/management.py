"""
🔧 Licenzy Management - License activation and status management

This module provides functions for managing licenses: activating,
deactivating, and checking status. Perfect for CLI integration.
"""

from pathlib import Path
from typing import Optional
from .core import LicenseManager, get_license_manager


def activate_license(license_key: str) -> bool:
    """
    🔓 Activate a license key
    
    Validates and stores the license key for future use.
    
    Args:
        license_key: The license key to activate
        
    Returns:
        bool: True if activation successful, False otherwise
    """
    # Validate the license first
    manager = LicenseManager(license_key)
    valid, message = manager.validate_license()
    
    if valid:
        # Save to user's home directory
        license_dir = Path.home() / ".licenzy"
        license_dir.mkdir(exist_ok=True)
        
        license_file = license_dir / "license.key"
        license_file.write_text(license_key)
        
        print("✅ License activated successfully!")
        print(f"📍 Saved to: {license_file}")
        print(f"📋 {message}")
        return True
    else:
        print(f"❌ License activation failed: {message}")
        return False


def deactivate_license():
    """
    🔒 Deactivate the current license
    
    Removes the stored license key from the system.
    """
    license_file = Path.home() / ".licenzy" / "license.key"
    
    if license_file.exists():
        license_file.unlink()
        print("✅ License deactivated successfully")
        print(f"🗑️ Removed: {license_file}")
    else:
        print("ℹ️ No active license to deactivate")


def show_license_status():
    """
    📊 Show current license status
    
    Displays detailed information about the current license state.
    """
    manager = get_license_manager()
    valid, message = manager.validate_license()
    
    print("🔑" + "=" * 59)
    print("🔑 LICENZY LICENSE STATUS")
    print("🔑" + "=" * 59)
    
    if valid:
        print("📋 License Status: 🟢 ACTIVE")
        print(f"📋 {message}")
        
        if manager.license_info:
            info = manager.license_info
            print(f"👤 User ID: {info['user_id']}")
            print(f"📦 Plan: {info['plan']}")
            print(f"📅 Expires: {info['expires'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏰ Days Remaining: {info['days_remaining']}")
    else:
        print("📋 License Status: 🔴 INVALID")
        print(f"❌ {message}")
        print()
        print("💡 To activate a license:")
        print("   licenzy activate your-license-key")
    
    print("🔑" + "=" * 59)


def get_license_key_location() -> Optional[Path]:
    """
    📍 Get the location of the stored license key
    
    Returns:
        Path to license file if it exists, None otherwise
    """
    license_file = Path.home() / ".licenzy" / "license.key"
    return license_file if license_file.exists() else None
