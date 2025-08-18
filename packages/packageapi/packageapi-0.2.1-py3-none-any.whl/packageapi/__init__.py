"""
packageapi
----------

Read the README
"""

from .gui import gui_package_manager, install_package, check_package, check_and_install_package

__all__ = [
    "gui_package_manager",
    "install_package",
    "check_package",
    "check_and_install_package",
]
