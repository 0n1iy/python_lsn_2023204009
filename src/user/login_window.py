"""登录界面"""

import os
from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont

from src.user.user_manager import UserManager
from src.user.permission import CurrentUser
from src.config import APP_TITLE


class LoginWindow(QDialog):
    """登录对话框"""

    def __init__(self):
        super().__init__()
        self._user_manager = UserManager()
        self._login_success = False
        self._settings = QSettings("SimControl", "LoginInfo")
        self._init_ui()
        self._load_saved_credentials()

    def _init_ui(self):
        self.setWindowTitle(f"{APP_TITLE} - 登录")
        self.setFixedSize(400, 280)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(40, 30, 40, 30)

        # 标题
        title_label = QLabel("PID温度控制仿真系统")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        layout.addSpacing(10)

        # 用户名
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("用户名:"))
        self._user_edit = QLineEdit()
        self._user_edit.setPlaceholderText("请输入用户名")
        user_layout.addWidget(self._user_edit)
        layout.addLayout(user_layout)

        # 密码
        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(QLabel("密  码:"))
        self._pwd_edit = QLineEdit()
        self._pwd_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._pwd_edit.setPlaceholderText("请输入密码")
        self._pwd_edit.returnPressed.connect(self._on_login)
        pwd_layout.addWidget(self._pwd_edit)
        layout.addLayout(pwd_layout)

        # 记住密码
        self._remember_check = QCheckBox("记住密码")
        layout.addWidget(self._remember_check)

        layout.addSpacing(5)

        # 登录按钮
        self._login_btn = QPushButton("登 录")
        self._login_btn.setFixedHeight(36)
        self._login_btn.clicked.connect(self._on_login)
        layout.addWidget(self._login_btn)

        self.setLayout(layout)

    def _load_saved_credentials(self):
        """加载保存的登录凭据"""
        remember = self._settings.value("remember", False, type=bool)
        if remember:
            user_id = self._settings.value("user_id", "")
            password = self._settings.value("password", "")
            self._user_edit.setText(user_id)
            self._pwd_edit.setText(password)
            self._remember_check.setChecked(True)

    def _save_credentials(self):
        """保存登录凭据"""
        if self._remember_check.isChecked():
            self._settings.setValue("remember", True)
            self._settings.setValue("user_id", self._user_edit.text().strip())
            self._settings.setValue("password", self._pwd_edit.text())
        else:
            self._settings.setValue("remember", False)
            self._settings.remove("user_id")
            self._settings.remove("password")

    def _on_login(self):
        """处理登录"""
        user_id = self._user_edit.text().strip()
        password = self._pwd_edit.text()

        if not user_id:
            QMessageBox.warning(self, "登录失败", "请输入用户名")
            self._user_edit.setFocus()
            return

        if not password:
            QMessageBox.warning(self, "登录失败", "请输入密码")
            self._pwd_edit.setFocus()
            return

        try:
            if self._user_manager.verify_login(user_id, password):
                self._save_credentials()
                # 获取用户角色
                role = self._user_manager.get_user_role(user_id)
                CurrentUser().login(user_id, role)
                self._login_success = True
                self.accept()
            else:
                QMessageBox.warning(self, "登录失败", "用户名或密码错误，请重试。")
                self._pwd_edit.clear()
                self._pwd_edit.setFocus()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"登录过程出错：{str(e)}")

    @property
    def login_success(self) -> bool:
        return self._login_success
