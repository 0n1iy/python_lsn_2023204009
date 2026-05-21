"""程序入口 - 初始化→登录→主界面"""

import sys
import os

# 将项目根目录加入路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from src.config import Paths, APP_TITLE
from src.exception import install_exception_handler
from src.user.login_window import LoginWindow
from src.user.permission import CurrentUser
from src.ui.main_window import MainWindow


def main():
    """程序主入口"""
    # 1. 安装全局异常处理器
    install_exception_handler()

    # 2. 创建数据目录
    Paths.ensure_dirs()

    # 3. 启动Qt应用
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    app.setStyle("Fusion")

    # 加载样式表
    try:
        style_path = Paths.STYLE_QSS
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
    except Exception:
        pass

    # 4. 显示登录窗口
    while True:
        login = LoginWindow()
        if login.exec() != LoginWindow.DialogCode.Accepted:
            # 用户关闭登录窗口
            break

        if login.login_success:
            # 5. 验证通过后启动主界面
            main_window = MainWindow()
            main_window.show()

            # 进入Qt事件循环
            app.exec()

            # 主界面关闭后，判断是退出登录还是退出程序
            if not CurrentUser().is_logged_in:
                continue  # 用户选择退出登录，重新显示登录窗口
            else:
                break  # 用户关闭主窗口，退出程序
        else:
            break

    sys.exit(0)


if __name__ == "__main__":
    main()
