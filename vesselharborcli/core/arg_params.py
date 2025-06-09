#  Copyright (c) 2025.  VesselHarbor
#  ____   ____                          .__    ___ ___             ___.
#  \   \ /   /____   ______ ______ ____ |  |  /   |   \_____ ______\_ |__   ___________
#   \   Y   // __ \ /  ___//  ___// __ \|  | /    ~    \__  \\_  __ \ __ \ /  _ \_  __ \
#    \     /\  ___/ \___ \ \___ \\  ___/|  |_\    Y    // __ \|  | \/ \_\ (  <_> )  | \/
#     \___/  \___  >____  >____  >\___  >____/\___|_  /(____  /__|  |___  /\____/|__|
#                \/     \/     \/     \/            \/      \/          \/
#  MIT License
#

import argparse
import textwrap


class arg_parser():
    def __init__(self, program, version, description, basic_options, instances_desc = None, instances = None, generic= True):
        """
        Summarizes the functionality of a class designed to create argument parsers
        with specific modes and options.

        :param program: The name of the program.
        :type program: str

        :param version: The version of the program.
        :type version: str

        :param description: A brief description of what the program does.
        :type description: str

        :param basic_options: A function that adds basic options to the argument parser.
        :type basic_options: callable

        :param instances_desc: A dictionary containing descriptions for instance-specific
            options. This is optional and defaults to None.
        :type instances_desc: dict, optional

        :param instances: A list of instances that define specific modes or subparsers.
            This is optional and defaults to None.
        :type instances: list, optional

        :param generic: A boolean indicating whether to use a generic mode selection
            mechanism. Defaults to True.

        :raises AttributeError: If the 'subparser' method does not return a tuple with at least two elements.
        :raises TypeError: If an instance in the 'instances' list does not have a 'params'
            method that takes a single argument."""
        self.version = version
        self.program = program
        self.parser = argparse.ArgumentParser(description=description)
        basic_options(self.parser)

        desc = {'title': 'mode', 'description': 'Select mode', 'help': 'get help with --help', 'dest': 'mode'}
        if instances_desc is not None:
            for key, value in instances_desc.items():
                desc[key] = value
        if generic == True:
            if instances is not None and len(instances) > 0:
                subparsers = self.parser.add_subparsers( title = desc['title'], description =desc['description'], help = desc['help'], dest = desc['dest'])
                for instance in instances:
                    name = instance.subparser()
                    if len(name) > 2 and name[2] is not None:
                        sub = subparsers.add_parser(name[0], help = name[1],formatter_class=argparse.RawDescriptionHelpFormatter, epilog=textwrap.dedent(name[2]))
                    else:
                        sub = subparsers.add_parser(name[0], help=name[1])
                    instance.params(sub)
        else:
            if instances is not None and len(instances) > 0:
                instances[0].params(self.parser)


    def parse_args(self,args):
        """
        Summarizes the process to parse arguments using a parser and returns the parsed result.

        This function is designed to handle argument parsing within an existing parser structure.
        It takes a list of command-line arguments, skips the first element (assumed to be the script name),
        and processes the remaining arguments through the parser. The resulting parsed arguments are then returned.

        :param args: A list containing command-line arguments. The first element is expected
                     to be the script name and will be ignored during parsing.
        :type args: List[str]

        :return: An object representing the parsed arguments.
        :rtype: argparse.Namespace

        .. note::
            This function assumes that `self.parser` is an instance of `argparse.ArgumentParser`
            or a similar compatible parser.

        """
        res = self.parser.parse_args(args[1:])
        return res

    def parse_known_args(self,args):
        """
        A class responsible for parsing command-line arguments.

        This class provides functionality to handle and process command-line arguments
        using a pre-defined parser. It includes methods for initializing the parser,
        adding arguments, and parsing known arguments from the command line.

        :ivar parser: An instance of ArgumentParser used for parsing command-line
            arguments.
        :type parser: argparse.ArgumentParser

        """
        res = self.parser.parse_known_args(args[1:])
        return res

    def print_help(self):
        self.parser.print_help()

    def print_version(self):
        print(self.program + " version : "+ self.version)


