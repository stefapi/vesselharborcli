"""Command-line interface for the VesselHarbor CLI."""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

from rich.console import Console
from rich.table import Table

from vesselharborcli.auth import TokenManager, AuthenticationError
from vesselharborcli.client import get_client, APIError, OrganizationCreate, OrganizationUpdate
from vesselharborcli.config import get_settings

# Create console for rich output
console = Console()

# Create the main parser
parser = argparse.ArgumentParser(
    prog="vesselharbor",
    description="CLI tool for interacting with the VesselHarbor API",
)

# Add global options
parser.add_argument("--server", "-s", help="Override server name for this session")
parser.add_argument("--port", "-p", type=int, help="Override server port for this session")

# Create subparsers for commands
subparsers = parser.add_subparsers(dest="command", help="Command to execute")
subparsers.required = True

# Dictionary to store command functions
command_functions: Dict[str, Callable] = {}


# Authentication commands
auth_parser = subparsers.add_parser("auth", help="Authentication commands")
auth_subparsers = auth_parser.add_subparsers(dest="auth_command", help="Auth command to execute")
auth_subparsers.required = True

# Login command
login_parser = auth_subparsers.add_parser("login", help="Login with username and password")
login_parser.add_argument("--username", help="Username", required=True)
login_parser.add_argument("--password", help="Password", required=True)

def login(args):
    """Login with username and password."""
    try:
        token_manager = TokenManager(server=args.server, port=args.port)
        token_response = token_manager.login_with_password
        console.print(f"[green]Successfully logged in as {args.username}[/green]")
    except AuthenticationError as e:
        console.print(f"[red]Authentication failed: {str(e)}[/red]")
        sys.exit(1)

command_functions["auth_login"] = login

# Login with API key command
login_key_parser = auth_subparsers.add_parser("login-key", help="Login with API key")
login_key_parser.add_argument("--api-key", help="API Key", required=True)

def login_key(args):
    """Login with API key."""
    try:
        token_manager = TokenManager(server=args.server, port=args.port)
        token_response = token_manager.login_with_api_key(args.api_key)
        console.print(f"[green]Successfully logged in with API key[/green]")
    except AuthenticationError as e:
        console.print(f"[red]Authentication failed: {str(e)}[/red]")
        sys.exit(1)

command_functions["auth_login-key"] = login_key

# Logout command
logout_parser = auth_subparsers.add_parser("logout", help="Logout and clear tokens")

def logout(args):
    """Logout and clear tokens."""
    try:
        token_manager = TokenManager(server=args.server, port=args.port)
        token_manager.logout()
        console.print("[green]Successfully logged out[/green]")
    except Exception as e:
        console.print(f"[red]Logout failed: {str(e)}[/red]")
        sys.exit(1)

command_functions["auth_logout"] = logout

# Auth status command
auth_status_parser = auth_subparsers.add_parser("status", help="Check authentication status")

def auth_status(args):
    """Check authentication status."""
    token_manager = TokenManager(server=args.server, port=args.port)
    if token_manager.settings.auth.token:
        console.print("[green]Authenticated with token[/green]")
    elif token_manager.settings.auth.api_key:
        console.print("[green]Authenticated with API key[/green]")
    else:
        console.print("[yellow]Not authenticated[/yellow]")

command_functions["auth_status"] = auth_status


# Organization commands
org_parser = subparsers.add_parser("org", help="Organization commands")
org_subparsers = org_parser.add_subparsers(dest="org_command", help="Organization command to execute")
org_subparsers.required = True

# List organizations command
list_org_parser = org_subparsers.add_parser("list", help="List organizations")

def list_organizations(args):
    """List organizations."""
    try:
        client = get_client(server=args.server, port=args.port)
        organizations = client.list_organizations()

        if not organizations:
            console.print("[yellow]No organizations found[/yellow]")
            return

        table = Table(title="Organizations")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="green")
        table.add_column("Description")

        for org in organizations:
            table.add_row(
                str(org.id),
                org.name,
                org.description or ""
            )

        console.print(table)
    except APIError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

command_functions["org_list"] = list_organizations

# Get organization command
get_org_parser = org_subparsers.add_parser("get", help="Get organization details")
get_org_parser.add_argument("org_id", type=int, help="Organization ID")

def get_organization(args):
    """Get organization details."""
    try:
        client = get_client(server=args.server, port=args.port)
        org = client.get_organization(args.org_id)

        table = Table(title=f"Organization: {org.name}")
        table.add_column("Field", style="blue")
        table.add_column("Value")

        table.add_row("ID", str(org.id))
        table.add_row("Name", org.name)
        table.add_row("Description", org.description or "")

        console.print(table)
    except APIError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

command_functions["org_get"] = get_organization

# Create organization command
create_org_parser = org_subparsers.add_parser("create", help="Create a new organization")
create_org_parser.add_argument("--name", required=True, help="Organization name")
create_org_parser.add_argument("--description", help="Organization description")

def create_organization(args):
    """Create a new organization."""
    try:
        client = get_client(server=args.server, port=args.port)
        org_data = OrganizationCreate(name=args.name, description=args.description)
        org = client.create_organization(org_data)

        console.print(f"[green]Organization created successfully with ID: {org.id}[/green]")
    except APIError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

command_functions["org_create"] = create_organization

# Update organization command
update_org_parser = org_subparsers.add_parser("update", help="Update an organization")
update_org_parser.add_argument("org_id", type=int, help="Organization ID")
update_org_parser.add_argument("--name", help="New organization name")
update_org_parser.add_argument("--description", help="New organization description")

def update_organization(args):
    """Update an organization."""
    try:
        # First get the current organization to use as defaults
        client = get_client(server=args.server, port=args.port)
        current_org = client.get_organization(args.org_id)

        # Use provided values or current values as defaults
        update_name = args.name if args.name is not None else current_org.name
        update_description = args.description if args.description is not None else current_org.description

        # Update the organization
        org_data = OrganizationUpdate(name=update_name, description=update_description)
        org = client.update_organization(args.org_id, org_data)

        console.print(f"[green]Organization updated successfully: {org.name}[/green]")
    except APIError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

command_functions["org_update"] = update_organization

# Delete organization command
delete_org_parser = org_subparsers.add_parser("delete", help="Delete an organization")
delete_org_parser.add_argument("org_id", type=int, help="Organization ID")
delete_org_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")

def delete_organization(args):
    """Delete an organization."""
    try:
        if not args.yes:
            # Use input() instead of typer.confirm
            response = input(f"Are you sure you want to delete organization with ID {args.org_id}? (y/n): ")
            if response.lower() not in ["y", "yes"]:
                console.print("[yellow]Operation cancelled[/yellow]")
                return

        client = get_client(server=args.server, port=args.port)
        client.delete_organization(args.org_id)

        console.print(f"[green]Organization with ID {args.org_id} deleted successfully[/green]")
    except APIError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

command_functions["org_delete"] = delete_organization


# Config commands
config_parser = subparsers.add_parser("config", help="Configuration commands")
config_subparsers = config_parser.add_subparsers(dest="config_command", help="Config command to execute")
config_subparsers.required = True

# Set API URL command
set_url_parser = config_subparsers.add_parser("set-url", help="Set the API URL")
set_url_parser.add_argument("url", help="API URL")

def set_api_url(args):
    """Set the API URL."""
    settings = get_settings()

    # Update environment variable
    os.environ["VESSELHARBOR_API_URL"] = args.url

    # Also update the settings object
    settings.api_url = args.url

    # Save the configuration to the highest-priority location
    config_dir = Path.home() / ".config" / "vesselharbor"
    config_file = config_dir / "config.json"

    # Create directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)

    # Load existing config or create a new one
    config_data = {}
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                config_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Update config with new API URL
    config_data["api_url"] = args.url

    # Save config
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2)

    console.print(f"[green]API URL set to: {args.url}[/green]")

command_functions["config_set-url"] = set_api_url

# Set server name command
set_server_parser = config_subparsers.add_parser("set-server", help="Set the server name or IP address")
set_server_parser.add_argument("server_name", help="Server name or IP address")

def set_server_name(args):
    """Set the server name or IP address."""
    settings = get_settings()

    # Update environment variable
    os.environ["VESSELHARBOR_SERVER_NAME"] = args.server_name

    # Also update the settings object
    settings.server_name = args.server_name
    settings.api_url = f"http://{settings.server_name}:{settings.server_port}"

    # Save the configuration to the highest-priority location
    config_dir = Path.home() / ".config" / "vesselharbor"
    config_file = config_dir / "config.json"

    # Create directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)

    # Load existing config or create a new one
    config_data = {}
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                config_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Update config with new server name
    config_data["server_name"] = args.server_name
    config_data["api_url"] = settings.api_url

    # Save config
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2)

    console.print(f"[green]Server name set to: {args.server_name}[/green]")
    console.print(f"[green]API URL updated to: {settings.api_url}[/green]")

command_functions["config_set-server"] = set_server_name

# Set server port command
set_port_parser = config_subparsers.add_parser("set-port", help="Set the server port")
set_port_parser.add_argument("port_value", type=int, help="Server port")

def set_server_port(args):
    """Set the server port."""
    settings = get_settings()

    # Update environment variable
    os.environ["VESSELHARBOR_SERVER_PORT"] = str(args.port_value)

    # Also update the settings object
    settings.server_port = args.port_value
    settings.api_url = f"http://{settings.server_name}:{settings.server_port}"

    # Save the configuration to the highest-priority location
    config_dir = Path.home() / ".config" / "vesselharbor"
    config_file = config_dir / "config.json"

    # Create directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)

    # Load existing config or create a new one
    config_data = {}
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                config_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Update config with new server port
    config_data["server_port"] = args.port_value
    config_data["api_url"] = settings.api_url

    # Save config
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2)

    console.print(f"[green]Server port set to: {args.port_value}[/green]")
    console.print(f"[green]API URL updated to: {settings.api_url}[/green]")

command_functions["config_set-port"] = set_server_port

# Get API URL command
get_url_parser = config_subparsers.add_parser("get-url", help="Get the current API URL")

def get_api_url(args):
    """Get the current API URL."""
    settings = get_settings(override_server=args.server, override_port=args.port)
    console.print(f"API URL: {settings.api_url}")

command_functions["config_get-url"] = get_api_url

# Get server name command
get_server_parser = config_subparsers.add_parser("get-server", help="Get the current server name")

def get_server_name(args):
    """Get the current server name."""
    settings = get_settings(override_server=args.server, override_port=args.port)
    console.print(f"Server name: {settings.server_name}")

command_functions["config_get-server"] = get_server_name

# Get server port command
get_port_parser = config_subparsers.add_parser("get-port", help="Get the current server port")

def get_server_port(args):
    """Get the current server port."""
    settings = get_settings(override_server=args.server, override_port=args.port)
    console.print(f"Server port: {settings.server_port}")

command_functions["config_get-port"] = get_server_port


def main():
    """Main entry point for the CLI."""
    args = parser.parse_args()

    # Determine the command to execute
    if args.command == "auth":
        command_key = f"auth_{args.auth_command}"
    elif args.command == "org":
        command_key = f"org_{args.org_command}"
    elif args.command == "config":
        command_key = f"config_{args.config_command}"
    else:
        parser.print_help()
        sys.exit(1)

    # Execute the command function
    if command_key in command_functions:
        command_functions[command_key](args)
    else:
        console.print(f"[red]Unknown command: {command_key}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
