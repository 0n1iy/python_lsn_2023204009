"""PID控制器实现 - 位置式、增量式、抗饱和"""

import numpy as np
from src.config import TempConfig


class SimplePIDController:
    """纯PID控制器（无输出限幅，教学演示用）"""

    def __init__(self, kp: float = 2.0, ti: float = 2.0, td: float = 0.5, dt: float = 0.05):
        self.kp = kp
        self.ti = ti
        self.td = td
        self.dt = dt
        self.reset()

    def reset(self):
        self._integral = 0.0
        self._prev_error = 0.0
        self._output = 0.0

    def compute(self, setpoint: float, process_value: float) -> float:
        error = setpoint - process_value
        self._integral += error * self.dt
        derivative = (error - self._prev_error) / self.dt if self.dt > 0 else 0.0
        self._prev_error = error

        p_term = self.kp * error
        i_term = self.kp / self.ti * self._integral if self.ti > 0 else 0.0
        d_term = self.kp * self.td * derivative

        self._output = p_term + i_term + d_term
        return self._output

    @property
    def integral(self) -> float:
        return self._integral

    @integral.setter
    def integral(self, value: float):
        self._integral = value

    @property
    def output(self) -> float:
        return self._output


class PIDController:
    """位置式PID控制器（带条件积分抗饱和）"""

    def __init__(self, kp: float = 2.0, ti: float = 2.0, td: float = 0.5,
                 dt: float = 0.05, u_min: float = -30.0, u_max: float = 30.0,
                 anti_windup: bool = True):
        self.kp = kp
        self.ti = ti
        self.td = td
        self.dt = dt
        self.u_min = u_min
        self.u_max = u_max
        self.anti_windup = anti_windup
        self.reset()

    def reset(self):
        self._integral = 0.0
        self._prev_error = 0.0
        self._output = 0.0
        self._saturated = False

    def compute(self, setpoint: float, process_value: float) -> float:
        error = setpoint - process_value

        # 条件积分抗饱和
        if self.anti_windup:
            would_saturate_high = self._output > self.u_max and error > 0
            would_saturate_low = self._output < self.u_min and error < 0
            if not (would_saturate_high or would_saturate_low):
                self._integral += error * self.dt
        else:
            self._integral += error * self.dt

        derivative = (error - self._prev_error) / self.dt if self.dt > 0 else 0.0
        self._prev_error = error

        p_term = self.kp * error
        i_term = self.kp / self.ti * self._integral if self.ti > 0 else 0.0
        d_term = self.kp * self.td * derivative

        output_raw = p_term + i_term + d_term

        # 输出限幅
        if self.u_min is not None and self.u_max is not None:
            self._output = np.clip(output_raw, self.u_min, self.u_max)
        else:
            self._output = output_raw

        self._saturated = (self._output != output_raw) if (self.u_min is not None and self.u_max is not None) else False
        return self._output

    @property
    def integral(self) -> float:
        return self._integral

    @integral.setter
    def integral(self, value: float):
        self._integral = value

    @property
    def output(self) -> float:
        return self._output

    @property
    def is_saturated(self) -> bool:
        return self._saturated

    def track_output(self, manual_output: float):
        """无扰动切换 - 跟踪手动输出值，调整积分项"""
        if self.kp != 0 and self.ti > 0:
            self._integral = (manual_output / self.kp) * self.ti
        else:
            self._integral = 0.0
        self._output = manual_output
        self._prev_error = 0.0
