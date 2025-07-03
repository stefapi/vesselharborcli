"""Interactive interface for organizations."""

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

import curses
from typing import List, Dict, Any

from ..orgs.organizations import APIOrganization, Organization, OrganizationCreate, OrganizationUpdate, get_APIorg
from .base import InteractiveBase
from .environments import run_interactive_environments


class OrgsInteractive(InteractiveBase):
    """Interactive interface for organizations."""

    def __init__(self, config):
        """Initialize the interactive interface.

        Args:
            config: The application configuration.
        """
        super().__init__(config)
        self.api = get_APIorg(config)

    def load_data(self):
        """Load organizations from the API."""
        try:
            self.items = self.api.list_organizations()
        except Exception as e:
            self.show_message(f"Error loading organizations: {str(e)}", "error")
            self.items = []

    def get_title(self):
        """Get the title for the interface."""
        return "VesselHarbor Organizations"

    def get_commands(self):
        """Get the available commands."""
        commands = super().get_commands()
        commands.update({
            'e': 'Edit',
            'd': 'Delete',
            'v': 'View Environments',
            'r': 'Refresh',
            'b': 'Back to main menu',
        })

        # Only show create option for superadmins
        if self.api.token_manager.is_superadmin():
            commands['c'] = 'Create'

        return commands

    def format_list_item(self, item):
        """Format an organization for display in the list."""
        return f"{item.id}: {item.name}"

    def get_item_details(self, item):
        """Get details for an organization."""
        details = [
            f"ID: {item.id}",
            f"Name: {item.name}",
        ]

        if item.description:
            details.append(f"Description: {item.description}")

        # Add empty line
        details.append("")

        # Add available actions
        details.append("Actions:")
        details.append("  e: Edit organization")
        details.append("  d: Delete organization")
        details.append("  v: View environments")

        return details

    def select_item(self):
        """Handle organization selection."""
        # Currently just shows details, which are already visible
        pass

    def handle_command(self, key):
        """Handle a command key."""
        if key == ord('c'):
            # Only allow superadmins to create organizations
            if self.api.token_manager.is_superadmin():
                self.create_organization()
            else:
                self.show_message("Only superadmins can create organizations", "error")
        elif key == ord('e'):
            if self.items and 0 <= self.selected_index < len(self.items):
                self.edit_organization(self.items[self.selected_index])
        elif key == ord('d'):
            if self.items and 0 <= self.selected_index < len(self.items):
                self.delete_organization(self.items[self.selected_index])
        elif key == ord('v'):
            if self.items and 0 <= self.selected_index < len(self.items):
                self.view_environments(self.items[self.selected_index])
        elif key == ord('r'):
            self.load_data()
        elif key == ord('b'):
            # Return to main menu by ending this interface
            self.running = False

    def show_help(self):
        """Show help information."""
        help_text = """
Organization Interactive Mode Help

Navigation:
  Up/Down Arrow: Move selection
  Enter: Select organization
  q: Quit
  b: Back to main menu

Commands:
"""
        # Only show create option for superadmins
        if self.api.token_manager.is_superadmin():
            help_text += "  c: Create new organization\n"

        help_text += """  e: Edit selected organization
  d: Delete selected organization
  v: View environments for selected organization
  r: Refresh organization list
  ?: Show this help
        """
        self.show_message(help_text, "info")

    def create_organization(self):
        """Create a new organization."""
        name = self.prompt_input("Enter organization name: ")
        if not name:
            self.show_message("Organization name cannot be empty", "error")
            return

        description = self.prompt_input("Enter organization description (optional): ")

        try:
            new_org = self.api.create_organization(OrganizationCreate(
                name=name,
                description=description if description else None
            ))
            self.show_message(f"Organization '{name}' created successfully", "success")
            self.load_data()

            # Select the new organization
            for i, org in enumerate(self.items):
                if org.id == new_org.id:
                    self.selected_index = i
                    break
        except Exception as e:
            self.show_message(f"Error creating organization: {str(e)}", "error")

    def edit_organization(self, org):
        """Edit an organization.

        Args:
            org: The organization to edit.
        """
        name = self.prompt_input("Enter new organization name (leave empty to keep current): ", org.name)
        description = self.prompt_input("Enter new organization description (leave empty to keep current): ",
                                       org.description or "")

        try:
            updated_org = self.api.update_organization(
                org.id,
                OrganizationUpdate(
                    name=name,
                    description=description if description else None
                )
            )
            self.show_message(f"Organization updated successfully", "success")
            self.load_data()

            # Keep the same organization selected
            for i, o in enumerate(self.items):
                if o.id == org.id:
                    self.selected_index = i
                    break
        except Exception as e:
            self.show_message(f"Error updating organization: {str(e)}", "error")

    def delete_organization(self, org):
        """Delete an organization.

        Args:
            org: The organization to delete.
        """
        if not self.confirm_action(f"Are you sure you want to delete organization '{org.name}'?"):
            return

        try:
            self.api.delete_organization(org.id)
            self.show_message(f"Organization '{org.name}' deleted successfully", "success")

            # Update the list and adjust selection
            prev_index = self.selected_index
            self.load_data()
            if self.items:
                self.selected_index = min(prev_index, len(self.items) - 1)
        except Exception as e:
            self.show_message(f"Error deleting organization: {str(e)}", "error")

    def view_environments(self, org):
        """View environments for an organization.

        Args:
            org: The organization to view environments for.
        """
        # Clean up curses before switching to environments view
        self.cleanup()

        # Run the environments interactive interface with the selected organization
        run_interactive_environments(self.config, org.id, org.name)

        # Reinitialize curses for this interface
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.curs_set(0)  # Hide cursor
        self.screen.keypad(True)

        # Initialize color pairs
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Header/footer
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Selected item
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)    # Error message
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Success message
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Warning/info message

        # Refresh the data and screen
        self.load_data()
        self.draw_screen()


def run_interactive_orgs(config):
    """Run the interactive organizations interface.

    Args:
        config: The application configuration.

    Returns:
        Exit code.
    """
    interface = OrgsInteractive(config)
    return interface.start()
