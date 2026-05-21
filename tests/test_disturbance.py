"""干扰信号测试"""

import unittest
import time
from src.model.disturbance import SquareWaveDisturbance, DisturbanceGenerator


class TestSquareWaveDisturbance(unittest.TestCase):
    """方波干扰测试"""

    def test_initial_state(self):
        d = SquareWaveDisturbance(5.0, 2.0)
        self.assertFalse(d.is_active)
        self.assertEqual(d.update(), 0.0)

    def test_trigger(self):
        d = SquareWaveDisturbance(5.0, 10.0)
        d.trigger()
        self.assertTrue(d.is_active)
        val = d.update()
        self.assertEqual(val, 5.0)

    def test_remaining_time(self):
        d = SquareWaveDisturbance(3.0, 5.0)
        d.trigger()
        self.assertGreater(d.remaining_time, 0.0)
        self.assertLessEqual(d.remaining_time, 5.0)

    def test_cancel(self):
        d = SquareWaveDisturbance(5.0, 10.0)
        d.trigger()
        d.cancel()
        self.assertFalse(d.is_active)
        self.assertEqual(d.remaining_time, 0.0)

    def test_negative_amplitude(self):
        d = SquareWaveDisturbance(-3.0, 10.0)
        d.trigger()
        self.assertEqual(d.update(), -3.0)


class TestDisturbanceGenerator(unittest.TestCase):
    """干扰管理器测试"""

    def test_trigger_square_wave(self):
        gen = DisturbanceGenerator()
        gen.trigger_square_wave(4.0, 5.0)
        val = gen.update()
        self.assertEqual(val, 4.0)
        self.assertTrue(gen.is_active)

    def test_cancel(self):
        gen = DisturbanceGenerator()
        gen.trigger_square_wave(4.0, 5.0)
        gen.cancel()
        self.assertEqual(gen.value, 0.0)
        self.assertFalse(gen.is_active)


if __name__ == "__main__":
    unittest.main()
