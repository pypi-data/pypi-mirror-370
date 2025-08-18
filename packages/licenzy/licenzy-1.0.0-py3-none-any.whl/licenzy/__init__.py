"""
🔑 Licenzy - Simple, Pythonic license management for AI tools

Licenzy provides a clean, minimal API for adding license validation to your Python projects.
Perfect for indie developers and small teams building AI tools.

Key Features:
- @licensed decorator for gated access
- Simple check_license() API
- File-based and environment variable license storage
- HMAC-based validation
- CLI for license management
- Zero dependencies (except Click for CLI)

Example:
    ```python
    from licenzy import licensed, check_license
    
    @licensed
    def premium_feature():
        return "This requires a valid license!"
    
    # Or check manually
    if check_license():
        print("Access granted!")
    ```
"""

from .core import (
    LicenseManager,
    check_license,
    licensed,
    access_granted,
    require_key,
    unlock,
    LicenseError,
    get_license_manager,
)

from .management import (
    activate_license,
    deactivate_license,
    show_license_status,
)

__version__ = "1.0.0"
__all__ = [
    # Core functions
    "check_license",
    "licensed",
    "access_granted", 
    "require_key",
    "unlock",
    
    # Classes
    "LicenseManager",
    "LicenseError",
    
    # Management
    "activate_license",
    "deactivate_license", 
    "show_license_status",
    "get_license_manager",
]
