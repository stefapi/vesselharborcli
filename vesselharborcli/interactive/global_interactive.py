"""Global interactive interface for VesselHarbor CLI."""

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
from typing import List, Dict, Any, Optional

from ..orgs.organizations import get_APIorg
from ..environments.environments import get_APIenvironment
from .orgs import OrgsInteractive, run_interactive_orgs
from .environments import EnvironmentsInteractive, run_interactive_environments
from .base import InteractiveBase


class GlobalInteractive(InteractiveBase):
    """Global interactive interface for VesselHarbor CLI."""

    def __init__(self, config):
        """Initialize the interactive interface.

        Args:
            config: The application configuration.
        """
        super().__init__(config)
        self.mode = "selection"  # "selection", "orgs", "environments"
        self.items = [
            {"id": "orgs", "name": "Organizations", "description": "Manage organizations"},
            {"id": "environments", "name": "Environments", "description": "Manage environments"}
        ]

    def load_data(self):
        """Load data for the selection screen."""
        # Data is static for the selection screen
        pass

    def get_title(self):
        """Get the title for the interface."""
        return "VesselHarbor Interactive Mode"

    def get_commands(self):
        """Get the available commands."""
        commands = super().get_commands()
        return commands

    def format_list_item(self, item):
        """Format an item for display in the list."""
        return f"{item['name']}"

    def get_item_details(self, item):
        """Get details for an item."""
        details = [
            f"Name: {item['name']}",
            f"Description: {item['description']}",
            "",
            "Press Enter to select this option."
        ]
        return details

    def select_item(self):
        """Handle item selection."""
        if not self.items or not (0 <= self.selected_index < len(self.items)):
            return

        selected_item = self.items[self.selected_index]
        if selected_item["id"] == "orgs":
            self.cleanup()  # Clean up curses before switching
            run_interactive_orgs(self.config)
            self.running = False  # Exit after returning from the sub-interface
        elif selected_item["id"] == "environments":
            self.cleanup()  # Clean up curses before switching
            run_interactive_environments(self.config)
            self.running = False  # Exit after returning from the sub-interface

    def handle_command(self, key):
        """Handle a command key."""
        # No additional commands for the selection screen
        pass

    def show_help(self):
        """Show help information."""
        help_text = """
VesselHarbor Interactive Mode Help

This is the main selection screen for the interactive mode.
From here, you can select which type of resource to manage:

- Organizations: Manage your VesselHarbor organizations
- Environments: Manage your VesselHarbor environments

Navigation:
  Up/Down Arrow: Move selection
  Enter: Select option
  q: Quit
  ?: Show this help
        """
        self.show_message(help_text, "info")


def run_global_interactive(config):
    """Run the global interactive interface.

    Args:
        config: The application configuration.

    Returns:
        Exit code.
    """
    interface = GlobalInteractive(config)
    return interface.start()
