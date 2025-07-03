# VesselHarbor CLI Architecture

## Overview

VesselHarbor CLI is a command-line interface tool designed to interact with the VesselHarbor API. The architecture follows a modular approach to ensure maintainability, testability, and extensibility.

## Architectural Components

### 1. Command-Line Interface Layer

The CLI is built using Python's `argparse` library, which handles command parsing and execution. The entry point is in `__main__.py`, which sets up the command structure and routes commands to their respective handlers.

### 2. Command Modules

Commands are organized into logical modules:

- **Authentication Commands** (`auth_commands.py`): Handles user authentication, login, logout, and token management.
- **Organization Commands** (`orgs/main.py`): Manages organization-related operations.
- **Project Commands** (`projects/main.py`): Handles project-related operations.

### 3. Core Services

Core services provide functionality used across the application:

- **Authentication Service** (`auth.py`): Manages authentication state and tokens.
- **Configuration Management** (`core/config.py`, `core/config_file.py`): Handles application configuration.
- **Type Conversion** (`core/type_conv.py`): Utilities for type conversion and validation.
- **Settings Management** (`core/settings.py`): Manages application settings.

### 4. API Service Layer

The `service.py` module provides a service layer that abstracts the communication with the VesselHarbor API, handling HTTP requests, response parsing, and error handling.

## Data Flow

1. User inputs a command via the CLI
2. The command is parsed by the CLI layer
3. The appropriate command handler is invoked
4. The command handler uses services to perform operations
5. Services communicate with the API when necessary
6. Results are formatted and displayed to the user

## Configuration Management

The application uses a hierarchical configuration approach:

1. Default settings defined in code
2. Configuration file settings (stored in user's config directory)
3. Environment variables
4. Command-line arguments (highest precedence)

## Authentication Flow

1. User authenticates using `vesselharbor auth login`
2. Credentials are validated against the API
3. Upon successful authentication, a token is stored securely
4. Subsequent commands use the stored token for authorization
5. The token is refreshed automatically when needed

## Error Handling

The application implements a centralized error handling mechanism that:

1. Catches exceptions from the API layer
2. Translates them into user-friendly messages
3. Provides appropriate exit codes for scripting purposes

## Testing Strategy

The application is designed for testability:

1. Components are decoupled through dependency injection
2. Mock objects can be used to simulate API responses
3. Unit tests focus on individual components
4. Integration tests verify the interaction between components
