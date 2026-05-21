"""反馈环节模型 - 传感器模拟

一阶低通滤波器: H(s) = 1/(Tc*s + 1), Tc = 0.1s
"""

import numpy as np


class FeedbackModel:
    """反馈环节 - 一阶低通滤波器，模拟传感器动态特性"""

    def __init__(self, time_constant: float = 0.1, dt: float = 0.05):
        self.time_constant = time_constant
        self.dt = dt
        self._output = 0.0

    def reset(self):
        self._output = 0.0

    def step(self, input_val: float) -> float:
        tc = max(self.time_constant, 1e-10)
        self._output += (self.dt / tc) * (input_val - self._output)
        return self._output

    @property
    def output(self) -> float:
        return self._output


class SensorWithNoise(FeedbackModel):
    """带测量噪声的传感器模型"""

    def __init__(self, time_constant: float = 0.1, dt: float = 0.05,
                 noise_std: float = 0.0):
        super().__init__(time_constant, dt)
        self.noise_std = noise_std

    def step(self, input_val: float) -> float:
        filtered = super().step(input_val)
        noise = np.random.normal(0, self.noise_std) if self.noise_std > 0 else 0.0
        return filtered + noise
