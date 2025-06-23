"""API client for the VesselHarbor Environments API."""

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
#
#

from typing import Dict, List, Optional, Any


from pydantic import BaseModel

from ..core.auth import TokenManager
from ..core.config import get_base_url
from ..core.requests import make_request


class Environment(BaseModel):
    """Environment model."""

    id: int
    name: str
    description: Optional[str] = None
    organization_id: int


class EnvironmentCreate(BaseModel):
    """Environment creation model."""

    name: str
    description: Optional[str] = None
    organization_id: int


class EnvironmentUpdate(BaseModel):
    """Environment update model."""

    name: str
    description: Optional[str] = None
    organization_id: Optional[int] = None


class APIEnvironment:
    """API environment model."""

    def __init__(self, config):
        """Initialize with full configuration."""
        self.config = config
        self.token_manager = TokenManager()
        self.base_url = get_base_url()

    def list_environments(self, organization_id: int, skip: int = 0, limit: int = 100) -> List[Environment]:
        """List environments for an organization.

        Args:
            organization_id: The ID of the organization.
            skip: Number of items to skip.
            limit: Maximum number of items to return.

        Returns:
            List of environments.
        """
        response = make_request(self.token_manager,"GET", f"/organizations/{organization_id}/environments", params={"skip": skip, "limit": limit})
        data = response.json()

        if isinstance(data, dict) and "data" in data:
            environments = data.get("data", [])
        elif isinstance(data, list):
            environments = data
        else:
            environments = []

        # Ensure organization_id is set for each environment
        return [Environment(**{**env, "organization_id": organization_id}) for env in environments]

    def get_environment(self, organization_id: int, environment_id: int) -> Environment:
        """Get environment details.

        Args:
            organization_id: The ID of the organization.
            environment_id: The ID of the environment.

        Returns:
            Environment details.
        """
        response = make_request(self.token_manager,"GET", f"/organizations/{organization_id}/environments/{environment_id}")
        data = response.json()
        # TODO Traiter les cas d'erreur (permissions, pas d'environnement ...)
        if isinstance(data, dict) and "data" in data:
            env_data = data.get("data", {})
        else:
            env_data = data
        # Ensure organization_id is set
        return Environment(**{**env_data, "organization_id": organization_id})

    def create_environment(self, environment_data: EnvironmentCreate) -> Environment:
        """Create a new environment.

        Args:
            environment_data: The environment data including organization_id.

        Returns:
            The created environment.
        """
        organization_id = environment_data.organization_id
        # Create a copy of the data without organization_id for the request
        data_dict = environment_data.model_dump(exclude_none=True)
        if "organization_id" in data_dict:
            del data_dict["organization_id"]

        response = make_request(self.token_manager,
            "POST",
            f"/organizations/{organization_id}/environments",
            json=data_dict
        )
        data = response.json()
        # TODO Traiter les cas d'erreur (permissions, pas d'environnement ...)
        if isinstance(data, dict) and "data" in data:
            env_data = data.get("data", {})
        else:
            env_data = data
        # Ensure organization_id is set
        return Environment(**{**env_data, "organization_id": organization_id})

    def update_environment(self, organization_id: int, environment_id: int, environment_data: EnvironmentUpdate) -> Environment:
        """Update an environment.

        Args:
            organization_id: The ID of the organization.
            environment_id: The ID of the environment to update.
            environment_data: The updated environment data.

        Returns:
            The updated environment.
        """
        # Create a copy of the data without organization_id for the request
        data_dict = environment_data.model_dump(exclude_none=True)
        if "organization_id" in data_dict:
            del data_dict["organization_id"]

        response = make_request(self.token_manager,
            "PUT",
            f"/organizations/{organization_id}/environments/{environment_id}",
            json=data_dict
        )
        data = response.json()
        # TODO Traiter les cas d'erreur (permissions, pas d'environnement ...)
        if isinstance(data, dict) and "data" in data:
            env_data = data.get("data", {})
        else:
            env_data = data
        # Ensure organization_id is set
        return Environment(**{**env_data, "organization_id": organization_id})

    def delete_environment(self, organization_id: int, environment_id: int) -> Dict[str, Any]:
        """Delete an environment.

        Args:
            organization_id: The ID of the organization.
            environment_id: The ID of the environment to delete.

        Returns:
            Response data.
        """
        response = make_request(self.token_manager,"DELETE", f"/organizations/{organization_id}/environments/{environment_id}")
        return response.json()


def get_APIenvironment(config) -> APIEnvironment:
    """Get an API client instance with full configuration."""
    return APIEnvironment(config)
