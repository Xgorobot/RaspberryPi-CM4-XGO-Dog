
'''
密钥需要环境中获取
language_recognize.py中也有一个密钥需要配置
语音控制运动，需要在联网情况下运行
每次命令需要用“你好，lulu”唤醒，然后开始给命令，支持前进，后退，左转，右转，
以及趴下,站起,转圈,匍匐前进,原地踏步,蹲起,沿x转动,沿y转动,沿z转动,三轴转动,撒尿,坐下,招手,伸懒腰,波浪运动,摇摆运动,求食,找食物,握手,展示机械臂,俯卧撑，张望，跳舞，调皮
如需添加其他功能，可以在大模型调用的prompt给出，并同步修改后续运动
可视化相关的已经注释掉
'''
from PIL import Image, ImageDraw, ImageFont
import xgoscreen.LCD_2inch as LCD_2inch
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
#-Large model call-#
import os
import ast
from volcenginesdkarkruntime import Ark
def model_output(content):
    api_key = '67e1719b-fc92-43b7-979d-3692135428a4'
    model = "doubao-1.5-pro-32k-250115"
    client = Ark(api_key = api_key)
    prompt = '''
        我接下来会给你一段话，如果有退出，停止等意思，请返回字符'退出'，如果指令存在不符合下面要求或无法理解请返回'重试',请根据以下规则对其进行处理，并以列表形式返回结果。列表格式为：  
        `[['x', step], ['y', -step], ['turn', yaw], ...]`，列表中元素都是成对出现的，各元素的含义如下：  
        1. name:'x'：表示前后移动。  
           - `step` 为正时，表示向前移动的距离。  
           - `step` 为负时，表示向后移动的距离。  
        2. name:'y'：表示左右移动。  
           - `step` 为正时，表示向左平移的距离。  
           - `step` 为负时，表示向右平移的距离。  
        3. name:'turn'：表示转向。  
           - 'yaw'：为正时，表示向左转动的角度
           - 'yaw'：为负时，表示向右转动的角度
        4. name:action
           - id:趴下,站起,匍匐前进,转圈,原地踏步,蹲起,沿x转动,沿y转动,沿z转动,三轴转动,撒尿,坐下,招手,伸懒腰,波浪运动,摇摆运动,求食,找食物,握手,展示机械臂,俯卧撑，张望，跳舞，调皮，严格按照前面给的词语给出
        5. name:pace
           - mode, 取值为slow, normal, high,分别对应慢速，正常，高速
        6. name:translation
           - [direction,data], direction取值为'x','y','z' ,data的单位是毫米，沿X轴正方向平移为正数，0表示回到初始位置，沿着X负方向平移为负数，取值范围是[-35,35]mm，y轴和z轴同理。
        7. name:attitude
           - [direction,data], direction取值为'r','p','y' ,data的单位是度，沿X轴正时针旋转为正数，0表示回到初始位置，沿着X逆时针旋转为负数，取值范围是[-20,20]mm，y轴和z轴旋转运动同理。
        8. name:arm
           - [arm_x, arm_z],arm_x取值范围是[-80,155]和arm_z的取值范围是[-95，155] 
        9. name:claw
           - pos,取值是0-255，其中0表示夹爪完全张开，255表示夹爪完全闭合。          
        10. name:imu
           - mode,取值为0或者1，0代表关闭自稳定模式，1表示打开自稳定模式。        
        11. name:perform
           - mode, 取值为0或者1，0代表关闭表演模式，1表示打开表演模式。         
        12. name:reset
           - mode,取值为0,表示让机器狗复位      
        13. name:motor
           - [motor_id, data],motor_id的取值范围是 [11,12,13,21,22,23,31,32,33,41,42,43,51,52,53]，data表示舵机角度。
        14. name:battery
           - mode,取值为0,读取当前电池电量
       **默认值规则**：  
        - 如果未指定移动距离，默认移动距离为 `30`。  
        - 如果未指定转动角度，默认转动角度为 `90`。 
        - 招手为打招呼动作。
       name是指方法名字，后面是需要传入的参数以及参数规则,多个参数时需要以列表形式给出
       返回结果以'['作为开始，以']'作为结束,下面我将给出几个例子
       前进30，跳个舞，打个招呼然后退出应返回[['x', 30], [action, '跳舞'], [action, '招手'], ['退出']]
        退出退出退出应返回[['退出']]
        什么前进请说左转应返回[['重试']], ['x', 30], ['重试'],['turn', 90]]
        请严格按照上述规则处理输入内容，并返回结果列表。
    '''
    prompt = prompt + content
    # Create a dialog request
    completion = client.chat.completions.create(
        model = model,
        messages = [
            {"role": "user", "content": prompt},
        ],
    )
    result = completion.choices[0].message.content
    result = ast.literal_eval(result)
    return result
#-Wake Word Detection-#
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



action_id = {'趴下':1, '站起':2 ,'匍匐前进':3 ,'转圈':4, '原地踏步':5 ,'蹲起':6 ,'沿x转动':7 ,'沿y转动':8 ,'沿z转动':9 ,'三轴转动': 10,'撒尿': 11,'坐下':12, '招手':13,'伸懒腰': 14,
             '波浪运动':15 ,'摇摆运动':16 ,'求食':17 ,'找食物':18 ,'握手': 19, '展示机械臂': 20, '俯卧撑': 21, '张望':22, '跳舞':23, '调皮':24}
time_list = [3, 3, 5, 5, 4, 4, 4, 4, 4, 7, 7, 5,7, 10, 6, 6, 6, 6, 10, 9, 8, 8, 6, 7]

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

#-Dog Robot Initialization-#
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
#-Screen Initialization-#


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

#-Dog Robot Speed Adjustment-#
def adaptive_move(distance):
    if distance < 15:
        speed = 10
    elif distance < 30:
        speed = 15
    else:
        speed = 20
    return speed
def adaptive_turn(yaw):
    if dog_type == 'M' :
        if yaw < 20:
            turn_speed = 10
        elif yaw < 50 :
            turn_speed = 20
        else:
            turn_speed = 30
        return turn_speed
    else :
        turn_speed = 30
        return turn_speed

p = pyaudio.PyAudio()
#-Record parameter-#
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000
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
threading.Thread(target = check_exit,daemon = True).start()        
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
  draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height), fill=color)
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
  wake = wake_up(p,RATE,CHUNK)
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
    #start_recording()
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
    result = model_output(content=content)
    print(result)
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
            time.sleep(int(time_list[int(action_id[i[1]])]-1))
            dog.stop()
            time.sleep(0.5)
          elif i[0] == 'pace':
            dog.pace(i[1])
            time.sleep(0.2)
          elif i[0] == 'translation':
            dog.translation(i[1][0], i[1][1])
            time.sleep(1)
          elif i[0] == 'attitude':
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


