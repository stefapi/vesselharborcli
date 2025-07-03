"""Interactive interface for environments."""

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

import curses
from typing import List, Dict, Any

from ..environments.environments import APIEnvironment, Environment, EnvironmentCreate, EnvironmentUpdate, get_APIenvironment
from .base import InteractiveBase


class EnvironmentsInteractive(InteractiveBase):
    """Interactive interface for environments."""

    def __init__(self, config, organization_id=None, organization_name=None):
        """Initialize the interactive interface.

        Args:
            config: The application configuration.
            organization_id: The ID of the organization to show environments for.
            organization_name: The name of the organization (for display purposes).
        """
        super().__init__(config)
        self.api = get_APIenvironment(config)
        self.organization_id = organization_id
        self.organization_name = organization_name

    def load_data(self):
        """Load environments from the API."""
        if not self.organization_id:
            self.show_message("No organization selected", "error")
            self.items = []
            return

        try:
            self.items = self.api.list_environments(self.organization_id)
        except Exception as e:
            self.show_message(f"Error loading environments: {str(e)}", "error")
            self.items = []

    def get_title(self):
        """Get the title for the interface."""
        if self.organization_name:
            return f"VesselHarbor Environments - Organization: {self.organization_name}"
        return "VesselHarbor Environments"

    def get_commands(self):
        """Get the available commands."""
        commands = super().get_commands()
        commands.update({
            'c': 'Create',
            'e': 'Edit',
            'd': 'Delete',
            'r': 'Refresh',
            'b': 'Back to organizations',
        })
        return commands

    def format_list_item(self, item):
        """Format an environment for display in the list."""
        # If we're showing environments for a specific organization, no need to repeat the org name
        if self.organization_name:
            return f"{item.id}: {item.name}"
        # Otherwise, show the organization ID if available
        elif hasattr(item, 'organization_id'):
            return f"{item.id}: {item.name} (Org: {item.organization_id})"
        else:
            return f"{item.id}: {item.name}"

    def get_item_details(self, item):
        """Get details for an environment."""
        details = [
            f"ID: {item.id}",
            f"Name: {item.name}",
        ]

        if item.description:
            details.append(f"Description: {item.description}")

        # Show organization information
        if self.organization_name:
            details.append(f"Organization: {self.organization_name}")
        elif hasattr(item, 'organization_id'):
            details.append(f"Organization ID: {item.organization_id}")

        # Add empty line
        details.append("")

        # Add available actions
        details.append("Actions:")
        details.append("  e: Edit environment")
        details.append("  d: Delete environment")

        return details

    def select_item(self):
        """Handle environment selection."""
        # Currently just shows details, which are already visible
        pass

    def handle_command(self, key):
        """Handle a command key."""
        if key == ord('c'):
            self.create_environment()
        elif key == ord('e'):
            if self.items and 0 <= self.selected_index < len(self.items):
                self.edit_environment(self.items[self.selected_index])
        elif key == ord('d'):
            if self.items and 0 <= self.selected_index < len(self.items):
                self.delete_environment(self.items[self.selected_index])
        elif key == ord('r'):
            self.load_data()
        elif key == ord('b'):
            # Return to organizations menu by ending this interface
            self.running = False

    def show_help(self):
        """Show help information."""
        help_text = """
Environment Interactive Mode Help

Environments are subitems of an organization. Each environment belongs to a specific organization.

Navigation:
  Up/Down Arrow: Move selection
  Enter: Select environment
  q: Quit
  b: Back to organizations

Commands:
  c: Create new environment in the current organization
  e: Edit selected environment
  d: Delete selected environment
  r: Refresh environment list
  ?: Show this help
        """
        self.show_message(help_text, "info")

    def create_environment(self):
        """Create a new environment."""
        if not self.organization_id:
            self.show_message("No organization selected", "error")
            return

        name = self.prompt_input("Enter environment name: ")
        if not name:
            self.show_message("Environment name cannot be empty", "error")
            return

        description = self.prompt_input("Enter environment description (optional): ")

        try:
            new_environment = self.api.create_environment(EnvironmentCreate(
                name=name,
                description=description if description else None,
                organization_id=self.organization_id
            ))
            self.show_message(f"Environment '{name}' created successfully", "success")
            self.load_data()

            # Select the new environment
            for i, environment in enumerate(self.items):
                if environment.id == new_environment.id:
                    self.selected_index = i
                    break
        except Exception as e:
            self.show_message(f"Error creating environment: {str(e)}", "error")

    def edit_environment(self, environment):
        """Edit an environment.

        Args:
            environment: The environment to edit.
        """
        if not self.organization_id:
            self.show_message("No organization selected", "error")
            return

        name = self.prompt_input("Enter new environment name (leave empty to keep current): ", environment.name)
        description = self.prompt_input("Enter new environment description (leave empty to keep current): ",
                                       environment.description or "")

        try:
            updated_environment = self.api.update_environment(
                self.organization_id,
                environment.id,
                EnvironmentUpdate(
                    name=name,
                    description=description if description else None,
                    organization_id=self.organization_id
                )
            )
            self.show_message(f"Environment updated successfully", "success")
            self.load_data()

            # Keep the same environment selected
            for i, e in enumerate(self.items):
                if e.id == environment.id:
                    self.selected_index = i
                    break
        except Exception as e:
            self.show_message(f"Error updating environment: {str(e)}", "error")

    def delete_environment(self, environment):
        """Delete an environment.

        Args:
            environment: The environment to delete.
        """
        if not self.organization_id:
            self.show_message("No organization selected", "error")
            return

        if not self.confirm_action(f"Are you sure you want to delete environment '{environment.name}'?"):
            return

        try:
            self.api.delete_environment(self.organization_id, environment.id)
            self.show_message(f"Environment '{environment.name}' deleted successfully", "success")

            # Update the list and adjust selection
            prev_index = self.selected_index
            self.load_data()
            if self.items:
                self.selected_index = min(prev_index, len(self.items) - 1)
        except Exception as e:
            self.show_message(f"Error deleting environment: {str(e)}", "error")


def run_interactive_environments(config, organization_id=None, organization_name=None):
    """Run the interactive environments interface.

    Args:
        config: The application configuration.
        organization_id: The ID of the organization to show environments for.
        organization_name: The name of the organization (for display purposes).

    Returns:
        Exit code.
    """
    interface = EnvironmentsInteractive(config, organization_id, organization_name)
    return interface.start()
