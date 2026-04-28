#!/bin/bash
# Master script to launch myCobot 5-DOF with Gazebo, Controllers, and MoveIt 2

# Colors for better terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

cleanup() {
    echo -e "${BLUE}Cleaning up ROS 2 and Gazebo processes...${NC}"
    # Kill all related processes
    pkill -9 -f "ros2|gazebo|gz|rviz2|robot_state_publisher|moveit|move_group"
    # Wait for everything to shut down
    sleep 2
    echo -e "${GREEN}Cleanup complete.${NC}"
}

# Set up cleanup trap
trap 'cleanup' SIGINT SIGTERM

echo -e "${BLUE}1. Launching Gazebo simulation with Bullet Physics...${NC}"
# Note: We use --physics-engine to avoid the mimic joint constraint errors in DART
ros2 launch mycobot_gazebo mycobot.gazebo.launch.py \
    load_controllers:=true \
    world_file:=pick_and_place_demo.world \
    use_camera:=true \
    use_rviz:=false \
    use_robot_state_pub:=true \
    use_sim_time:=true \
    x:=0.0 y:=0.0 z:=0.03 \
    gz_args:="--physics-engine gz-physics-bullet-featherstone-plugin" &

echo "Waiting for Gazebo to initialize (20s)..."
sleep 20

# Active check for Controller Manager
echo -e "${BLUE}2. Checking Controller Manager status...${NC}"
until ros2 control list_controllers > /dev/null 2>&1; do
  echo "Still waiting for controller_manager service..."
  sleep 2
done
echo -e "${GREEN}Controller Manager is UP.${NC}"

echo -e "${BLUE}3. Launching MoveIt 2 (The Brain)...${NC}"
ros2 launch mycobot_moveit_config moveit.launch.py use_sim_time:=true &

# Give MoveIt a moment to load the SRDF and Planning Scene
sleep 10

echo -e "${BLUE}4. Adjusting Gazebo Camera View...${NC}"
gz service -s /gui/move_to/pose \
    --reqtype gz.msgs.GUICamera \
    --reptype gz.msgs.Boolean \
    --timeout 2000 \
    --req "pose: {position: {x: 1.36, y: -0.58, z: 0.95} orientation: {x: -0.26, y: 0.1, z: 0.89, w: 0.35}}"

echo -e "${GREEN}System is ready. Use MoveIt RViz to plan trajectories.${NC}"

# Keep the script running until Ctrl+C
wait