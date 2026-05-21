"""双惯性环节串联模型 - 被控对象

传递函数: G(s) = K / ((T1*s + 1)(T2*s + 1))

离散化采用欧拉方法:
  y1[k] = y1[k-1] + (dt/T1) * (K*u[k-1] - y1[k-1])
  y2[k] = y2[k-1] + (dt/T2) * (y1[k-1] - y2[k-1])
"""

import numpy as np


class FirstOrderLag:
    """一阶惯性环节: G(s) = 1/(Ts + 1)"""

    def __init__(self, time_constant: float = 1.0, gain: float = 1.0, dt: float = 0.05):
        self.time_constant = time_constant
        self.gain = gain
        self.dt = dt
        self._output = 0.0

    def reset(self):
        self._output = 0.0

    def step(self, input_val: float) -> float:
        """单步计算

        dy/dt = (gain * u - y) / T
        离散化: y[k] = y[k-1] + (dt/T) * (gain * u[k-1] - y[k-1])
        """
        tc = max(self.time_constant, 1e-10)
        self._output += (self.dt / tc) * (self.gain * input_val - self._output)
        return self._output

    @property
    def output(self) -> float:
        return self._output

    @output.setter
    def output(self, value: float):
        self._output = value


class TwoInertiaModel:
    """双惯性环节串联模型

    G(s) = K / ((T1*s + 1)(T2*s + 1))

    信号流向:
    控制量u → [惯性环节1] → 中间变量 → [惯性环节2] → 输出y
    """

    def __init__(self, t1: float = 1.0, t2: float = 2.0, gain: float = 1.0, dt: float = 0.05):
        self.stage1 = FirstOrderLag(t1, gain, dt)
        self.stage2 = FirstOrderLag(t2, 1.0, dt)
        self.dt = dt
        self._inner_output = 0.0

    def reset(self):
        self.stage1.reset()
        self.stage2.reset()
        self._inner_output = 0.0

    def step(self, control_input: float) -> tuple[float, float]:
        """单步计算

        Args:
            control_input: 控制量u

        Returns:
            (最终输出y, 中间变量/内环输出)
        """
        self._inner_output = self.stage1.step(control_input)
        final_output = self.stage2.step(self._inner_output)
        return final_output, self._inner_output

    @property
    def inner_output(self) -> float:
        return self._inner_output

    @property
    def t1(self) -> float:
        return self.stage1.time_constant

    @t1.setter
    def t1(self, value: float):
        self.stage1.time_constant = max(value, 1e-10)

    @property
    def t2(self) -> float:
        return self.stage2.time_constant

    @t2.setter
    def t2(self, value: float):
        self.stage2.time_constant = max(value, 1e-10)

    @property
    def gain(self) -> float:
        return self.stage1.gain

    @gain.setter
    def gain(self, value: float):
        self.stage1.gain = value
