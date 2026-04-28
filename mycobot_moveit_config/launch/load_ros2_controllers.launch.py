#!/usr/bin/env python3
"""
Sequentially launches the ROS 2 controllers for the mycobot arm and gripper.
Includes a delay to ensure Gazebo's controller manager is ready.
"""

from launch import LaunchDescription
from launch.actions import ExecuteProcess, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit


def generate_launch_description():
    controller_manager_timeout = '120'
    # Use the relative name so it resolves correctly in Gazebo
    controller_manager_name = 'controller_manager'

    def spawn_if_not_active(controller_name):
        check_and_spawn_cmd = (
            f"if ros2 control list_controllers --controller-manager {controller_manager_name} 2>/dev/null "
            f"| grep -E '^\\s*{controller_name}\\b' "
            f"| grep -q '\\bactive\\b'; then "
            f"echo '[spawner_{controller_name}] already active, skipping'; "
            f"exit 0; "
            f"fi; "
            f"ros2 run controller_manager spawner {controller_name} "
            f"--controller-manager {controller_manager_name} "
            f"--controller-manager-timeout {controller_manager_timeout}"
        )

        return ExecuteProcess(
            cmd=['bash', '-lc', check_and_spawn_cmd],
            shell=False,
            output='screen')

    # 1. Joint State Broadcaster
    start_joint_state_broadcaster_cmd = spawn_if_not_active('joint_state_broadcaster')

    # 2. Arm Controller
    start_arm_controller_cmd = spawn_if_not_active('arm_controller')

    # 3. Gripper Controller
    start_gripper_controller_cmd = spawn_if_not_active('gripper_controller')

    # Add a 5-8 second delay before the very first spawner runs
    # This ensures Gazebo has finished spawning the robot and loading the plugin
    delayed_jsb_start = TimerAction(
        period=7.0,
        actions=[start_joint_state_broadcaster_cmd]
    )

    # Sequencing logic
    load_arm_controller_event = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=start_joint_state_broadcaster_cmd,
            on_exit=[start_arm_controller_cmd]))

    load_gripper_controller_event = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=start_arm_controller_cmd,
            on_exit=[start_gripper_controller_cmd]))

    ld = LaunchDescription()
    ld.add_action(delayed_jsb_start)
    ld.add_action(load_arm_controller_event)
    ld.add_action(load_gripper_controller_event)

    return ld