"""用户管理测试"""

import unittest
import os
import json
from src.user.user_data import UserDataManager
from src.user.user_manager import UserManager
from src.user.permission import CurrentUser
from src.config import Paths, DEFAULT_USERS, UserRole, Permissions


class TestUserDataManager(unittest.TestCase):
    """用户数据管理测试"""

    def setUp(self):
        self.manager = UserDataManager()

    def tearDown(self):
        """恢复默认用户数据"""
        self.manager.save_users(DEFAULT_USERS)

    def test_encode_decode(self):
        """编码解码测试"""
        original = "test123"
        encoded = self.manager._encode(original)
        decoded = self.manager._decode(encoded)
        self.assertEqual(original, decoded)

    def test_default_users_exist(self):
        """默认用户数据应可加载"""
        users = self.manager.load_users()
        self.assertIn("admin", users)
        self.assertIn("user", users)
        self.assertEqual(users["admin"]["role"], "admin")
        self.assertEqual(users["user"]["role"], "user")

    def test_verify_password(self):
        """密码验证测试"""
        self.assertTrue(self.manager.verify_password("admin", "admin123"))
        self.assertTrue(self.manager.verify_password("user", "user123"))
        self.assertFalse(self.manager.verify_password("admin", "wrong"))
        self.assertFalse(self.manager.verify_password("nonexistent", "test"))

    def test_save_and_load_roundtrip(self):
        """保存和加载用户数据往返测试"""
        test_users = {
            "test1": {"password": "pass1", "role": "user"},
            "test2": {"password": "pass2", "role": "admin"},
        }
        self.manager.save_users(test_users)
        loaded = self.manager.load_users()
        self.assertEqual(loaded["test1"]["password"], "pass1")
        self.assertEqual(loaded["test2"]["role"], "admin")


class TestUserManager(unittest.TestCase):
    """用户管理逻辑测试"""

    def setUp(self):
        self.manager = UserManager()

    def test_verify_login(self):
        self.assertTrue(self.manager.verify_login("admin", "admin123"))
        self.assertFalse(self.manager.verify_login("admin", "wrong"))

    def test_get_all_users(self):
        users = self.manager.get_all_users()
        self.assertIsInstance(users, list)
        self.assertGreater(len(users), 0)
        for user in users:
            self.assertIn("user_id", user)
            self.assertIn("role", user)


class TestCurrentUser(unittest.TestCase):
    """当前用户上下文测试"""

    def setUp(self):
        self.user = CurrentUser()

    def test_default_state(self):
        self.assertFalse(self.user.is_logged_in)

    def test_login_logout(self):
        self.user.login("admin", "admin")
        self.assertTrue(self.user.is_logged_in)
        self.assertEqual(self.user.user_id, "admin")
        self.assertTrue(self.user.is_admin)

        self.user.logout()
        self.assertFalse(self.user.is_logged_in)
        self.assertFalse(self.user.is_admin)

    def test_permissions_admin(self):
        self.user.login("admin", "admin")
        self.assertTrue(self.user.has_permission(Permissions.MANAGE_USERS))
        self.assertTrue(self.user.has_permission(Permissions.MODIFY_PERMISSIONS))

    def test_permissions_user(self):
        self.user.login("user", "user")
        self.assertTrue(self.user.has_permission(Permissions.RUN_SIMULATION))
        self.assertFalse(self.user.has_permission(Permissions.MANAGE_USERS))
        self.assertFalse(self.user.has_permission(Permissions.MODIFY_PERMISSIONS))


if __name__ == "__main__":
    unittest.main()
