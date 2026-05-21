"""全局异常捕获与处理"""

import sys
import traceback
import logging
from typing import Callable

from src.config import Paths


class SimulationError(Exception):
    """仿真系统基础异常"""
    pass


class CalculationException(SimulationError):
    """计算异常（除零、溢出等）"""
    pass


class ParameterException(SimulationError):
    """参数异常（非法值、越界）"""
    pass


class FileOperationException(SimulationError):
    """文件操作异常"""
    pass


class UserAuthException(SimulationError):
    """用户认证异常"""
    pass


def setup_logging():
    """配置日志系统"""
    Paths.ensure_dirs()
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(Paths.ERROR_LOG, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def _global_exception_hook(exc_type, exc_value, exc_tb):
    """全局未捕获异常处理钩子"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return

    logger = logging.getLogger("GlobalExceptionHandler")
    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.critical(f"未捕获的异常:\n{tb_str}")

    # 尝试弹窗提示
    try:
        from PyQt6.QtWidgets import QMessageBox, QApplication
        if QApplication.instance():
            QMessageBox.critical(
                None,
                "程序错误",
                f"发生未预期的错误:\n{str(exc_value)}\n\n"
                f"详细信息已记录到日志文件。\n程序将继续运行。",
            )
    except Exception:
        pass


def install_exception_handler():
    """安装全局异常处理器"""
    setup_logging()
    sys.excepthook = _global_exception_hook


def show_error_dialog(parent, title: str, message: str):
    """显示错误对话框"""
    try:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(parent, title, message)
    except Exception:
        pass


def show_info_dialog(parent, title: str, message: str):
    """显示信息对话框"""
    try:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(parent, title, message)
    except Exception:
        pass


def show_warning_dialog(parent, title: str, message: str):
    """显示警告对话框"""
    try:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(parent, title, message)
    except Exception:
        pass
