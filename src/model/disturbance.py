"""干扰信号发生器 - 方波干扰"""

import time
from typing import Optional


class SquareWaveDisturbance:
    """方波干扰信号

    作用于被控对象输出端，叠加到最终输出上。
    振幅可正可负。
    """

    def __init__(self, amplitude: float = 0.0, duration: float = 5.0):
        self.amplitude = amplitude
        self.duration = duration
        self._active = False
        self._start_time: Optional[float] = None
        self._remaining_time = 0.0

    def trigger(self):
        """触发方波干扰"""
        self._active = True
        self._start_time = time.time()
        self._remaining_time = self.duration

    def update(self) -> float:
        """更新干扰值并返回当前值"""
        if not self._active:
            return 0.0

        elapsed = time.time() - self._start_time
        self._remaining_time = max(0.0, self.duration - elapsed)

        if elapsed >= self.duration:
            self._active = False
            self._remaining_time = 0.0
            return 0.0

        return self.amplitude

    def cancel(self):
        """取消当前干扰"""
        self._active = False
        self._remaining_time = 0.0

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def remaining_time(self) -> float:
        return self._remaining_time


class DisturbanceGenerator:
    """干扰信号管理器"""

    def __init__(self):
        self.square_wave = SquareWaveDisturbance(0.0, 5.0)
        self._current_value = 0.0

    def trigger_square_wave(self, amplitude: float, duration: float):
        """触发方波干扰

        Args:
            amplitude: 振幅
            duration: 持续时间（秒）
        """
        self.square_wave.amplitude = amplitude
        self.square_wave.duration = duration
        self.square_wave.trigger()

    def update(self) -> float:
        """更新并返回当前干扰值"""
        self._current_value = self.square_wave.update()
        return self._current_value

    def cancel(self):
        self.square_wave.cancel()
        self._current_value = 0.0

    @property
    def value(self) -> float:
        return self._current_value

    @property
    def is_active(self) -> bool:
        return self.square_wave.is_active

    @property
    def remaining_time(self) -> float:
        return self.square_wave.remaining_time
