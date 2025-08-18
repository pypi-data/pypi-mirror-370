"""
🔑 Licenzy Core - License validation and management

This module provides the core functionality for license validation,
including the main LicenseManager class and the @licensed decorator.
"""

import os
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, Callable
from pathlib import Path
from functools import wraps


class LicenseError(Exception):
    """🚫 Raised when license validation fails"""
    pass


class LicenseManager:
    """
    🔑 Core license management class
    
    Handles license validation, storage, and checking with a clean,
    Pythonic API that's perfect for AI tools and indie projects.
    """
    
    def __init__(self, license_key: Optional[str] = None):
        """Initialize license manager with optional license key."""
        self.license_key = license_key or self._find_license_key()
        self.license_info: Optional[Dict[str, Any]] = None
        self._validated = False
        
    def _find_license_key(self) -> Optional[str]:
        """🔍 Find license key from environment or file"""
        # 1. Check environment variable
        env_key = os.environ.get("LICENZY_LICENSE_KEY")
        if env_key:
            return env_key.strip()
        
        # 2. Check local project directory  
        local_license = Path(".licenzy_license")
        if local_license.exists():
            return local_license.read_text().strip()
        
        # 3. Check user's home directory
        home_license = Path.home() / ".licenzy" / "license.key"
        if home_license.exists():
            return home_license.read_text().strip()
        
        return None
    
    def validate_license(self) -> Tuple[bool, str]:
        """
        🔐 Validate the license key
        
        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        if not self.license_key:
            return False, "No license key found"
        
        try:
            # Parse license key format: user_id:plan:expires_timestamp:signature
            parts = self.license_key.split(":")
            if len(parts) != 4:
                return False, "Invalid license key format"
                
            user_id, plan, expires_timestamp, signature = parts
            
            # Check expiration
            expires = datetime.fromtimestamp(int(expires_timestamp))
            if datetime.now() > expires:
                return False, f"License expired on {expires.strftime('%Y-%m-%d')}"
            
            # Verify HMAC signature
            expected_signature = self._generate_signature(user_id, plan, expires_timestamp)
            if not hmac.compare_digest(signature, expected_signature):
                return False, "Invalid license signature"
            
            # Store license info
            self.license_info = {
                "user_id": user_id,
                "plan": plan,
                "expires": expires,
                "days_remaining": (expires - datetime.now()).days
            }
            
            self._validated = True
            return True, f"✅ License valid until {expires.strftime('%Y-%m-%d')} ({self.license_info['days_remaining']} days remaining)"
            
        except Exception as e:
            return False, f"License validation error: {e}"
    
    def _generate_signature(self, user_id: str, plan: str, expires: str) -> str:
        """🔒 Generate HMAC signature for license validation"""
        # In production, use a proper signing key stored securely
        secret_key = "licenzy-signing-key-2025"  # Replace with actual key
        data = f"{user_id}:{plan}:{expires}"
        return hmac.new(secret_key.encode(), data.encode(), hashlib.sha256).hexdigest()[:16]
    
    def check_license(self) -> bool:
        """
        ✨ Check if license is valid (main API function)
        
        This is the core function that most users will interact with.
        It caches the validation result for performance.
        """
        # Development mode bypass
        if os.environ.get("LICENZY_DEV_MODE") == "true":
            return True
            
        if not self._validated:
            valid, message = self.validate_license()
            if not valid:
                self._show_license_warning(message)
                return False
        return True
    
    def _show_license_warning(self, message: str):
        """⚠️ Show friendly license warning to user"""
        print("🔑" + "=" * 59)
        print("🔑 LICENZY - LICENSE REQUIRED")
        print("🔑" + "=" * 59)
        print(f"❌ {message}")
        print()
        print("💡 To activate your license:")
        print("   1. Set environment: LICENZY_LICENSE_KEY=your-key")
        print("   2. Run: licenzy activate your-license-key")
        print("   3. Save to: ~/.licenzy/license.key")
        print()
        print("🛒 Get a license at: https://your-licensing-site.com")
        print("🔑" + "=" * 59)
    
    def get_license_info(self) -> Optional[Dict[str, Any]]:
        """📋 Get detailed license information if valid"""
        if self.check_license():
            return self.license_info
        return None


# Global license manager instance
_license_manager: Optional[LicenseManager] = None


def get_license_manager() -> LicenseManager:
    """🎯 Get the global license manager instance (singleton pattern)"""
    global _license_manager
    if _license_manager is None:
        _license_manager = LicenseManager()
    return _license_manager


def check_license() -> bool:
    """
    ✅ Simple function to check if license is valid
    
    This is the main API function for quick license checks.
    Perfect for startup validation or feature gating.
    
    Returns:
        bool: True if license is valid, False otherwise
    """
    return get_license_manager().check_license()


def licensed(func: Optional[Callable] = None, *, message: Optional[str] = None):
    """
    🎨 @licensed decorator - The main Licenzy decorator
    
    Use this decorator to protect functions that require a valid license.
    Clean, Pythonic, and startup-friendly.
    
    Usage:
        @licensed
        def premium_feature():
            return "This needs a license!"
            
        @licensed(message="Custom error message")
        def another_feature():
            return "Also protected!"
    
    Args:
        func: Function to protect (when used without parentheses)
        message: Custom error message (optional)
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not check_license():
                error_msg = message or f"🔑 License required to access '{f.__name__}'"
                raise LicenseError(error_msg)
            return f(*args, **kwargs)
        return wrapper
    
    # Handle both @licensed and @licensed() usage
    if func is None:
        return decorator
    else:
        return decorator(func)


# Friendly aliases for different use cases
def access_granted() -> bool:
    """🎉 Alias for check_license() - more expressive for some use cases"""
    return check_license()


def require_key(func: Callable) -> Callable:
    """🗝️ Alias for @licensed decorator - alternative naming"""
    return licensed(func)


def unlock(func: Callable) -> Callable:
    """🔓 Alias for @licensed decorator - playful naming"""
    return licensed(func)
