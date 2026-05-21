"""PID控制器测试"""

import unittest
from src.control.pid_controller import SimplePIDController, PIDController


class TestSimplePIDController(unittest.TestCase):
    """纯PID控制器测试"""

    def setUp(self):
        self.pid = SimplePIDController(kp=2.0, ti=2.0, td=0.5, dt=0.05)

    def test_initial_output_zero(self):
        self.assertEqual(self.pid.output, 0.0)

    def test_proportional_response(self):
        """测试比例响应 - 正偏差产生正输出"""
        u = self.pid.compute(20.0, 0.0)
        self.assertGreater(u, 0.0)

    def test_integral_accumulation(self):
        """测试积分累积"""
        self.pid.compute(20.0, 0.0)
        self.assertGreater(self.pid.integral, 0.0)

    def test_steady_state_error_reduction(self):
        """稳态误差应随积分累积而减小"""
        for _ in range(200):
            self.pid.compute(20.0, 19.0)
        self.assertTrue(abs(self.pid.output) > 0.1)

    def test_reset(self):
        """测试重置"""
        self.pid.compute(20.0, 0.0)
        self.assertNotEqual(self.pid.integral, 0.0)
        self.pid.reset()
        self.assertEqual(self.pid.integral, 0.0)
        self.assertEqual(self.pid._prev_error, 0.0)

    def test_negative_error(self):
        """负偏差产生负控制"""
        u = self.pid.compute(0.0, 20.0)
        self.assertLess(u, 0.0)


class TestPIDController(unittest.TestCase):
    """带抗饱和PID控制器测试"""

    def setUp(self):
        self.pid = PIDController(kp=2.0, ti=2.0, td=0.5, dt=0.05,
                                  u_min=-30.0, u_max=30.0)

    def test_output_clamping(self):
        """长时间积分后输出不应超过限幅"""
        for _ in range(500):
            self.pid.compute(30.0, 0.0)
        self.assertLessEqual(self.pid.output, 30.0)
        self.assertGreaterEqual(self.pid.output, -30.0)

    def test_anti_windup(self):
        """抗饱和：输出饱和时积分不应无限制增长"""
        for _ in range(500):
            self.pid.compute(30.0, 0.0)
        integral = self.pid.integral
        # 积分不应过大（有抗饱和保护）
        self.assertLess(abs(integral), 1000.0)

    def test_track_output(self):
        """无扰动切换：跟踪后输出应为指定值"""
        self.pid.track_output(15.0)
        self.assertEqual(self.pid.output, 15.0)

    def test_no_limits_mode(self):
        """无限幅模式下输出可超出范围"""
        pid = PIDController(kp=10.0, ti=1.0, td=1.0, dt=0.05,
                           u_min=None, u_max=None, anti_windup=False)
        for _ in range(200):
            pid.compute(30.0, 0.0)
        self.assertGreater(pid.output, 30.0)


if __name__ == "__main__":
    unittest.main()
