"""Authentication functionality for the VesselHarbor CLI."""

import json
import os
import time
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

import requests
from pydantic import BaseModel

from vesselharborcli.core.config import get_config, get_base_url


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None

class AuthenticationError(Exception):
    """Authentication error."""
    pass

class TokenManager:
    """Token manager for handling authentication tokens."""
    def __init__(self):
        config = get_config()
        self.token_file = Path(config.path.DATA_DIR) / "tokens.json"
        self.load_tokens()
        self.access_token = None
        self.refresh_token = None

    def login_with_password(self) -> bool:
        """Login with configured username and password."""
        config = get_config()
        url = f"{get_base_url()}/login"
        data = {
            "username": config['application.user'],
            "password": config['application.password'],
            "grant_type": "password",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            if token_data.status == 'success':
                self.access_token = response.cookies.get('access_token')
                self.refresh_token = response.cookies.get('refresh_token')
                return True
            return False
        except requests.HTTPError as e:
            raise AuthenticationError(f"Password auth failed: {e.response.text}")
        except requests.RequestException as e:
            raise AuthenticationError(f"Request failed: {str(e)}")

    def login_with_api_key(self) -> bool:
        """Login with configured API key."""
        config = get_config()
        url = f"{get_base_url()}/login"
        headers = {"Authorization": f"Bearer {config['application.api_key']}"}

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            if token_data.status == 'success':
                self.access_token = response.cookies.get('access_token')
                self.refresh_token = response.cookies.get('refresh_token')
                return True
            return False
        except requests.HTTPError as e:
            raise AuthenticationError(f"API key auth failed: {e.response.text}")
        except requests.RequestException as e:
            raise AuthenticationError(f"Request failed: {str(e)}")

    def refresh_token(self) -> TokenResponse:
        """Refresh the access token using the refresh token."""
        if not self.refresh_token:
            raise AuthenticationError("No refresh token available")

        url = f"{get_base_url()}/refresh-token"
        headers = {"Authorization": f"Bearer {self.refresh_token}"}

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            if token_data.status == 'success':
                self.access_token = response.cookies.get('access_token')
                self.refresh_token = response.cookies.get('refresh_token')
                return True
            return False
        except requests.HTTPError as e:
            self.token = None
            self.refresh_token = None
            raise AuthenticationError(f"Token refresh failed: {e.response.text}")
        except requests.RequestException as e:
            raise AuthenticationError(f"Request failed: {str(e)}")

    def get_auth_header(self) -> Dict[str, str]:
        """Get the authorization header for API requests."""
        config = get_config()
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        else:
            raise AuthenticationError("No authentication token or API key available")

    def ensure_authentication(self):
        """Ensure valid authentication credentials."""
        config = get_config()
        if self.refresh_token():
            return
        elif config['application.api_key']:
            self.login_with_api_key()
        elif config['application.user'] and config['application.password']:
            self.login_with_password()
        else:
            raise AuthenticationError(
                "No authentication credentials available. "
                "Please configure user/password or API key."
            )

def authenticated_request(
    method: str,
    endpoint: str,
    **kwargs
) -> requests.Response:
    """Make an authenticated request with automatic token refresh."""
    token_manager = TokenManager()

    try:
        token_manager.ensure_authentication()
        url = f"{get_base_url()}{endpoint}"
        headers = token_manager.get_auth_header()

        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']

        # First attempt
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response
    except requests.HTTPError as e:
        # Handle token expiration
        if e.response.status_code == 401:
            try:
                token_manager.refresh_token()
                # Retry with new token
                headers = token_manager.get_auth_header()
                response = requests.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                return response
            except Exception:
                raise AuthenticationError("Authentication failed after refresh")
        else:
            raise
    except requests.RequestException as e:
        raise AuthenticationError(f"Request failed: {str(e)}")
