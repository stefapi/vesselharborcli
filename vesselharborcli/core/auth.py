"""Authentication functionality for the VesselHarbor CLI."""

#  Copyright (c) 2025.  VesselHarbor
#  ____   ____                          .__    ___ ___             ___.
#  \   \ /   /____   ______ ______ ____ |  |  /   |   \_____ ______\_ |__   ___________
#   \   Y   // __ \ /  ___//  ___// __ \|  | /    ~    \__  \\_  __ \ __ \ /  _ \_  __ \
#    \     /\  ___/ \___ \ \___ \\  ___/|  |_\    Y    // __ \|  | \/ \_\ (  <_> )  | \/
#     \___/  \___  >____  >____  >\___  >____/\___|_  /(____  /__|  |___  /\____/|__|
#                \/     \/     \/     \/            \/      \/          \/
#  MIT License
#
#

import json
import os
import time
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from http.cookies import SimpleCookie

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
            if token_data['status'] == 'success':
                set_cookie = response.headers.get('set-cookie')
                if not set_cookie:
                    return False
                cookie_parts = set_cookie.split(', ')
                cookie_strings = []
                current = ""
                for part in cookie_parts:
                    if '=' in part and part.split('=')[0].strip() in ('access_token', 'refresh_token'):
                        if current:
                            cookie_strings.append(current)
                        current = part
                    else:
                        current += ', ' + part
                if current:
                    cookie_strings.append(current)
                tokens = {}
                for raw_cookie in cookie_strings:
                    cookie = SimpleCookie()
                    cookie.load(raw_cookie)
                    for key in cookie:
                        tokens[key] = cookie[key].value
                self.access_token = tokens['access_token'] if 'access_token' in tokens else None
                self.refresh_token = tokens['refresh_token'] if 'refresh_token' in tokens else None
                return self.access_token is not None and self.refresh_token is not None
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
            if token_data['status'] == 'success':
                set_cookie = response.headers.get('set-cookie')
                if not set_cookie:
                    return False
                cookie_parts = set_cookie.split(', ')
                cookie_strings = []
                current = ""
                for part in cookie_parts:
                    if '=' in part and part.split('=')[0].strip() in ('access_token', 'refresh_token'):
                        if current:
                            cookie_strings.append(current)
                        current = part
                    else:
                        current += ', ' + part
                if current:
                    cookie_strings.append(current)
                tokens = {}
                for raw_cookie in cookie_strings:
                    cookie = SimpleCookie()
                    cookie.load(raw_cookie)
                    for key in cookie:
                        tokens[key] = cookie[key].value
                self.access_token = tokens['access_token'] if 'access_token' in tokens else None
                self.refresh_token = tokens['refresh_token'] if 'refresh_token' in tokens else None
                return True
            return False
        except requests.HTTPError as e:
            raise AuthenticationError(f"API key auth failed: {e.response.text}")
        except requests.RequestException as e:
            raise AuthenticationError(f"Request failed: {str(e)}")

    def refresh(self) -> TokenResponse:
        """Refresh the access token using the refresh token."""
        if not self.refresh_token:
            return False

        self.access_token = None
        url = f"{get_base_url()}/refresh-token"
        headers = {"Authorization": f"Bearer {self.refresh_token}"}

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            if token_data['status'] == 'success':
                set_cookie = response.headers.get('set-cookie')
                if not set_cookie:
                    return False
                cookie_parts = set_cookie.split(', ')
                cookie_strings = []
                current = ""
                for part in cookie_parts:
                    if '=' in part and part.split('=')[0].strip() in ('access_token', 'refresh_token'):
                        if current:
                            cookie_strings.append(current)
                        current = part
                    else:
                        current += ', ' + part
                if current:
                    cookie_strings.append(current)
                tokens = {}
                for raw_cookie in cookie_strings:
                    cookie = SimpleCookie()
                    cookie.load(raw_cookie)
                    for key in cookie:
                        tokens[key] = cookie[key].value
                self.access_token = tokens['access_token'] if 'access_token' in tokens else None
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
        """Ensure valid authentication credentials exist."""

        if self.access_token and self.refresh_token:
            return True
        config = get_config()
        if config['application.user'] and config['application.password']:
            # Attempt to login with password
            return self.login_with_password()
        if config.config['application.api_key']:
            # Attempt to login with password
            return self.login_with_api_key()
        return False

    def refresh_authentication(self):
        """Ensure valid authentication credentials."""
        config = get_config()
        if self.refresh_token():
            return True
        else:
            return self.ensure_authentication()
