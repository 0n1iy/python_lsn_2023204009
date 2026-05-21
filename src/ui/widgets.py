"""自定义控件 - PID参数面板、状态栏等"""

from PyQt6.QtWidgets import (
    QWidget, QGroupBox, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QGridLayout, QComboBox,
    QDoubleSpinBox, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.config import TempConfig, ControlStrategy


class PIDParamGroup(QGroupBox):
    """PID参数输入面板"""

    params_changed = pyqtSignal(float, float, float)  # kp, ti, td

    def __init__(self, title: str = "PID参数", parent=None):
        super().__init__(title, parent)
        self._init_ui()

    def _init_ui(self):
        layout = QGridLayout()

        layout.addWidget(QLabel("Kp:"), 0, 0)
        self._kp_spin = QDoubleSpinBox()
        self._kp_spin.setRange(TempConfig.KP_MIN, 9999.0)
        self._kp_spin.setDecimals(2)
        self._kp_spin.setValue(TempConfig.PID_KP_DEFAULT)
        self._kp_spin.setSingleStep(0.1)
        self._kp_spin.valueChanged.connect(self._on_changed)
        layout.addWidget(self._kp_spin, 0, 1)

        layout.addWidget(QLabel("Ti:"), 0, 2)
        self._ti_spin = QDoubleSpinBox()
        self._ti_spin.setRange(TempConfig.TI_MIN, 9999.0)
        self._ti_spin.setDecimals(2)
        self._ti_spin.setValue(TempConfig.PID_TI_DEFAULT)
        self._ti_spin.setSingleStep(0.1)
        self._ti_spin.valueChanged.connect(self._on_changed)
        layout.addWidget(self._ti_spin, 0, 3)

        layout.addWidget(QLabel("Td:"), 0, 4)
        self._td_spin = QDoubleSpinBox()
        self._td_spin.setRange(TempConfig.TD_MIN, 9999.0)
        self._td_spin.setDecimals(2)
        self._td_spin.setValue(TempConfig.PID_TD_DEFAULT)
        self._td_spin.setSingleStep(0.1)
        self._td_spin.valueChanged.connect(self._on_changed)
        layout.addWidget(self._td_spin, 0, 5)

        self.setLayout(layout)

    def _on_changed(self):
        self.params_changed.emit(self._kp_spin.value(),
                                 self._ti_spin.value(),
                                 self._td_spin.value())

    def get_values(self) -> tuple:
        return self._kp_spin.value(), self._ti_spin.value(), self._td_spin.value()

    def set_values(self, kp: float, ti: float, td: float):
        self._kp_spin.blockSignals(True)
        self._ti_spin.blockSignals(True)
        self._td_spin.blockSignals(True)
        self._kp_spin.setValue(kp)
        self._ti_spin.setValue(ti)
        self._td_spin.setValue(td)
        self._kp_spin.blockSignals(False)
        self._ti_spin.blockSignals(False)
        self._td_spin.blockSignals(False)

    @property
    def kp(self) -> float:
        return self._kp_spin.value()

    @property
    def ti(self) -> float:
        return self._ti_spin.value()

    @property
    def td(self) -> float:
        return self._td_spin.value()


class CascadeParamGroup(QGroupBox):
    """串级PID参数面板（外环+内环）"""

    outer_changed = pyqtSignal(float, float, float)
    inner_changed = pyqtSignal(float, float, float)

    def __init__(self, parent=None):
        super().__init__("PID参数", parent)
        self._outer = PIDParamGroup()
        self._inner = PIDParamGroup()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        outer_label = QLabel("外环参数")
        outer_font = QFont()
        outer_font.setBold(True)
        outer_label.setFont(outer_font)
        layout.addWidget(outer_label)

        self._outer = PIDParamGroup()
        self._outer.set_values(TempConfig.CASCADE_OUTER_KP_DEFAULT,
                               TempConfig.CASCADE_OUTER_TI_DEFAULT,
                               TempConfig.CASCADE_OUTER_TD_DEFAULT)
        self._outer.params_changed.connect(
            lambda k, i, d: self.outer_changed.emit(k, i, d))
        layout.addWidget(self._outer)

        inner_label = QLabel("内环参数")
        inner_label.setFont(outer_font)
        layout.addWidget(inner_label)

        self._inner = PIDParamGroup()
        self._inner.set_values(TempConfig.CASCADE_INNER_KP_DEFAULT,
                               TempConfig.CASCADE_INNER_TI_DEFAULT,
                               TempConfig.CASCADE_INNER_TD_DEFAULT)
        self._inner.params_changed.connect(
            lambda k, i, d: self.inner_changed.emit(k, i, d))
        layout.addWidget(self._inner)

        self.setLayout(layout)

    def get_outer_values(self) -> tuple:
        return self._outer.get_values()

    def get_inner_values(self) -> tuple:
        return self._inner.get_values()


class DisturbanceControl(QGroupBox):
    """干扰信号控制面板"""

    trigger_signal = pyqtSignal(float, float)  # amplitude, duration

    def __init__(self, parent=None):
        super().__init__("干扰信号", parent)
        self._init_ui()

    def _init_ui(self):
        layout = QGridLayout()

        layout.addWidget(QLabel("振幅:"), 0, 0)
        self._amp_spin = QDoubleSpinBox()
        self._amp_spin.setRange(-50.0, 50.0)
        self._amp_spin.setDecimals(1)
        self._amp_spin.setValue(0.0)
        self._amp_spin.setSingleStep(0.5)
        layout.addWidget(self._amp_spin, 0, 1)

        layout.addWidget(QLabel("持续时间(秒):"), 0, 2)
        self._duration_spin = QDoubleSpinBox()
        self._duration_spin.setRange(0.1, 3600.0)
        self._duration_spin.setDecimals(1)
        self._duration_spin.setValue(5.0)
        self._duration_spin.setSingleStep(1.0)
        layout.addWidget(self._duration_spin, 0, 3)

        self._trigger_btn = QPushButton("施加方波干扰")
        self._trigger_btn.setFixedHeight(32)
        self._trigger_btn.clicked.connect(self._on_trigger)
        layout.addWidget(self._trigger_btn, 0, 4)

        self._status_label = QLabel("")
        layout.addWidget(self._status_label, 1, 0, 1, 5)

        self.setLayout(layout)

    def _on_trigger(self):
        amp = self._amp_spin.value()
        dur = self._duration_spin.value()
        self._trigger_btn.setEnabled(False)
        self.trigger_signal.emit(amp, dur)

    def update_remaining(self, remaining: float):
        if remaining > 0:
            self._status_label.setText(f"干扰中... 剩余 {remaining:.1f}s")
        else:
            self._status_label.setText("")
            self._trigger_btn.setEnabled(True)


class SimStatusBar(QStatusBar):
    """仿真状态栏"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._time_label = QLabel("仿真时间: 0.0s")
        self._status_label = QLabel("就绪")
        self._strategy_label = QLabel("策略: 单回路PID")

        self.addWidget(self._time_label)
        self.addWidget(self._strategy_label, 1)
        self.addPermanentWidget(self._status_label)

    def update_time(self, t: float):
        self._time_label.setText(f"仿真时间: {t:.1f}s")

    def update_status(self, text: str):
        self._status_label.setText(text)

    def update_strategy(self, text: str):
        self._strategy_label.setText(f"策略: {text}")
