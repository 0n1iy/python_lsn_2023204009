"""实时波形显示组件 - 基于pyqtgraph"""

import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor
import numpy as np


class PlotWidget(QWidget):
    """实时波形显示组件"""

    def __init__(self, max_points: int = 500, parent=None):
        super().__init__(parent)
        self._max_points = max_points
        self._paused = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self._plot = pg.PlotWidget()
        self._plot.setBackground("w")
        self._plot.showGrid(x=True, y=True, alpha=0.3)
        self._plot.setLabel("left", "数值")
        self._plot.setLabel("bottom", "时间 (s)")
        self._plot.addLegend()
        self._plot.setMouseEnabled(x=True, y=True)

        # 曲线颜色配置
        colors = {
            "SV": QColor(255, 0, 0),       # 红色
            "PV": QColor(0, 180, 0),       # 绿色
            "u": QColor(0, 0, 255),        # 蓝色
            "干扰": QColor(160, 0, 160),   # 紫色
            "误差": QColor(0, 180, 180),   # 青色
        }

        self._curves = {}
        for name, color in colors.items():
            pen = pg.mkPen(color=color, width=1.5)
            if name == "干扰":
                pen = pg.mkPen(color=color, width=1.5, style=Qt.PenStyle.DashLine)
            elif name == "误差":
                pen = pg.mkPen(color=color, width=1.5, style=Qt.PenStyle.DashDotLine)
            self._curves[name] = self._plot.plot([], [], pen=pen, name=name)

        self._time_data = []
        self._sv_data = []
        self._pv_data = []
        self._u_data = []
        self._disturbance_data = []
        self._error_data = []

        layout.addWidget(self._plot)
        self.setLayout(layout)

    def add_data(self, timestamp: float, sv: float, pv: float, u: float,
                 disturbance: float, error_val: float):
        """添加一个采样点的数据"""
        if self._paused:
            return

        self._time_data.append(timestamp)
        self._sv_data.append(sv)
        self._pv_data.append(pv)
        self._u_data.append(u)
        self._disturbance_data.append(disturbance)
        self._error_data.append(error_val)

        # 限制显示点数
        if len(self._time_data) > self._max_points:
            self._time_data = self._time_data[-self._max_points:]
            self._sv_data = self._sv_data[-self._max_points:]
            self._pv_data = self._pv_data[-self._max_points:]
            self._u_data = self._u_data[-self._max_points:]
            self._disturbance_data = self._disturbance_data[-self._max_points:]
            self._error_data = self._error_data[-self._max_points:]

        self._curves["SV"].setData(self._time_data, self._sv_data)
        self._curves["PV"].setData(self._time_data, self._pv_data)
        self._curves["u"].setData(self._time_data, self._u_data)
        self._curves["干扰"].setData(self._time_data, self._disturbance_data)
        self._curves["误差"].setData(self._time_data, self._error_data)

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def clear(self):
        self._time_data.clear()
        self._sv_data.clear()
        self._pv_data.clear()
        self._u_data.clear()
        self._disturbance_data.clear()
        self._error_data.clear()
        for curve in self._curves.values():
            curve.setData([], [])

    @property
    def is_paused(self) -> bool:
        return self._paused


class HistoryPlotWidget(QWidget):
    """历史曲线显示组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self._plot = pg.PlotWidget()
        self._plot.setBackground("w")
        self._plot.showGrid(x=True, y=True, alpha=0.3)
        self._plot.setLabel("left", "数值")
        self._plot.setLabel("bottom", "时间 (s)")
        self._plot.addLegend()

        colors = {
            "SV": QColor(255, 0, 0),
            "PV": QColor(0, 180, 0),
            "u": QColor(0, 0, 255),
            "干扰": QColor(160, 0, 160),
        }

        self._curves = {}
        for name, color in colors.items():
            pen = pg.mkPen(color=color, width=1.5)
            if name == "干扰":
                pen = pg.mkPen(color=color, width=1.5, style=Qt.PenStyle.DashLine)
            self._curves[name] = self._plot.plot([], [], pen=pen, name=name)

        self._plot.setMouseEnabled(x=True, y=True)
        layout.addWidget(self._plot)
        self.setLayout(layout)

    def load_data(self, records: list):
        """加载历史数据

        Args:
            records: 记录列表，每条含 time, sv, pv, u, disturbance
        """
        times = [r["time"] for r in records]
        self._curves["SV"].setData(times, [r["sv"] for r in records])
        self._curves["PV"].setData(times, [r["pv"] for r in records])
        self._curves["u"].setData(times, [r["u"] for r in records])
        self._curves["干扰"].setData(times, [r.get("disturbance", 0) for r in records])

    def clear(self):
        for curve in self._curves.values():
            curve.setData([], [])
