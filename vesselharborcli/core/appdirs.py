#  Copyright (c) 2025.  VesselHarbor
#  ____   ____                          .__    ___ ___             ___.
#  \   \ /   /____   ______ ______ ____ |  |  /   |   \_____ ______\_ |__   ___________
#   \   Y   // __ \ /  ___//  ___// __ \|  | /    ~    \__  \\_  __ \ __ \ /  _ \_  __ \
#    \     /\  ___/ \___ \ \___ \\  ___/|  |_\    Y    // __ \|  | \/ \_\ (  <_> )  | \/
#     \___/  \___  >____  >____  >\___  >____/\___|_  /(____  /__|  |___  /\____/|__|
#                \/     \/     \/     \/            \/      \/          \/
#  MIT License
#


import sys
import os
from pathlib import Path

system = sys.platform

BASE_DIR = Path(__file__).parent.parent


def _ensure_exists(path, mode=0o700):
    if not os.path.exists(path):
        head, tail = os.path.split(path)
        _ensure_exists(head)
        os.mkdir(path, mode)
    return path


class paths(object):
    def __init__(self, app_name, app_author):
        self.dirs = AppDirs(app_name, app_author)
        self.app_name = app_name
        self.app_author = app_author


def user_data_dir(appname=None, appauthor=None, version=None, roaming=False):
    r"""Return full path to the user-specific data dir for this application.

        :param appname: is the name of application.
            If None, just the system directory is returned.
        :param appauthor: (only used on Windows) is the name of the
            appauthor or distributing body for this application. Typically
            it is the owning company name. This falls back to appname. You may
            pass False to disable it.
        :param version: is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.
        :param roaming: (boolean, default False) can be set True to use the Windows
            roaming appdata directory. That means that for users on a Windows
            network setup for roaming profiles, this user data will be
            sync'd on login. See
            <http://technet.microsoft.com/en-us/library/cc766489(WS.10).aspx>
            for a discussion of issues.

    Typical user data directories are:
        Mac OS X:               ~/Library/Application Support/<AppName>
        Unix:                   ~/.local/share/<AppName>    # or in $XDG_DATA_HOME, if defined
        Win XP (not roaming):   C:\Documents and Settings\<username>\Application Data\<AppAuthor>\<AppName>
        Win XP (roaming):       C:\Documents and Settings\<username>\Local Settings\Application Data\<AppAuthor>\<AppName>
        Win 7  (not roaming):   C:\Users\<username>\AppData\Local\<AppAuthor>\<AppName>
        Win 7  (roaming):       C:\Users\<username>\AppData\Roaming\<AppAuthor>\<AppName>

    For Unix, we follow the XDG spec and support $XDG_DATA_HOME.
    That means, by default "~/.local/share/<AppName>".
    """
    if system == "win32":
        if appauthor is None:
            appauthor = appname
        const = "CSIDL_APPDATA" if roaming else "CSIDL_LOCAL_APPDATA"
        path = os.path.normpath(_get_win_folder(const))
        if appname:
            if appauthor is not False:
                path = os.path.join(path, appauthor, appname)
            else:
                path = os.path.join(path, appname)
    elif system == 'darwin':
        path = os.path.expanduser('~/Library/Application Support/')
        if appname:
            path = os.path.join(path, appname)
    else:
        path = os.getenv('XDG_DATA_HOME', os.path.expanduser("~/.local/share"))
        if appname:
            path = os.path.join(path, appname)
    if appname and version:
        path = os.path.join(path, version)
    return path


def site_data_dir(appname=None, appauthor=None, version=None):
    r"""Return full path to the user-shared data dir for this application.

        :param appname: is the name of application.
            If None, just the system directory is returned.
        :param appauthor: (only used on Windows) is the name of the
            appauthor or distributing body for this application. Typically
            it is the owning company name. This falls back to appname. You may
            pass False to disable it.
        :param version: is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.

    Typical site data directories are:
        Mac OS X:   /Library/Application Support/<AppName>
        Unix:       /usr/local/share/<AppName> or /usr/share/<AppName>
        Win XP:     C:\Documents and Settings\All Users\Application Data\<AppAuthor>\<AppName>
        Vista:      (Fail! "C:\ProgramData" is a hidden *system* directory on Vista.)
        Win 7:      C:\ProgramData\<AppAuthor>\<AppName>   # Hidden, but writeable on Win 7.

    WARNING: Do not use this on Windows. See the Vista-Fail note above for why.
    """
    if system == "win32":
        if appauthor is None:
            appauthor = appname
        path = os.path.normpath(_get_win_folder("CSIDL_COMMON_APPDATA"))
        if appname:
            if appauthor is not False:
                path = os.path.join(path, appauthor, appname)
            else:
                path = os.path.join(path, appname)
    elif system == 'darwin':
        path = os.path.expanduser('/Library/Application Support')
        if appname:
            path = os.path.join(path, appname)
    else:
        # XDG default for $XDG_DATA_DIRS
        # only first, if multipath is False
        path = os.getenv('XDG_DATA_DIRS',
                         os.pathsep.join(['/usr/local/share', '/usr/share']))
        pathlist = [os.path.expanduser(x.rstrip(os.sep)) for x in path.split(os.pathsep)]
        if appname:
            if version:
                appname = os.path.join(appname, version)
            pathlist = [os.sep.join([x, appname]) for x in pathlist]

        for path in pathlist:
            if os.path.exists(path):
                return path
    return os.path.join("/app", appname, "data")


def site_lib_dir(appname=None, appauthor=None, version=None):
    r"""Return full path to the site library directory

        :param appname: is the name of application.
            If None, just the system directory is returned.
        :param appauthor: (only used on Windows) is the name of the
            appauthor or distributing body for this application. Typically
            it is the owning company name. This falls back to appname. You may
            pass False to disable it.
        :param version: is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.

    WARNING: Do not use this on Windows. See the Vista-Fail note above for why.
    """
    return  BASE_DIR


def user_config_dir(appname=None, appauthor=None, version=None, roaming=False):
    r"""Return full path to the user-specific config dir for this application.

        :param appname:is the name of application.
            If None, just the system directory is returned.
        :param appauthor: (only used on Windows) is the name of the
            appauthor or distributing body for this application. Typically
            it is the owning company name. This falls back to appname. You may
            pass False to disable it.
        :param version: is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.
        :param roaming: (boolean, default False) can be set True to use the Windows
            roaming appdata directory. That means that for users on a Windows
            network setup for roaming profiles, this user data will be
            sync'd on login. See
            <http://technet.microsoft.com/en-us/library/cc766489(WS.10).aspx>
            for a discussion of issues.

    Typical user config directories are:
        Mac OS X:               ~/Library/Preferences/<AppName>
        Unix:                   ~/.config/<AppName>     # or in $XDG_CONFIG_HOME, if defined
        Win *:                  same as user_data_dir

    For Unix, we follow the XDG spec and support $XDG_CONFIG_HOME.
    That means, by default "~/.config/<AppName>".
    """
    if system == "win32":
        path = user_data_dir(appname, appauthor, None, roaming)
    elif system == 'darwin':
        path = os.path.expanduser('~/Library/Preferences/')
        if appname:
            path = os.path.join(path, appname)
    else:
        path = os.getenv('XDG_CONFIG_HOME', os.path.expanduser("~/.config"))
        if appname:
            path = os.path.join(path, appname)
    if appname and version:
        path = os.path.join(path, version)
    return path


def site_config_dir(appname=None, appauthor=None, version=None):
    r"""Return full path to the user-shared data dir for this application.

        :param appname: is the name of application.
            If None, just the system directory is returned.
        :param appauthor: (only used on Windows) is the name of the
            appauthor or distributing body for this application. Typically
            it is the owning company name. This falls back to appname. You may
            pass False to disable it.
        :param version: is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.

    Typical site config directories are:
        Mac OS X:   same as site_data_dir
        Unix:       /etc/<AppName>
        Win *:      same as site_data_dir
        Vista:      (Fail! "C:\ProgramData" is a hidden *system* directory on Vista.)

    For Unix, this is using the $XDG_CONFIG_DIRS[0] default, if multipath=False

    WARNING: Do not use this on Windows. See the Vista-Fail note above for why.
    """
    if system == 'win32':
        path = site_data_dir(appname, appauthor)
        if appname and version:
            path = os.path.join(path, version)
    elif system == 'darwin':
        path = os.path.expanduser('/Library/Preferences')
        if appname:
            path = os.path.join(path, appname)
    else:
        path = os.path.expanduser('/etc')
        if appname:
            path = os.path.join(path, appname)
    return path


def user_cache_dir(appname=None, appauthor=None, version=None, opinion=True):
    r"""Return full path to the user-specific cache dir for this application.

        :param appname: is the name of application.
            If None, just the system directory is returned.
        :param appauthor: (only used on Windows) is the name of the
            appauthor or distributing body for this application. Typically
            it is the owning company name. This falls back to appname. You may
            pass False to disable it.
        :param version: is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.
        :param opinion: (boolean) can be False to disable the appending of
            "Cache" to the base app data dir for Windows. See
            discussion below.

    Typical user cache directories are:
        Mac OS X:   ~/Library/Caches/<AppName>
        Unix:       ~/.cache/<AppName> (XDG default)
        Win XP:     C:\Documents and Settings\<username>\Local Settings\Application Data\<AppAuthor>\<AppName>\Cache
        Vista:      C:\Users\<username>\AppData\Local\<AppAuthor>\<AppName>\Cache

    On Windows the only suggestion in the MSDN docs is that local settings go in
    the `CSIDL_LOCAL_APPDATA` directory. This is identical to the non-roaming
    app data dir (the default returned by `user_data_dir` above). Apps typically
    put cache data somewhere *under* the given dir here. Some examples:
        ...\Mozilla\Firefox\Profiles\<ProfileName>\Cache
        ...\Acme\SuperApp\Cache\1.0
    """
    if system == "win32":
        if appauthor is None:
            appauthor = appname
        path = os.path.normpath(_get_win_folder("CSIDL_LOCAL_APPDATA"))
        if appname:
            if appauthor is not False:
                path = os.path.join(path, appauthor, appname)
            else:
                path = os.path.join(path, appname)
            if opinion:
                path = os.path.join(path, "Cache")
    elif system == 'darwin':
        path = os.path.expanduser('~/Library/Caches')
        if appname:
            path = os.path.join(path, appname)
    else:
        path = os.getenv('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))
        if appname:
            path = os.path.join(path, appname)
    if appname and version:
        path = os.path.join(path, version)
    return path


def site_cache_dir(appname=None, appauthor=None, version=None):
    r"""
    The site_cache_dir function is intended to return a directory where the
    application can store cache data that will be used across sessions. It should
    be writable by the process running PyInstaller, but readable by all users.


    :param appname: Force site_cache_dir() to use the application name
    :param appauthor: (only used on Windows) is the name of the
            appauthor or distributing body for this application. Typically
            it is the owning company name. This falls back to appname. You may
            pass False to disable it.
    :param version: is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.
    :return: The full path to the user-specific cache dir for this application


    Typical user cache directories are:
        Mac OS X:   /Library/Caches/<AppName>
        Unix:       /var/cache/<AppName>
        Win XP:     C:\Documents and Settings\All Users\Application Data\<AppAuthor>\<AppName>\cache
        Vista:      (Fail! "C:\ProgramData" is a hidden *system* directory on Vista.)
        Win 7:      C:\ProgramData\<AppAuthor>\<AppName>\cache  # Hidden, but writeable on Win 7.

    On Windows the only suggestion in the MSDN docs is that local settings go in
    the `CSIDL_LOCAL_APPDATA` directory. This is identical to the non-roaming
    app data dir (the default returned by `user_data_dir` above). Apps typically
    put cache data somewhere *under* the given dir here. Some examples:
        ...\Mozilla\Firefox\Profiles\<ProfileName>\Cache
        ...\Acme\SuperApp\Cache\1.0
    OPINION: This function appends "Cache" to the `CSIDL_LOCAL_APPDATA` value.
    This can be disabled with the `opinion=False` option.
    """
    if system == "win32":
        path = site_data_dir(appname, appauthor, version)
        path = os.path.join(path, "cache")
    elif system == 'darwin':
        path = os.path.expanduser('/Library/Caches')
        if appname:
            path = os.path.join(path, appname)
    else:
        path = os.path.expanduser("/var/cache")
        if appname:
            path = os.path.join(path, appname)
    if appname and version:
        path = os.path.join(path, version)
    return path


def site_log_dir(appname=None, appauthor=None, version=None):
    r"""
    The site_log_dir function is intended to return a directory where the
    application can store log data that will be used across sessions. It should
    be writable by the process running PyInstaller, but readable by all users.


    :param appname: Force site_cache_dir() to use the application name
    :param appauthor: (only used on Windows) is the name of the
            appauthor or distributing body for this application. Typically
            it is the owning company name. This falls back to appname. You may
            pass False to disable it.
    :param version: is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.
    :return: The full path to the system log dir for this application


    Typical user cache directories are:
        Mac OS X:   /Library/Logs/<AppName>
        Unix:       /var/log/<AppName>
        Win XP:     C:\Documents and Settings\All Users\Application Data\<AppAuthor>\<AppName>\log
        Vista:      (Fail! "C:\ProgramData" is a hidden *system* directory on Vista.)
        Win 7:      C:\ProgramData\<AppAuthor>\<AppName>\log  # Hidden, but writeable on Win 7.

    On Windows the only suggestion in the MSDN docs is that local settings go in
    the `CSIDL_LOCAL_APPDATA` directory. This is identical to the non-roaming
    app data dir (the default returned by `user_data_dir` above). Apps typically
    put cache data somewhere *under* the given dir here. Some examples:
        ...\Mozilla\Firefox\Profiles\<ProfileName>\Cache
        ...\Acme\SuperApp\Cache\1.0
    OPINION: This function appends "Cache" to the `CSIDL_LOCAL_APPDATA` value.
    This can be disabled with the `opinion=False` option.
    """
    if system == "win32":
        path = site_data_dir(appname, appauthor, version)
        path = os.path.join(path, "log")
    elif system == 'darwin':
        path = os.path.expanduser('/Library/Logs')
        if appname:
            path = os.path.join(path, appname)
    else:
        path = os.path.expanduser("/var/log")
        if appname:
            path = os.path.join(path, appname)
    if appname and version:
        path = os.path.join(path, version)
    return path

def user_state_dir(appname=None, appauthor=None, version=None, roaming=False):
    r"""Return full path to the user-specific state dir for this application.

        :param appname: is the name of application.
            If None, just the system directory is returned.
        :param appauthor: (only used on Windows) is the name of the
            appauthor or distributing body for this application. Typically
            it is the owning company name. This falls back to appname. You may
            pass False to disable it.
        :param version: is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.
        :param roaming: (boolean, default False) can be set True to use the Windows
            roaming appdata directory. That means that for users on a Windows
            network setup for roaming profiles, this user data will be
            sync'd on login. See
            <http://technet.microsoft.com/en-us/library/cc766489(WS.10).aspx>
            for a discussion of issues.

    Typical user state directories are:
        Mac OS X:  same as user_data_dir
        Unix:      ~/.local/state/<AppName>   # or in $XDG_STATE_HOME, if defined
        Win *:     same as user_data_dir

    For Unix, we follow this Debian proposal <https://wiki.debian.org/XDGBaseDirectorySpecification#state>
    to extend the XDG spec and support $XDG_STATE_HOME.

    That means, by default "~/.local/state/<AppName>".
    """
    if system in ["win32", "darwin"]:
        path = user_data_dir(appname, appauthor, None, roaming)
    else:
        path = os.getenv('XDG_STATE_HOME', os.path.expanduser("~/.local/state"))
        if appname:
            path = os.path.join(path, appname)
    if appname and version:
        path = os.path.join(path, version)
    return path


def user_log_dir(appname=None, appauthor=None, version=None, opinion=True):
    r"""Return full path to the user-specific log dir for this application.

        :param appname: is the name of application.
            If None, just the system directory is returned.
        :param appauthor: (only used on Windows) is the name of the
            appauthor or distributing body for this application. Typically
            it is the owning company name. This falls back to appname. You may
            pass False to disable it.
        :param version: is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.
        :param opinion: (boolean) can be False to disable the appending of
            "Logs" to the base app data dir for Windows, and "log" to the
            base cache dir for Unix. See discussion below.

    Typical user log directories are:
        Mac OS X:   ~/Library/Logs/<AppName>
        Unix:       ~/.cache/<AppName>/log  # or under $XDG_CACHE_HOME if defined
        Win XP:     C:\Documents and Settings\<username>\Local Settings\Application Data\<AppAuthor>\<AppName>\Logs
        Vista:      C:\Users\<username>\AppData\Local\<AppAuthor>\<AppName>\Logs

    On Windows the only suggestion in the MSDN docs is that local settings
    go in the `CSIDL_LOCAL_APPDATA` directory. (Note: I'm interested in
    examples of what some windows apps use for a logs dir.)
    """
    if system == "darwin":
        path = os.path.join(
            os.path.expanduser('~/Library/Logs'),
            appname)
    elif system == "win32":
        path = user_data_dir(appname, appauthor, version)
        version = False
        if opinion:
            path = os.path.join(path, "Logs")
    else:
        path = user_cache_dir(appname, appauthor, version)
        version = False
        if opinion:
            path = os.path.join(path, "log")
    if appname and version:
        path = os.path.join(path, version)
    return path


class AppDirs(object):
    """Convenience wrapper for getting application dirs."""

    def __init__(self, appname=None, appauthor=None, version=None, roaming=False):
        self.appname = appname
        self.appauthor = appauthor
        self.version = version
        self.roaming = roaming

    @property
    def user_data_dir(self):
        return user_data_dir(self.appname, self.appauthor,
                             version=self.version, roaming=self.roaming)

    @property
    def site_data_dir(self):
        return site_data_dir(self.appname, self.appauthor,
                             version=self.version)

    @property
    def site_lib_dir(self):
        return site_lib_dir(self.appname, self.appauthor,
                             version=self.version)

    @property
    def user_config_dir(self):
        return user_config_dir(self.appname, self.appauthor,
                               version=self.version, roaming=self.roaming)

    @property
    def site_config_dir(self):
        return site_config_dir(self.appname, self.appauthor,
                               version=self.version)

    @property
    def user_cache_dir(self):
        return user_cache_dir(self.appname, self.appauthor,
                              version=self.version)

    @property
    def site_cache_dir(self):
        return site_cache_dir(self.appname, self.appauthor,
                              version=self.version)

    @property
    def user_state_dir(self):
        return user_state_dir(self.appname, self.appauthor,
                              version=self.version)

    @property
    def user_log_dir(self):
        return user_log_dir(self.appname, self.appauthor,
                            version=self.version)

    @property
    def site_log_dir(self):
        return site_log_dir(self.appname, self.appauthor,
                            version=self.version)


# ---- internal support stuff

def _get_win_folder_from_registry(csidl_name):
    """This is a fallback technique at best. I'm not sure if using the
    registry for this guarantees us the correct answer for all CSIDL_*
    names.
    """
    import winreg as _winreg

    shell_folder_name = {
        "CSIDL_APPDATA": "AppData",
        "CSIDL_COMMON_APPDATA": "Common AppData",
        "CSIDL_LOCAL_APPDATA": "Local AppData",
    }[csidl_name]

    key = _winreg.OpenKey(
        _winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
    )
    dir, type = _winreg.QueryValueEx(key, shell_folder_name)
    return dir


def _get_win_folder_with_ctypes(csidl_name):
    import ctypes

    csidl_const = {
        "CSIDL_APPDATA": 26,
        "CSIDL_COMMON_APPDATA": 35,
        "CSIDL_LOCAL_APPDATA": 28,
    }[csidl_name]

    buf = ctypes.create_unicode_buffer(1024)
    ctypes.windll.shell32.SHGetFolderPathW(None, csidl_const, None, 0, buf)

    # Downgrade to short path name if have highbit chars. See
    # <http://bugs.activestate.com/show_bug.cgi?id=85099>.
    has_high_char = False
    for c in buf:
        if ord(c) > 255:
            has_high_char = True
            break
    if has_high_char:
        buf2 = ctypes.create_unicode_buffer(1024)
        if ctypes.windll.kernel32.GetShortPathNameW(buf.value, buf2, 1024):
            buf = buf2

    return buf.value


def _get_win_folder_from_environ(csidl_name):
    env_var_name = {
        "CSIDL_APPDATA": "APPDATA",
        "CSIDL_COMMON_APPDATA": "ALLUSERSPROFILE",
        "CSIDL_LOCAL_APPDATA": "LOCALAPPDATA",
    }[csidl_name]

    return os.environ[env_var_name]


if system == "win32":
    try:
        from ctypes import windll
    except ImportError:
        try:
            import winreg as _winreg
        except ImportError:
            _get_win_folder = _get_win_folder_from_environ
        else:
            _get_win_folder = _get_win_folder_from_registry
    else:
        _get_win_folder = _get_win_folder_with_ctypes
