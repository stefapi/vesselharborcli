#  Copyright (c) 2025.  VesselHarbor
#  ____   ____                          .__    ___ ___             ___.
#  \   \ /   /____   ______ ______ ____ |  |  /   |   \_____ ______\_ |__   ___________
#   \   Y   // __ \ /  ___//  ___// __ \|  | /    ~    \__  \\_  __ \ __ \ /  _ \_  __ \
#    \     /\  ___/ \___ \ \___ \\  ___/|  |_\    Y    // __ \|  | \/ \_\ (  <_> )  | \/
#     \___/  \___  >____  >____  >\___  >____/\___|_  /(____  /__|  |___  /\____/|__|
#                \/     \/     \/     \/            \/      \/          \/
#  MIT License
#

from __future__ import annotations

import re


def snake2camel(snake: str, start_lower: bool = False) -> str:
    """
    Convert a snake_case string to camelCase.

    This function takes a string in snake_case format and converts it to camelCase.
    It provides an option to start the resulting string with a lowercase letter.

    .. _`snake_case`: https://en.wikipedia.org/wiki/Snake_case

    :param snake: The input string in snake_case format.
    :type snake: str
    :param start_lower: A flag indicating whether the first character of the
                         camelCase output should be lowercase. Default is False.
    :type start_lower: bool
    :return: The converted string in camelCase format.
    :rtype: str

    """
    camel = snake.title()
    camel = re.sub("([0-9A-Za-z])_(?=[0-9A-Z])", lambda m: m.group(1), camel)
    if start_lower:
        camel = re.sub("(^_*[A-Z])", lambda m: m.group(1).lower(), camel)
    return camel


def camel2snake(camel: str) -> str:
    """
    Convert a string from CamelCase to snake_case

    This function takes a string in CamelCase format and converts it to
    snake_case by inserting underscores before digits or capital letters,
    and then converting the entire string to lowercase.

    :param camel: A string in CamelCase format.
    :type camel: str

    :return: The converted string in snake_case format.
    :rtype: str"""
    snake = re.sub(r"([a-zA-Z])([0-9])", lambda m: f"{m.group(1)}_{m.group(2)}", camel)
    snake = re.sub(r"([a-z0-9])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    return snake.lower()
