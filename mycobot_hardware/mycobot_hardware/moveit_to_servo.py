#!/usr/bin/env python3
"""
Description:
    Subscribes to /joint_states, converts radians to degrees,
    and sends joint angles to ESP32 via serial (PCA9685 -> Servos)
    Only sends data when joint angles change more than 0.5 degrees.
--------
Subscribing Topics:
    /joint_states - sensor_msgs/msg/JointState
--------
Author: Chirag Khanna
Date: April 22, 2026
"""

#!/usr/bin/env python3
"""
Subscribes to /joint_states, converts radians to degrees,
and sends joint angles to ESP32 via serial (PCA9685 -> Servos)
Only sends data when joint angles change more than 0.5 degrees.
"""
import math
import serial
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class SerialReader(Node):
    def __init__(self):
        super().__init__("serial_reader")

        self.declare_parameter("port", "/dev/ttyUSB0")
        self.declare_parameter("baudrate", 115200)
        port     = self.get_parameter("port").value
        baudrate = self.get_parameter("baudrate").value

        # Corrected joint names from /joint_states
        self.joint_channel_map = {
            "gear01": 0,  # CH0 - base gear
            "link01": 1,  # CH1
            "link02": 2,  # CH2
            "link03": 3,  # CH3
            "link04": 4,  # CH4
            "link05": 5,  # CH5
        }

        # Per-joint servo center offset — tune these per your mechanical zero
        self.joint_offsets = {
            "gear01": 90.0,
            "link01": 90.0,
            "link02": 90.0,
            "link03": 90.0,
            "link04": 90.0,
            "link05": 90.0,
        }

        self.last_angles = None
        self.CHANGE_THRESHOLD = 0.5  # degrees

        try:
            self.esp32 = serial.Serial(port=port, baudrate=baudrate, timeout=0.1)
            self.get_logger().info(f"Connected to ESP32 on {port} at {baudrate} baud")
        except serial.SerialException as e:
            self.get_logger().error(f"Failed to open port {port}: {e}")
            raise SystemExit(1)

        self.sub = self.create_subscription(
            JointState,
            "/joint_states",
            self.joint_state_callback,
            10
        )
        self.get_logger().info("Waiting for /joint_states...")

    def angles_changed(self, new_angles):
        if self.last_angles is None:
            return True
        return any(abs(a - b) > self.CHANGE_THRESHOLD
                   for a, b in zip(new_angles, self.last_angles))

    def joint_state_callback(self, msg: JointState):
        try:
            angles = [90.0] * len(self.joint_channel_map)

            for i, name in enumerate(msg.name):
                if name in self.joint_channel_map:
                    ch = self.joint_channel_map[name]
                    offset = self.joint_offsets.get(name, 90.0)
                    deg = math.degrees(msg.position[i]) + offset
                    angles[ch] = max(0.0, min(180.0, round(deg, 2)))

            if not self.angles_changed(angles):
                return

            self.last_angles = angles
            data = "J:" + ",".join(str(a) for a in angles) + "\n"
            self.esp32.write(data.encode())
            self.get_logger().info(f"Sent: {data.strip()}")

        except Exception as e:
            self.get_logger().error(f"Error in callback: {e}")

    def destroy_node(self):
        if hasattr(self, 'esp32') and self.esp32.is_open:
            self.esp32.close()
            self.get_logger().info("Serial port closed.")
        super().destroy_node()


def main():
    rclpy.init()
    node = SerialReader()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()