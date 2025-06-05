# Raspberry-CM4-XGO-DOG

XGO-DOG，一个有趣的四足仿生机器狗。

## 目录

- [项目简介](#项目简介)
- [安装和使用](#安装和使用)
- [功能特性](#功能特性)
- [贡献](#贡献)
- [许可证](#许可证)
- [致谢](#致谢)

## 项目简介

XGO-DOG一款具有十二自由度桌面级Al机器狗，背部搭载机械臂和末端夹爪，内置树莓派CM4模组实现AI边缘计算应用，采用4.5KG.CM全金属磁编码总线串口舵机作为关节，可实现全向移动、六维姿态控制、姿态稳定、多种运动步态和夹持任务，内部搭载IMU、关节位置传感器和电流传感器反馈自身姿态和关节转角与力矩，用于内部算法和二次开发。支持跨python编程和ROS编程。
## 目录结构
-  RaspberryPi-CM4-main:主程序文件夹
    - demos:示例程序
      - expression：表情符号文件
      - music：音频文件
      - speechCn：中文语音识别
      - speechEn：英语语音识别
      - xiaozhi：小智实时语音对话
    - flacksocket：通过flacksocket图形传输和控制机器人
    - language：语言配置信息
    - pics：图片文件
    - volume：音量配置信息
## 安装和使用

1. 克隆本仓库：
    ```bash
    git clone https://github.com/Xgorobot/RaspberryPi-CM4-XGO-Dog.git 
    ```

2. 进入项目目录：
    ```bash
    cd RaspberryPi-CM4-main
    ```

3. 运行main.py：
    ```bash
    sudo python3 main.py
    ```
## 功能特性
1.web遥控：基于flacksocket的可视化遥控。  
2.语音对话：基于火山大模型的语音交互。  
3.小智互动：可以和小智进行有趣互动。

## 📜 更新日志
### 2025-04-14
- **代码改进**优化了 /RaspberryPi-CM4-main/demos/language.py 的语言切换，使得不需重启整个系统即可切换语言
- **功能新增**添加了 update.sh脚本，运行此脚本可优化系统启动时间
### 2025-05-18
- **代码改进**
1. 优化了 /RaspberryPi-CM4-main/demos/color.py的颜色识别，识别更加灵敏与正确。
2. 优化了 /RaspberryPi-CM4-main/demos/hp.py的指尖识别，识别指尖更加灵敏。
3. 优化了 /RaspberryPi-CM4-main/demos/qrcode.py，在识别长串字符时可自动换行。
4. 更新了 /RaspberryPi-CM4-main/demos/device.py中的配置信息。
- **功能新增**
1. 增加了 /RaspberryPi-CM4-main/demos/ball.py，自动抓取小球功能。
2. 增加了 /RaspberryPi-CM4-main/demos/dog_Joystick.py,手柄控制功能。
3. 增加了 /RaspberryPi-CM4-main/demos/follow_line.py,自动巡线功能。
4. 增加了 /RaspberryPi-CM4-main/demos/xiaozhi_test,小智实现具身智能与趣味对话的功能。
5. 增加了 /RaspberryPi-CM4-main/demos/speech/ei.py,豆包实现具身智能的功能。
6. 增加了 /RaspberryPi-CM4-main/demos/speech/coze.py,智能体实现具身智能的功能。
- **特别提醒**
1. 在 /RaspberryPi-CM4-main/demos/speech/coze.py,此功能的默认API有效期为30天，如果失效，需要使用自己账号进行创建API，具体创建过程参考语雀文档
2. 每次使用小智、智能体、具身智能或语言识别功能后，系统需要 3~4 秒完成资源释放。在此期间，请勿立即再次打开这些功能中的任何一个，否则可能导致功能运行异常。
### 2025-06-05
- **代码改进**
1. 优化了 /RaspberryPi-CM4-main/demos/speech/ei.py, /RaspberryPi-CM4-main/demos/speech/coze.py, /RaspberryPi-CM4-main/demos/speech/speech.py,是三个功能未联网的UI部分
2. 已重新上传部分图标
## 贡献
欢迎贡献！我们欢迎任何建议、修复和功能增强。如果你有兴趣为这个项目贡献，可以按照以下步骤操作:  
1.Fork 本仓库  
2.创建你自己的分支 (git checkout -b feature-branch)  
3.提交你的修改 (git commit -m 'Add new feature')  
4.Push 到你的分支 (git push origin feature-branch)  
5.提交 Pull Request

## 许可证
此项目遵循 MIT 许可证。

## 感谢以下人员对项目的贡献：
- 刘鹏飞Robotics  
- jd3096  
- 张益龙 YIL Zhang  
- 王云馨 KEENNESS19  

如果你在使用本项目时遇到了问题，欢迎提交 Issues 或 Pull Requests!
