# VesselHarbor CLI

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/CLI-000000?style=for-the-badge&logo=windows-terminal&logoColor=white" alt="CLI">
  <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/REST%20API-005571?style=for-the-badge&logo=fastapi&logoColor=white" alt="REST API">
</div>

<p align="center">
  <em>A powerful command-line interface for interacting with the VesselHarbor platform</em>
</p>

VesselHarbor CLI is a command-line tool for interacting with the VesselHarbor API. It provides functionality for authentication, organization management, environment management, and configuration.

## 🚢 What is VesselHarbor?

VesselHarbor is a self-hosted platform that simplifies private cloud deployment on Raspberry Pi or VPS with VMs, containers, websites, email, DNS, and one-click apps. This CLI tool allows you to interact with the VesselHarbor API to manage your resources efficiently from the command line.

## ✨ Features

- **Authentication**: Login with username/password or API key with automatic token refresh
- **Organization Management**: List, create, update, and delete organizations
- **Environment Management**: List, create, update, and delete environments
- **Configuration Management**: Easily configure API endpoints and server settings
- **Interactive Mode**: User-friendly interface for managing resources
- **Modern Python**: Built with modern Python practices and libraries
- **Comprehensive Documentation**: Detailed help for all commands

## 🚀 Quick Start

### Prerequisites

- Python ≥ 3.8
- pip (Python package manager)

### Installation

#### Using pip

```bash
pip install vesselharborcli
```

#### From source

```bash
# Clone the repository
git clone https://github.com/stefapi/vesselharborcli.git
cd vesselharborcli

# Install in development mode
pip install -e .
```

## 📖 Usage

### Authentication

```bash
# Login with username and password
vesselharbor auth login

# Login with API key
vesselharbor auth login-key

# Check authentication status
vesselharbor auth status

# Logout
vesselharbor auth logout
```

### Configuration

```bash
# Set API URL
vesselharbor config set-url https://api.example.com

# Set server name
vesselharbor config set-server api.example.com

# Set server port
vesselharbor config set-port 8080

# Get current API URL
vesselharbor config get-url
```

### Organizations

```bash
# List organizations
vesselharbor org list

# Get organization details
vesselharbor org get <org_id>

# Create a new organization
vesselharbor org create --name "My Organization" --description "My organization description"

# Update an organization
vesselharbor org update <org_id> --name "New Name" --description "New description"

# Delete an organization
vesselharbor org delete <org_id>
```

### Environments

```bash
# List environments
vesselharbor environment list

# Get environment details
vesselharbor environment get <environment_id>

# Create a new environment
vesselharbor environment create --name "My Environment" --description "My environment description"

# Update an environment
vesselharbor environment update <environment_id> --name "New Name" --description "New description"

# Delete an environment
vesselharbor environment delete <environment_id>
```

### Interactive Mode

```bash
# Launch interactive mode
vesselharbor interactive
```

This will launch an interactive interface where you can select which resource type (organizations or environments) you want to manage. From there, you can perform operations like viewing, creating, editing, and deleting resources in a visual environment.

The interactive mode provides a user-friendly interface similar to cfdisk, making it easier to manage your resources.

## 💻 Development

### Development Environment

The project uses Poetry for dependency management. To set up the development environment:

1. Install Poetry if not already installed: https://python-poetry.org/docs/#installation
2. Clone the repository
3. Run `poetry install` to install dependencies

### Project Structure

The project follows a modular structure:

- `vesselharborcli/` - Main package directory
  - `__main__.py` - Entry point for the CLI application
  - `auth_commands.py` - Authentication command implementations
  - `service.py` - Service management
  - `core/` - Core utilities and configuration
  - `orgs/` - Organization-related commands and functionality
  - `environments/` - Environment-related commands and functionality
  - `interactive/` - Interactive mode functionality
- `tests/` - Test directory
  - `test_cli.py` - Tests for CLI functionality
- `main.py` - Wrapper script for the CLI

### Testing

Run tests with pytest:

```bash
poetry run pytest

# For test coverage
poetry run pytest --cov=vesselharborcli
```

### Building the Package

```bash
poetry build
```

This creates distribution packages in the `dist/` directory.

## 🔧 Configuration

### Environment Variables

The following environment variables can be used to configure the CLI:

- `VESSELHARBOR_API_URL`: The URL of the VesselHarbor API
- `VESSELHARBOR_SERVER_NAME`: The server name or IP address
- `VESSELHARBOR_SERVER_PORT`: The server port
- `VESSELHARBOR_USERNAME`: Username for authentication
- `VESSELHARBOR_PASSWORD`: Password for authentication
- `VESSELHARBOR_API_KEY`: API key for authentication

You can also use a `.env` file in the current directory to set these variables.

## 🤝 Contributing

Contributions are welcome! Before submitting changes:

1. Ensure all tests pass
2. Format code with Black and isort
   ```bash
   poetry run black vesselharborcli tests
   poetry run isort vesselharborcli tests
   ```
3. Check types with mypy
   ```bash
   poetry run mypy vesselharborcli
   ```
4. Update documentation if necessary

## 🔍 Troubleshooting

If you encounter issues with the CLI:

1. Check authentication status with `vesselharbor auth status`
2. Verify configuration settings with `vesselharbor config get-url`
3. Enable verbose output with the `-V` or `--verbose` flag

## 📄 License

This project is licensed under the Apache License, Version 2.0 - see the LICENSE file for details.
