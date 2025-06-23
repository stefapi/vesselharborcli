"""Base class for interactive interfaces."""

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
import sys
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Callable

class InteractiveBase(ABC):
    """Base class for interactive interfaces."""

    def __init__(self, config):
        """Initialize the interactive interface.

        Args:
            config: The application configuration.
        """
        self.config = config
        self.screen = None
        self.items = []
        self.selected_index = 0
        self.top_index = 0
        self.max_items_visible = 0
        self.header_lines = 3
        self.footer_lines = 2
        self.detail_width = 50
        self.running = True
        self.message = ""
        self.message_type = "info"  # "info", "error", "success"

    def start(self):
        """Start the interactive interface."""
        #try:
        if True:
            # Initialize curses
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

            # Load initial data
            self.load_data()

            # Main loop
            self.main_loop()
        #except Exception as e:
        #    self.cleanup()
        #    print(f"Error: {str(e)}", file=sys.stderr)
        #    return 1
        #finally:
        #    self.cleanup()

            return 0

    def cleanup(self):
        """Clean up curses settings."""
        if self.screen:
            self.screen.keypad(False)
            curses.nocbreak()
            curses.echo()
            curses.endwin()

    def main_loop(self):
        """Main loop for the interactive interface."""
        while self.running:
            self.draw_screen()
            self.handle_input()

    def draw_screen(self):
        """Draw the screen."""
        self.screen.clear()
        height, width = self.screen.getmaxyx()

        # Calculate dimensions
        list_width = width - self.detail_width
        self.max_items_visible = height - self.header_lines - self.footer_lines

        # Draw header
        self.draw_header()

        # Draw list panel
        self.draw_list_panel(list_width)

        # Draw detail panel
        self.draw_detail_panel(list_width)

        # Draw footer
        self.draw_footer()

        # Draw message if any
        if self.message:
            self.draw_message()

        self.screen.refresh()

    def draw_header(self):
        """Draw the header."""
        height, width = self.screen.getmaxyx()
        header_attr = curses.color_pair(1)

        for i in range(self.header_lines):
            self.screen.addstr(i, 0, " " * (width - 1), header_attr)

        title = self.get_title()
        self.screen.addstr(1, (width - len(title)) // 2, title, header_attr)

        # Add help text
        help_text = "Use ↑/↓ to navigate, Enter to select, q to quit, ? for help"
        self.screen.addstr(2, 2, help_text, header_attr)

    def draw_footer(self):
        """Draw the footer."""
        height, width = self.screen.getmaxyx()
        footer_attr = curses.color_pair(1)

        for i in range(self.footer_lines):
            self.screen.addstr(height - self.footer_lines + i, 0, " " * (width - 1), footer_attr)

        # Add status
        status_text = f"Total items: {len(self.items)}"
        self.screen.addstr(height - 2, 2, status_text, footer_attr)

        # Add commands
        commands = self.get_commands()
        commands_text = " | ".join([f"{key}: {desc}" for key, desc in commands.items()])
        max_cmd_len = width - 4
        if len(commands_text) > max_cmd_len:
            commands_text = commands_text[:max_cmd_len - 3] + "..."
        self.screen.addstr(height - 1, 2, commands_text, footer_attr)

    def draw_list_panel(self, list_width):
        """Draw the list panel.

        Args:
            list_width: Width of the list panel.
        """
        height, _ = self.screen.getmaxyx()
        list_height = height - self.header_lines - self.footer_lines

        # Draw items
        for i in range(min(list_height, len(self.items))):
            item_index = self.top_index + i
            if item_index < len(self.items):
                item = self.items[item_index]
                item_str = self.format_list_item(item)

                # Truncate if necessary
                if len(item_str) > list_width - 2:
                    item_str = item_str[:list_width - 5] + "..."

                # Pad with spaces
                item_str = item_str + " " * (list_width - len(item_str) - 2)

                # Highlight selected item
                if item_index == self.selected_index:
                    self.screen.addstr(i + self.header_lines, 1, item_str, curses.color_pair(2))
                else:
                    self.screen.addstr(i + self.header_lines, 1, item_str)

    def draw_detail_panel(self, list_width):
        """Draw the detail panel.

        Args:
            list_width: Width of the list panel (to calculate position).
        """
        height, width = self.screen.getmaxyx()
        detail_height = height - self.header_lines - self.footer_lines

        # Draw vertical separator
        for i in range(detail_height):
            self.screen.addstr(i + self.header_lines, list_width, "│")

        # Draw details if an item is selected
        if self.items and 0 <= self.selected_index < len(self.items):
            selected_item = self.items[self.selected_index]
            details = self.get_item_details(selected_item)

            for i, line in enumerate(details):
                if i < detail_height:
                    # Truncate if necessary
                    if len(line) > self.detail_width - 2:
                        line = line[:self.detail_width - 5] + "..."

                    self.screen.addstr(i + self.header_lines, list_width + 2, line)

    def draw_message(self):
        """Draw a message box."""
        height, width = self.screen.getmaxyx()

        # Determine message color
        if self.message_type == "error":
            msg_attr = curses.color_pair(3)
        elif self.message_type == "success":
            msg_attr = curses.color_pair(4)
        else:  # info or default
            msg_attr = curses.color_pair(5)

        # Calculate message box dimensions
        msg_lines = self.message.split("\n")
        msg_height = len(msg_lines) + 2
        msg_width = max(len(line) for line in msg_lines) + 4

        # Center the message box
        start_y = (height - msg_height) // 2
        start_x = (width - msg_width) // 2

        # Draw box
        for i in range(msg_height):
            if start_y + i < height:
                self.screen.addstr(start_y + i, start_x, " " * (msg_width - 1), msg_attr)

        # Draw message
        for i, line in enumerate(msg_lines):
            if start_y + i + 1 < height:
                self.screen.addstr(start_y + i + 1, start_x + 2, line, msg_attr)

    def handle_input(self):
        """Handle user input."""
        key = self.screen.getch()

        if key == ord('q'):
            self.running = False
        elif key == curses.KEY_UP:
            self.move_selection(-1)
        elif key == curses.KEY_DOWN:
            self.move_selection(1)
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            self.select_item()
        elif key == ord('?'):
            self.show_help()
        else:
            # Handle custom commands
            self.handle_command(key)

    def move_selection(self, direction):
        """Move the selection up or down.

        Args:
            direction: -1 for up, 1 for down.
        """
        if not self.items:
            return

        new_index = self.selected_index + direction
        if 0 <= new_index < len(self.items):
            self.selected_index = new_index

            # Adjust view if selection is out of visible area
            if self.selected_index < self.top_index:
                self.top_index = self.selected_index
            elif self.selected_index >= self.top_index + self.max_items_visible:
                self.top_index = self.selected_index - self.max_items_visible + 1

    def show_message(self, message, message_type="info"):
        """Show a message.

        Args:
            message: The message to show.
            message_type: The type of message ("info", "error", "success").

        The message will be displayed for a maximum of 4 seconds or until any key is pressed.
        """
        # Save the message but don't display it yet
        self.message = ""
        self.message_type = message_type

        # First draw and refresh the screen without the message
        self.draw_screen()

        # Now set the message and draw it
        self.message = message
        self.draw_message()
        self.screen.refresh()

        # Set timeout to 4 seconds (4000 milliseconds)
        self.screen.timeout(4000)
        self.screen.getch()  # Wait for any key or timeout

        # Reset timeout to blocking mode
        self.screen.timeout(-1)
        self.message = ""

    def prompt_input(self, prompt, default=""):
        """Prompt for user input.

        Args:
            prompt: The prompt to display.
            default: Default value.

        Returns:
            The user input.
        """
        height, width = self.screen.getmaxyx()

        # Save current cursor state
        curses.curs_set(1)  # Show cursor

        # Clear the footer area
        for i in range(self.footer_lines):
            self.screen.addstr(height - self.footer_lines + i, 0, " " * (width - 1))

        # Show prompt
        self.screen.addstr(height - 2, 2, prompt)
        self.screen.addstr(height - 2, 2 + len(prompt) + 1, default)
        self.screen.refresh()

        # Get input
        curses.echo()
        input_str = ""
        try:
            input_str = self.screen.getstr(height - 2, 2 + len(prompt) + 1, 100).decode('utf-8')
        except Exception:
            input_str = default

        # Restore cursor state and echo
        curses.noecho()
        curses.curs_set(0)  # Hide cursor

        return input_str if input_str else default

    def confirm_action(self, message):
        """Confirm an action.

        Args:
            message: The confirmation message.

        Returns:
            True if confirmed, False otherwise.
        """
        height, width = self.screen.getmaxyx()

        # Clear the footer area
        for i in range(self.footer_lines):
            self.screen.addstr(height - self.footer_lines + i, 0, " " * (width - 1))

        # Show message
        self.screen.addstr(height - 2, 2, f"{message} (y/n)")
        self.screen.refresh()

        # Get input
        while True:
            key = self.screen.getch()
            if key in (ord('y'), ord('Y')):
                return True
            elif key in (ord('n'), ord('N')):
                return False

    @abstractmethod
    def load_data(self):
        """Load data from the API."""
        pass

    @abstractmethod
    def get_title(self):
        """Get the title for the interface."""
        pass

    @abstractmethod
    def get_commands(self):
        """Get the available commands.

        Returns:
            A dictionary mapping command keys to descriptions.
        """
        return {
            'q': 'Quit',
            '?': 'Help',
        }

    @abstractmethod
    def format_list_item(self, item):
        """Format an item for display in the list.

        Args:
            item: The item to format.

        Returns:
            A string representation of the item.
        """
        pass

    @abstractmethod
    def get_item_details(self, item):
        """Get details for an item.

        Args:
            item: The item to get details for.

        Returns:
            A list of strings with the item details.
        """
        pass

    @abstractmethod
    def select_item(self):
        """Handle item selection."""
        pass

    @abstractmethod
    def handle_command(self, key):
        """Handle a command key.

        Args:
            key: The key code.
        """
        pass

    @abstractmethod
    def show_help(self):
        """Show help information."""
        pass
