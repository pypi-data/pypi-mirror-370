"""
Fast Rust implementation of xacro with enhanced features for modular robotics.

This module provides a high-performance Rust-based implementation of xacro
with additional features like formatting output and removing first joints for
modular robot assemblies.
"""

import sys


if (sys.version_info[0] == 3 and sys.version_info[1] >= 8) or sys.version_info[0] > 3:
    import importlib.metadata
    _version = None

    def determine_version(module_name):
        return importlib.metadata.version(module_name)

    def __getattr__(name):
        global _version
        if name == "__version__":
            if _version is None:
                _version = determine_version('zacro')
            return _version
        raise AttributeError(
            "module {} has no attribute {}".format(__name__, name))

else:
    import pkg_resources

    def determine_version(module_name):
        return pkg_resources.get_distribution(module_name).version

    __version__ = determine_version('zacro')

from .tree import print_urdf_tree
from .tree import print_urdf_tree_from_file
from .zacro import PyXacroProcessor as XacroProcessor
from .zacro import xacro_from_string
from .zacro import xacro_to_file
from .zacro import xacro_to_string


__all__ = [
    "XacroProcessor",
    "xacro_to_string",
    "xacro_from_string",
    "xacro_to_file",
    "print_urdf_tree",
    "print_urdf_tree_from_file",
]
