"""被控对象模型测试"""

import unittest
from src.model.two_inertia_model import FirstOrderLag, TwoInertiaModel


class TestFirstOrderLag(unittest.TestCase):
    """一阶惯性环节测试"""

    def setUp(self):
        self.lag = FirstOrderLag(time_constant=1.0, gain=1.0, dt=0.05)

    def test_initial_output_zero(self):
        self.assertEqual(self.lag.output, 0.0)

    def test_step_response(self):
        """阶跃响应：多次迭代后输出趋近输入"""
        for _ in range(200):
            self.lag.step(1.0)
        self.assertGreater(self.lag.output, 0.8)
        self.assertLessEqual(self.lag.output, 1.0)

    def test_reset(self):
        for _ in range(100):
            self.lag.step(1.0)
        self.assertNotEqual(self.lag.output, 0.0)
        self.lag.reset()
        self.assertEqual(self.lag.output, 0.0)

    def test_gain(self):
        """增益测试"""
        lag = FirstOrderLag(time_constant=0.5, gain=2.0, dt=0.05)
        for _ in range(100):
            lag.step(1.0)
        self.assertGreater(lag.output, 1.0)

    def test_time_constant_effect(self):
        """时间常数越大，响应越慢"""
        fast = FirstOrderLag(time_constant=0.1, gain=1.0, dt=0.05)
        slow = FirstOrderLag(time_constant=5.0, gain=1.0, dt=0.05)
        fast.step(1.0)
        slow.step(1.0)
        self.assertGreater(fast.output, slow.output)


class TestTwoInertiaModel(unittest.TestCase):
    """双惯性环节模型测试"""

    def setUp(self):
        self.model = TwoInertiaModel(t1=1.0, t2=2.0, gain=1.0, dt=0.05)

    def test_initial_outputs_zero(self):
        y, inner = self.model.step(0.0)
        self.assertEqual(y, 0.0)
        self.assertEqual(inner, 0.0)

    def test_step_response(self):
        """双惯性串联：更长延迟"""
        for _ in range(400):
            y, inner = self.model.step(1.0)
        self.assertGreater(y, 0.7)
        self.assertLessEqual(y, 1.0)

    def test_inner_output(self):
        """内环输出(中间变量)应早于最终输出"""
        self.model.reset()
        self.model.step(1.0)
        self.assertGreater(self.model.inner_output, 0.0)

    def test_reset(self):
        for _ in range(100):
            self.model.step(1.0)
        self.model.reset()
        y, _ = self.model.step(0.0)
        self.assertEqual(y, 0.0)


if __name__ == "__main__":
    unittest.main()
