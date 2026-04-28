# 5-DOF Digital Twin Robotic Arm (ROS 2 + MoveIt)

<img width="1000" height="745" alt="robotic_arm" src="https://github.com/user-attachments/assets/0967396c-b3ab-4ee2-b11a-983f7ea18760" />
<img width="1600" height="904" alt="rviz_moveit_gazebo" src="https://github.com/user-attachments/assets/82bf3f3c-4e15-45b9-8e50-ab9750cd5ccc" />

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
