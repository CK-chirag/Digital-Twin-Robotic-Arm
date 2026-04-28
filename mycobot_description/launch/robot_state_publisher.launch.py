#!/usr/bin/env python3
"""
Launch RViz visualization for the mycobot robot.

This launch file sets up the complete visualization environment for the mycobot robot,
including robot state publisher, joint state publisher, and RViz2. It handles loading
and processing of URDF/XACRO files and controller configurations.

:author: Chirag Khanna
:date: April 22, 2026
"""

import os
from pathlib import Path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def process_ros2_controllers_config(context):
    """Process the ROS2 controller configuration yaml before loading the URDF."""

    prefix      = LaunchConfiguration('prefix').perform(context)
    flange_link = LaunchConfiguration('flange_link').perform(context)
    # robot_name is kept for replacement logic if needed, but removed from paths
    home        = str(Path.home())

    # Search in all potential workspace names
    for ws_name in ['arm_5dof_ws', 'arm_ws', 'arm_ws_new']:
        src_config_path = os.path.join(
            home, f'{ws_name}/src/mycobot_ros2/mycobot_moveit_config/config')
        
        install_config_path = os.path.join(
            home, f'{ws_name}/install/mycobot_moveit_config/share/mycobot_moveit_config/config')

        template_path = os.path.join(src_config_path, 'ros2_controllers_template.yaml')
        
        # Check if the template exists in this workspace
        if not os.path.exists(template_path):
            continue

        # Read the template
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Perform the variable replacements
        content = content.replace('${prefix}', prefix)
        content = content.replace('${flange_link}', flange_link)

        # Write the processed file to both src and install (to ensure persistence)
        for config_path in [src_config_path, install_config_path]:
            if os.path.exists(os.path.dirname(config_path)): # Check if workspace exists
                os.makedirs(config_path, exist_ok=True)
                target_file = os.path.join(config_path, 'ros2_controllers.yaml')
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(content)

    return []


# ── Launch arguments ────────────────────────────────────────────────────────
ARGUMENTS = [
    DeclareLaunchArgument(
        'robot_name', default_value='mycobot_280'),
    DeclareLaunchArgument(
        'prefix', default_value=''),
    DeclareLaunchArgument(
        'add_world', default_value='true',
        choices=['true', 'false']),
    DeclareLaunchArgument(
        'base_link', default_value='base_link'),
    DeclareLaunchArgument(
        'flange_link', default_value='link_5'),
    DeclareLaunchArgument(
        'use_camera', default_value='false',
        choices=['true', 'false']),
    DeclareLaunchArgument(
        'use_gazebo', default_value='false',
        choices=['true', 'false']),
]


def generate_launch_description():

    urdf_package         = 'mycobot_description'
    # CHANGED: Now using assembled_arm.urdf.xacro as the top-level file
    urdf_filename        = 'assembled_arm.urdf.xacro'
    rviz_config_filename = 'mycobot_280_description.rviz'

    pkg_share = FindPackageShare(urdf_package)

    default_rviz_config = PathJoinSubstitution([pkg_share, 'rviz', rviz_config_filename])
    # PATH UPDATED: Based on your screenshot, it is in urdf/robots/
    default_urdf_path   = PathJoinSubstitution([pkg_share, 'urdf', 'robots', urdf_filename])

    jsp_gui      = LaunchConfiguration('jsp_gui')
    rviz_config  = LaunchConfiguration('rviz_config_file')
    urdf_model   = LaunchConfiguration('urdf_model')
    use_jsp      = LaunchConfiguration('use_jsp')
    use_rviz     = LaunchConfiguration('use_rviz')
    use_sim_time = LaunchConfiguration('use_sim_time')

    declare_jsp_gui = DeclareLaunchArgument(
        'jsp_gui', default_value='true', choices=['true', 'false'],
        description='Enable joint_state_publisher_gui')

    declare_rviz_config = DeclareLaunchArgument(
        'rviz_config_file', default_value=default_rviz_config)

    declare_urdf_model = DeclareLaunchArgument(
        'urdf_model', default_value=default_urdf_path)

    declare_use_jsp = DeclareLaunchArgument(
        'use_jsp', default_value='false', choices=['true', 'false'])

    declare_use_rviz = DeclareLaunchArgument(
        'use_rviz', default_value='true')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='false')

    # robot_description via xacro
    robot_description_content = ParameterValue(Command([
        'xacro', ' ', urdf_model,        ' ',
        'robot_name:=',  LaunchConfiguration('robot_name'),  ' ',
        'prefix:=',      LaunchConfiguration('prefix'),      ' ',
        'add_world:=',   LaunchConfiguration('add_world'),   ' ',
        'base_link:=',   LaunchConfiguration('base_link'),   ' ',
        'flange_link:=', LaunchConfiguration('flange_link'), ' ',
        'use_camera:=',  LaunchConfiguration('use_camera'),  ' ',
        'use_gazebo:=',  LaunchConfiguration('use_gazebo'),
    ]), value_type=str)

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time':      use_sim_time,
            'robot_description': robot_description_content,
        }])

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(use_jsp))

    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(jsp_gui))

    rviz2 = Node(
        condition=IfCondition(use_rviz),
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}])

    ld = LaunchDescription(ARGUMENTS)

    ld.add_action(OpaqueFunction(function=process_ros2_controllers_config))
    ld.add_action(declare_jsp_gui)
    ld.add_action(declare_rviz_config)
    ld.add_action(declare_urdf_model)
    ld.add_action(declare_use_jsp)
    ld.add_action(declare_use_rviz)
    ld.add_action(declare_use_sim_time)
    ld.add_action(joint_state_publisher)
    ld.add_action(joint_state_publisher_gui)
    ld.add_action(robot_state_publisher)
    ld.add_action(rviz2)

    return ld