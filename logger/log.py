import logging
import os
import time
from logging.handlers import RotatingFileHandler

# 创建日志文件目录
if not os.path.exists("logs"):
    os.mkdir("logs")

# 创建并配置日志器
logger = logging.getLogger()

# 避免重复添加处理器
if not logger.hasHandlers():
    logger.setLevel(logging.INFO)  # 默认日志级别

    # 创建控制台处理器
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)  # 控制台日志级别

    # 创建文件处理器，并配置日志轮转
    log_filename = f"logs/log_{time.strftime('%Y%m%d')}.txt"
    fh = RotatingFileHandler(log_filename, maxBytes=5*1024*1024, backupCount=3)
    fh.setLevel(logging.INFO)  # 文件日志级别

    # 定义日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(module)s - %(funcName)s - line:%(lineno)d - %(levelname)s - %(message)s"
    )
    formatter2 = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # 设置处理器的日志格式
    fh.setFormatter(formatter)
    ch.setFormatter(formatter2)

    # 添加处理器到日志器
    logger.addHandler(ch)
    logger.addHandler(fh)

# 示例日志
# logger.debug("This is a debug message.")
# logger.info("This is an info message.")
# logger.warning("This is a warning message.")
# logger.error("This is an error message.")
# logger.critical("This is a critical message.")
