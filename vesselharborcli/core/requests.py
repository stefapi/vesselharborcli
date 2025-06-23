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

from .config import get_base_url, get_config

import requests

from typing import Dict, List, Optional, Any, Union
from ..core.auth import AuthenticationError

class APIError(Exception):
    """API error."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        """Initialize the API error."""
        self.status_code = status_code
        super().__init__(message)


def make_request(token_manager, method: str, endpoint: str, **kwargs) -> requests.Response:
    """Make authenticated request with error handling."""
    try:
         return authenticated_request(token_manager = token_manager,
            method = method,
            endpoint = endpoint,
            **kwargs
        )
    except AuthenticationError as e:
        raise APIError(f"Authentication error: {str(e)}")
    except requests.HTTPError as e:
        status_code = e.response.status_code
        if status_code in [403, 404]:
            raise APIError(f"{e.response.text} ({status_code})", status_code)
        else:
            raise APIError(f"API error: {e.response.text}", status_code)
    except requests.RequestException as e:
        raise APIError(f"Request failed: {str(e)}")


def authenticated_request( token_manager,
    method: str,
    endpoint: str,
    **kwargs
) -> requests.Response:
    """Make an authenticated request with automatic token refresh."""
    try:
        if not token_manager.ensure_authentication():
            raise AuthenticationError("Invalid authentication credentials")
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
            #try:
            if True:

                token_manager.refresh()
                # Retry with new token
                headers = token_manager.get_auth_header()
                if 'headers' in kwargs:
                    headers.update(kwargs['headers'])
                    del kwargs['headers']

                response = requests.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                return response
            #except Exception:
            #    raise AuthenticationError("Authentication failed after refresh")
        else:
            raise
    except Exception as e:
        print (e)
        raise AuthenticationError(f"Request failed: {str(e)}")
