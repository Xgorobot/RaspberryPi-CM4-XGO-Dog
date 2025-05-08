import pyaudio
import wave
import numpy as np
from scipy import fftpack
import time
import random,os

# 录音参数
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 600  # 最大录音时长
SAVE_FILE = "recorded_audio.wav"
START_THRESHOLD = 6000  # 开始录音的音量阈值
END_THRESHOLD = 4000  # 停止录音的音量阈值
ENDLAST = 10

KEYWORD_MODEL_PATH = "./demos/src/lulu_v3.1.907.premium"
KEYWORD_THRESHOLD = 0.7
PLAY_COMMAND = "aplay" 

def calculate_volume(data):
    """计算音频数据的音量"""
    rt_data = np.frombuffer(data, dtype=np.int16)
    fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
    fft_data = np.abs(fft_temp_data)[0: fft_temp_data.size // 2 + 1]
    return sum(fft_data) // len(fft_data)

def start_recording():
    os.system(f"{PLAY_COMMAND} /home/pi/RaspberryPi-CM4-main/demos/ding.wav")
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    print("等待声音开始...")
    frames = []
    start_recording_flag = False
    end_data_list = [0] * ENDLAST
    pre_record_frames = []  
    pre_record_length = int(RATE / CHUNK * 1)
    silence_duration = 0 
    max_silence_duration = int(RATE / CHUNK * 4)
    recording_start_time = None
    no_sound_timeout = int(RATE / CHUNK * 6)
    no_sound_counter = 0 
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        volume = calculate_volume(data)
        
        rt_data = np.frombuffer(data, dtype=np.int16)
        fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
        fft_data = np.abs(fft_temp_data)[0:fft_temp_data.size // 2 + 1]
        vol = sum(fft_data) // len(fft_data)
        
        if not start_recording_flag:
            pre_record_frames.append(data)
            if len(pre_record_frames) > pre_record_length:
                pre_record_frames.pop(0)
            if volume > START_THRESHOLD:
                print("detected voice, start recording...")
                start_recording_flag = True
                recording_start_time = time.time()
                frames.extend(pre_record_frames)
                frames.append(data)
                no_sound_counter = 0

        else:
            end_data_list.pop(0)
            end_data_list.append(volume)
            frames.append(data)
            if volume < END_THRESHOLD:
                silence_duration += 1
            else:
                silence_duration = 0

            if recording_start_time and (time.time() - recording_start_time) >= 2:
                if max(end_data_list) < START_THRESHOLD:
                    print("No valid sound detected within 2 seconds, end recording")
                    break

    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(SAVE_FILE, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f"The recording has been saved as: {SAVE_FILE}")


