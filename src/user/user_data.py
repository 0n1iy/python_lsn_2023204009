"""用户数据存储 - JSON读写与加密"""

import json
import os
import base64
from typing import Dict, Optional

from src.config import Paths, DEFAULT_USERS


class UserDataManager:
    """用户数据持久化管理

    使用base64简单编码存储密码（教学演示用，非生产级安全）
    """

    def __init__(self):
        self._file_path = Paths.USERS_FILE

    def _encode(self, text: str) -> str:
        """简单编码"""
        return base64.b64encode(text.encode("utf-8")).decode("utf-8")

    def _decode(self, encoded: str) -> str:
        """简单解码"""
        return base64.b64decode(encoded.encode("utf-8")).decode("utf-8")

    def load_users(self) -> Dict:
        """加载用户数据，文件不存在时创建默认数据"""
        if not os.path.exists(self._file_path):
            self._create_default_users()
            return DEFAULT_USERS

        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 兼容明文和编码存储
            decoded = {}
            for user_id, info in data.items():
                pwd = info["password"]
                try:
                    decoded_pwd = self._decode(pwd)
                except Exception:
                    decoded_pwd = pwd
                decoded[user_id] = {
                    "password": decoded_pwd,
                    "role": info.get("role", "user"),
                }
            return decoded
        except (json.JSONDecodeError, IOError):
            self._create_default_users()
            return DEFAULT_USERS

    def save_users(self, users: Dict):
        """保存用户数据（编码存储）"""
        Paths.ensure_dirs()
        encoded = {}
        for user_id, info in users.items():
            encoded[user_id] = {
                "password": self._encode(info["password"]),
                "role": info["role"],
            }
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(encoded, f, ensure_ascii=False, indent=2)

    def _create_default_users(self):
        """创建默认用户数据文件"""
        self.save_users(DEFAULT_USERS)

    def verify_password(self, user_id: str, password: str) -> bool:
        """验证用户密码"""
        users = self.load_users()
        if user_id not in users:
            return False
        return users[user_id]["password"] == password

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """修改密码"""
        users = self.load_users()
        if user_id not in users:
            return False
        if users[user_id]["password"] != old_password:
            return False
        users[user_id]["password"] = new_password
        self.save_users(users)
        return True

    def add_user(self, user_id: str, password: str, role: str) -> bool:
        """添加用户"""
        users = self.load_users()
        if user_id in users:
            return False
        users[user_id] = {"password": password, "role": role}
        self.save_users(users)
        return True

    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        users = self.load_users()
        if user_id not in users:
            return False
        del users[user_id]
        self.save_users(users)
        return True

    def update_user_role(self, user_id: str, role: str) -> bool:
        """更新用户角色"""
        users = self.load_users()
        if user_id not in users:
            return False
        users[user_id]["role"] = role
        self.save_users(users)
        return True
