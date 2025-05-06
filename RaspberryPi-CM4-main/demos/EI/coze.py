'''
pip install cozepy
https://www.coze.cn/home,程序中的coze_api_token会过期，用户需要自己去注册（免费）
'''
from PIL import Image, ImageDraw, ImageFont
import xgoscreen.LCD_2inch as LCD_2inch
import logging

display = LCD_2inch.LCD_2inch()
display.clear()
splash_theme_color = (15, 21, 46)
splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
font2 = ImageFont.truetype("/home/pi/model/msyh.ttc", 16)
draw = ImageDraw.Draw(splash)
display.ShowImage(splash)

import sys

# 获取 vosk 模块的安装路径，根据实际情况修改
vosk_path = '/home/pi/.local/lib/python3.9/site-packages'

# 检查路径是否已经在 sys.path 中，如果不在则添加
if vosk_path not in sys.path:
    sys.path.append(vosk_path)
# -Large model call-#
import os
import ast
from volcenginesdkarkruntime import Ark

from cozepy import Coze, TokenAuth, BotPromptInfo, Message, ChatEventType, MessageContentType, \
    COZE_CN_BASE_URL  # 忽略代码检查工具对该行import的警告
def model_output(content):
    coze_api_token = 'pat_rdTYS4U5jVUlnNfEWVPFl7TwmrWtw3Im9IBEzZedR6hVPp5bHfV41e9ewjsk7Xw3'

    # 初始化Coze客户端
    coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=COZE_CN_BASE_URL)

    bot_id = '7491285379560177664'
    user_id = '123'
    # 调用coze.chat.stream方法创建一个聊天会话。此创建方法是流式聊天，会返回一个聊天迭代器。
    # 开发者应迭代该迭代器以获取聊天事件并进行处理
    chat_poll = coze.chat.create_and_poll(
        bot_id=bot_id,
        user_id=user_id,
        additional_messages=[
            # 构建用户提问消息
            Message.build_user_question_text(content)
        ],
    )
    result = chat_poll.messages[0].content
    result = ast.literal_eval(result)
    return result


# -Wake Word Detection-#
from libnyumaya import AudioRecognition, FeatureExtractor
from auto_platform import AudiostreamSource, play_command
import time
import os
from datetime import datetime

from vosk import Model, KaldiRecognizer

model_path = "/home/pi/RaspberryPi-CM4-main/demos/EI/vosk-model-small-cn-0.22/"
wake_word1 = "你好"
wake_word2 = '您好'
model = Model(model_path)


# def wake_up(stream, rate, chunk_size):
#     break_luyin = False
#     audio_stream = AudiostreamSource()
#     libpath = "/home/pi/RaspberryPi-CM4-main/demos/EI/src/libnyumaya_premium.so.3.1.0"
#     extractor = FeatureExtractor(libpath)
#     detector = AudioRecognition(libpath)
#     extactor_gain = 1.0
#     keywordIdlulu = detector.addModel("/home/pi/RaspberryPi-CM4-main/demos/EI/src/lulu_v3.1.907.premium", 0.7)
#     bufsize = detector.getInputDataSize()
#     rec = KaldiRecognizer(model, rate)
#     audio_stream.start()
#     while True:
#         frame = audio_stream.read(bufsize * 2, bufsize * 2)
#         data = stream.read(chunk_size)
#         if rec.AcceptWaveform(data):
#             result = rec.Result()
#             text = eval(result)["text"]
#             print(text)
#             if wake_word1 in text or wake_word2 in text:
#                 print("唤醒词已检测到！")
#                 return 1
#         if not frame:
#             time.sleep(0.01)
#             continue
#         features = extractor.signalToMel(frame, extactor_gain)
#         prediction = detector.runDetection(features)
#         if prediction != 0:
#             now = datetime.now().strftime("%d.%b %Y %H:%M:%S")
#             if prediction == keywordIdlulu:
#                 print("唤醒成功" + "lulu detected:" + now)
#                 #os.system(play_command + " /home/pi/RaspberryPi-CM4-main/demos/src/ding.wav")
#                 return 1
def wake_up(p, rate, chunk_size):
    break_luyin = False
    audio_stream = AudiostreamSource()
    libpath = "/home/pi/RaspberryPi-CM4-main/demos/EI/src/libnyumaya_premium.so.3.1.0"
    extractor = FeatureExtractor(libpath)
    detector = AudioRecognition(libpath)
    extactor_gain = 1.0
    keywordIdlulu = detector.addModel("/home/pi/RaspberryPi-CM4-main/demos/EI/src/lulu_v3.1.907.premium", 0.7)
    bufsize = detector.getInputDataSize()
    audio_stream.start()
    rec = KaldiRecognizer(model, rate)

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk_size)

    while True:
        try:
            frame = audio_stream.read(bufsize * 2, bufsize * 2)
            data = stream.read(chunk_size, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                result = rec.Result()
                text = eval(result)["text"]
                print(text)
                if wake_word1 in text or wake_word2 in text:
                    print("唤醒词已检测到！")
                    stream.stop_stream()
                    stream.close()
                    return 1
            if not frame:
                time.sleep(0.01)
                continue
            features = extractor.signalToMel(frame, extactor_gain)
            prediction = detector.runDetection(features)
            if prediction != 0:
                now = datetime.now().strftime("%d.%b %Y %H:%M:%S")
                if prediction == keywordIdlulu:
                    print("唤醒成功" + "lulu detected:" + now)
                    # os.system(play_command + " /home/pi/RaspberryPi-CM4-main/demos/src/ding.wav")
                    audio_stream.stop()
                    stream.stop_stream()
                    stream.close()
                    return 1
            time.sleep(0.01)  # 降低睡眠时间，提高读取频率
        except OSError as e:
            if e.errno == -9981:
                print("Input overflowed, cleaning buffer...")
                stream.stop_stream()
                stream.close()
                stream = p.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=rate,
                                input=True,
                                frames_per_buffer=chunk_size)
            else:
                raise

    return 0


action_id = {'趴下': 1, '站起': 2, '匍匐前进': 3, '转圈': 4, '原地踏步': 5, '蹲起': 6, '沿x转动': 7, '沿y转动': 8,
             '沿z转动': 9, '三轴转动': 10, '撒尿': 11, '坐下': 12, '招手': 13, '伸懒腰': 14,
             '波浪运动': 15, '摇摆运动': 16, '求食': 17, '找食物': 18, '握手': 19, '展示机械臂': 20, '俯卧撑': 21,
             '张望': 22, '跳舞': 23, '调皮': 24}
time_list = [3, 3, 5, 5, 4, 4, 4, 4, 4, 7, 7, 5, 7, 10, 6, 6, 6, 6, 10, 9, 8, 8, 6, 7]

import os, re
from xgolib import XGO
import cv2
import os, socket, sys, time
import spidev as SPI
from key import Button
import threading
import json, base64
import subprocess
import pyaudio
import wave
import numpy as np
from datetime import datetime
from audio import start_recording
from language_recognize import test_one

# -Dog Robot Initialization-#
dog = XGO(port='/dev/ttyAMA0', version="xgomini")
fm = dog.read_firmware()
if fm[0] == 'M':
    print('XGO-MINI')
    dog = XGO(port='/dev/ttyAMA0', version="xgomini")
    dog_type = 'M'
else:
    dog = XGO(port='/dev/ttyAMA0', version="xgolite")
    print('XGO-LITE')
    dog_type = 'L'
if dog_type == 'L':
    mintime_yaw = 0.8
    mintime_x = 0.1
else:
    mintime_yaw = 0.7
    mintime_x = 0.3
button = Button()


# -Screen Initialization-#


def lcd_draw_string(
        splash,
        x,
        y,
        text,
        color=(255, 255, 255),
        font_size=16,
        max_width=220,
        max_lines=5,
        clear_area=False
):
    font = ImageFont.truetype("/home/pi/model/msyh.ttc", font_size)

    line_height = font_size + 2
    total_height = max_lines * line_height

    if clear_area:
        draw.rectangle((x, y, x + max_width, y + total_height), fill=(15, 21, 46))
    lines = []
    current_line = ""
    for char in text:
        test_line = current_line + char
        if font.getlength(test_line) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = char
    if current_line:
        lines.append(current_line)
    if max_lines:
        lines = lines[:max_lines]

    for i, line in enumerate(lines):
        splash.text((x, y + i * line_height), line, fill=color, font=font)


# -Dog Robot Speed Adjustment-#
def adaptive_move(distance):
    if distance < 15:
        speed = 10
    elif distance < 30:
        speed = 15
    else:
        speed = 20
    return speed


def adaptive_turn(yaw):
    if dog_type == 'M':
        if yaw < 20:
            turn_speed = 10
        elif yaw < 50:
            turn_speed = 20
        else:
            turn_speed = 30
        return turn_speed
    else:
        turn_speed = 30
        return turn_speed


p = pyaudio.PyAudio()
# -Record parameter-#
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)


def check_exit():
    while True:
        if button.press_b():
            print("Button B Pressed")
            try:
                stream.stop_stream()
                stream.close()
            except Exception as e:
                print('音频流未打开')
            p.terminate()
            os._exit(0)


threading.Thread(target=check_exit, daemon=True).start()
while True:
    print("等待唤醒词")
    splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
    draw = ImageDraw.Draw(splash)
    draw.rectangle([0, 0, display.width, display.height], fill=(15, 21, 46))
    text_color = (255, 255, 255)
    color = (102, 178, 255)
    gray_color = (128, 128, 128)
    rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
    rectangle_y = 50  # 矩形条y坐标
    rectangle_width = 200
    rectangle_height = 30
    draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                   fill=color)
    draw.text((rectangle_x + 70, rectangle_y + 5), '等待唤醒', fill=text_color, font=font2)
    rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
    rectangle_y = 100  # 矩形条y坐标
    rectangle_width = 200
    rectangle_height = 100
    draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                   fill=gray_color)
    lcd_draw_string(
        draw,
        x=70,
        y=105,
        text="请说“你好,lulu”",
        color=(255, 255, 255),
        font_size=16,
        max_width=190,
        max_lines=5,
        clear_area=False
    )
    display.ShowImage(splash)
    wake = wake_up(p, RATE, CHUNK)
    if wake:
        splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
        draw = ImageDraw.Draw(splash)
        text_color = (255, 255, 255)
        color = (102, 178, 255)
        gray_color = (128, 128, 128)
        rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
        rectangle_y = 50  # 矩形条y坐标
        rectangle_width = 200
        rectangle_height = 30
        draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                       fill=color)
        draw.text((rectangle_x + 70, rectangle_y + 5), '下达指令', fill=text_color, font=font2)
        rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
        rectangle_y = 100  # 矩形条y坐标
        rectangle_width = 200
        rectangle_height = 100
        draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                       fill=gray_color)
        lcd_draw_string(
            draw,
            x=70,
            y=105,
            text="唤醒成功,请给出运动指令",
            color=(255, 255, 255),
            font_size=16,
            max_width=190,
            max_lines=5,
            clear_area=False
        )
        display.ShowImage(splash)
        print("唤醒成功")
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        stream.stop_stream()
        time.sleep(0.1)
        stream.start_stream()
        start_recording(p, stream)
        # start_recording()
    try:
        content = test_one()
        print(content)
    except Exception as e:
        print(f'发生未知错误: {e}')
        splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
        draw = ImageDraw.Draw(splash)
        text_color = (255, 255, 255)
        color = (102, 178, 255)
        gray_color = (128, 128, 128)
        rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
        rectangle_y = 50  # 矩形条y坐标
        rectangle_width = 200
        rectangle_height = 30
        draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                       fill=color)
        draw.text((rectangle_x + 70, rectangle_y + 5), '识别错误', fill=text_color, font=font2)
        rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
        rectangle_y = 100  # 矩形条y坐标
        rectangle_width = 200
        rectangle_height = 100
        draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                       fill=gray_color)
        lcd_draw_string(
            draw,
            x=70,
            y=105,
            text="语音识别错误，请重试",
            color=(255, 255, 255),
            font_size=16,
            max_width=190,
            max_lines=5,
            clear_area=False
        )
        display.ShowImage(splash)
        time.sleep(2)
        continue
    if content == 0:
        print('识别失败')
        splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
        draw = ImageDraw.Draw(splash)
        text_color = (255, 255, 255)
        color = (102, 178, 255)
        gray_color = (128, 128, 128)
        rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
        rectangle_y = 50  # 矩形条y坐标
        rectangle_width = 200
        rectangle_height = 30
        draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                       fill=color)
        draw.text((rectangle_x + 70, rectangle_y + 5), '识别错误', fill=text_color, font=font2)
        rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
        rectangle_y = 100  # 矩形条y坐标
        rectangle_width = 200
        rectangle_height = 100
        draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                       fill=gray_color)
        lcd_draw_string(
            draw,
            x=70,
            y=105,
            text="语音识别错误，请重试",
            color=(255, 255, 255),
            font_size=16,
            max_width=190,
            max_lines=5,
            clear_area=False
        )
        display.ShowImage(splash)
        time.sleep(2)
        continue
    else:
        print(content)
        splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
        draw = ImageDraw.Draw(splash)
        text_color = (255, 255, 255)
        color = (102, 178, 255)
        gray_color = (128, 128, 128)
        rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
        rectangle_y = 50  # 矩形条y坐标
        rectangle_width = 200
        rectangle_height = 30
        draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                       fill=color)
        draw.text((rectangle_x + 70, rectangle_y + 5), '指令内容', fill=text_color, font=font2)
        rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
        rectangle_y = 100  # 矩形条y坐标
        rectangle_width = 200
        rectangle_height = 100
        draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                       fill=gray_color)
        lcd_draw_string(
            draw,
            x=70,
            y=105,
            text=content,
            color=(255, 255, 255),
            font_size=16,
            max_width=190,
            max_lines=5,
            clear_area=False
        )
        display.ShowImage(splash)
        try:
            result = model_output(content=content)
            logging.warning(result)
        except Exception as e:
            print(f'发生未知错误: {e}')
            splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
            draw = ImageDraw.Draw(splash)
            text_color = (255, 255, 255)
            color = (102, 178, 255)
            gray_color = (128, 128, 128)
            rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
            rectangle_y = 50  # 矩形条y坐标
            rectangle_width = 200
            rectangle_height = 30
            draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                           fill=color)
            draw.text((rectangle_x + 70, rectangle_y + 5), '识别错误', fill=text_color, font=font2)
            rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
            rectangle_y = 100  # 矩形条y坐标
            rectangle_width = 200
            rectangle_height = 100
            draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                           fill=gray_color)
            lcd_draw_string(
                draw,
                x=70,
                y=105,
                text="指令识别错误，请重试",
                color=(255, 255, 255),
                font_size=16,
                max_width=190,
                max_lines=5,
                clear_area=False
            )
            display.ShowImage(splash)
            time.sleep(2)
            continue
        try:
            for i in result:
                print(i[0])
                if i[0] == 'x' or i[0] == 'y':
                    speed = adaptive_move(int(i[1]))
                    dog.move(i[0], speed * int(i[1]) / abs(int(i[1])))
                    time.sleep(abs(int(i[1] / speed)))
                    dog.stop()
                    time.sleep(0.5)
                elif i[0] == 'turn':
                    if dog_type == 'L':
                        i[1] = 3 * int(i[1])
                    turn_speed = adaptive_turn(int(i[1]))
                    dog.turn(turn_speed * int(i[1]) / abs(int(i[1])))
                    time.sleep(abs(int(i[1] / turn_speed)))
                    dog.stop()
                    time.sleep(0.5)
                elif i[0] == 'action':
                    dog.action(int(action_id[i[1]]))
                    time.sleep(int(time_list[int(action_id[i[1]]) - 1]))
                    dog.stop()
                    time.sleep(0.5)
                elif i[0] == 'pace':
                    dog.pace(i[1])
                    time.sleep(0.2)
                elif i[0] == 'translation':
                    logging.warning(f'沿着{i[1][0]}轴平移{i[1][1]}')
                    dog.translation(i[1][0], i[1][1])
                    time.sleep(1)
                elif i[0] == 'attitude':
                    logging.warning(f'沿着{i[1][0]}轴旋转{i[1][1]}')
                    dog.attitude(i[1][0], i[1][1])
                    time.sleep(1)
                elif i[0] == 'arm':
                    dog.arm(i[1][0], i[1][1])
                    time.sleep(1)
                elif i[0] == 'claw':
                    dog.claw(i[1])
                    time.sleep(1)
                elif i[0] == 'imu':
                    dog.imu(i[1])
                    time.sleep(1)
                elif i[0] == 'perform':
                    dog.perform(i[1])
                    time.sleep(10)
                elif i[0] == 'reset':
                    dog.reset()
                    time.sleep(1)
                elif i[0] == 'motor':
                    dog.motor(i[1][0], i[1][1])
                    time.sleep(1)
                elif i[0] == 'battery':
                    print(dog.read_battery())
                    time.sleep(1)
                elif i[0] == '重试':
                    continue
                elif i[0] == '退出':
                    print('退出')
                    exit()
                else:
                    continue
        except Exception as e:
            print(f'发生未知错误: {e}')
            splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
            draw = ImageDraw.Draw(splash)
            text_color = (255, 255, 255)
            color = (102, 178, 255)
            gray_color = (128, 128, 128)
            rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
            rectangle_y = 50  # 矩形条y坐标
            rectangle_width = 200
            rectangle_height = 30
            draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                           fill=color)
            draw.text((rectangle_x + 70, rectangle_y + 5), '指令错误', fill=text_color, font=font2)
            rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
            rectangle_y = 100  # 矩形条y坐标
            rectangle_width = 200
            rectangle_height = 100
            draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                           fill=gray_color)
            lcd_draw_string(
                draw,
                x=70,
                y=105,
                text="指令识别错误，请重试",
                color=(255, 255, 255),
                font_size=16,
                max_width=190,
                max_lines=5,
                clear_area=False
            )
            display.ShowImage(splash)
            time.sleep(2)
            continue


