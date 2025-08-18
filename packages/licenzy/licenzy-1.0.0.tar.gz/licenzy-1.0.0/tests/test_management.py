"""
🧪 Test Suite for Licenzy Management Functionality

Tests for license activation, deactivation, and status management.
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from licenzy.management import (
    activate_license,
    deactivate_license,
    show_license_status,
    get_license_key_location,
)
from licenzy.core import LicenseManager


class TestLicenseActivation:
    """Test cases for license activation."""

    @patch.object(LicenseManager, 'validate_license')
    @patch('pathlib.Path.write_text')
    @patch('pathlib.Path.mkdir')
    @patch('builtins.print')
    def test_activate_license_success(self, mock_print, mock_mkdir, mock_write_text, mock_validate):
        """Test successful license activation."""
        mock_validate.return_value = (True, "License valid until 2025-12-31")
        
        result = activate_license("test:pro:123456:abcd1234")
        
        assert result is True
        mock_mkdir.assert_called_once_with(exist_ok=True)
        mock_write_text.assert_called_once_with("test:pro:123456:abcd1234")
        
        # Verify success messages were printed
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("License activated successfully" in call for call in print_calls)

    @patch.object(LicenseManager, 'validate_license')
    @patch('builtins.print')
    def test_activate_license_failure(self, mock_print, mock_validate):
        """Test failed license activation."""
        mock_validate.return_value = (False, "Invalid license key")
        
        result = activate_license("invalid-key")
        
        assert result is False
        
        # Verify failure message was printed
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("License activation failed" in call for call in print_calls)


class TestLicenseDeactivation:
    """Test cases for license deactivation."""

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.unlink')
    @patch('builtins.print')
    def test_deactivate_license_exists(self, mock_print, mock_unlink, mock_exists):
        """Test license deactivation when file exists."""
        mock_exists.return_value = True
        
        deactivate_license()
        
        mock_unlink.assert_called_once()
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("License deactivated successfully" in call for call in print_calls)

    @patch('pathlib.Path.exists')
    @patch('builtins.print')
    def test_deactivate_license_not_exists(self, mock_print, mock_exists):
        """Test license deactivation when file doesn't exist."""
        mock_exists.return_value = False
        
        deactivate_license()
        
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("No active license to deactivate" in call for call in print_calls)


class TestLicenseStatus:
    """Test cases for license status display."""

    @patch('licenzy.management.get_license_manager')
    @patch('builtins.print')
    def test_show_license_status_valid(self, mock_print, mock_get_manager):
        """Test showing valid license status."""
        mock_manager = Mock()
        mock_manager.validate_license.return_value = (True, "License valid until 2025-12-31")
        mock_manager.license_info = {
            "user_id": "user123",
            "plan": "pro",
            "expires": datetime(2025, 12, 31),
            "days_remaining": 365
        }
        mock_get_manager.return_value = mock_manager
        
        show_license_status()
        
        # Verify that status information was printed
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("License Status: 🟢 ACTIVE" in call for call in print_calls)
        assert any("user123" in call for call in print_calls)
        assert any("pro" in call for call in print_calls)

    @patch('licenzy.management.get_license_manager')
    @patch('builtins.print')
    def test_show_license_status_invalid(self, mock_print, mock_get_manager):
        """Test showing invalid license status."""
        mock_manager = Mock()
        mock_manager.validate_license.return_value = (False, "No license key found")
        mock_get_manager.return_value = mock_manager
        
        show_license_status()
        
        # Verify that invalid status was printed
        assert mock_print.called
        print_args = [call.args for call in mock_print.call_args_list if call.args]
        assert any("License Status: 🔴 INVALID" in str(args) for args in print_args)
        assert any("No license key found" in str(args) for args in print_args)
        assert any("licenzy activate" in str(args) for args in print_args)

    @patch('licenzy.management.get_license_manager')
    @patch('builtins.print')
    def test_show_license_status_valid_no_info(self, mock_print, mock_get_manager):
        """Test showing valid license status without detailed info."""
        mock_manager = Mock()
        mock_manager.validate_license.return_value = (True, "License valid")
        mock_manager.license_info = None
        mock_get_manager.return_value = mock_manager
        
        show_license_status()
        
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("License Status: 🟢 ACTIVE" in call for call in print_calls)


class TestLicenseKeyLocation:
    """Test cases for license key location detection."""

    @patch('pathlib.Path.exists')
    def test_get_license_key_location_exists(self, mock_exists):
        """Test getting license key location when file exists."""
        mock_exists.return_value = True
        
        location = get_license_key_location()
        
        assert location is not None
        assert isinstance(location, Path)
        assert ".licenzy" in str(location)
        assert "license.key" in str(location)

    @patch('pathlib.Path.exists')
    def test_get_license_key_location_not_exists(self, mock_exists):
        """Test getting license key location when file doesn't exist."""
        mock_exists.return_value = False
        
        location = get_license_key_location()
        
        assert location is None


# Import datetime for the test
from datetime import datetime
