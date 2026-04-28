# 5-DOF Digital Twin Robotic Arm (ROS 2 + MoveIt)
<p align="center">
  <img src="https://github.com/user-attachments/assets/ff0b0b4c-46e9-4cda-803a-bc5f429e98eb" width="48%" />
  <img src="https://github.com/user-attachments/assets/d9877f2e-458a-4f34-bead-6b4cf45cd684" width="48%" />
</p>

## Overview
This project presents a 5-DOF robotic arm integrated with a digital twin using ROS 2, MoveIt 2, and Gazebo. The system enables motion planning in a simulated environment and executes the planned trajectories on a physical robotic arm in real time via serial communication.

The robotic arm is a servo-driven manipulator designed for lightweight pick-and-place and research applications. It consists of five revolute joints providing sufficient flexibility for basic manipulation tasks, along with an end-effector for object interaction.

---

## Features
- 5-DOF articulated robotic arm
- Digital twin in Gazebo and RViz
- Motion planning using MoveIt 2
- Real-time synchronization between simulation and hardware
- Serial communication interface for hardware control
- Modular ROS 2 package structure

---

## System Architecture
- **Simulation Layer:** Gazebo (physics) and RViz (visualization)
- **Planning Layer:** MoveIt 2 motion planning framework
- **Execution Layer:** ROS 2 node for trajectory-to-serial communication
- **Hardware Layer:** Servo-based 5-DOF robotic arm

---

## Requirements
- ROS 2 (Jazzy or compatible)
- MoveIt 2
- Gazebo
- Python 3
- Serial communication support

---

## Usage

### 1. Launch Simulation, RViz, and MoveIt
```bash
bash src/mycobot_ros2/mycobot_bringup/scripts/mycobot_gazebo_rviz_moveit.sh
```

### 2. Connect and control the real hardware
```bash
ros2 run mycobot_hardware moveit_to_serial.py --ros-args -p port:=/dev/ttyUSB0 -p baudrate:=115200
```

### Future Work (that i am working on)
- Integration of Mediapipe to control it with hand gestures
