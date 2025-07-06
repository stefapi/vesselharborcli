"""API client for the VesselHarbor API."""

from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel

from ..core.auth import TokenManager
from ..core.config import get_base_url
from ..core.requests import make_request


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
        self.token_manager = TokenManager()
        self.base_url = get_base_url()

    def list_organizations(self, skip: int = 0, limit: int = 100) -> List[Organization]:
        """List organizations."""
        response = make_request(self.token_manager,"GET", "/organizations")
        data = response.json()

        if isinstance(data, dict) and "data" in data:
            organizations = data.get("data", [])

        return [Organization(**org) for org in organizations]

    def get_organization(self, org_id: int) -> Organization:
        """Get organization details."""
        response = make_request(self.token_manager,"GET", f"/organizations/{org_id}")
        data = response.json()
        # TODO Handle error cases (permissions, no organization ...)
        if isinstance(data, dict) and "data" in data:
            organization = data.get("data", [])
        return Organization(**organization)

    def create_organization(self, org_data: OrganizationCreate) -> Organization:
        """Create a new organization.

        Only superadmins can create organizations.

        Args:
            org_data: Organization data to create.

        Returns:
            The created organization.

        Raises:
            APIError: If the user is not a superadmin or if the API request fails.
        """
        # Check if the user is a superadmin
        if not self.token_manager.is_superadmin():
            raise APIError("Only superadmins can create organizations", 403)

        response = make_request(self.token_manager,
            "POST",
            "/organizations",
            json=org_data.model_dump(exclude_none=True)
        )
        data = response.json()
        # TODO Handle error cases (permissions, no organization ...)
        if isinstance(data, dict) and "data" in data:
            organization = data.get("data", [])
        return Organization(**organization)

    def update_organization(self, org_id: int, org_data: OrganizationUpdate) -> Organization:
        """Update an organization."""
        response = make_request(self.token_manager,
            "PUT",
            f"/organizations/{org_id}",
            json=org_data.model_dump(exclude_none=True)
        )
        data = response.json()
        # TODO Handle error cases (permissions, no organization ...)
        if isinstance(data, dict) and "data" in data:
            organization = data.get("data", [])
        return Organization(**organization)

    def delete_organization(self, org_id: int) -> Dict[str, Any]:
        """Delete an organization."""
        response = make_request(self.token_manager,"DELETE", f"/organizations/{org_id}")
        return response.json()

def get_APIorg(config) -> APIOrganization:
    """Get an API client instance with full configuration."""
    return APIOrganization(config)
