# Project Guidelines for VesselHarbor CLI

## Project Overview
VesselHarbor CLI is a command-line interface tool for interacting with the VesselHarbor platform, which is a self-hosted solution that simplifies private cloud deployment on Raspberry Pi or VPS with VMs, containers, websites, email, DNS, and one-click apps. The CLI provides functionality for:

- Authentication (login, logout, token management)
- Organization management (list, create, update, delete)
- Environment management (list, create, update, delete)
- Configuration management
- Interactive mode for user-friendly resource management

## Project Structure
The project follows a modular architecture:

- `vesselharborcli/` - Main package directory
  - `__main__.py` - Entry point for the CLI application
  - `auth_commands.py` - Authentication command implementations
  - `service.py` - Service management
  - `core/` - Core utilities and configuration
    - `auth.py` - Authentication service
    - `config.py` - Configuration management
    - `settings.py` - Settings management
    - `type_conv.py` - Type conversion utilities
  - `orgs/` - Organization-related commands and functionality
  - `environments/` - Environment-related commands and functionality
  - `interactive/` - Interactive mode functionality
- `tests/` - Test directory
  - `test_cli.py` - Tests for CLI functionality
- `main.py` - Wrapper script for the CLI

## Testing Guidelines
When making changes to the codebase, Junie should:

1. Run the existing tests to ensure no regressions:
   ```bash
   poetry run pytest
   ```

2. For test coverage analysis:
   ```bash
   poetry run pytest --cov=vesselharborcli
   ```

3. When implementing new features, add appropriate tests to maintain test coverage.

## Code Style Guidelines
The project follows these code style guidelines:

1. Format code with Black and isort:
   ```bash
   poetry run black vesselharborcli tests
   poetry run isort vesselharborcli tests
   ```

2. Check types with mypy:
   ```bash
   poetry run mypy vesselharborcli
   ```

3. Follow PEP 8 guidelines for Python code style.
4. Use docstrings for all functions, classes, and modules.
5. Keep functions small and focused on a single responsibility.

## Building the Project
To build the project:

1. Ensure all dependencies are installed:
   ```bash
   poetry install
   ```

2. Build the package:
   ```bash
   poetry build
   ```

This creates distribution packages in the `dist/` directory.

## Development Workflow
When working on this project, Junie should:

1. Understand the issue or feature request thoroughly.
2. Identify the relevant modules and files that need to be modified.
3. Make minimal changes to address the issue while maintaining compatibility.
4. Run tests to ensure the changes don't break existing functionality.
5. Format the code according to the project's style guidelines.
6. Provide a clear explanation of the changes made and how they address the issue.

## Important Considerations
1. Authentication and security are critical aspects of this application. Any changes to authentication flows should be carefully reviewed.
2. The CLI is designed to be user-friendly, so error messages should be clear and helpful.
3. The application uses a hierarchical configuration approach (defaults, config file, environment variables, command-line arguments).
4. The project uses Poetry for dependency management.
