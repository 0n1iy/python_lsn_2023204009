"""串级控制器 - 外环+内环"""

import numpy as np
from src.control.pid_controller import PIDController
from src.config import TempConfig


class CascadeController:
    """串级PID控制器（双回路）

    外环：控制最终输出（第二惯性环节输出+干扰）
    内环：控制第一惯性环节输出（中间变量）
    """

    def __init__(self,
                 outer_kp: float = 2.0, outer_ti: float = 2.0, outer_td: float = 0.5,
                 inner_kp: float = 1.0, inner_ti: float = 2.0, inner_td: float = 0.0,
                 dt: float = 0.05, u_min: float = -30.0, u_max: float = 30.0):
        self.outer = PIDController(outer_kp, outer_ti, outer_td, dt, None, None, anti_windup=False)
        self.inner = PIDController(inner_kp, inner_ti, inner_td, dt, u_min, u_max, anti_windup=True)
        self.dt = dt
        self._output = 0.0

    def reset(self):
        self.outer.reset()
        self.inner.reset()
        self._output = 0.0

    def compute(self, setpoint: float, process_value: float, inner_pv: float) -> float:
        """计算控制量

        Args:
            setpoint: 最终设定值
            process_value: 最终过程值（第二环节输出+干扰）
            inner_pv: 内环过程值（第一环节输出）

        Returns:
            控制量u
        """
        outer_output = self.outer.compute(setpoint, process_value)
        self._output = self.inner.compute(outer_output, inner_pv)
        return self._output

    def track_output(self, manual_output: float):
        """无扰动切换跟踪"""
        self.inner.track_output(manual_output)
        self._output = manual_output

    @property
    def output(self) -> float:
        return self._output

    def update_outer_params(self, kp: float = None, ti: float = None, td: float = None):
        if kp is not None:
            self.outer.kp = kp
        if ti is not None:
            self.outer.ti = ti
        if td is not None:
            self.outer.td = td

    def update_inner_params(self, kp: float = None, ti: float = None, td: float = None):
        if kp is not None:
            self.inner.kp = kp
        if ti is not None:
            self.inner.ti = ti
        if td is not None:
            self.inner.td = td


class CascadeWithFeedforward(CascadeController):
    """串级+前馈控制器"""

    def __init__(self,
                 outer_kp: float = 2.0, outer_ti: float = 2.0, outer_td: float = 0.5,
                 inner_kp: float = 1.0, inner_ti: float = 2.0, inner_td: float = 0.0,
                 ff_gain: float = -0.5,
                 dt: float = 0.05, u_min: float = -30.0, u_max: float = 30.0):
        super().__init__(outer_kp, outer_ti, outer_td,
                         inner_kp, inner_ti, inner_td, dt, u_min, u_max)
        self.ff_gain = ff_gain

    def compute(self, setpoint: float, process_value: float, inner_pv: float,
                disturbance: float = 0.0) -> float:
        """计算控制量（含前馈补偿）

        Args:
            setpoint: 最终设定值
            process_value: 最终过程值
            inner_pv: 内环过程值
            disturbance: 干扰值（用于前馈补偿）

        Returns:
            控制量u
        """
        outer_output = self.outer.compute(setpoint, process_value)
        inner_output = self.inner.compute(outer_output, inner_pv)
        ff_compensation = self.ff_gain * disturbance
        self._output = inner_output + ff_compensation
        return self._output

    def track_output(self, manual_output: float):
        self.inner.track_output(manual_output)
        self._output = manual_output
