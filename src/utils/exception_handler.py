"""异常处理工具类"""

import logging
import traceback
from PyQt6.QtWidgets import QMessageBox


logger = logging.getLogger("ExceptionHandler")


def show_error_dialog(parent, title: str, message: str, exception: Exception = None):
    """显示错误对话框并记录日志"""
    if exception:
        tb = traceback.format_exc()
        logger.error(f"{title}: {message}\n异常: {str(exception)}\n{tb}")
    else:
        logger.error(f"{title}: {message}")

    QMessageBox.critical(parent, title, message)


def log_error(message: str, exception: Exception = None):
    """记录错误日志"""
    if exception:
        logger.error(f"{message}: {str(exception)}\n{traceback.format_exc()}")
    else:
        logger.error(message)


def log_info(message: str):
    """记录信息日志"""
    logger.info(message)


def safe_call(func, default_return=None, error_msg: str = "操作失败"):
    """安全调用函数，捕获所有异常"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_error(error_msg, e)
            return default_return
    return wrapper
