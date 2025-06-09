# VesselHarbor CLI Project Guidelines

This document provides guidelines and information for developing and maintaining the VesselHarbor CLI project.

## Project Overview

VesselHarbor CLI is a command-line tool for interacting with the VesselHarbor API. It provides functionality for authentication, organization management, and configuration.

## Project Structure

The project follows a modular structure:

- `vesselharborcli/` - Main package directory
  - `__main__.py` - Entry point for the CLI application
  - `auth.py` - Authentication functionality
  - `auth_commands.py` - Authentication command implementations
  - `service.py` - Service management
  - `core/` - Core utilities and configuration
  - `orgs/` - Organization-related commands and functionality
  - `projects/` - Project-related commands and functionality
- `tests/` - Test directory
  - `test_cli.py` - Tests for CLI functionality
- `main.py` - Wrapper script for the CLI

## Development Environment

The project uses Poetry for dependency management. To set up the development environment:

1. Install Poetry if not already installed: https://python-poetry.org/docs/#installation
2. Clone the repository
3. Run `poetry install` to install dependencies

## Testing

### Running Tests

Tests should be run to verify that changes don't break existing functionality. Use pytest to run the tests:

```bash
poetry run pytest
```

For more detailed output, including test coverage:

```bash
poetry run pytest --cov=vesselharborcli
```

### Test Structure

Tests are written using the unittest framework and are located in the `tests/` directory. The tests use mocking to isolate components and avoid making actual API calls.

Note: There appears to be a discrepancy between the tests (which reference a Typer-based CLI) and the actual implementation (which uses argparse). When making changes, ensure that tests are updated to match the implementation.

## Building and Installation

### Building the Package

To build the package:

```bash
poetry build
```

This will create distribution packages in the `dist/` directory.

### Installing the Package

For development, install the package in editable mode:

```bash
pip install -e .
```

For regular installation:

```bash
pip install .
```

## Code Style Guidelines

The project follows these code style guidelines:

1. **Black**: Code should be formatted using Black with a line length of 88 characters.
   ```bash
   poetry run black vesselharborcli tests
   ```

2. **isort**: Imports should be sorted using isort with the Black profile.
   ```bash
   poetry run isort vesselharborcli tests
   ```

3. **mypy**: Type hints should be used and checked with mypy.
   ```bash
   poetry run mypy vesselharborcli
   ```

4. **Docstrings**: Functions and classes should have docstrings following the Google style.

## Submitting Changes

Before submitting changes:

1. Ensure all tests pass
2. Format code with Black and isort
3. Check types with mypy
4. Update documentation if necessary

## Troubleshooting

If you encounter issues with the CLI:

1. Check authentication status with `vesselharbor auth status`
2. Verify configuration settings with `vesselharbor config get-url`
3. Enable verbose output for more detailed information
