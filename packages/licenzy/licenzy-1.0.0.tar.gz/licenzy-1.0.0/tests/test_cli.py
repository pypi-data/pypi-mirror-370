"""
🧪 Test Suite for Licenzy CLI Functionality

Tests for command-line interface commands and user interactions.
"""

import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner

from licenzy.cli import main, activate, deactivate, status, check, info


class TestCLICommands:
    """Test cases for CLI commands."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_main_help(self):
        """Test main command help."""
        result = self.runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert "Licenzy" in result.output
        assert "Simple license management" in result.output

    def test_main_version(self):
        """Test version command."""
        result = self.runner.invoke(main, ['--version'])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    @patch('licenzy.cli.activate_license')
    def test_activate_command_success(self, mock_activate):
        """Test successful license activation command."""
        mock_activate.return_value = True
        
        result = self.runner.invoke(activate, ['test-license-key'])
        
        assert result.exit_code == 0
        mock_activate.assert_called_once_with('test-license-key')

    @patch('licenzy.cli.activate_license')
    def test_activate_command_failure(self, mock_activate):
        """Test failed license activation command."""
        mock_activate.return_value = False
        
        result = self.runner.invoke(activate, ['invalid-key'])
        
        assert result.exit_code == 1
        mock_activate.assert_called_once_with('invalid-key')

    @patch('licenzy.cli.deactivate_license')
    def test_deactivate_command(self, mock_deactivate):
        """Test license deactivation command."""
        result = self.runner.invoke(deactivate)
        
        assert result.exit_code == 0
        mock_deactivate.assert_called_once()

    @patch('licenzy.cli.show_license_status')
    def test_status_command(self, mock_status):
        """Test license status command."""
        result = self.runner.invoke(status)
        
        assert result.exit_code == 0
        mock_status.assert_called_once()

    @patch('licenzy.cli.check_license')
    def test_check_command_valid(self, mock_check):
        """Test license check command with valid license."""
        mock_check.return_value = True
        
        result = self.runner.invoke(check)
        
        assert result.exit_code == 0
        assert "License is valid" in result.output

    @patch('licenzy.cli.check_license')
    def test_check_command_invalid(self, mock_check):
        """Test license check command with invalid license."""
        mock_check.return_value = False
        
        result = self.runner.invoke(check)
        
        assert result.exit_code == 1
        assert "License is invalid" in result.output

    def test_info_command(self):
        """Test info command output."""
        result = self.runner.invoke(info)
        
        assert result.exit_code == 0
        assert "Licenzy" in result.output
        assert "Quick Start" in result.output
        assert "Python Integration" in result.output
        assert "Environment Variables" in result.output
        assert "License Storage Locations" in result.output
        assert "@licensed" in result.output
        assert "check_license" in result.output

    def test_info_command_content(self):
        """Test info command contains all expected sections."""
        result = self.runner.invoke(info)
        
        # Check for key sections
        assert "licenzy activate" in result.output
        assert "licenzy status" in result.output
        assert "licenzy check" in result.output
        assert "LICENZY_LICENSE_KEY" in result.output
        assert "LICENZY_DEV_MODE" in result.output
        assert "~/.licenzy/license.key" in result.output
        assert ".licenzy_license" in result.output

    def test_activate_command_missing_key(self):
        """Test activate command without license key argument."""
        result = self.runner.invoke(activate)
        
        assert result.exit_code == 2  # Click error for missing argument
        assert "Missing argument" in result.output or "Usage:" in result.output


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_help_for_all_commands(self):
        """Test help works for all commands."""
        commands = [activate, deactivate, status, check, info]
        
        for command in commands:
            result = self.runner.invoke(command, ['--help'])
            assert result.exit_code == 0
            assert "Usage:" in result.output

    @patch('licenzy.cli.activate_license')
    @patch('licenzy.cli.check_license')
    def test_workflow_activate_then_check(self, mock_check, mock_activate):
        """Test typical workflow: activate then check."""
        # Activate license
        mock_activate.return_value = True
        result1 = self.runner.invoke(activate, ['test-key'])
        assert result1.exit_code == 0
        
        # Check license
        mock_check.return_value = True
        result2 = self.runner.invoke(check)
        assert result2.exit_code == 0
        assert "License is valid" in result2.output
