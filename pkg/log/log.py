import errno
import logging
import logging.handlers
import os

from contextvars import ContextVar
from functools import wraps

import yaml

TRACE_ID_CTX = ContextVar("trace_id", default="")


class TraceIDFilter(logging.Filter):
    def filter(self, record):
        trace_id = TRACE_ID_CTX.get()
        if trace_id:
            record.trace_id = trace_id
        else:
            record.trace_id = 'system'
        return True

def ensure_dir(path):
    """os.path.makedirs without EEXIST."""
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e

def get_logger_by_file(file_path, log_dir='logs/', level=logging.INFO):
    logger_name = os.path.basename(file_path)
    # 创建 logger 实例
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addFilter(TraceIDFilter())

    stdout_file = os.path.join(log_dir, logger_name)
    error_file = os.path.join(log_dir, 'error', logger_name)
    for file_path in (stdout_file, error_file):
        ensure_dir(os.path.dirname(file_path))

    # 创建 TimedRotatingFileHandler 实例，按天切分滚动
    info_handler = logging.handlers.TimedRotatingFileHandler(
        filename=f"{stdout_file}.log",
        when='MIDNIGHT',
        interval=1,
        backupCount=14,
        encoding='utf-8'
    )
    error_handler = logging.handlers.TimedRotatingFileHandler(
        filename=f"{error_file}.log",
        when='MIDNIGHT',
        interval=1,
        backupCount=14,
        encoding='utf-8'
    )

    # 设置日志记录的级别
    info_handler.setLevel(level)
    error_handler.setLevel(logging.ERROR)

    # 创建 Formatter 实例，设置日志格式
    log_format = "[%(asctime)s] %(filename)s[line:%(lineno)d] : [%(levelname)s] - [trace_id:%(trace_id)s] - %(message)s"
    formatter = logging.Formatter(log_format)

    # 将 Formatter 添加到 Handler 中
    info_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    # 将 Handler 添加到 logger 中
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

    return logger


def cached_logger():
    logger_cache = []

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if logger_cache:
                return logger_cache[0]
            logger = func(*args, **kwargs)
            logger_cache.append(logger)
            return logger

        return inner

    return wrapper


@cached_logger()
def get_logger(log_dir="", level=logging.INFO):
    if log_dir == "":
        # 从configs/app.yaml中获取log_dir
        with open('configs/app.yaml', 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        log_dir = config['logs']['path']
    else:
        pass

    import inspect
    # 获取调用层级最顶层的信息
    def get_top_level_caller():
        frame = inspect.currentframe()
        while frame.f_back:
            frame = frame.f_back
        top_level_frame = frame
        top_level_info = inspect.getframeinfo(top_level_frame)
        return top_level_info

    # 调用函数并打印最顶层调用的信息
    caller_info = get_top_level_caller()
    file_path = caller_info.filename
    return get_logger_by_file(file_path, log_dir=log_dir, level=level)
