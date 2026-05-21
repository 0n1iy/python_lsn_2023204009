"""UI组件测试"""

import unittest
import sys
from PyQt6.QtWidgets import QApplication


class TestUIComponents(unittest.TestCase):
    """UI组件基础测试"""

    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance()
        if cls._app is None:
            cls._app = QApplication(sys.argv)

    def test_pid_param_group_creation(self):
        """PID参数面板创建测试"""
        from src.ui.widgets import PIDParamGroup
        panel = PIDParamGroup()
        kp, ti, td = panel.get_values()
        self.assertEqual(kp, 2.0)
        self.assertEqual(ti, 2.0)
        self.assertEqual(td, 0.5)

    def test_pid_param_group_set_values(self):
        """PID参数面板设置测试"""
        from src.ui.widgets import PIDParamGroup
        panel = PIDParamGroup()
        panel.set_values(3.0, 4.0, 1.0)
        kp, ti, td = panel.get_values()
        self.assertEqual(kp, 3.0)
        self.assertEqual(ti, 4.0)
        self.assertEqual(td, 1.0)

    def test_cascade_param_group_creation(self):
        """串级参数面板创建测试"""
        from src.ui.widgets import CascadeParamGroup
        panel = CascadeParamGroup()
        outer = panel.get_outer_values()
        inner = panel.get_inner_values()
        self.assertEqual(outer[0], 2.0)
        self.assertEqual(inner[0], 1.0)

    def test_plot_widget_creation(self):
        """波形显示组件创建测试"""
        from src.ui.plot_widget import PlotWidget
        widget = PlotWidget(max_points=100)
        self.assertFalse(widget.is_paused)
        widget.add_data(0.1, 20.0, 15.0, 5.0, 0.0, 5.0)
        widget.pause()
        self.assertTrue(widget.is_paused)
        widget.resume()
        self.assertFalse(widget.is_paused)

    def test_status_bar_creation(self):
        """状态栏创建测试"""
        from src.ui.widgets import SimStatusBar
        bar = SimStatusBar()
        bar.update_time(10.5)
        bar.update_status("测试中")
        bar.update_strategy("单回路PID")


if __name__ == "__main__":
    unittest.main()
