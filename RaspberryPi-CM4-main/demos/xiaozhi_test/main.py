import argparse
import logging
import sys
import signal
import subprocess  # 新增
from src.application import Application
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

def kill_pulseaudio():
    """关闭 PulseAudio 服务"""
    try:
        subprocess.run(["pulseaudio", "--kill"], check=True)
        logger.info("已关闭 PulseAudio")
    except subprocess.CalledProcessError as e:
        logger.warning(f"关闭 PulseAudio 失败: {e}")

def start_pulseaudio():
    """启动 PulseAudio 服务"""
    try:
        subprocess.run(["pulseaudio", "--start"], check=True)
        logger.info("已启动 PulseAudio")
    except subprocess.CalledProcessError as e:
        logger.warning(f"启动 PulseAudio 失败: {e}")

def signal_handler(sig, frame):
    """处理 Ctrl+C 信号"""
    logger.info("接收到中断信号，正在关闭...")
    app = Application.get_instance()
    app.shutdown()
    start_pulseaudio()  # 退出时恢复 PulseAudio
    sys.exit(0)

def main():
    """程序入口点"""
    signal.signal(signal.SIGINT, signal_handler)
    kill_pulseaudio()  # 启动时关闭 PulseAudio

    try:
        app = Application.get_instance()
        logger.info("应用程序已启动，按 Ctrl+C 退出")
        app.run()
    except Exception as e:
        logger.error(f"程序发生错误: {e}", exc_info=True)
        start_pulseaudio()  # 出错时恢复 PulseAudio
        return 1
    finally:
        start_pulseaudio()  # 确保无论如何都恢复 PulseAudio

    return 0

if __name__ == "__main__":
    sys.exit(main())
