"""前馈控制器 - 静态+动态补偿"""

import numpy as np
from src.control.pid_controller import PIDController


class FeedforwardController:
    """前馈控制器（干扰补偿）"""

    def __init__(self, ff_gain: float = -0.5):
        self.ff_gain = ff_gain

    def compute(self, disturbance: float) -> float:
        """计算前馈补偿量

        Args:
            disturbance: 当前干扰值

        Returns:
            前馈补偿控制量
        """
        return self.ff_gain * disturbance

    @property
    def gain(self) -> float:
        return self.ff_gain

    @gain.setter
    def gain(self, value: float):
        self.ff_gain = value


class FeedforwardFeedbackController:
    """前馈+反馈复合控制器"""

    def __init__(self, kp: float = 2.0, ti: float = 2.0, td: float = 0.5,
                 ff_gain: float = -0.5, dt: float = 0.05,
                 u_min: float = -30.0, u_max: float = 30.0):
        self.pid = PIDController(kp, ti, td, dt, u_min, u_max, anti_windup=True)
        self.ff = FeedforwardController(ff_gain)
        self._output = 0.0

    def reset(self):
        self.pid.reset()
        self._output = 0.0

    def compute(self, setpoint: float, process_value: float, disturbance: float = 0.0) -> float:
        """计算控制量 = PID反馈 + 前馈补偿"""
        fb_output = self.pid.compute(setpoint, process_value)
        ff_output = self.ff.compute(disturbance)
        self._output = fb_output + ff_output
        return self._output

    def track_output(self, manual_output: float):
        self.pid.track_output(manual_output)
        self._output = manual_output

    @property
    def output(self) -> float:
        return self._output
