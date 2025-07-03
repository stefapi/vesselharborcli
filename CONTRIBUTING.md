# Contributing to VesselHarbor CLI

Thank you for your interest in contributing to VesselHarbor CLI! This document provides guidelines and information to help you contribute effectively.

## Development Environment

### Prerequisites

- Python ≥ 3.8
- pip (Python package manager)

### Setup

The project uses Poetry for dependency management. To set up the development environment:

1. Install Poetry if not already installed: https://python-poetry.org/docs/#installation
2. Clone the repository
3. Run `poetry install` to install dependencies

## Project Structure

The project follows a modular structure:

- `vesselharborcli/` - Main package directory
  - `__main__.py` - Entry point for the CLI application
  - `auth_commands.py` - Authentication command implementations
  - `service.py` - Service management
  - `core/` - Core utilities and configuration
    - `auth.py` - Authentication functionality
    - `config.py` - Configuration management
    - `settings.py` - Settings management
    - `requests.py` - API request handling
  - `orgs/` - Organization-related commands and functionality
  - `environments/` - Environment-related commands and functionality
  - `interactive/` - Interactive mode functionality
- `tests/` - Test directory
  - `test_cli.py` - Tests for CLI functionality
- `main.py` - Wrapper script for the CLI

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

## Configuration

### Environment Variables

The following environment variables can be used to configure the CLI:

- `VESSELHARBOR_API_URL`: The URL of the VesselHarbor API
- `VESSELHARBOR_SERVER_NAME`: The server name or IP address
- `VESSELHARBOR_SERVER_PORT`: The server port
- `VESSELHARBOR_USERNAME`: Username for authentication
- `VESSELHARBOR_PASSWORD`: Password for authentication
- `VESSELHARBOR_API_KEY`: API key for authentication

You can also use a `.env` file in the current directory to set these variables.

## Interactive Mode

The CLI provides an interactive mode for managing resources:

```bash
vesselharbor interactive
```

This launches a user-friendly interface for managing organizations and environments.

## Troubleshooting

If you encounter issues with the CLI:

1. Check authentication status with `vesselharbor auth status`
2. Verify configuration settings with `vesselharbor config get-url`
3. Enable verbose output with the `-V` or `--verbose` flag for more detailed information

## Pull Request Process

1. Fork the repository and create a new branch for your feature or bug fix
2. Make your changes, following the code style guidelines
3. Add tests for your changes when applicable
4. Ensure all tests pass by running `poetry run pytest`
5. Update documentation if necessary
6. Submit a pull request with a clear description of the changes and any relevant issue numbers

## Commit Messages

Write clear, concise commit messages that explain the changes made. Follow these guidelines:

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

## Reporting Bugs

When reporting bugs, please include:

1. A clear, descriptive title
2. Steps to reproduce the issue
3. Expected behavior
4. Actual behavior
5. Environment information (OS, Python version, etc.)

## Feature Requests

Feature requests are welcome. Please provide:

1. A clear, descriptive title
2. A detailed description of the proposed feature
3. Any relevant examples or use cases
4. If possible, a suggestion for how to implement the feature

## License

By contributing to VesselHarbor CLI, you agree that your contributions will be licensed under the project's MIT License.
