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
import re
import tempfile
import json
from pathlib import Path
from enum import Enum
from .appdirs import AppDirs
from .config_file import config_file

from ..version import __software__, __author__
import dotenv

settings = None

class EnumSettings(Enum):
    Debug = 0
    Docker = 1
    System = 2
    User = 3

class AppDirectories:
    def __init__(self, env: EnumSettings):
        """
        Create and manage application directories based on the environment.

        This class is responsible for setting up various directory paths used by
        the application. The directories are determined based on the provided
        environment settings. It ensures that all necessary directories exist
        and handles the creation of temporary directories if needed.

        :param env: EnumSettings, specifies the environment in which the
            application is running. This determines how the directories should be
            structured and where they should be located.
        """
        self.__appdirs = AppDirs(__software__, __author__)
        self.LIB_DIR = os.path.join(self.__appdirs.site_lib_dir)
        self.WEB_DIR = os.path.join(self.LIB_DIR, "client", "dist")
        self.SYSCONF_DIR = os.path.join(self.__appdirs.site_config_dir)

        if env == EnumSettings.Docker:
            self.DATA_DIR = os.path.expanduser("/app/data")
            self.LOG_DIR = os.path.join(self.DATA_DIR,"log")
            self.CONF_DIR = os.path.join(self.DATA_DIR,"conf")
        elif env == EnumSettings.Debug:
            self.DATA_DIR = os.path.join(self.__appdirs.site_lib_dir.parent,"dev","data")
            self.LOG_DIR = os.path.join(self.DATA_DIR,"log")
            self.CONF_DIR = os.path.join(self.DATA_DIR,"conf")
        elif env == EnumSettings.System:
            self.DATA_DIR = os.path.join(self.__appdirs.site_cache_dir)
            self.LOG_DIR = os.path.join(self.__appdirs.site_log_dir)
            self.CONF_DIR = os.path.join(self.__appdirs.site_config_dir)
        else:
            self.DATA_DIR = os.path.join(self.__appdirs.user_cache_dir)
            self.LOG_DIR = os.path.join(self.__appdirs.user_log_dir)
            self.CONF_DIR = os.path.join(self.__appdirs.user_config_dir)

        self.BACKUP_DIR = os.path.join(self.DATA_DIR,"backups")
        self.DEBUG_DIR = os.path.join(self.DATA_DIR,"debug")
        self.MIGRATION_DIR = os.path.join(self.DATA_DIR,"migration")
        self.TEMPLATE_DIR = os.path.join(self.DATA_DIR,"templates")
        self.USER_DIR = os.path.join(self.DATA_DIR,"users")
        if env in [EnumSettings.System, EnumSettings.User]:
            self.TEMP_DIR = os.path.join(tempfile.gettempdir(), __software__)
        else:
            self.TEMP_DIR = os.path.join(self.DATA_DIR,".temp")

        self.__ensure_directories(env == EnumSettings.System)

    def json(self, **kwargs):
        """
        Returns a JSON string representation of the object, excluding private app directories.

        This method converts the instance variables of the object into a dictionary, removes
        the `_AppDirectories__appdirs` key (which stores application directory paths), and then
        converts the resulting dictionary to a JSON string using the `json.dumps()` function. The
        `**kwargs` allows for additional parameters to be passed directly to `json.dumps()`.

        :param kwargs: Additional keyword arguments to pass to :func:`json.dumps`.
                       See the `json.dumps() <https://docs.python.org/3/library/json.html#json.dumps>`_
                       documentation for details.

        :return: A JSON string representation of the object, excluding the `_AppDirectories__appdirs`
                 key.
        :type kwargs: dict

        """
        var = vars(self)
        del var["_AppDirectories__appdirs"]
        return json.dumps(var, **kwargs)

    def __ensure_directories(self, system=False):
        """
        Ensure that the necessary directories are created. This method checks whether certain directories exist and creates them if they do not.

        :param system: A flag indicating whether to use system-specific directory paths.
                       Default is False, which means standard directories will be used.
        :type system: bool

        :return: None
        """
        required_system_dirs = [
            self.BACKUP_DIR,
            self.DATA_DIR,
            self.DEBUG_DIR,
            self.LOG_DIR,
            self.MIGRATION_DIR,
            self.TEMPLATE_DIR,
            self.TEMP_DIR,
            self.USER_DIR,
        ]

        required_std_dirs = [
            self.BACKUP_DIR,
            self.CONF_DIR,
            self.DATA_DIR,
            self.DEBUG_DIR,
            self.LOG_DIR,
            self.MIGRATION_DIR,
            self.TEMPLATE_DIR,
            self.TEMP_DIR,
            self.USER_DIR,
        ]
        required_dirs = required_system_dirs if system else required_std_dirs
        for dir in required_dirs:
            Path(dir).mkdir(parents=True, exist_ok=True)

class AppSettings():
    def __init__(self, type : EnumSettings, conf_file, args, default_config, params_link):
        """
        Initializes the Config object with configuration settings.

        This constructor sets up the configuration by loading default and user-defined settings from various sources such as environment variables, configuration files, and command-line arguments. It initializes paths for different directories based on the type of settings (system or user). Additionally, it loads environment variables from a `.env` file if the setting type is neither system nor user.

        :param type: An enumeration value indicating the type of settings (EnumSettings).
        :type type: EnumSettings

        :param conf_file: Optional path to a specific configuration file. If not provided, default paths will be used.
        :type conf_file: str or None

        :param args: Command-line arguments passed to the application. These can override other configurations.
        :type args: argparse.Namespace

        :param default_config: A dictionary containing the default configuration settings.
        :type default_config: dict

        :param params_link: Optional parameter link for additional configuration data.
        :type params_link: Any or None

        :raises TypeError: If `type` is not an instance of EnumSettings.

        :returns: A new instance of Config object with initialized settings and configurations.
        :rtype: Config
        """
        self.default_config = default_config
        self.config = default_config.copy()
        self.params_link = params_link
        self.path = AppDirectories(type)
        self.args = args

        if type != EnumSettings.System and type != EnumSettings.User:
            dotenv.load_dotenv(Path(self.path.LIB_DIR).parent.joinpath(".env"))

        if conf_file is not None:
            self.etc_conf = config_file(default_config, conf_file)
            self.local_conf = None
        else:
            self.etc_conf = config_file(default_config, os.path.join(self.path.SYSCONF_DIR, "config.toml"))
            self.local_conf = config_file(default_config, os.path.join(self.path.CONF_DIR, "config.toml"))
        self.env_list = os.environ.copy()

        self.config_calc()
        self.config.confDir = self.local_conf.confDir
        self.config.confFile = self.local_conf.confFile

    def __getitem__(self, key):
        return self.config.get(*key.split('.'))

    def __setitem__(self, key, value):
        return self.config.set_modify(value, *key.split('.'))

    def __delitem__(self, key, value):
        return self.config.delete(*key.split('.'))

    def __contains__(self, key):
        return self.config.has(*key.split('.'))

    def __iter__(self):
        return iter(self.config)

    def __next__(self):
        val = self.config.enumerate()

    def json(self, indent = 4, internal = False):
        """
        Return a JSON string representation of the configuration.

        This method creates a deep copy of the current configuration and
        applies certain modifications based on the provided arguments.
        The resulting configuration is then serialized into a JSON string.

        :param indent: The indentation level for the JSON output. Defaults to 4.
        :type indent: int

        :param internal: A flag indicating whether to apply internal overrides.
                         Defaults to False.
        :type internal: bool

        :return: A JSON string representation of the modified configuration.
        :rtype: str
        """
        import copy
        conf = copy.deepcopy(self.config)
        def get(args):
            return conf.get(*args)
        conf.override(get, internal)
        return json.dumps(conf.config, indent=indent)

    def config_calc(self):
        """
        Configures the application by merging and overriding parameters from various sources.

        This method sets default parameters using a configuration file,
        then applies environment variables, .env parameters, etc configuration files,
        local configuration files, and finally command-line options.
        The resulting configuration is stored in `self.config`.

        .. note::

            This method does not return anything. It modifies the instance's
            `self.config` attribute.

        """
        # set default parameters
        params = config_file(self.default_config, 'None')

        def get_environ(options):
            path = None
            for items in list(options):
                path = items if path == None else path+'.'+items
            if path in self.params_link:
                environ = self.params_link[path][1]
                if environ is not None:
                    environ = environ.upper()
                    if environ in self.env_list:
                        return self.env_list[environ]
            return None

        # apply environment variables
        params.override(get_environ, True)

        def get_dotenv(options):
            path = None
            for items in options:
                path = items if path == None else path+'.'+items
            if path in self.params_link:
                environ = self.params_link[path][2]
                if environ is not None:
                    environ = environ.upper()
                    if environ in self.env_list:
                        return self.env_list[environ]
            return None

        # apply .env parameters
        params.override(get_dotenv, True)

        # override with etc configuration file if any
        params.override(self.etc_conf.get_config, True)

        # override with local configuration file if any
        if self.local_conf is not None:
            params.override(self.local_conf.get_config, True)

        def get_option(options):
            path = None
            for items in options:
                path = items if path == None else path+'.'+items
            if path in self.params_link:
                option = self.params_link[path][0]
                if option is not None:
                    match = re.findall(r"^([^\[\]]+)(\[([0-9]+)\])?$", option)
                    if len(match) == 0:
                        return None
                    if hasattr(self.args, match[0][0]):
                        if len(match[0][1]) == 0:
                            return getattr(self.args, match[0][0])
                        else:
                            arg = getattr(self.args, match[0][0])
                            if isinstance(arg, list):
                                return arg[int(match[0][2])]
            return None

        # apply command line options
        params.override(get_option, True)
        self.config = params

    def writeto(self, filename, with_internal=False):
        """
        The writeto function writes the configuration to a file.
        It does not write the internal data, only what is visible to the user.

        :param self: Reference the object itself
        :param filename: Specify the file to write to
        :param with_internal: Determine if the internal data should be written to file
        :return: `none`
        """
        if not with_internal:
            data = self.config.filter_internal()
        else:
            data = self.config
        data.writeto(filename)

    def write(self, with_internal = False):
        """
        The write function writes the configuration to a file.
        It does not write the internal data, only what is visible to the user.

        :param self: Reference the object itself
        :param with_internal: Determine if the internal data should be written to file
        :return: `none`
        """
        if not with_internal:
            data = self.config.filter_internal()
        else:
            data = self.config
        data.write()


    def set(self):
        global settings

        settings = self
        pass

