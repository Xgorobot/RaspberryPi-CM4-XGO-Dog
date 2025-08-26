# Raspberry-CM4-XGO-DOG

XGO-DOG, an interesting four-legged bionic robot dog.

# Choose Language / 选择语言

- [中文](README.md)
- [English](#README_en.md)

## Table of Contents

- [Project Introduction](#project-introduction)
- [Installation and Usage](#installation-and-usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Project Introduction

XGO-DOG is a twelve-degree-of-freedom desktop-level AI robot dog, equipped with a mechanical arm and gripper on its back. It uses a Raspberry Pi CM4 module for AI edge computing applications. The robot uses 4.5KG.CM all-metal magnetic encoding bus serial servo motors as joints, capable of omnidirectional movement, six-degree-of-freedom posture control, stability, various motion gaits, and gripping tasks. The robot is equipped with IMU, joint position sensors, and current sensors to feedback its posture, joint angles, and torque for internal algorithms and secondary development. It supports both Python programming and ROS programming.

## Directory Structure

- **RaspberryPi-CM4-main**: Main program folder
  - **demos**: Example programs
    - **expression**: Emoji files
    - **music**: Audio files
    - **speechCn**: Chinese speech recognition
    - **speechEn**: English speech recognition
    - **xiaozhi**: Xiaozhi real-time voice interaction
  - **flacksocket**: Graphical transmission and control of the robot through flacksocket
  - **language**: Language configuration information
  - **pics**: Image files
  - **volume**: Volume configuration information

## Installation and Usage

1. Clone this repository:
    ```bash
    git clone https://github.com/Xgorobot/RaspberryPi-CM4-XGO-Dog.git
    ```

2. Enter the project directory:
    ```bash
    cd RaspberryPi-CM4-main
    ```

3. Run main.py:
    ```bash
    sudo python3 main.py
    ```

## Features

1. **Web remote control**: Visualization control based on flacksocket.
2. **Voice interaction**: Voice interaction based on the Volcano large model.
3. **Xiaozhi interaction**: Fun interactions with Xiaozhi.

## 📜 Change Log

### 2025-04-14
- **Code Improvement**: Optimized the language switching in `/RaspberryPi-CM4-main/demos/language.py` so that language switching can be done without restarting the entire system.
- **New Features**: Added the `update.sh` script, which optimizes system startup time.

### 2025-05-18
- **Code Improvement**:
  1. Optimized color recognition in `/RaspberryPi-CM4-main/demos/color.py` for better sensitivity and accuracy.
  2. Improved fingertip recognition in `/RaspberryPi-CM4-main/demos/hp.py` for better sensitivity.
  3. Enhanced `/RaspberryPi-CM4-main/demos/qrcode.py` to automatically wrap lines when recognizing long strings of characters.
  4. Updated configuration information in `/RaspberryPi-CM4-main/demos/device.py`.

- **New Features**:
  1. Added `/RaspberryPi-CM4-main/demos/ball.py`, an automatic ball grabbing function.
  2. Added `/RaspberryPi-CM4-main/demos/dog_Joystick.py`, joystick control feature.
  3. Added `/RaspberryPi-CM4-main/demos/follow_line.py`, automatic line-following function.
  4. Added `/RaspberryPi-CM4-main/demos/xiaozhi_test`, Xiaozhi's embodied intelligence and interactive conversation features.
  5. Added `/RaspberryPi-CM4-main/demos/speech/ei.py`, which implements embodied intelligence.
  6. Added `/RaspberryPi-CM4-main/demos/speech/coze.py`, which implements embodied intelligence for intelligent agents.

- **Special Reminder**:
  1. In `/RaspberryPi-CM4-main/demos/speech/coze.py`, the default API for this feature is valid for 30 days. If it expires, you need to create an API using your own account. Please refer to the documentation in Yuque for the creation process.
  2. After using Xiaozhi, intelligent agents, embodied intelligence, or speech recognition functions, the system requires 3-4 seconds to release resources. Please do not reopen any of these features immediately after use, as this may cause functional abnormalities.

### 2025-06-05
- **Code Improvement**:
  1. Optimized the UI parts of `/RaspberryPi-CM4-main/demos/speech/ei.py`, `/RaspberryPi-CM4-main/demos/speech/coze.py`, and `/RaspberryPi-CM4-main/demos/speech/speech.py` that are not connected to the internet.
  2. Re-uploaded some icons.

## Contributing

We welcome contributions! Any suggestions, fixes, and feature enhancements are appreciated. If you are interested in contributing to this project, please follow these steps:

1. Fork this repository
2. Create your own branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to your branch (`git push origin feature-branch`)
5. Submit a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgements

Special thanks to the following contributors:

- Liu Pengfei Robotics
- jd3096
- Zhang Yilong (YIL Zhang)
- Wang Yunxin (KEENNESS19)

If you encounter any issues while using this project, feel free to submit Issues or Pull Requests!
