"""用户管理逻辑 - 增删改查"""

from typing import List, Dict, Optional

from src.user.user_data import UserDataManager
from src.user.permission import CurrentUser
from src.config import UserRole
from src.exception import UserAuthException


class UserManager:
    """用户管理业务逻辑"""

    def __init__(self):
        self._data = UserDataManager()

    def verify_login(self, user_id: str, password: str) -> bool:
        """验证登录"""
        return self._data.verify_password(user_id, password)

    def get_user_role(self, user_id: str) -> str:
        """获取用户角色"""
        users = self._data.load_users()
        if user_id in users:
            return users[user_id]["role"]
        return "user"

    def change_password(self, user_id: str, old_pwd: str, new_pwd: str) -> bool:
        """修改密码"""
        if not new_pwd or len(new_pwd.strip()) == 0:
            raise UserAuthException("新密码不能为空")
        if len(new_pwd) < 3:
            raise UserAuthException("密码长度至少3位")
        success = self._data.change_password(user_id, old_pwd, new_pwd)
        if not success:
            raise UserAuthException("原密码错误")
        return True

    def get_all_users(self) -> List[Dict]:
        """获取所有用户列表"""
        users = self._data.load_users()
        result = []
        for uid, info in users.items():
            result.append({
                "user_id": uid,
                "role": info["role"],
                "password": info["password"],
            })
        return result

    def add_user(self, user_id: str, password: str, role: str) -> bool:
        """添加用户"""
        if not user_id or not user_id.strip():
            raise UserAuthException("用户名不能为空")
        if not password or len(password) < 3:
            raise UserAuthException("密码长度至少3位")
        if role not in [r.value for r in UserRole]:
            raise UserAuthException("无效的角色类型")
        success = self._data.add_user(user_id.strip(), password, role)
        if not success:
            raise UserAuthException(f"用户 '{user_id}' 已存在")
        return True

    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        current = CurrentUser()
        if user_id == current.user_id:
            raise UserAuthException("不能删除当前登录的用户")
        success = self._data.delete_user(user_id)
        if not success:
            raise UserAuthException(f"用户 '{user_id}' 不存在")
        return True

    def update_user_role(self, user_id: str, role: str) -> bool:
        """更新用户角色"""
        if role not in [r.value for r in UserRole]:
            raise UserAuthException("无效的角色类型")
        success = self._data.update_user_role(user_id, role)
        if not success:
            raise UserAuthException(f"用户 '{user_id}' 不存在")
        return True
