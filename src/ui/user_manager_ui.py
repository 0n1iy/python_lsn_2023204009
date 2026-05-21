"""用户管理界面 - 管理员专用"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt

from src.user.user_manager import UserManager
from src.user.permission import CurrentUser
from src.config import UserRole


class UserManagerWindow(QDialog):
    """用户管理窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user_manager = UserManager()
        self._init_ui()
        self._refresh_table()

    def _init_ui(self):
        self.setWindowTitle("用户管理")
        self.setMinimumSize(600, 450)

        layout = QVBoxLayout()

        # 用户表格
        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["用户名", "角色", "密码"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._table)

        # 操作面板
        op_layout = QHBoxLayout()

        op_layout.addWidget(QLabel("用户名:"))
        self._user_edit = QLineEdit()
        self._user_edit.setPlaceholderText("新用户名")
        op_layout.addWidget(self._user_edit)

        op_layout.addWidget(QLabel("密码:"))
        self._pwd_edit = QLineEdit()
        self._pwd_edit.setPlaceholderText("密码(至少3位)")
        op_layout.addWidget(self._pwd_edit)

        op_layout.addWidget(QLabel("角色:"))
        self._role_combo = QComboBox()
        self._role_combo.addItems([r.value for r in UserRole])
        op_layout.addWidget(self._role_combo)

        layout.addLayout(op_layout)

        # 按钮
        btn_layout = QHBoxLayout()
        self._add_btn = QPushButton("添加用户")
        self._add_btn.clicked.connect(self._on_add_user)
        btn_layout.addWidget(self._add_btn)

        self._delete_btn = QPushButton("删除选中用户")
        self._delete_btn.clicked.connect(self._on_delete_user)
        btn_layout.addWidget(self._delete_btn)

        self._change_role_btn = QPushButton("修改角色")
        self._change_role_btn.clicked.connect(self._on_change_role)
        btn_layout.addWidget(self._change_role_btn)

        btn_layout.addStretch()

        self._close_btn = QPushButton("关闭")
        self._close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self._close_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _refresh_table(self):
        """刷新用户列表"""
        try:
            users = self._user_manager.get_all_users()
            self._table.setRowCount(len(users))
            for i, user in enumerate(users):
                self._table.setItem(i, 0, QTableWidgetItem(user["user_id"]))
                role_item = QTableWidgetItem(user["role"])
                if user["user_id"] == CurrentUser().user_id:
                    role_item.setForeground(Qt.GlobalColor.blue)
                self._table.setItem(i, 1, role_item)
                self._table.setItem(i, 2, QTableWidgetItem("******"))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载用户列表失败：{str(e)}")

    def _on_add_user(self):
        """添加用户"""
        user_id = self._user_edit.text().strip()
        password = self._pwd_edit.text().strip()
        role = self._role_combo.currentText()

        if not user_id:
            QMessageBox.warning(self, "提示", "请输入用户名")
            return
        if not password:
            QMessageBox.warning(self, "提示", "请输入密码")
            return

        try:
            if self._user_manager.add_user(user_id, password, role):
                QMessageBox.information(self, "成功", f"用户 '{user_id}' 添加成功")
                self._user_edit.clear()
                self._pwd_edit.clear()
                self._refresh_table()
        except Exception as e:
            QMessageBox.critical(self, "添加失败", str(e))

    def _on_delete_user(self):
        """删除用户"""
        row = self._table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择要删除的用户")
            return

        user_id = self._table.item(row, 0).text()

        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除用户 '{user_id}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            if self._user_manager.delete_user(user_id):
                QMessageBox.information(self, "成功", f"用户 '{user_id}' 已删除")
                self._refresh_table()
        except Exception as e:
            QMessageBox.critical(self, "删除失败", str(e))

    def _on_change_role(self):
        """修改角色"""
        row = self._table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择用户")
            return

        user_id = self._table.item(row, 0).text()
        new_role = self._role_combo.currentText()

        try:
            if self._user_manager.update_user_role(user_id, new_role):
                QMessageBox.information(self, "成功",
                    f"用户 '{user_id}' 角色已更改为 '{new_role}'")
                self._refresh_table()
        except Exception as e:
            QMessageBox.critical(self, "修改失败", str(e))
