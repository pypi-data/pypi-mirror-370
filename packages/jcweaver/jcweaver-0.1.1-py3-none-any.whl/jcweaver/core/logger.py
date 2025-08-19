import logging
import os
import sys
from logging import Logger

# 默认日志格式
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 是否写入日志文件
ENABLE_FILE_LOG = False
LOG_DIR = os.getenv("JCWEAVER_LOG_DIR", "./logs")
LOG_LEVEL = os.getenv("JCWEAVER_LOG_LEVEL", "INFO").upper()


def ensure_log_dir():
    if ENABLE_FILE_LOG and not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)


def _create_stream_handler() -> logging.StreamHandler:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    handler.setFormatter(formatter)
    return handler


def _create_file_handler(name: str) -> logging.FileHandler:
    ensure_log_dir()
    filepath = os.path.join(LOG_DIR, f"{name}.log")
    handler = logging.FileHandler(filepath, encoding="utf-8")
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    handler.setFormatter(formatter)
    return handler


def get_logger(name: str = "JCWeaver") -> Logger:
    """
    获取一个统一配置的 logger，按模块名分离。
    """
    getLogger = logging.getLogger(name)
    if not getLogger.handlers:  # 防止重复添加 handler
        getLogger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
        getLogger.addHandler(_create_stream_handler())

        if ENABLE_FILE_LOG:
            getLogger.addHandler(_create_file_handler(name))
        getLogger.propagate = False  # 防止重复打印

    return getLogger


# 默认 logger，可直接 import 使用
logger = get_logger("JCWeaver")
