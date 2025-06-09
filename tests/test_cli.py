"""Tests for the VesselHarbor CLI."""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

from typer.testing import CliRunner

from vesselharborcli.cli import app


class TestCLI(unittest.TestCase):
    """Test the CLI commands."""

    def setUp(self):
        """Set up the test environment."""
        self.runner = CliRunner()

    @patch("vesselharborcli.auth.TokenManager")
    def test_login(self, mock_token_manager):
        """Test the login command."""
        # Mock the token manager
        mock_instance = MagicMock()
        mock_token_manager.return_value = mock_instance

        # Run the command
        result = self.runner.invoke(
            app, ["auth", "login"], input="testuser\ntestpassword\n"
        )

        # Check that the command was successful
        self.assertEqual(result.exit_code, 0)

        # Check that the token manager was called with the correct arguments
        mock_instance.login_with_password.assert_called_once_with("testuser", "testpassword")

    @patch("vesselharborcli.auth.TokenManager")
    def test_login_key(self, mock_token_manager):
        """Test the login-key command."""
        # Mock the token manager
        mock_instance = MagicMock()
        mock_token_manager.return_value = mock_instance

        # Run the command
        result = self.runner.invoke(
            app, ["auth", "login-key"], input="testkey\n"
        )

        # Check that the command was successful
        self.assertEqual(result.exit_code, 0)

        # Check that the token manager was called with the correct arguments
        mock_instance.login_with_api_key.assert_called_once_with("testkey")

    @patch("vesselharborcli.client.get_client")
    def test_list_organizations(self, mock_get_client):
        """Test the list organizations command."""
        # Mock the client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock the response
        mock_client.list_organizations.return_value = [
            MagicMock(id=1, name="Org 1", description="Description 1"),
            MagicMock(id=2, name="Org 2", description="Description 2"),
        ]

        # Run the command
        result = self.runner.invoke(app, ["org", "list"])

        # Check that the command was successful
        self.assertEqual(result.exit_code, 0)

        # Check that the client was called
        mock_client.list_organizations.assert_called_once()

        # Check that the output contains the organization names
        self.assertIn("Org 1", result.stdout)
        self.assertIn("Org 2", result.stdout)

    @patch("vesselharborcli.client.get_client")
    def test_create_organization(self, mock_get_client):
        """Test the create organization command."""
        # Mock the client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock the response
        mock_client.create_organization.return_value = MagicMock(id=1, name="New Org")

        # Run the command
        result = self.runner.invoke(
            app, ["org", "create", "--name", "New Org", "--description", "New Description"]
        )

        # Check that the command was successful
        self.assertEqual(result.exit_code, 0)

        # Check that the client was called with the correct arguments
        mock_client.create_organization.assert_called_once()
        args, _ = mock_client.create_organization.call_args
        self.assertEqual(args[0].name, "New Org")
        self.assertEqual(args[0].description, "New Description")

        # Check that the output contains the success message
        self.assertIn("Organization created successfully", result.stdout)

    @patch("vesselharborcli.config.get_settings")
    @patch("os.environ")
    @patch("json.dump")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_set_server(self, mock_open, mock_dump, mock_environ, mock_get_settings):
        """Test the set-server command."""
        # Mock the settings
        mock_settings = MagicMock()
        mock_settings.server_name = "localhost"
        mock_settings.server_port = 8000
        mock_get_settings.return_value = mock_settings

        # Run the command
        result = self.runner.invoke(app, ["config", "set-server", "api.example.com"])

        # Check that the command was successful
        self.assertEqual(result.exit_code, 0)

        # Check that the environment variable was set
        mock_environ.__setitem__.assert_called_with("VESSELHARBOR_SERVER_NAME", "api.example.com")

        # Check that the settings were updated
        self.assertEqual(mock_settings.server_name, "api.example.com")

        # Check that the api_url was reconstructed
        self.assertEqual(mock_settings.api_url, f"http://{mock_settings.server_name}:{mock_settings.server_port}")

        # Check that the output contains the success message
        self.assertIn("Server name set to: api.example.com", result.stdout)

    @patch("vesselharborcli.config.get_settings")
    @patch("os.environ")
    @patch("json.dump")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_set_port(self, mock_open, mock_dump, mock_environ, mock_get_settings):
        """Test the set-port command."""
        # Mock the settings
        mock_settings = MagicMock()
        mock_settings.server_name = "localhost"
        mock_settings.server_port = 8000
        mock_get_settings.return_value = mock_settings

        # Run the command
        result = self.runner.invoke(app, ["config", "set-port", "8080"])

        # Check that the command was successful
        self.assertEqual(result.exit_code, 0)

        # Check that the environment variable was set
        mock_environ.__setitem__.assert_called_with("VESSELHARBOR_SERVER_PORT", "8080")

        # Check that the settings were updated
        self.assertEqual(mock_settings.server_port, 8080)

        # Check that the api_url was reconstructed
        self.assertEqual(mock_settings.api_url, f"http://{mock_settings.server_name}:{mock_settings.server_port}")

        # Check that the output contains the success message
        self.assertIn("Server port set to: 8080", result.stdout)


if __name__ == "__main__":
    unittest.main()
