#!/usr/bin/env python

import unittest

import zacro


class TestBasicFunctionality(unittest.TestCase):
    """Test basic zacro functionality"""

    def test_import(self):
        """Test that zacro can be imported"""
        import zacro
        self.assertTrue(hasattr(zacro, 'xacro_to_string'))
        self.assertTrue(hasattr(zacro, 'xacro_from_string'))
        self.assertTrue(hasattr(zacro, 'xacro_to_file'))
        self.assertTrue(hasattr(zacro, 'XacroProcessor'))

    def test_simple_macro_expansion(self):
        """Test basic macro expansion"""
        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:macro name="simple_link" params="link_name">
    <link name="${link_name}">
      <visual>
        <geometry>
          <box size="1 1 1"/>
        </geometry>
      </visual>
    </link>
  </xacro:macro>

  <xacro:simple_link link_name="test_link"/>
</robot>'''

        result = zacro.xacro_from_string(xml_str)
        self.assertIn('<link name="test_link">', result)
        self.assertNotIn('<xacro:simple_link', result)
        self.assertNotIn('<xacro:macro', result)

    def test_property_substitution(self):
        """Test property substitution"""
        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:property name="width" value="0.2"/>
  <link name="base">
    <visual>
      <geometry>
        <box size="${width} ${width} 0.1"/>
      </geometry>
    </visual>
  </link>
</robot>'''

        result = zacro.xacro_from_string(xml_str)
        self.assertIn('size="0.2 0.2 0.1"', result)
        self.assertNotIn('${width}', result)
        self.assertNotIn('<xacro:property', result)

    def test_empty_robot(self):
        """Test processing empty robot"""
        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
</robot>'''

        # Disable validation for empty robot as it has no links
        result = zacro.xacro_from_string(xml_str, validate_urdf=False)
        self.assertIn('<robot', result)
        # Empty robot may be self-closing
        self.assertTrue('</robot>' in result or '/>' in result)


if __name__ == '__main__':
    unittest.main()
