"""权限校验 - 角色与权限常量"""

from src.config import UserRole, Permissions


class CurrentUser:
    """当前登录用户上下文"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._user_id = ""
            self._role = UserRole.USER
            self._initialized = True

    def login(self, user_id: str, role_str: str):
        self._user_id = user_id
        try:
            self._role = UserRole(role_str)
        except ValueError:
            self._role = UserRole.USER

    def logout(self):
        self._user_id = ""
        self._role = UserRole.USER

    def has_permission(self, permission: str) -> bool:
        """检查当前用户是否有指定权限"""
        perms = Permissions.ROLE_PERMISSIONS.get(self._role, [])
        return permission in perms

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def role(self) -> UserRole:
        return self._role

    @property
    def is_admin(self) -> bool:
        return self._role == UserRole.ADMIN

    @property
    def is_logged_in(self) -> bool:
        return bool(self._user_id)
