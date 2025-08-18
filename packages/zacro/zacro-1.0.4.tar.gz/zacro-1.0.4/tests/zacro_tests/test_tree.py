#!/usr/bin/env python

import unittest

import zacro


class TestTreeVisualization(unittest.TestCase):
    """Test URDF tree visualization functionality"""

    def test_simple_tree(self):
        """Test basic tree visualization"""
        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <link name="base"/>
  <joint name="joint1" type="revolute">
    <parent link="base"/>
    <child link="child"/>
  </joint>
  <link name="child"/>
</robot>'''

        result = zacro.xacro_from_string(xml_str, validate_urdf=False)
        tree = zacro.print_urdf_tree(result)

        self.assertIn('URDF Link Tree Structure:', tree)
        self.assertIn('└── base', tree)
        self.assertIn('└── child', tree)

    def test_branched_tree(self):
        """Test tree with multiple branches"""
        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <link name="root"/>

  <joint name="joint1" type="revolute">
    <parent link="root"/>
    <child link="branch1"/>
  </joint>
  <link name="branch1"/>

  <joint name="joint2" type="revolute">
    <parent link="root"/>
    <child link="branch2"/>
  </joint>
  <link name="branch2"/>

  <joint name="joint3" type="revolute">
    <parent link="branch1"/>
    <child link="leaf"/>
  </joint>
  <link name="leaf"/>
</robot>'''

        result = zacro.xacro_from_string(xml_str, validate_urdf=False)
        tree = zacro.print_urdf_tree(result)

        self.assertIn('└── root', tree)
        self.assertIn('├── branch1', tree)
        self.assertIn('└── branch2', tree)
        self.assertIn('└── leaf', tree)

    def test_print_urdf_tree_from_file(self):
        """Test tree visualization from file"""
        import os
        import tempfile

        xml_content = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <link name="base"/>
  <joint name="joint1" type="revolute">
    <parent link="base"/>
    <child link="child"/>
  </joint>
  <link name="child"/>
</robot>'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.urdf', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name

        try:
            tree = zacro.print_urdf_tree_from_file(temp_file)
            self.assertIn('URDF Link Tree Structure:', tree)
            self.assertIn('└── base', tree)
            self.assertIn('└── child', tree)
        finally:
            os.unlink(temp_file)

    def test_empty_robot(self):
        """Test tree with no links"""
        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
</robot>'''

        result = zacro.xacro_from_string(xml_str, validate_urdf=False)
        tree = zacro.print_urdf_tree(result)

        self.assertIn('No base links found', tree)


if __name__ == '__main__':
    unittest.main()
