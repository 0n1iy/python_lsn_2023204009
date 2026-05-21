"""修改密码对话框"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

from src.user.user_manager import UserManager
from src.user.permission import CurrentUser


class ChangePasswordDialog(QDialog):
    """修改密码对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user_manager = UserManager()
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("修改密码")
        self.setFixedSize(350, 220)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(30, 25, 30, 25)

        # 原密码
        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(QLabel("原密码:"))
        self._old_pwd_edit = QLineEdit()
        self._old_pwd_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._old_pwd_edit.setPlaceholderText("请输入原密码")
        pwd_layout.addWidget(self._old_pwd_edit)
        layout.addLayout(pwd_layout)

        # 新密码
        new_layout = QHBoxLayout()
        new_layout.addWidget(QLabel("新密码:"))
        self._new_pwd_edit = QLineEdit()
        self._new_pwd_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._new_pwd_edit.setPlaceholderText("请输入新密码")
        new_layout.addWidget(self._new_pwd_edit)
        layout.addLayout(new_layout)

        # 确认新密码
        confirm_layout = QHBoxLayout()
        confirm_layout.addWidget(QLabel("确  认:"))
        self._confirm_edit = QLineEdit()
        self._confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._confirm_edit.setPlaceholderText("请再次输入新密码")
        confirm_layout.addWidget(self._confirm_edit)
        layout.addLayout(confirm_layout)

        layout.addSpacing(5)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self._ok_btn = QPushButton("确认修改")
        self._ok_btn.clicked.connect(self._on_change)
        btn_layout.addWidget(self._ok_btn)

        self._cancel_btn = QPushButton("取消")
        self._cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self._cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _on_change(self):
        """修改密码"""
        old_pwd = self._old_pwd_edit.text()
        new_pwd = self._new_pwd_edit.text()
        confirm = self._confirm_edit.text()

        if not old_pwd:
            QMessageBox.warning(self, "提示", "请输入原密码")
            return
        if not new_pwd:
            QMessageBox.warning(self, "提示", "请输入新密码")
            return
        if new_pwd != confirm:
            QMessageBox.warning(self, "提示", "两次输入的新密码不一致")
            return
        if new_pwd == old_pwd:
            QMessageBox.warning(self, "提示", "新密码不能与原密码相同")
            return

        try:
            user_id = CurrentUser().user_id
            if self._user_manager.change_password(user_id, old_pwd, new_pwd):
                QMessageBox.information(self, "成功", "密码修改成功")
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "修改失败", str(e))
