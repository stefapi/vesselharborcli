#  Copyright (c) 2025.  VesselHarbor
#  ____   ____                          .__    ___ ___             ___.
#  \   \ /   /____   ______ ______ ____ |  |  /   |   \_____ ______\_ |__   ___________
#   \   Y   // __ \ /  ___//  ___// __ \|  | /    ~    \__  \\_  __ \ __ \ /  _ \_  __ \
#    \     /\  ___/ \___ \ \___ \\  ___/|  |_\    Y    // __ \|  | \/ \_\ (  <_> )  | \/
#     \___/  \___  >____  >____  >\___  >____/\___|_  /(____  /__|  |___  /\____/|__|
#                \/     \/     \/     \/            \/      \/          \/
#  MIT License
#

import json
import os
from copy import copy
from pathlib import Path

import tomllib
import tomli_w

from .type_conv import to_type

class config_file():

    def __init__(self, default_config, file_name = "none"):
        """ On init, read the saved configuration file if exists which is stored in $HOME directory as .(app_name)
        if the file does not exists, the default configuration defined in this class is used.
        special cases:
        * if a parameter is defined in internal section, this parameter is never exported or defined if not explicitly
        defined by the user or the application. Most of the time this is used for internal purpose, debug or non disclosed
        functionalities
        * if a parameter is defined as <>, it's considered as a template parameter. It's convenient if for example you have to configure
        several items with the same structure. for example: account definitions, remote servers definitions ...
        Conformity of each element (section, setting, subsetting and type) is compared with the default configuration. If not compatible, the value is rejected silently
        TODO: No version management of the configuration file implemented so far.


        :param app_name:  the name of the application. this is used to define the name of parameter file
        :type app_name: str
        :param app_author:  the author of the application. This is used to define the path of the software.
        :type app_author: str
        :param default_config:  a recursive dictionary containing the configuration
        :type default_config: dictionary
        :param scope: the scope of configuration file: 'data', 'etc', 'local', 'path'
        :type scope: str
        :param file_name:  the name of the configuration file. default as 'conf.ini'
        :type file_name: str
        """

        self.default_config = default_config
        self.config = None
        if file_name != "none":
            self.confDir = Path(file_name).parent
            self.confFile = file_name
        else:
            self.confDir = None
            self.confFile = None

        if self.confFile is not None and os.path.isfile(self.confFile):
            with open(self.confFile, "rb") as f:
                readconfig = tomllib.load(f)
            self.new = False
        else:
            readconfig = {}
            self.new = True
        # normalize configuration
        # or create a new config structure based on default_config structure

        def get_elem(elem_list):
            if readconfig is None:
                return None
            cur_conf= None
            cur_subconf = readconfig
            for elem in elem_list:
                cur_conf = cur_subconf
                cur_subconf = cur_conf.get(elem)
                if cur_subconf is None:
                    # elem is not present in the configuration
                    return None
            if cur_conf is None:
                return None
            return cur_subconf

        self.override(get_elem)


    @staticmethod
    def level_treat(old_config, ref_config, item_getter, options, with_internal):
        """
        Treats the old configuration based on reference configuration.

        Iterates over the sections in the reference configuration and applies
        settings to create a new configuration. If the section exists in the
        old configuration, its settings are used as default values.

        :param old_config: Dictionary representing the old configuration.
        :type old_config: dict or None

        :param ref_config: Reference configuration that defines how to treat
                           sections from the old config.
        :type ref_config: dict

        :param item_getter: Function to retrieve section data based on options.
        :type item_getter: callable

        :param options: List of options to pass to the item getter function.
        :type options: list[str]

        :param with_internal: Boolean flag indicating if internal sections should
                              be included in processing.
        :type with_internal: bool

        :return: New configuration dictionary after treatment.
        :rtype: dict
        """
        new_config = {}
        genericEnv = False
        if "<>" in ref_config and len(ref_config) == 1:
            ref_section = set([] if old_config is None else old_config.keys())
            item_dict = item_getter(options)
            ref_section = list(ref_section | set([] if item_dict is None else item_dict.keys()))
            genericEnv = True
        else:
            ref_section = ref_config.keys()
        for section in ref_section:
            if old_config is not None and section in old_config:
                config_section = old_config[section]
            else:
                config_section = None

            if genericEnv:
                settings = ref_config["<>"]
            else:
                settings = ref_config[section]

            if not isinstance(settings, dict):
                if with_internal or section != 'internal':
                    val = item_getter(options + [section])
                    if val is None:
                        if config_section is not None:
                            new_config[section] = to_type(settings, config_section)
                    else:
                        new_config[section] =  to_type(settings, val)
            else:
                if with_internal or section != 'internal':
                    results = config_file.level_treat(config_section, settings, item_getter, options + [section], with_internal)
                    if len(results) != 0:
                        new_config[section] = results
        return new_config

    def override(self, item_getter=None, with_internal=False):
        """
        The override function is used to override the current config with values from the injected_config.
        The override function takes a getter function as an argument, which is used to retrieve the value of a setting in injected_config.
        If no override function is given,it is assumed that item_getter is from config_file

        :param self: Access variables that belong to the class
        :param item_getter=None: Retrieve the value of a setting in injected_config
        :param with_internal=False: Ignore the internal section
        :return: A dictionary with the new configuration
        """

        #replace with the new configuration calculated
        self.config = config_file.level_treat(self.config, self.default_config, item_getter, [], with_internal)

    @staticmethod
    def __get_elem_generic(ref, config, options):
        """
        The __get_elem_generic function is a recursive function that takes three arguments:
        ref, config, and options. The ref argument is the reference to the configuration data.
        The config argument is a dictionary of dictionaries containing all of the sections in
        the configuration file with their respective keys and values. The options argument is
        a list of dictionary keys.

        :param ref: Store the configuration template
        :param config: Store the configuration data
        :param options: Specify the section and subsection of the config file that is being searched
        :return: A value from the configuration file
        """
        cur_ref = ref
        cur_config = config
        treated = []
        for elem in options:
            treated.append(elem)
            if len(cur_ref) == 1 and "<>" in cur_ref:
                ref_section = "<>"
            else:
                ref_section =elem
            if ref_section not in cur_ref:
                raise ConfigException(treated)
            if elem not in cur_config:
                return None
            cur_ref = cur_ref[ref_section]
            cur_config = cur_config[elem]
        return cur_config

    def get_default(self, *args):
        """
        The get_default function returns the default value for a setting of a section.
        If the setting is a dictionary, it returns the dictionary. You may indicated
        a subsetting in order to obtain the value from the dictionary stored in
        the setting:

        :param self: Access the class attributes
        :param *args: Pass a variable number of arguments to a function
        :return: The default value for a setting of a section
        """
        return copy(config_file.__get_elem_generic(self.default_config, self.default_config, args))

    def get_config(self, *args):
        """
        The get_config function is used to get the value of a setting or subsetting.
        If no value is stored, the default value is returned.
        You may indicated a subsetting in order to obtain the value from the dictionary stored in the setting

        :param self: Reference the current instance of the class
        :param *args: Pass a variable number of arguments to a function
        :return: The value of the setting or subsetting
        """
        if len(args) == 1 and isinstance(args[0], list):
            args = tuple(args[0])
        return config_file.__get_elem_generic(self.default_config, self.config, args)

    def get(self, *args):
        """
        The get function returns the value of a config option.

        :param self: Access variables that belongs to the class
        :param *args: Pass a variable number of arguments to a function
        :return: The value of the key that is passed as an argument
        """
        ret = self.get_config(*args)
        if ret is None:
            return self.get_default(*args)
        return ret

    def set_modify(self, value, *args):
        """
        The set_modify function is used to set a value in the configuration file.
        The value to be set (value). This can be any type of data, but it must match the type of data that is expected for this key. For example, if a key expects

        :param self: Reference the class instance
        :param value: Set the value of the key in the configuration file
        :param *args: Pass a variable number of arguments to a function
        :return: The value written
        """

        cur_ref = self.default_config
        cur_config = self.config
        old_config = None
        treated = []
        for elem in args:
            treated.append(elem)
            if len(cur_ref) == 1 and "<>" in cur_ref:
                ref_section = "<>"
            else:
                ref_section =elem
            if ref_section not in cur_ref:
                raise ConfigException(treated)
            if elem not in cur_config:
                cur_config[elem] = {}
            cur_ref = cur_ref[ref_section]
            old_config = cur_config
            cur_config = cur_config[elem]
        if old_config is not None:
            old_config[elem] = value
        return value

    def set_default(self, *args):
        """
        The set_default function is used to set the default value for a setting from a section. This is particularly useful for a setting based on a template in order to define the default values

        :param self: Access the attributes and methods of the class
        :param *args: Pass a variable number of arguments to select configuration element
        :return: The default value for a setting from a section
        """
        self.set_modify(self.get_default(*args), *args)

    def has(self, *args):
        """
        The has function checks if a setting is defined in the configuration.
        It can be used to check if a section exists or not, and it can also be used
        to check for specific settings within a section.

        :param self: Reference a class instance inside the class
        :param *args: Pass a non-keyworded, variable-length argument list
        :return: True if the setting is defined, false otherwise
        """

        cur_ref = self.default_config
        cur_config = self.config
        treated = []
        for elem in args:
            treated.append(elem)
            if len(cur_ref) == 1 and "<>" in cur_ref:
                ref_section = "<>"
            else:
                ref_section =elem
            if ref_section not in cur_ref:
                raise ConfigException(treated)
            if elem not in cur_config:
                return False
            cur_ref = cur_ref[ref_section]
            cur_config = cur_config[elem]
        return True

    def delete(self, *args):
        """
        Delete a specific setting of a section.

        The delete function is used to delete a specific setting of a section. This is useful when a setting is defined based on a template setting. The function raises an exception if the section and/or settings are not defined.

        :param args: Variable length argument list.
                    *section* : Section in which to delete the setting (str)
                    *setting* : Setting to be deleted (str)

        :return: Returns True if the setting was successfully deleted, False otherwise (bool).

        :raises config_exception: If a section or setting is not defined.

        :Example:

        .. code-block:: python

            # Assuming `config` is an instance of some class that implements this method
            success = config.delete("my_section", "my_setting")
        """

        cur_ref = self.default_config
        cur_config = self.config
        treated = []
        old_config = None
        for elem in args:
            treated.append(elem)
            if len(cur_ref) == 1 and "<>" in cur_ref:
                ref_section = "<>"
            else:
                ref_section =elem
            if ref_section not in cur_ref:
                raise ConfigException(treated)
            if elem not in cur_config:
                return False
            cur_ref = cur_ref[ref_section]
            old_config = cur_config
            cur_config = cur_config[elem]
        if old_config is not None:
            del old_config[elem]
            return True
        return False

    def filter_internal(self):
        """
        Filter internal configuration.

        This method is responsible for removing any 'internal' keys from a
        configuration dictionary. It uses recursion to traverse through all nested
        dictionaries and remove the specified key if found.

        :return:
            A new configuration object with 'internal' keys removed.
        """

        def filter_internal_recur(value):
            new_config = {}
            for section, value in value.items():
                if not isinstance(value, dict):
                    if section != 'internal':
                        new_config[section] = value
                else:
                    if section != 'internal':
                        results =  filter_internal_recur(value)
                        if len(results) != 0:
                            new_config[section] = results
            return new_config

        newconf= config_file(self.default_config)
        newconf.confDir = self.confDir
        newconf.confFile = self.confFile
        newconf.config = filter_internal_recur(self.config)
        return newconf

    def write(self) -> None:

        """
            Write configuration data to the specified directory.

            This function checks if a configuration directory is set. If it is, it ensures that the directory exists.
            If the directory does not exist, it creates one. After confirming or creating the directory,
            it writes the configuration file using an internal method.

            :returns:
                The result of the `writeto` method for the configuration file.

            .. note:: If no configuration directory is set, this function will return immediately without performing any operations.
            """
        if self.confDir is None:
            return
        if self.confDir != '' and not os.path.exists(self.confDir):
            os.makedirs(self.confDir)
        return self.writeto(self.confFile)

    def writeto(self, filename: str) -> None:

        """
            Write configuration data to a file in TOML format.

            This method serializes the configuration object and writes it
            to a specified file. If the file does not exist, it will be created.
            If the file already exists, its contents will be overwritten.

            :param filename: The name of the file to write the configuration to.
            :type filename: str

            :raises TypeError: If `filename` is not a string.

            :return: None
            """
        serialized = tomli_w.dumps(self.config)
        with open(filename, 'wb') as confFileid:
            confFileid.write(serialized)

    def enumerate(self, *args):
        """
        Enumerates configuration items based on the given arguments.

        This method traverses through the configuration dictionary using the provided
        arguments as keys. If at any point an argument does not exist within the current
        level of the configuration, a ``config_exception`` is raised with the list of
        processed arguments up to that point.

        :param args: Variable-length arguments representing the keys used to navigate
                     through the nested configuration dictionary.
        :type args: tuple
        :raises config_exception: If an argument does not exist within the current level
                                 of the configuration.
        :yield: The keys from the final level of the nested configuration dictionary.
        :ytype: str

        .. note:: This method will yield all keys in the final level of the traversed
                  configuration dictionary.

        """
        cur_ref = self.default_config
        treated= []
        for elem in args:
            treated.append(elem)
            if len(cur_ref) == 1 and "<>" in cur_ref:
                ref_section = "<>"
            else:
                ref_section =elem
            if ref_section not in cur_ref:
                raise ConfigException(treated)
            cur_ref = cur_ref[ref_section]

        for read_item in cur_ref.keys():
            yield read_item

    def json(self, **kwargs):
        return json.dumps(self.config, **kwargs)


class ConfigException(Exception):
    def __init__(self,sections = None, message="Exception in configuration"):
        self.sections = sections
        if sections is not None:
            if isinstance(sections, list):
                text = sections[0]
                for section in sections[1:]:
                    text += "->"+section
            else:
                text = sections
            message = text + " is not defined in configuration"
        self.message =  message
        super().__init__(message)

