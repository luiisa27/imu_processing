# ROS 2 IMU Data Processing Pipeline (`imu_processing`)

ROS 2 Humble Python package for real-time IMU data acquisition, signal filtering, and quaternion orientation publishing from an MPU-6050 sensor driven by an ESP32 micro-controller.

## 🚀 System Architecture

```text
[ MPU-6050 IMU ] ──(I2C)──► [ ESP32 Microcontroller ]
                                      │
                              (USB Serial / UART)
                                      ▼
[ WSL2 / Ubuntu 22.04 ] ──► [ PySerial (Non-blocking) ]
                                      │
                                      ▼
                            [ ROS 2 Node (50Hz) ]
                                      │
                             (/imu/data Topic)
                                      ▼
                            [ 3D RViz2 Display ]
# Clone repository inside your ROS 2 workspace
cd ~/ros2_ws/src
git clone [https://github.com/luiisa27/imu_processing.git](https://github.com/luiisa27/imu_processing.git)

# Build package
cd ~/ros2_ws
colcon build --packages-select imu_processing
source install/setup.bash

# Configure serial interface (WSL2 / Linux)
stty -F /dev/ttyACM0 115200 raw -echo
sudo chmod 666 /dev/ttyACM0

# Launch node
ros2 run imu_processing imu_node
