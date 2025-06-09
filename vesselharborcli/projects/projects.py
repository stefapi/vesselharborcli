"""API client for the VesselHarbor Projects API."""

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

from typing import Dict, List, Optional, Any, Union

import requests
from pydantic import BaseModel

from vesselharborcli.auth import AuthenticationError, TokenManager, authenticated_request


class Project(BaseModel):
    """Project model."""

    id: int
    name: str
    description: Optional[str] = None


class ProjectCreate(BaseModel):
    """Project creation model."""

    name: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Project update model."""

    name: str
    description: Optional[str] = None


class APIError(Exception):
    """API error."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        """Initialize the API error."""
        self.status_code = status_code
        super().__init__(message)


class APIProject:
    """API project model."""

    def __init__(self, config):
        """Initialize with full configuration."""
        self.config = config
        self.token_manager = TokenManager(config)
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

    def list_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """List projects."""
        response = self._make_request("GET", "/projects")
        data = response.json()

        if isinstance(data, dict) and "items" in data:
            projects = data.get("items", [])
        elif isinstance(data, list):
            projects = data
        else:
            projects = []

        return [Project(**proj) for proj in projects]

    def get_project(self, project_id: int) -> Project:
        """Get project details."""
        response = self._make_request("GET", f"/projects/{project_id}")
        return Project(**response.json())

    def create_project(self, project_data: ProjectCreate) -> Project:
        """Create a new project."""
        response = self._make_request(
            "POST",
            "/projects",
            json=project_data.model_dump(exclude_none=True)
        )
        return Project(**response.json())

    def update_project(self, project_id: int, project_data: ProjectUpdate) -> Project:
        """Update a project."""
        response = self._make_request(
            "PUT",
            f"/projects/{project_id}",
            json=project_data.model_dump(exclude_none=True)
        )
        return Project(**response.json())

    def delete_project(self, project_id: int) -> Dict[str, Any]:
        """Delete a project."""
        response = self._make_request("DELETE", f"/projects/{project_id}")
        return response.json()


def get_APIproject(config) -> APIProject:
    """Get an API client instance with full configuration."""
    return APIProject(config)
