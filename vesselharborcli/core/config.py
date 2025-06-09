#  Copyright (c) 2025.  VesselHarbor
#  ____   ____                          .__    ___ ___             ___.
#  \   \ /   /____   ______ ______ ____ |  |  /   |   \_____ ______\_ |__   ___________
#   \   Y   // __ \ /  ___//  ___// __ \|  | /    ~    \__  \\_  __ \ __ \ /  _ \_  __ \
#    \     /\  ___/ \___ \ \___ \\  ___/|  |_\    Y    // __ \|  | \/ \_\ (  <_> )  | \/
#     \___/  \___  >____  >____  >\___  >____/\___|_  /(____  /__|  |___  /\____/|__|
#                \/     \/     \/     \/            \/      \/          \/
#  MIT License
#

import os
import sys

from .settings import EnumSettings, AppSettings

_config = {}

def has_system():
    """
    **Summary:**
    The `has_system` function determines whether the current user has system-level
    privileges based on the operating system. It does so by checking specific
    conditions: for Windows, it attempts to read a restricted directory; for Unix-like
    systems, it checks the user's ID.

    **Details:**

    This function is useful for verifying administrative rights in cross-platform
    applications where different privilege verification methods are needed.
    """
    import getpass
    user = getpass.getuser()
    if sys.platform == 'win32':
        try:
            # only windows users with admin privileges can read the C:\windows\temp
            temp = os.listdir(os.sep.join([os.environ.get('SystemRoot','C:\\windows'),'temp']))
        except:
            return (user,False)
        else:
            return (user,True)
    else:
        if os.geteuid() < 1000:
            return (user,True)
        else:
            return (user,False)

def get_base_url():
    """Construct base URL from configuration."""
    if _config['application.socket']:
        return f"http://unix:{_config['application.socket']}"
    return f"http://{_config['application.ip_address']}:{_config['application.port']}"

def create_config(conf_file, args, params_link, default_config, devel = False):
    """
    Creates a configuration object based on the given parameters and environment.

    This function determines the execution environment, then creates an
    AppSettings instance using the provided parameters. The AppSettings instance
    can be used to configure an application accordingly.

    :param conf_file: Path to the main configuration file.
    :type conf_file: str

    :param args: Command-line arguments passed to the script.
    :type args: list[str]

    :param params_link: Link or path to additional parameter files.
    :type params_link: Union[str, List[str]]

    :param default_config: Default configuration settings.
    :type default_config: dict

    :param devel: Flag indicating if the application is running in development mode.
    :type devel: bool

    :return: An AppSettings instance configured for the current environment and parameters.
    :rtype: AppSettings
    """
    if devel == True:
        env = EnumSettings.Debug
    elif  os.path.exists("/.dockerenv"):
        env = EnumSettings.Docker
    else:
        sysrights = has_system()
        if sysrights[1]:
            env = EnumSettings.System
        else:
            env = EnumSettings.User

    global _config
    _config = AppSettings(env, conf_file, args, default_config, params_link)
    return _config

def get_config():
    return _config
