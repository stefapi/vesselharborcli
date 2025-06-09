# VesselHarbor CLI

A command-line tool for interacting with the VesselHarbor API.

## Features

- Authentication with username/password or API key
- Automatic token refresh
- Organization management (list, create, update, delete)
- Configuration management

## Installation

### Using pip

```bash
pip install vesselharborcli
```

### From source

```bash
git clone https://github.com/yourusername/vesselharborcli.git
cd vesselharborcli
pip install -e .
```

## Usage

### Authentication

Login with username and password:

```bash
vesselharbor auth login
```

Login with API key:

```bash
vesselharbor auth login-key
```

Check authentication status:

```bash
vesselharbor auth status
```

Logout:

```bash
vesselharbor auth logout
```

### Configuration

Set API URL:

```bash
vesselharbor config set-url https://api.example.com
```

Set server name:

```bash
vesselharbor config set-server api.example.com
```

Set server port:

```bash
vesselharbor config set-port 8080
```

Get current API URL:

```bash
vesselharbor config get-url
```

Get current server name:

```bash
vesselharbor config get-server
```

Get current server port:

```bash
vesselharbor config get-port
```

### Organizations

List organizations:

```bash
vesselharbor org list
```

Get organization details:

```bash
vesselharbor org get <org_id>
```

Create a new organization:

```bash
vesselharbor org create --name "My Organization" --description "My organization description"
```

Update an organization:

```bash
vesselharbor org update <org_id> --name "New Name" --description "New description"
```

Delete an organization:

```bash
vesselharbor org delete <org_id>
```

Use the `-y` or `--yes` flag to skip confirmation:

```bash
vesselharbor org delete <org_id> -y
```

## Environment Variables

The following environment variables can be used to configure the CLI:

- `VESSELHARBOR_API_URL`: The URL of the VesselHarbor API
- `VESSELHARBOR_SERVER_NAME`: The server name or IP address (will override API URL)
- `VESSELHARBOR_SERVER_PORT`: The server port (will override API URL)
- `VESSELHARBOR_USERNAME`: Username for authentication
- `VESSELHARBOR_PASSWORD`: Password for authentication
- `VESSELHARBOR_API_KEY`: API key for authentication

You can also use a `.env` file in the current directory to set these variables.

Note: If both `VESSELHARBOR_SERVER_NAME` and `VESSELHARBOR_SERVER_PORT` are set, they will override the `VESSELHARBOR_API_URL` setting.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
