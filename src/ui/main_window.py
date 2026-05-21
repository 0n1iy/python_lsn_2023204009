"""主界面 - 菜单、控制面板、波形显示"""

import traceback
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QGroupBox, QLabel, QPushButton, QComboBox, QDoubleSpinBox,
    QMenuBar, QMenu, QMessageBox, QFrame, QGridLayout, QScrollArea,
    QStatusBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QFont

from src.config import ControlStrategy, TempConfig, APP_TITLE, APP_VERSION
from src.control.control_strategy import ControlStrategyManager, ControlMode
from src.model.two_inertia_model import TwoInertiaModel
from src.model.feedback_model import FeedbackModel
from src.model.disturbance import DisturbanceGenerator
from src.ui.plot_widget import PlotWidget
from src.ui.history_window import HistoryWindow
from src.ui.user_manager_ui import UserManagerWindow
from src.ui.change_pwd_ui import ChangePasswordDialog
from src.ui.widgets import PIDParamGroup, CascadeParamGroup, DisturbanceControl, SimStatusBar
from src.user.permission import CurrentUser, Permissions
from src.utils.data_logger import DataLogger
from src.utils.validator import validate_pid_params
from src.exception import show_error_dialog, show_info_dialog


STRATEGY_NAMES = {
    ControlStrategy.PLAIN_PID: "普通PID（无限幅）",
    ControlStrategy.SINGLE_LOOP_PID: "单回路PID（抗饱和）",
    ControlStrategy.FEEDFORWARD_FB: "前馈+反馈",
    ControlStrategy.CASCADE: "串级PID",
    ControlStrategy.CASCADE_FF: "串级+前馈",
}


class MainWindow(QMainWindow):
    """主界面窗口"""

    def __init__(self):
        super().__init__()
        self._sim_running = False
        self._sim_paused = False
        self._sim_time = 0.0
        self._dt = TempConfig.DT_DEFAULT

        # 仿真组件
        self._strategy_mgr = ControlStrategyManager(self._dt)
        self._model = TwoInertiaModel(
            t1=TempConfig.T1_DEFAULT,
            t2=TempConfig.T2_DEFAULT,
            gain=TempConfig.GAIN_DEFAULT,
            dt=self._dt,
        )
        self._feedback = FeedbackModel(TempConfig.TC_DEFAULT, self._dt)
        self._disturbance_gen = DisturbanceGenerator()
        self._data_logger = DataLogger()

        # 子窗口引用
        self._history_window: HistoryWindow = None
        self._user_manager_window: UserManagerWindow = None

        self._init_ui()
        self._init_menu()

        # 仿真定时器
        self._timer = QTimer()
        self._timer.timeout.connect(self._simulation_step)
        self._timer.setInterval(int(self._dt * 1000))  # 转换为毫秒

        # 干扰倒计时定时器
        self._disturbance_timer = QTimer()
        self._disturbance_timer.timeout.connect(self._update_disturbance_status)
        self._disturbance_timer.setInterval(200)  # 200ms更新一次

    def _init_ui(self):
        self.setWindowTitle(f"{APP_TITLE} {APP_VERSION}")
        self.setMinimumSize(1200, 750)

        # 中央控件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # 左侧控制面板（可滚动）
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumWidth(380)
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(8)

        # 仿真控制
        sim_group = QGroupBox("仿真控制")
        sim_layout = QVBoxLayout()

        # SV 设定值
        sv_layout = QHBoxLayout()
        sv_layout.addWidget(QLabel("SV 设定温度:"))
        self._sv_spin = QDoubleSpinBox()
        self._sv_spin.setRange(TempConfig.SV_MIN, TempConfig.SV_MAX)
        self._sv_spin.setDecimals(1)
        self._sv_spin.setValue(TempConfig.SV_DEFAULT)
        self._sv_spin.setSuffix(" °C")
        sv_layout.addWidget(self._sv_spin)
        sim_layout.addLayout(sv_layout)

        # PV 显示
        pv_layout = QHBoxLayout()
        pv_layout.addWidget(QLabel("PV 过程温度:"))
        self._pv_label = QLabel("0.00 °C")
        font = QFont()
        font.setBold(True)
        self._pv_label.setFont(font)
        pv_layout.addWidget(self._pv_label)
        pv_layout.addStretch()
        sim_layout.addLayout(pv_layout)

        # 控制量显示
        u_layout = QHBoxLayout()
        u_layout.addWidget(QLabel("控制量 u:"))
        self._u_label = QLabel("0.00")
        self._u_label.setFont(font)
        u_layout.addWidget(self._u_label)
        u_layout.addStretch()
        sim_layout.addLayout(u_layout)

        # 控制策略选择
        strategy_layout = QHBoxLayout()
        strategy_layout.addWidget(QLabel("控制策略:"))
        self._strategy_combo = QComboBox()
        for strategy, name in STRATEGY_NAMES.items():
            self._strategy_combo.addItem(name, strategy)
        self._strategy_combo.currentIndexChanged.connect(self._on_strategy_changed)
        strategy_layout.addWidget(self._strategy_combo)
        sim_layout.addLayout(strategy_layout)

        # 手动/自动模式
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("控制模式:"))
        self._mode_combo = QComboBox()
        self._mode_combo.addItem("自动模式", ControlMode.AUTO)
        self._mode_combo.addItem("手动模式", ControlMode.MANUAL)
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self._mode_combo)
        sim_layout.addLayout(mode_layout)

        # 手动输出
        manual_layout = QHBoxLayout()
        manual_layout.addWidget(QLabel("手动输出值:"))
        self._manual_spin = QDoubleSpinBox()
        self._manual_spin.setRange(-TempConfig.CONTROL_MANUAL_LIMIT,
                                    TempConfig.CONTROL_MANUAL_LIMIT)
        self._manual_spin.setDecimals(2)
        self._manual_spin.setValue(0.0)
        self._manual_spin.setEnabled(False)
        self._manual_spin.valueChanged.connect(self._on_manual_value_changed)
        manual_layout.addWidget(self._manual_spin)
        sim_layout.addLayout(manual_layout)

        # 仿真按钮
        btn_layout = QHBoxLayout()
        self._start_btn = QPushButton("开始")
        self._start_btn.clicked.connect(self._on_start)
        btn_layout.addWidget(self._start_btn)

        self._pause_btn = QPushButton("暂停")
        self._pause_btn.clicked.connect(self._on_pause)
        self._pause_btn.setEnabled(False)
        btn_layout.addWidget(self._pause_btn)

        self._stop_btn = QPushButton("停止")
        self._stop_btn.clicked.connect(self._on_stop)
        self._stop_btn.setEnabled(False)
        btn_layout.addWidget(self._stop_btn)

        sim_layout.addLayout(btn_layout)
        sim_group.setLayout(sim_layout)
        control_layout.addWidget(sim_group)

        # PID参数面板
        self._pid_panel = PIDParamGroup()
        self._pid_panel.params_changed.connect(self._on_pid_params_changed)
        control_layout.addWidget(self._pid_panel)

        # 串级PID参数面板（初始隐藏）
        self._cascade_panel = CascadeParamGroup()
        self._cascade_panel.outer_changed.connect(self._on_cascade_outer_changed)
        self._cascade_panel.inner_changed.connect(self._on_cascade_inner_changed)
        self._cascade_panel.hide()
        control_layout.addWidget(self._cascade_panel)

        # 被控对象参数
        model_group = QGroupBox("被控对象参数")
        model_layout = QGridLayout()

        model_layout.addWidget(QLabel("T₁:"), 0, 0)
        self._t1_spin = QDoubleSpinBox()
        self._t1_spin.setRange(0.01, 100.0)
        self._t1_spin.setDecimals(2)
        self._t1_spin.setValue(TempConfig.T1_DEFAULT)
        self._t1_spin.setSingleStep(0.1)
        self._t1_spin.valueChanged.connect(lambda v: setattr(self._model, 't1', v))
        model_layout.addWidget(self._t1_spin, 0, 1)

        model_layout.addWidget(QLabel("T₂:"), 0, 2)
        self._t2_spin = QDoubleSpinBox()
        self._t2_spin.setRange(0.01, 100.0)
        self._t2_spin.setDecimals(2)
        self._t2_spin.setValue(TempConfig.T2_DEFAULT)
        self._t2_spin.setSingleStep(0.1)
        self._t2_spin.valueChanged.connect(lambda v: setattr(self._model, 't2', v))
        model_layout.addWidget(self._t2_spin, 0, 3)

        model_layout.addWidget(QLabel("增益:"), 1, 0)
        self._gain_spin = QDoubleSpinBox()
        self._gain_spin.setRange(0.01, 100.0)
        self._gain_spin.setDecimals(2)
        self._gain_spin.setValue(TempConfig.GAIN_DEFAULT)
        self._gain_spin.setSingleStep(0.1)
        self._gain_spin.valueChanged.connect(lambda v: setattr(self._model, 'gain', v))
        model_layout.addWidget(self._gain_spin, 1, 1)

        model_group.setLayout(model_layout)
        control_layout.addWidget(model_group)

        # 干扰控制
        self._disturbance_ctrl = DisturbanceControl()
        self._disturbance_ctrl.trigger_signal.connect(self._on_disturbance_triggered)
        control_layout.addWidget(self._disturbance_ctrl)

        control_layout.addStretch()

        scroll.setWidget(control_panel)
        main_layout.addWidget(scroll)

        # 右侧波形显示
        self._plot_widget = PlotWidget(max_points=TempConfig.DISPLAY_POINTS_DEFAULT)
        main_layout.addWidget(self._plot_widget, 1)

        # 状态栏
        self._status_bar = SimStatusBar()
        self.setStatusBar(self._status_bar)

    def _init_menu(self):
        """初始化菜单栏"""
        menu_bar = self.menuBar()

        # 系统菜单
        sys_menu = menu_bar.addMenu("系统")

        logout_action = QAction("退出登录", self)
        logout_action.triggered.connect(self._on_logout)
        sys_menu.addAction(logout_action)

        sys_menu.addSeparator()

        exit_action = QAction("退出程序", self)
        exit_action.triggered.connect(self.close)
        sys_menu.addAction(exit_action)

        # 功能菜单
        func_menu = menu_bar.addMenu("功能")

        history_action = QAction("历史曲线", self)
        history_action.triggered.connect(self._on_open_history)
        func_menu.addAction(history_action)

        # 用户管理菜单
        user_menu = menu_bar.addMenu("用户管理")

        change_pwd_action = QAction("修改密码", self)
        change_pwd_action.triggered.connect(self._on_change_password)
        user_menu.addAction(change_pwd_action)

        self._manage_user_action = QAction("管理用户", self)
        self._manage_user_action.triggered.connect(self._on_manage_users)
        self._manage_user_action.setVisible(CurrentUser().has_permission(Permissions.MANAGE_USERS))
        user_menu.addAction(self._manage_user_action)

        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")

        about_action = QAction("关于软件", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _on_strategy_changed(self, index: int):
        """切换控制策略"""
        strategy = self._strategy_combo.currentData()
        self._strategy_mgr.set_strategy(strategy)

        # 切换PID参数面板
        is_cascade = strategy in (ControlStrategy.CASCADE, ControlStrategy.CASCADE_FF)
        self._pid_panel.setVisible(not is_cascade)
        self._cascade_panel.setVisible(is_cascade)

        self._status_bar.update_strategy(STRATEGY_NAMES.get(strategy, ""))

    def _on_mode_changed(self, index: int):
        """切换手动/自动模式"""
        mode = self._mode_combo.currentData()
        self._strategy_mgr.set_mode(mode)

        is_manual = mode == ControlMode.MANUAL
        self._manual_spin.setEnabled(is_manual)
        self._sv_spin.setEnabled(not is_manual)

        if is_manual:
            self._status_bar.update_status("手动模式")
        else:
            self._status_bar.update_status("自动模式")

    def _on_manual_value_changed(self, value: float):
        self._strategy_mgr.set_manual_output(value)

    def _on_pid_params_changed(self, kp: float, ti: float, td: float):
        self._strategy_mgr.update_pid_params(kp, ti, td)

    def _on_cascade_outer_changed(self, kp: float, ti: float, td: float):
        self._strategy_mgr.update_cascade_outer_params(kp, ti, td)

    def _on_cascade_inner_changed(self, kp: float, ti: float, td: float):
        self._strategy_mgr.update_cascade_inner_params(kp, ti, td)

    def _on_start(self):
        """开始仿真"""
        sv = self._sv_spin.value()
        if sv < TempConfig.SV_MIN or sv > TempConfig.SV_MAX:
            QMessageBox.warning(self, "参数错误",
                f"SV设定值超出范围 [{TempConfig.SV_MIN}, {TempConfig.SV_MAX}]")
            return

        if not self._sim_running:
            self._sim_running = True
            self._sim_paused = False
            self._sim_time = 0.0

            # 重置模型和控制器
            self._model.reset()
            self._feedback.reset()
            self._strategy_mgr.reset_all()
            self._disturbance_gen.cancel()
            self._data_logger.clear()
            self._plot_widget.clear()

            self._start_btn.setEnabled(False)
            self._pause_btn.setEnabled(True)
            self._stop_btn.setEnabled(True)
            self._sv_spin.setEnabled(True)
            self._strategy_combo.setEnabled(False)

            self._timer.start()
            self._disturbance_timer.start()
            self._status_bar.update_status("运行中...")

    def _on_pause(self):
        """暂停/继续仿真"""
        if not self._sim_running:
            return

        if self._sim_paused:
            self._sim_paused = False
            self._plot_widget.resume()
            self._pause_btn.setText("暂停")
            self._status_bar.update_status("运行中...")
        else:
            self._sim_paused = True
            self._plot_widget.pause()
            self._pause_btn.setText("继续")
            self._status_bar.update_status("已暂停")

    def _on_stop(self):
        """停止仿真"""
        self._sim_running = False
        self._sim_paused = False
        self._timer.stop()
        self._disturbance_timer.stop()

        # 保存会话数据
        try:
            self._data_logger.save_session()
        except Exception as e:
            show_error_dialog(self, "保存失败", f"保存仿真数据失败：{str(e)}")

        self._start_btn.setEnabled(True)
        self._pause_btn.setEnabled(False)
        self._stop_btn.setEnabled(False)
        self._pause_btn.setText("暂停")
        self._strategy_combo.setEnabled(True)
        self._status_bar.update_status("已停止")

    def _simulation_step(self):
        """单步仿真计算"""
        if not self._sim_running or self._sim_paused:
            return

        try:
            sv = self._sv_spin.value()

            # 被控对象
            u = self._strategy_mgr.output
            y_raw, inner_y = self._model.step(u)

            # 干扰
            disturbance = self._disturbance_gen.update()
            y_with_dist = y_raw + disturbance

            # 反馈环节
            pv = self._feedback.step(y_with_dist)

            # 误差
            error = sv - pv

            # 控制量计算
            strategy = self._strategy_mgr.strategy
            if strategy in (ControlStrategy.CASCADE, ControlStrategy.CASCADE_FF):
                u = self._strategy_mgr.compute(sv, pv, inner_y, disturbance)
            elif strategy == ControlStrategy.FEEDFORWARD_FB:
                u = self._strategy_mgr.compute(sv, pv, disturbance=disturbance)
            else:
                u = self._strategy_mgr.compute(sv, pv)

            # 更新显示
            self._pv_label.setText(f"{pv:.2f} °C")
            self._u_label.setText(f"{u:.2f}")

            # 记录数据
            self._data_logger.record(self._sim_time, sv, pv, u, disturbance, error)

            # 更新波形
            self._plot_widget.add_data(self._sim_time, sv, pv, u, disturbance, error)

            # 更新状态栏
            self._status_bar.update_time(self._sim_time)

            self._sim_time += self._dt

        except Exception as e:
            traceback.print_exc()
            show_error_dialog(self, "仿真计算错误",
                f"仿真计算过程中发生错误：{str(e)}\n仿真已暂停。")
            self._on_pause()

    def _on_disturbance_triggered(self, amplitude: float, duration: float):
        """触发方波干扰"""
        self._disturbance_gen.trigger_square_wave(amplitude, duration)

    def _update_disturbance_status(self):
        """更新干扰状态显示"""
        remaining = self._disturbance_gen.remaining_time
        self._disturbance_ctrl.update_remaining(remaining)

    def _on_logout(self):
        """退出登录"""
        reply = QMessageBox.question(
            self, "退出登录", "确定要退出登录吗？\n当前仿真数据将丢失。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._on_stop()
            CurrentUser().logout()
            self.close()

    def _on_open_history(self):
        """打开历史曲线窗口"""
        if self._history_window is None:
            self._history_window = HistoryWindow(self)
        self._history_window.show()
        self._history_window.raise_()

    def _on_change_password(self):
        """打开修改密码对话框"""
        dialog = ChangePasswordDialog(self)
        dialog.exec()

    def _on_manage_users(self):
        """打开用户管理窗口"""
        if not CurrentUser().has_permission(Permissions.MANAGE_USERS):
            QMessageBox.warning(self, "权限不足", "您没有管理用户的权限")
            return

        if self._user_manager_window is None:
            self._user_manager_window = UserManagerWindow(self)
        self._user_manager_window = UserManagerWindow(self)
        self._user_manager_window.show()

    def _on_about(self):
        """关于软件"""
        about_text = (
            f"<h3>{APP_TITLE}</h3>"
            f"<p>版本: {APP_VERSION}</p>"
            f"<p>基于Python + PyQt6 + pyqtgraph开发的<br>"
            f"温度控制仿真教学软件</p>"
            f"<p>功能特性:</p>"
            f"<ul>"
            f"<li>5种控制策略（PID / 串级 / 前馈）</li>"
            f"<li>实时波形显示</li>"
            f"<li>用户权限管理</li>"
            f"<li>历史数据查询与Excel导出</li>"
            f"<li>方波干扰模拟</li>"
            f"</ul>"
        )
        QMessageBox.about(self, "关于软件", about_text)

    def closeEvent(self, event):
        """关闭窗口事件"""
        if self._sim_running:
            reply = QMessageBox.question(
                self, "确认退出",
                "仿真正在运行中，确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            self._on_stop()

        # 关闭子窗口
        if self._history_window:
            self._history_window.close()
        if self._user_manager_window:
            self._user_manager_window.close()

        event.accept()
