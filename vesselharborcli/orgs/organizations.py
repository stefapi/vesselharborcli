"""API client for the VesselHarbor API."""

from typing import Dict, List, Optional, Any, Union

import requests
from pydantic import BaseModel

from vesselharborcli.auth import AuthenticationError, TokenManager, authenticated_request


class Organization(BaseModel):
    """Organization model."""

    id: int
    name: str
    description: Optional[str] = None


class OrganizationCreate(BaseModel):
    """Organization creation model."""

    name: str
    description: Optional[str] = None


class OrganizationUpdate(BaseModel):
    """Organization update model."""

    name: str
    description: Optional[str] = None


class APIError(Exception):
    """API error."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        """Initialize the API error."""
        self.status_code = status_code
        super().__init__(message)


class APIOrganization:
    """API organization model."""

    def __init__(self, config):
        """Initialize with full configuration."""
        self.config = config
        self.token_manager = TokenManager(config
        )
        self.base_url = self._get_base_url()

    def _get_base_url(self):
        """Construct base URL from configuration."""
        if self.config.application.socket:
            return f"http://unix:{self.config.application.socket}"
        return f"http://{self.config.application.ip_address}:{self.config.application.port}"

    def _ensure_authentication(self):
        """Ensure valid authentication credentials exist."""
        if not self.token_manager.settings.auth.token and not self.token_manager.settings.auth.api_key:
            if self.token_manager.settings.auth.username and self.token_manager.settings.auth.password:
                self.token_manager.login_with_password(
                    self.token_manager.settings.auth.username,
                    self.token_manager.settings.auth.password
                )
            else:
                raise AuthenticationError("No authentication credentials available")

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request with error handling."""
        self._ensure_authentication()
        url = f"{self.base_url}{endpoint}"

        try:
            return authenticated_request(
                method,
                endpoint,
                **kwargs
            )
        except AuthenticationError as e:
            raise APIError(f"Authentication error: {str(e)}")
        except requests.HTTPError as e:
            raise APIError(f"API error: {e.response.text}", e.response.status_code)
        except requests.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")

    def list_organizations(self, skip: int = 0, limit: int = 100) -> List[Organization]:
        """List organizations."""
        response = self._make_request("GET", "/organizations")
        data = response.json()

        if isinstance(data, dict) and "items" in data:
            organizations = data.get("items", [])
        elif isinstance(data, list):
            organizations = data
        else:
            organizations = []

        return [Organization(**org) for org in organizations]

    def get_organization(self, org_id: int) -> Organization:
        """Get organization details."""
        response = self._make_request("GET", f"/organizations/{org_id}")
        return Organization(**response.json())

    def create_organization(self, org_data: OrganizationCreate) -> Organization:
        """Create a new organization."""
        response = self._make_request(
            "POST",
            "/organizations",
            json=org_data.model_dump(exclude_none=True)
        )
        return Organization(**response.json())

    def update_organization(self, org_id: int, org_data: OrganizationUpdate) -> Organization:
        """Update an organization."""
        response = self._make_request(
            "PUT",
            f"/organizations/{org_id}",
            json=org_data.model_dump(exclude_none=True)
        )
        return Organization(**response.json())

    def delete_organization(self, org_id: int) -> Dict[str, Any]:
        """Delete an organization."""
        response = self._make_request("DELETE", f"/organizations/{org_id}")
        return response.json()

def get_APIorg(config) -> APIOrganization:
    """Get an API client instance with full configuration."""
    return APIOrganization(config)
