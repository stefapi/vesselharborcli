"""Interactive service for VesselHarbor CLI."""

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

from .service import svc_class
from .version import __software__
from .core.config import get_config
from .interactive.global_interactive import run_global_interactive

class interactive_services(svc_class):
    """Service class for interactive mode."""

    default_config = {
    }

    params_link = {
    }

    def __init__(self):
        pass

    @staticmethod
    def subparser():
        return ("interactive", f"Interactive {__software__} management")

    @staticmethod
    def params(parser):
        # No subcommands needed for interactive mode
        parser.set_defaults(func='run_interactive')

    @staticmethod
    def test_name(name):
        return name == __software__ + 'interactive'

    @staticmethod
    def cmd_name(name):
        return name == 'interactive'

    def run(self):
        config = get_config()
        return run_global_interactive(config)
