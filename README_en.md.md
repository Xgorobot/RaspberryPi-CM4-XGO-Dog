# Raspberry-CM4-XGO-DOG

XGO-DOG, an interesting quadruped bionic robot dog.

Select language / 选择语言:

- [中文](#中文)
- [English](#english)

## Table of Contents

- [Project Introduction](#project-introduction)
- [Installation and Usage](#installation-and-usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Project Introduction

XGO-DOG is a desktop-level AI robot dog with twelve degrees of freedom. It features a robotic arm and an end-effector claw mounted on its back. The robot integrates a Raspberry Pi CM4 module for AI edge computing. It uses 4.5KG.CM all-metal magnetic encoding bus serial servos for the joints, enabling omnidirectional movement, six-dimensional posture control, stability, various gaits, and gripping tasks. The robot is equipped with IMU, joint position sensors, and current sensors, which provide feedback on posture, joint angles, and torque for internal algorithms and secondary development. The system supports cross-Python programming and ROS programming.

## Directory Structure

-  RaspberryPi-CM4-main: Main program folder
    - demos: Example programs
      - expression: Expression files
      - music: Audio files
      - speechCn: Chinese speech recognition
      - speechEn: English speech recognition
      - xiaozhi: Xiaozhi real-time voice interaction
    - flacksocket: Graphic transmission and control of the robot via flacksocket
    - language: Language configuration files
    - pics: Image files
    - volume: Volume configuration files

## Installation and Usage

1. Clone this repository:
    ```bash
    git clone https://github.com/Xgorobot/RaspberryPi-CM4-XGO-Dog.git 
    ```

2. Navigate to the project directory:
    ```bash
    cd RaspberryPi-CM4-main
    ```

3. Run the main program:
    ```bash
    sudo python3 main.py
    ```

## Features

1. Web remote control: Visual remote control based on flacksocket.  
2. Voice interaction: Voice interaction based on Volcano large model.  
3. Xiaozhi interaction: Fun interactions with Xiaozhi.

## 📜 Changelog
### 2025-04-14
- **Code Improvement**: Optimized language switching in `/RaspberryPi-CM4-main/demos/language.py` so that the system no longer requires a restart to change languages.
- **New Feature**: Added the `update.sh` script. Running this script will optimize system boot time.

## Contributing
We welcome contributions! We are open to suggestions, fixes, and feature enhancements. If you're interested in contributing, follow these steps:  
1. Fork this repository  
2. Create your own branch (git checkout -b feature-branch)  
3. Commit your changes (git commit -am 'Add new feature')  
4. Push to your branch (git push origin feature-branch)  
5. Submit a Pull Request

## License
This project is licensed under the MIT License.

## Acknowledgments
Special thanks to the following contributors:
- Liu Pengfei (Robotics)  
- jd3096  
- Zhang Yilong (YIL Zhang)  
- Wang Yunxin (KEENNESS19)

If you encounter any issues using this project, feel free to submit Issues or Pull Requests!
