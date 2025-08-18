import os
import platform
from getpass import getuser
from typing import Optional

from packaging import version
from davidkhala.syntax import is_windows, is_linux, is_mac
from davidkhala.syntax.path import resolve

APPDATA = {
    'Roaming': os.environ.get('APPDATA'),
    'Local': os.environ.get('LOCALAPPDATA')
}
USER = getuser()


def python_paths(major: str, minor: str) -> Optional[dict]:
    if is_windows():
        home = resolve(APPDATA['Local'], 'Programs', 'Python', f"Python{major}{minor}")

        return {
            'home': home,
            'executable': resolve(home, 'python.exe'),
        }
    elif is_linux():
        home = '/usr/bin'
        return {
            'home': home,
            'executable': resolve(home, f"python{major}.{minor}"),
        }
    elif is_mac():
        home = f"/Library/Frameworks/Python.framework/Versions/{major}.{minor}/bin"
        return {
            "home": home,
            "executable": resolve(home, f"python{major}.{minor}"),
        }


class Version:
    """
    Python version
    """

    def __init__(self):
        self.major, self.minor, self.patch = platform.python_version_tuple()

    @staticmethod
    def sem_ver() -> str:
        return platform.python_version()

    @property
    def micro(self) -> str:
        return self.patch

    @staticmethod
    def is_older_than(target_version):
        """
        Check if the current Python version is older than the specified target version.

        :param target_version: A string representing the target version (e.g., "3.8.0").
        """
        current_version = Version.sem_ver()

        return version.parse(current_version) < version.parse(target_version)
