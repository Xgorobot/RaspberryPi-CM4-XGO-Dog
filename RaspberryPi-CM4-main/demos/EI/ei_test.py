import ast
import logging
import sys
from volcenginesdkarkruntime import Ark
from record import AudiostreamSource
from auto_platform import AudiostreamSource, play_command
from libnyumaya import AudioRecognition, FeatureExtractor
vosk_path = '/home/pi/.local/lib/python3.9/site-packages'
if vosk_path not in sys.path:
    sys.path.append(vosk_path)
from vosk import Model, KaldiRecognizer
import threading
import pyaudio
import time
from datetime import datetime
import os
from key import Button
from xgolib import XGO
from PIL import Image, ImageDraw, ImageFont
import xgoscreen.LCD_2inch as LCD_2inch
from audio import start_recording
from language_recognize import test_one
class GPTCMD:
    def __init__(self):
        """
        初始化一些参数
        """
        self.splash_theme_color = (15, 21, 46)
        self.font2 = ImageFont.truetype("/home/pi/model/msyh.ttc", 16)
        self.display = LCD_2inch.LCD_2inch()
        self.visual(title='启动中', content='请稍后')
        self.dog = XGO(port='/dev/ttyAMA0', version="xgomini")
        self.button = Button()
        self.chunk_size =1024
        self.rate = 16000
        self.audio_stream = AudiostreamSource()
        self.doubao_model ="doubao-1.5-pro-32k-250115"
        self.api_key = '67e1719b-fc92-43b7-979d-3692135428a4'
        self.client = Ark(api_key = self.api_key)
        self.action_id = {'趴下': 1, '站起': 2, '匍匐前进': 3, '转圈': 4, '原地踏步': 5, '蹲起': 6, '沿x转动': 7,
                     '沿y转动': 8, '沿z转动': 9, '三轴转动': 10, '撒尿': 11, '坐下': 12, '招手': 13, '伸懒腰': 14,
                     '波浪运动': 15, '摇摆运动': 16, '求食': 17, '找食物': 18, '握手': 19, '展示机械臂': 20,
                     '俯卧撑': 21, '张望': 22, '跳舞': 23, '调皮': 24, '向上抓取': 128, '向中抓取': 129,
                     '向下抓取': 130}
        self.time_list = [0] * 131
        self.time_list[1:25] = [3, 3, 5, 5, 4, 4, 4, 4, 4, 7, 7, 5, 7, 10, 6, 6, 6, 6, 10, 9, 8, 8, 6, 7]
        self.time_list[128:131] = [10, 10, 10]
        self.prompt =  '''
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
               - id:趴下,站起,匍匐前进,转圈,原地踏步,蹲起,沿x转动,沿y转动,沿z转动,三轴转动,撒尿,坐下,招手,伸懒腰,波浪运动,摇摆运动,求食,找食物,握手,展示机械臂,俯卧撑，张望，跳舞，调皮，向上抓取，向中抓取，向下抓取，严格按照前面给的词语给出
            5. name:pace
               - mode, 取值为slow, normal, high,分别对应慢速，正常，高速
            6. name:translation
               - [direction,data], direction取值为'x','y','z' ,data的单位是毫米，沿X轴正方向平移为正数，0表示回到初始位置，沿着X负方向平移为负数，取值范围是[-35,35]mm，y轴和z轴同理。
            7. name:attitude
               - [direction,data], direction取值为'r','p','y' ,data的单位是度，沿X轴正时针旋转为正数，0表示回到初始位置，沿着X逆时针旋转为负数，取值范围是[-20,20]mm，y轴和z轴旋转运动同理。
            8. name:arm
               - [arm_x, arm_z],arm_x取值范围是[-80,155]和arm_z的取值范围是[-95，155]，是机械臂的相关动作，arm_x是机械狗的机械臂相对于机械臂的基座的x坐标，arm_z机械狗的机械臂相对于机械臂的基座的z坐标
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
            - 如某些命令未给出参数，可自行随机生成，但必须有参数。
            - 招手为打招呼动作。
            - 机械b 就是机械臂
            - 眼外周运动、歪轴运动、外轴运动等类近音文字，都是沿y轴运动。
            - 厘米是毫米的10倍,分米是毫米的100倍，米是毫米的1000倍。
           name是指方法名字，后面是需要传入的参数以及参数规则,多个参数时需要以列表形式给出
           返回结果以'['作为开始，以']'作为结束,下面我将给出几个例子
           前进30，跳个舞，打个招呼然后退出应返回[['x', 30], [action, '跳舞'], [action, '招手'], ['退出']]
            退出退出退出应返回[['退出']]
            什么前进请说左转应返回[['重试']], ['x', 30], ['重试'],['turn', 90]]
            沿x轴旋转，沿x轴运动都应返回['action','沿x转动']
            沿y轴旋转，沿y轴运动都应返回['action','沿y转动']
            沿z轴旋转，沿z轴运动都应返回['action','沿z转动']
            调整机械臂x为80，可以返回['arm',[80,100]]
            请严格按照上述规则处理输入内容，并返回结果列表。
        '''
        self.init_wake()
        self.dog_init()
    def model_output(self, content):
        prompt = self.prompt + content
        completion = self.client.chat.completions.create(
            model = self.doubao_model,
            messages = [
                {"role": "user", "content": prompt},
            ],
        )
        result = completion.choices[0].message.content
        result = ast.literal_eval(result)
        return result
    def init_wake(self):
        self.p = pyaudio.PyAudio()
        libpath = "/home/pi/RaspberryPi-CM4-main/demos/EI/src/libnyumaya_premium.so.3.1.0"
        self.extractor = FeatureExtractor(libpath)
        self.detector = AudioRecognition(libpath)
        self.extactor_gain = 1.0
        self.keywordIdlulu = self.detector.addModel("/home/pi/RaspberryPi-CM4-main/demos/EI/src/lulu_v3.1.907.premium",0.7)
        self.bufsize = self.detector.getInputDataSize()
        model_path = "/home/pi/RaspberryPi-CM4-main/demos/EI/vosk-model-small-cn-0.22/"
        self.wake_word1 = "你好"
        self.wake_word2 = '您好'
        self.vosk_model = Model(model_path)
        self.rec = KaldiRecognizer(self.vosk_model, self.rate)
        self.stream = self.p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk_size)
    def wake_up(self):
        try:
            self.audio_stream.start()
        except:
            pass
        while True:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                frame = self.audio_stream.read(self.bufsize * 2, self.bufsize * 2)
                if self.rec.AcceptWaveform(data):
                    result = self.rec.Result()
                    text = eval(result)["text"]
                    print(text)
                    if self.wake_word1 in text or self.wake_word2 in text:
                        logging.warning("唤醒词已检测到！")
                        self.stream.stop_stream()
                        self.audio_stream.stop()
                        # self.stream.close()
                        return 1
                if not frame:
                    logging.warning('not frame')
                    time.sleep(0.01)
                    continue
                features = self.extractor.signalToMel(frame, self.extactor_gain)
                prediction = self.detector.runDetection(features)
                if prediction != 0:
                    now = datetime.now().strftime("%d.%b %Y %H:%M:%S")
                    if prediction == self.keywordIdlulu:
                        logging.warning("唤醒成功" + "lulu detected:" + now)
                        self.audio_stream.stop()
                        self.stream.stop_stream()
                        #self.stream.close()
                        return 1
                time.sleep(0.01)  # 降低睡眠时间，提高读取频率
            except OSError as e:
                if e.errno == -9981:
                    logging.warning("Input overflowed, cleaning buffer...")
                    self.stream.stop_stream()
                    self.stream.close()
                    self.stream = self.p.open(format=pyaudio.paInt16,
                                    channels=1,
                                    rate=self.rate,
                                    input=True,
                                    frames_per_buffer=self.chunk_size)
                else:
                    raise

        return 0
    def dog_init(self):
        fm = self.dog.read_firmware()
        if fm[0] == 'M':
            print('XGO-MINI')
            self.dog = XGO(port='/dev/ttyAMA0', version="xgomini")
            self.dog_type = 'M'
        else:
            self.dog = XGO(port='/dev/ttyAMA0', version="xgolite")
            print('XGO-LITE')
            self.dog_type = 'L'
        if self.dog_type == 'L':
            self.mintime_yaw = 0.8
            self.mintime_x = 0.1
        else:
            self.mintime_yaw = 0.7
            self.mintime_x = 0.3
    def adaptive_move(self, distance):
        if distance < 15:
            speed = 10
        elif distance < 30:
            speed = 15
        else:
            speed = 20
        return speed
    def adaptive_turn(self, yaw):
        if self.dog_type == 'M':
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
    def visual(self, title, content):
        splash = Image.new("RGB", (self.display.height, self.display.width), self.splash_theme_color)
        draw = ImageDraw.Draw(splash)
        draw.rectangle([0, 0, self.display.width, self.display.height], fill=(15, 21, 46))
        text_color = (255, 255, 255)
        color = (102, 178, 255)
        gray_color = (128, 128, 128)
        rectangle_x = (self.display.width - 120) // 2  # 矩形条居中的x坐标
        rectangle_y = 50  # 矩形条y坐标
        rectangle_width = 200
        rectangle_height = 30
        draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                       fill=color)
        draw.text((rectangle_x + 70, rectangle_y + 5), title, fill=text_color, font=self.font2)
        rectangle_x = (self.display.width - 120) // 2  # 矩形条居中的x坐标
        rectangle_y = 100  # 矩形条y坐标
        rectangle_width = 200
        rectangle_height = 100
        draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                       fill=gray_color)

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

        lcd_draw_string(
            draw,
            x=70,
            y=105,
            text= content,
            color=(255, 255, 255),
            font_size=16,
            max_width=190,
            max_lines=5,
            clear_area=False
        )
        self.display.ShowImage(splash)
    def run(self):
        while True:
            self.visual(title='等待唤醒', content='请说“你好，lulu”')
            self.wake = self.wake_up()
            if self.wake:
                self.visual(title='下达指令', content='唤醒成功,请给出运动指令')
                self.stream.stop_stream()
                time.sleep(0.1)
                self.stream.start_stream()
                start_recording()
                try:
                    content = test_one()
                except Exception as e:
                    logging.warning(f'1发生未知错误: {e}')
                    self.visual(title='识别错误', content='语音识别错误，请重试')
                    time.sleep(2)
                    continue
                if content == 0:
                    self.visual(title='识别错误', content='语音识别错误，请重试')
                    time.sleep(2)
                    continue
                else:
                    self.visual(title='指令内容', content=content)
                    try:
                        result = self.model_output(content=content)
                        logging.warning(result)
                    except Exception as e:
                        logging.warning(f'2发生未知错误: {e}')
                        self.visual(title='识别错误', content="指令识别错误，请重试")
                        time.sleep(2)
                        continue
                    try:
                        for i in result:
                            print(i[0])
                            if i[0] == 'x' or i[0] == 'y':
                                speed = self.adaptive_move(int(i[1]))
                                self.dog.move(i[0], speed * int(i[1]) / abs(int(i[1])))
                                time.sleep(abs(int(i[1] / speed)))
                                self.dog.stop()
                                time.sleep(0.5)
                            elif i[0] == 'turn':
                                if self.dog_type == 'L':
                                    i[1] = 3 * int(i[1])
                                turn_speed = self.adaptive_turn(int(i[1]))
                                self.dog.turn(turn_speed * int(i[1]) / abs(int(i[1])))
                                time.sleep(abs(int(i[1] / turn_speed)))
                                self.dog.stop()
                                time.sleep(0.5)
                            elif i[0] == 'action':
                                self.dog.action(int(self.action_id[i[1]]))
                                time.sleep(int(self.time_list[int(self.action_id[i[1]])]))
                                self.dog.stop()
                                time.sleep(0.5)
                            elif i[0] == 'pace':
                                self.dog.pace(i[1])
                                time.sleep(0.2)
                            elif i[0] == 'translation':
                                logging.warning(f'沿着{i[1][0]}轴平移{i[1][1]}')
                                self.dog.translation(i[1][0], i[1][1])
                                time.sleep(1)
                            elif i[0] == 'attitude':
                                logging.warning(f'沿着{i[1][0]}轴旋转{i[1][1]}')
                                self.dog.attitude(i[1][0], i[1][1])
                                time.sleep(1)
                            elif i[0] == 'arm':
                                self.dog.arm(i[1][0], i[1][1])
                                time.sleep(1)
                            elif i[0] == 'claw':
                                self.dog.claw(i[1])
                                time.sleep(1)
                            elif i[0] == 'imu':
                                self.dog.imu(i[1])
                                time.sleep(1)
                            elif i[0] == 'perform':
                                self.dog.perform(i[1])
                                time.sleep(10)
                            elif i[0] == 'reset':
                                self.dog.reset()
                                time.sleep(1)
                            elif i[0] == 'motor':
                                self.dog.motor(i[1][0], i[1][1])
                                time.sleep(1)
                            elif i[0] == 'battery':
                                print(self.dog.read_battery())
                                time.sleep(1)
                            elif i[0] == '重试':
                                continue
                            elif i[0] == '退出':
                                print('退出')
                                exit()
                            else:
                                continue
                    except Exception as e:
                            logging.warning(f'发生未知错误: {e}')
                            self.visual(title='指令错误', content="指令识别错误，请重试")
                            time.sleep(2)
                            continue
    def check_exit(self):
        while True:
            if self.button.press_b():
                print("Button B Pressed")
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except Exception as e:
                    print('音频流未打开')
                self.p.terminate()
                os._exit(0)
cmd=GPTCMD()
threading.Thread(target = cmd.check_exit,daemon = True).start()
cmd.run()




