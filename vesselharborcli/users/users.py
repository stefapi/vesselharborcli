"""API client for the VesselHarbor User API."""

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

from pydantic import BaseModel

from ..core.auth import TokenManager
from ..core.config import get_base_url
from ..core.requests import make_request


class User(BaseModel):
    """User model."""

    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    is_superadmin: bool
    tags: List[Dict[str, Any]] = []


class UserCreate(BaseModel):
    """User creation model."""

    username: str
    first_name: str
    last_name: str
    email: str
    password: str


class UserUpdate(BaseModel):
    """User update model."""

    first_name: str
    last_name: str
    username: str
    email: str


class ChangePassword(BaseModel):
    """Password change model."""

    current_password: Optional[str] = None
    new_password: str


class APIError(Exception):
    """API error."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        """Initialize the API error."""
        self.status_code = status_code
        super().__init__(message)


class APIUser:
    """API user model."""

    def __init__(self, config):
        """Initialize with full configuration."""
        self.config = config
        self.token_manager = TokenManager()
        self.base_url = get_base_url()

    def list_users(self, skip: int = 0, limit: int = 100, email: Optional[str] = None) -> List[User]:
        """List users."""
        params = {"skip": skip, "limit": limit}
        if email:
            params["email"] = email

        response = make_request(self.token_manager, "GET", "/users", params=params)
        data = response.json()

        if isinstance(data, dict) and "data" in data:
            users = data.get("data", [])

        return [User(**user) for user in users]

    def get_user(self, user_id: int) -> User:
        """Get user details."""
        response = make_request(self.token_manager, "GET", f"/users/{user_id}")
        data = response.json()

        if isinstance(data, dict) and "data" in data:
            user = data.get("data", {})
        return User(**user)

    def create_user(self, user_data: UserCreate, organization_id: Optional[int] = None) -> User:
        """Create a new user.

        Args:
            user_data: User data to create.
            organization_id: Organization ID to attach the user to (optional).

        Returns:
            The created user.

        Raises:
            APIError: If the API request fails.
        """
        if organization_id:
            endpoint = f"/users/{organization_id}"
        else:
            endpoint = "/users"

        response = make_request(self.token_manager,
            "POST",
            endpoint,
            json=user_data.model_dump(exclude_none=True)
        )
        data = response.json()

        if isinstance(data, dict) and "data" in data:
            user = data.get("data", {})
        return User(**user)

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update a user."""
        response = make_request(self.token_manager,
            "PUT",
            f"/users/{user_id}",
            json=user_data.model_dump(exclude_none=True)
        )
        data = response.json()

        if isinstance(data, dict) and "data" in data:
            user = data.get("data", {})
        return User(**user)

    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """Delete a user."""
        response = make_request(self.token_manager, "DELETE", f"/users/{user_id}")
        return response.json()

    def change_password(self, user_id: int, password_data: ChangePassword) -> Dict[str, Any]:
        """Change user password."""
        response = make_request(self.token_manager,
            "PUT",
            f"/users/{user_id}/password",
            json=password_data.model_dump(exclude_none=True)
        )
        return response.json()

    def get_user_organizations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get organizations for a user."""
        try:
            response = make_request(self.token_manager, "GET", f"/users/{user_id}/organizations")
            data = response.json()

            if isinstance(data, dict) and "data" in data:
                organizations = data.get("data", [])
            else:
                organizations = data if isinstance(data, list) else []

            return organizations
        except Exception:
            # If the endpoint doesn't exist or fails, return empty list
            return []


def get_APIuser(config) -> APIUser:
    """Get an API client instance with full configuration."""
    return APIUser(config)
