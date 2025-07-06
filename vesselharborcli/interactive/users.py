"""Interactive user management interface."""

#  Copyright (c) 2024-2025.  VesselHarbor
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
#      ______                 _____
#     / ____/___ ________  __/ ___/___  ______   _____  _____
#    / __/ / __ `/ ___/ / / /\__ \/ _ \/ ___/ | / / _ \/ ___/
#   / /___/ /_/ (__  ) /_/ /___/ /  __/ /   | |/ /  __/ /
#  /_____/\__,_/____/\__, //____/\___/_/    |___/\___/_/
#                   /____/
#
#  Apache License
#  ================

import curses
from typing import List, Dict, Any

from ..users.users import APIUser, User, UserCreate, UserUpdate, ChangePassword, get_APIuser
from .base import InteractiveBase


class UsersInteractive(InteractiveBase):
    """Interactive user management interface."""

    def __init__(self, config):
        """Initialize the interactive user interface."""
        super().__init__(config)
        self.api = get_APIuser(config)
        self.items = []

    def load_data(self):
        """Load users from the API."""
        try:
            self.items = self.api.list_users()
        except Exception as e:
            self.items = []
            self.show_error(f"Failed to load users: {str(e)}")

    def get_title(self):
        """Get the title for the interface."""
        return "User Management"

    def get_commands(self):
        """Get available commands."""
        return {
            'c': 'Create User',
            'e': 'Edit User',
            'd': 'Delete User',
            'p': 'Change Password',
            'v': 'View Details',
            'r': 'Refresh',
            'h': 'Help',
            'q': 'Quit'
        }

    def format_list_item(self, item):
        """Format a user item for display in the list."""
        status = " (superadmin)" if item.is_superadmin else ""
        return f"{item.id}: {item.username} ({item.first_name} {item.last_name}) - {item.email}{status}"

    def get_item_details(self, item):
        """Get detailed information about a user."""
        details = [
            f"ID: {item.id}",
            f"Username: {item.username}",
            f"Name: {item.first_name} {item.last_name}",
            f"Email: {item.email}",
            f"Superadmin: {item.is_superadmin}",
        ]

        if item.tags:
            tag_values = [tag.get('value', '') for tag in item.tags if isinstance(tag, dict)]
            if tag_values:
                details.append(f"Tags: {', '.join(tag_values)}")

        # Get and display user organizations
        try:
            organizations = self.api.get_user_organizations(item.id)
            if organizations:
                org_names = []
                for org in organizations:
                    if isinstance(org, dict):
                        org_names.append(f"{org.get('name', 'Unknown')} (ID: {org.get('id', 'N/A')})")
                    else:
                        org_names.append(str(org))
                details.append(f"Organizations: {', '.join(org_names)}")
            else:
                details.append("Organizations: None")
        except Exception:
            details.append("Organizations: Error loading")

        return details

    def select_item(self):
        """Get the currently selected user."""
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None

    def handle_command(self, key):
        """Handle command input."""
        if key == ord('c'):
            self.create_user()
        elif key == ord('e'):
            user = self.select_item()
            if user:
                self.edit_user(user)
        elif key == ord('d'):
            user = self.select_item()
            if user:
                self.delete_user(user)
        elif key == ord('p'):
            user = self.select_item()
            if user:
                self.change_password(user)
        elif key == ord('v'):
            user = self.select_item()
            if user:
                self.view_user_details(user)
        elif key == ord('r'):
            self.load_data()
        elif key == ord('h'):
            self.show_help()
        else:
            return False
        return True

    def show_help(self):
        """Show help information."""
        help_text = [
            "User Management Help",
            "",
            "Navigation:",
            "  ↑/↓ or j/k - Move selection",
            "  Enter - View details",
            "",
            "Commands:",
            "  c - Create new user",
            "  e - Edit selected user",
            "  d - Delete selected user",
            "  p - Change user password",
            "  v - View user details",
            "  r - Refresh user list",
            "  h - Show this help",
            "  q - Quit",
            "",
            "Press any key to continue..."
        ]

        self.show_message_box(help_text)

    def create_user(self):
        """Create a new user."""
        try:
            # Get user input
            username = self.get_input("Enter username: ")
            if not username:
                return

            first_name = self.get_input("Enter first name: ")
            if not first_name:
                return

            last_name = self.get_input("Enter last name: ")
            if not last_name:
                return

            email = self.get_input("Enter email: ")
            if not email:
                return

            password = self.get_input("Enter password: ", hide=True)
            if not password:
                return

            org_id_str = self.get_input("Enter organization ID (optional): ")
            org_id = None
            if org_id_str:
                try:
                    org_id = int(org_id_str)
                except ValueError:
                    self.show_error("Invalid organization ID")
                    return

            # Create the user
            user_data = UserCreate(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )

            new_user = self.api.create_user(user_data, organization_id=org_id)
            self.show_success(f"User '{new_user.username}' created successfully!")
            self.load_data()

        except Exception as e:
            self.show_error(f"Failed to create user: {str(e)}")

    def edit_user(self, user):
        """Edit an existing user."""
        try:
            # Get updated information
            username = self.get_input(f"Username ({user.username}): ") or user.username
            first_name = self.get_input(f"First name ({user.first_name}): ") or user.first_name
            last_name = self.get_input(f"Last name ({user.last_name}): ") or user.last_name
            email = self.get_input(f"Email ({user.email}): ") or user.email

            # Update the user
            user_data = UserUpdate(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email
            )

            updated_user = self.api.update_user(user.id, user_data)
            self.show_success(f"User '{updated_user.username}' updated successfully!")
            self.load_data()

        except Exception as e:
            self.show_error(f"Failed to update user: {str(e)}")

    def delete_user(self, user):
        """Delete a user."""
        try:
            # Confirm deletion
            if self.confirm(f"Delete user '{user.username}'?"):
                self.api.delete_user(user.id)
                self.show_success(f"User '{user.username}' deleted successfully!")
                self.load_data()

        except Exception as e:
            self.show_error(f"Failed to delete user: {str(e)}")

    def change_password(self, user):
        """Change user password."""
        try:
            new_password = self.get_input("Enter new password: ", hide=True)
            if not new_password:
                return

            current_password = self.get_input("Enter current password (if changing own): ", hide=True)

            # Change the password
            password_data = ChangePassword(
                new_password=new_password,
                current_password=current_password if current_password else None
            )

            self.api.change_password(user.id, password_data)
            self.show_success(f"Password changed successfully for user '{user.username}'!")

        except Exception as e:
            self.show_error(f"Failed to change password: {str(e)}")

    def view_user_details(self, user):
        """View detailed user information."""
        details = self.get_item_details(user)
        details.append("")
        details.append("Press any key to continue...")
        self.show_message_box(details)

    # Convenience methods that delegate to base class methods
    def show_error(self, message):
        """Show an error message."""
        self.show_message(message, "error")

    def show_success(self, message):
        """Show a success message."""
        self.show_message(message, "success")

    def get_input(self, prompt, hide=False):
        """Get user input."""
        if hide:
            # For password input, we'll use a simple implementation
            # In a real implementation, you might want to use getpass or similar
            return self.prompt_input(prompt + " (hidden): ")
        return self.prompt_input(prompt)

    def confirm(self, message):
        """Confirm an action."""
        return self.confirm_action(message)

    def show_message_box(self, lines):
        """Show a message box with multiple lines."""
        message = "\n".join(lines)
        self.show_message(message, "info")


def run_interactive_users(config):
    """Run the interactive user management interface."""
    try:
        interface = UsersInteractive(config)
        interface.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error running interactive users: {e}")
