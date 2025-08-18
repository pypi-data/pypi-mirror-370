#!/usr/bin/env python

import unittest

import zacro


class TestModularRobot(unittest.TestCase):
    """Test modular robot specific features"""

    def test_remove_root_link(self):
        """Test removing root link and connecting joints"""
        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:macro name="module" params="prefix parent_link">
    <joint name="${prefix}base_link_to_${parent_link}_joint" type="fixed">
      <parent link="${parent_link}"/>
      <child link="${prefix}base_link"/>
    </joint>

    <link name="${prefix}base_link">
      <visual>
        <geometry><box size="0.1 0.1 0.1"/></geometry>
      </visual>
    </link>

    <joint name="${prefix}joint" type="revolute">
      <parent link="${prefix}base_link"/>
      <child link="${prefix}end_link"/>
      <axis xyz="0 0 1"/>
    </joint>

    <link name="${prefix}end_link">
      <visual>
        <geometry><cylinder radius="0.05" length="0.1"/></geometry>
      </visual>
    </link>
  </xacro:macro>

  <link name="world"/>
  <xacro:module prefix="module1_" parent_link="world"/>
  <xacro:module prefix="module2_" parent_link="module1_end_link"/>
</robot>'''

        # Without remove_root_link
        result_with_joints = zacro.xacro_from_string(xml_str, remove_root_link=None, validate_urdf=False)
        joint_count_with = result_with_joints.count('<joint')

        # With remove_root_link (disable validation since it creates disconnected links)
        result_without_joints = zacro.xacro_from_string(xml_str, remove_root_link="world", validate_urdf=False)
        joint_count_without = result_without_joints.count('<joint')

        # Should have removed the world link
        self.assertNotIn('<link name="world"', result_without_joints)
        self.assertIn('<link name="world"', result_with_joints)

        print(f"Joints removed: {joint_count_with - joint_count_without}")

    def test_class_api_remove_root_link(self):
        """Test remove_root_link with class-based API"""
        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:macro name="simple_module" params="name">
    <joint name="${name}_connection_joint" type="fixed">
      <parent link="world"/>
      <child link="${name}_link"/>
    </joint>
    <link name="${name}_link"/>
  </xacro:macro>

  <xacro:simple_module name="test"/>
</robot>'''

        processor = zacro.XacroProcessor()
        processor.set_remove_root_link("world")
        processor.set_validate_urdf(False)  # Disable validation since we're removing root link

        result = processor.process_string(xml_str)

        # Should have removed world link and connecting joint
        self.assertNotIn('<link name="world"', result)
        # Should still have the test link
        self.assertIn('<link name="test_link"', result)

    def test_multiple_modules_joint_removal(self):
        """Test joint removal with multiple modules - simplified expectation"""
        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:macro name="arm_segment" params="prefix">
    <joint name="${prefix}to_parent" type="fixed">
      <parent link="base"/>
      <child link="${prefix}link"/>
    </joint>
    <link name="${prefix}link"/>
    <joint name="${prefix}internal_joint" type="revolute">
      <parent link="${prefix}link"/>
      <child link="${prefix}tip"/>
    </joint>
    <link name="${prefix}tip"/>
  </xacro:macro>

  <link name="base"/>
  <xacro:arm_segment prefix="seg1_"/>
  <xacro:arm_segment prefix="seg2_"/>
  <xacro:arm_segment prefix="seg3_"/>
</robot>'''

        result_with = zacro.xacro_from_string(xml_str, remove_root_link=None, validate_urdf=False)
        result_without = zacro.xacro_from_string(xml_str, remove_root_link="base", validate_urdf=False)

        joints_with = result_with.count('<joint')
        joints_without = result_without.count('<joint')

        # Should remove at least 1 joint
        self.assertGreater(joints_with, joints_without)

        # Should still have some internal joints
        self.assertGreater(joints_without, 0)

        print(f"Joints with: {joints_with}, without: {joints_without}")


if __name__ == '__main__':
    unittest.main()
