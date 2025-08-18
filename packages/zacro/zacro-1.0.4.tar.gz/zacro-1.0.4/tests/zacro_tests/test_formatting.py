#!/usr/bin/env python

import unittest

import zacro


class TestFormatting(unittest.TestCase):
    """Test XML formatting features"""

    def test_formatted_output(self):
        """Test formatted XML output"""
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

        result = zacro.xacro_from_string(xml_str, format_output=True)

        # Check XML declaration
        self.assertTrue(result.startswith('<?xml version="1.0" encoding="UTF-8"?>'))

        # Check proper indentation (should have newlines and spaces)
        lines = result.split('\n')
        self.assertGreater(len(lines), 5)  # Should be multiple lines

        # Check for indented elements
        indented_lines = [line for line in lines if line.startswith('  ')]
        self.assertGreater(len(indented_lines), 0)

    def test_class_api_formatting(self):
        """Test formatting with class-based API"""
        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <link name="base"/>
</robot>'''

        processor = zacro.XacroProcessor()
        processor.set_format_output(True)

        result = processor.process_string(xml_str)
        self.assertTrue(result.startswith('<?xml version="1.0" encoding="UTF-8"?>'))
        self.assertIn('\n', result)


if __name__ == '__main__':
    unittest.main()
