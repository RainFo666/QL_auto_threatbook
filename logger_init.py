import logging
from logging.handlers import TimedRotatingFileHandler
import time


def logger_init():
    # 创建日志对象
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 定义日志文件名格式
    log_filename = "./logs/log_" + time.strftime("%Y%m%d%H%M%S") + ".log"

    # 创建文件日志处理器，按照每天保存日志，保留5个日志文件
    file_handler = TimedRotatingFileHandler(
        filename=log_filename, when="midnight", interval=1, backupCount=30, encoding="utf-8"
    )
    file_fmt = "%(asctime)s - %(levelname)s - %(message)s"
    file_handler.setFormatter(logging.Formatter(file_fmt))
    logger.addHandler(file_handler)

    # 创建控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = "%(asctime)s - %(levelname)s - %(message)s"
    console_handler.setFormatter(logging.Formatter(console_fmt))
    logger.addHandler(console_handler)

    return logger
