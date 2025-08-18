#!/usr/bin/env python

import unittest

import zacro


class TestAPI(unittest.TestCase):
    """Test API functionality and parameter handling"""

    def test_function_signatures(self):
        """Test that all functions accept expected parameters"""
        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <link name="test"/>
</robot>'''

        # Test xacro_from_string with all parameters
        result = zacro.xacro_from_string(
            xml_str,
            mappings=None,
            verbosity=1,
            format_output=True,
            remove_root_link=None
        )
        self.assertIn('<link name="test"', result)

    def test_class_api_methods(self):
        """Test XacroProcessor class methods"""
        processor = zacro.XacroProcessor()

        # Test method existence
        self.assertTrue(hasattr(processor, 'set_format_output'))
        self.assertTrue(hasattr(processor, 'set_remove_root_link'))
        self.assertTrue(hasattr(processor, 'process_string'))
        self.assertTrue(hasattr(processor, 'process_file'))

        # Test method functionality
        processor.set_format_output(True)
        processor.set_remove_root_link("world")

        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <link name="test"/>
</robot>'''

        result = processor.process_string(xml_str)
        self.assertIn('<link name="test"', result)

    def test_parameter_combinations(self):
        """Test different parameter combinations"""
        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <link name="world"/>
  <xacro:macro name="test_macro" params="name">
    <joint name="${name}_joint" type="fixed">
      <parent link="world"/>
      <child link="${name}_link"/>
    </joint>
    <link name="${name}_link"/>
  </xacro:macro>

  <xacro:test_macro name="test"/>
</robot>'''

        # Test format_output disabled (format is default now)
        result1 = zacro.xacro_from_string(xml_str, format_output=False, validate_urdf=False)
        self.assertTrue(result1.startswith('<?xml version="1.0" encoding="UTF-8"?>'))
        self.assertEqual(result1.count('<joint'), 1)

        # Test remove_root_link only (disable validation since it creates disconnected links)
        result2 = zacro.xacro_from_string(xml_str, remove_root_link="world", validate_urdf=False)
        self.assertEqual(result2.count('<joint'), 0)

        # Test both options (format_output=False to test non-formatted output)
        result3 = zacro.xacro_from_string(xml_str, format_output=False, remove_root_link="world", validate_urdf=False)
        self.assertTrue(result3.startswith('<?xml version="1.0" encoding="UTF-8"?>'))
        self.assertEqual(result3.count('<joint'), 0)

    def test_default_parameters(self):
        """Test that default parameters work correctly"""
        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <link name="default_test"/>
</robot>'''

        # Test with minimal parameters
        result = zacro.xacro_from_string(xml_str)
        self.assertIn('<link name="default_test"', result)
        # Should be formatted by default
        self.assertIn('\n  <', result)

    def test_version_info(self):
        """Test version information is available"""
        self.assertTrue(hasattr(zacro, '__version__'))
        self.assertIsInstance(zacro.__version__, str)


if __name__ == '__main__':
    unittest.main()
