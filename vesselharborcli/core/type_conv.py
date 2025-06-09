#  Copyright (c) 2025.  VesselHarbor
#  ____   ____                          .__    ___ ___             ___.
#  \   \ /   /____   ______ ______ ____ |  |  /   |   \_____ ______\_ |__   ___________
#   \   Y   // __ \ /  ___//  ___// __ \|  | /    ~    \__  \\_  __ \ __ \ /  _ \_  __ \
#    \     /\  ___/ \___ \ \___ \\  ___/|  |_\    Y    // __ \|  | \/ \_\ (  <_> )  | \/
#     \___/  \___  >____  >____  >\___  >____/\___|_  /(____  /__|  |___  /\____/|__|
#                \/     \/     \/     \/            \/      \/          \/
#  MIT License
#

def to_type(ref_var, value):
    """
    The to_type function converts a value to the type of a reference variable.

    This is useful when accepting user input and converting it to the correct type,
    or when printing values from variables that are not always strings. The function
    takes two arguments: ref_var, which is the reference variable used for type
    conversions; and value, which is the value that will be converted. If ref_var's
    type matches or contains value's current type then no conversion occurs and
    value simply returns as-is. Otherwise, if ref_var is boolean then any integer,
    float or string, the functions tries to convert it in ref_var type.

    For boolean, positive values, or strings like "on", "active", "yes", "y", "true",
    "t" or "1" are converted to True.

        >>> print(to_type(True, True)) # No change if same types already!

        True

        >>> print(to_type(True, "yes")) # Convert string "yes" -> bool True!

        True

        >>> print(to_type(True, 0)) # Convert int 0 -> bool False! (bool)0 = False! :)

        False

    :param ref_var: Used to define the type in which to convert the value.
    :param value: Used to Convert the value from a string to the type of ref_var.
    :return: The value as a bool, int, string or float if it can be converted.

    """
    if isinstance(ref_var, bool):
        if isinstance(value, bool):
            return value
        elif isinstance(value, int) or isinstance(value, float):
            return value != 0
        elif isinstance(value, str):
            return value.lower() in ("on", "active", "yes", "y", "true", "t", "1")
    elif isinstance(ref_var, int):
        return int(value)
    elif isinstance(ref_var, float):
        return float(value)
    elif isinstance(ref_var, str):
        return str(value)
    elif isinstance(ref_var, list):
        new_list = []
        for elem in value:
            new_list.append(to_type(ref_var[0], elem))
        return new_list
