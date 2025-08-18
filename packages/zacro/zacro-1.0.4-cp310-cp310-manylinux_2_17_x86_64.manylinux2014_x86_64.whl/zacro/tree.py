#!/usr/bin/env python
"""
URDF Tree Visualization

This module provides functions to visualize URDF link structures in a tree format.
"""

from .zacro import print_urdf_tree_rust


def print_urdf_tree(urdf_content: str) -> str:
    """
    Generate a tree-style visualization of URDF link structure.

    Args:
        urdf_content: URDF XML content as string

    Returns:
        Tree visualization as string

    Raises:
        RuntimeError: If URDF parsing fails
    """
    return print_urdf_tree_rust(urdf_content)


def print_urdf_tree_from_file(urdf_file: str) -> str:
    """
    Generate a tree-style visualization of URDF link structure from file.

    Args:
        urdf_file: Path to URDF file

    Returns:
        Tree visualization as string

    Raises:
        RuntimeError: If URDF parsing fails
        IOError: If file cannot be read
    """
    with open(urdf_file, 'r', encoding='utf-8') as f:
        urdf_content = f.read()
    return print_urdf_tree_rust(urdf_content)
