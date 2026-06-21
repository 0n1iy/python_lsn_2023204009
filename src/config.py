"""全局配置文件 - 路径、参数、权限常量"""

import os
import sys
from enum import Enum, auto


class ControlStrategy(Enum):
    """控制策略枚举"""
    PLAIN_PID = auto()          # 普通PID（无限幅）
    SINGLE_LOOP_PID = auto()    # 单回路PID（带抗饱和）
    FEEDFORWARD_FB = auto()     # 前馈+反馈
    CASCADE = auto()            # 串级PID
    CASCADE_FF = auto()         # 串级+前馈


class UserRole(Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    USER = "user"


class Permissions:
    """权限常量"""
    CHANGE_OWN_PASSWORD = "change_own_password"
    MANAGE_USERS = "manage_users"
    MODIFY_PERMISSIONS = "modify_permissions"
    RUN_SIMULATION = "run_simulation"
    EXPORT_DATA = "export_data"

    ROLE_PERMISSIONS = {
        UserRole.ADMIN: [
            CHANGE_OWN_PASSWORD,
            MANAGE_USERS,
            MODIFY_PERMISSIONS,
            RUN_SIMULATION,
            EXPORT_DATA,
        ],
        UserRole.USER: [
            CHANGE_OWN_PASSWORD,
            RUN_SIMULATION,
            EXPORT_DATA,
        ],
    }


class TempConfig:
    """温度控制参数配置"""
    SV_MIN = 0.0
    SV_MAX = 30.0
    SV_DEFAULT = 20.0
    PV_INITIAL = 0.0

    CONTROL_AUTO_LIMIT = 30.0      # 自动模式控制量限幅
    CONTROL_MANUAL_LIMIT = 30.0    # 手动模式控制量限幅

    # 被控对象默认参数
    T1_DEFAULT = 1.0
    T2_DEFAULT = 2.0
    GAIN_DEFAULT = 1.0

    # 反馈环节
    TC_DEFAULT = 0.1

    # PID默认参数
    PID_KP_DEFAULT = 2.0
    PID_TI_DEFAULT = 2.0
    PID_TD_DEFAULT = 0.5
    CASCADE_OUTER_KP_DEFAULT = 2.0
    CASCADE_OUTER_TI_DEFAULT = 2.0
    CASCADE_OUTER_TD_DEFAULT = 0.5
    CASCADE_INNER_KP_DEFAULT = 1.0
    CASCADE_INNER_TI_DEFAULT = 2.0
    CASCADE_INNER_TD_DEFAULT = 0.0

    # 前馈增益
    FF_GAIN_DEFAULT = -0.5

    # 仿真参数
    DT_DEFAULT = 0.05            # 仿真步长 50ms
    DISPLAY_POINTS_DEFAULT = 500 # 显示点数

    # 参数范围
    KP_MIN = 0.0
    KP_MAX = 100.0
    TI_MIN = 0.01
    TI_MAX = 100.0
    TD_MIN = 0.0
    TD_MAX = 50.0


class Paths:
    """路径配置 - 自适应开发和打包环境"""
    if getattr(sys, 'frozen', False):
        _BASE = os.path.dirname(sys.executable)
    else:
        _BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    DATA = os.path.join(_BASE, "data")
    HISTORY_DATA = os.path.join(DATA, "history_data")
    USERS = os.path.join(DATA, "users")
    LOGS = os.path.join(DATA, "logs")
    USERS_FILE = os.path.join(USERS, "users.json")
    ERROR_LOG = os.path.join(LOGS, "error.log")

    ASSETS = os.path.join(_BASE, "assets")
    STYLE_QSS = os.path.join(ASSETS, "style.qss")

    @classmethod
    def ensure_dirs(cls):
        """确保数据目录存在"""
        for d in [cls.DATA, cls.HISTORY_DATA, cls.USERS, cls.LOGS]:
            os.makedirs(d, exist_ok=True)


# 仿真采样周期
SIMULATION_DT = 0.05  # 秒

# 默认用户数据
DEFAULT_USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin",
    },
    "user": {
        "password": "user123",
        "role": "user",
    },
}

# 应用标题
APP_TITLE = "PID温度控制仿真系统"
APP_VERSION = "v1.0"
