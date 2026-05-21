"""控制策略管理器 - 5种策略切换，手动/自动模式"""

from enum import Enum, auto
from typing import Optional

from src.config import ControlStrategy, TempConfig
from src.control.pid_controller import SimplePIDController, PIDController
from src.control.cascade_control import CascadeController, CascadeWithFeedforward
from src.control.feedforward_control import FeedforwardFeedbackController


class ControlMode(Enum):
    """控制模式"""
    AUTO = auto()
    MANUAL = auto()


class ControlStrategyManager:
    """控制策略管理器

    管理5种控制策略，支持：
    - 运行中无缝切换策略
    - 手动/自动模式无扰动切换
    - 实时PID参数修改
    """

    def __init__(self, dt: float = 0.05):
        self.dt = dt
        self._strategy = ControlStrategy.SINGLE_LOOP_PID
        self._mode = ControlMode.AUTO
        self._manual_output = 0.0
        self._output = 0.0

        # 初始化所有策略控制器
        self._plain_pid = SimplePIDController(
            kp=TempConfig.PID_KP_DEFAULT,
            ti=TempConfig.PID_TI_DEFAULT,
            td=TempConfig.PID_TD_DEFAULT,
            dt=dt,
        )
        self._single_loop_pid = PIDController(
            kp=TempConfig.PID_KP_DEFAULT,
            ti=TempConfig.PID_TI_DEFAULT,
            td=TempConfig.PID_TD_DEFAULT,
            dt=dt,
            u_min=-TempConfig.CONTROL_AUTO_LIMIT,
            u_max=TempConfig.CONTROL_AUTO_LIMIT,
            anti_windup=True,
        )
        self._feedforward_fb = FeedforwardFeedbackController(
            kp=TempConfig.PID_KP_DEFAULT,
            ti=TempConfig.PID_TI_DEFAULT,
            td=TempConfig.PID_TD_DEFAULT,
            ff_gain=TempConfig.FF_GAIN_DEFAULT,
            dt=dt,
            u_min=-TempConfig.CONTROL_AUTO_LIMIT,
            u_max=TempConfig.CONTROL_AUTO_LIMIT,
        )
        self._cascade = CascadeController(
            outer_kp=TempConfig.CASCADE_OUTER_KP_DEFAULT,
            outer_ti=TempConfig.CASCADE_OUTER_TI_DEFAULT,
            outer_td=TempConfig.CASCADE_OUTER_TD_DEFAULT,
            inner_kp=TempConfig.CASCADE_INNER_KP_DEFAULT,
            inner_ti=TempConfig.CASCADE_INNER_TI_DEFAULT,
            inner_td=TempConfig.CASCADE_INNER_TD_DEFAULT,
            dt=dt,
            u_min=-TempConfig.CONTROL_AUTO_LIMIT,
            u_max=TempConfig.CONTROL_AUTO_LIMIT,
        )
        self._cascade_ff = CascadeWithFeedforward(
            outer_kp=TempConfig.CASCADE_OUTER_KP_DEFAULT,
            outer_ti=TempConfig.CASCADE_OUTER_TI_DEFAULT,
            outer_td=TempConfig.CASCADE_OUTER_TD_DEFAULT,
            inner_kp=TempConfig.CASCADE_INNER_KP_DEFAULT,
            inner_ti=TempConfig.CASCADE_INNER_TI_DEFAULT,
            inner_td=TempConfig.CASCADE_INNER_TD_DEFAULT,
            ff_gain=TempConfig.FF_GAIN_DEFAULT,
            dt=dt,
            u_min=-TempConfig.CONTROL_AUTO_LIMIT,
            u_max=TempConfig.CONTROL_AUTO_LIMIT,
        )

    def compute(self, setpoint: float, process_value: float,
                inner_pv: Optional[float] = None,
                disturbance: float = 0.0) -> float:
        """计算控制量

        Args:
            setpoint: 设定值
            process_value: 过程值
            inner_pv: 内环过程值（串级策略使用）
            disturbance: 干扰值

        Returns:
            控制量
        """
        if self._mode == ControlMode.MANUAL:
            self._output = self._manual_output
            return self._output

        strategy = self._strategy

        if strategy == ControlStrategy.PLAIN_PID:
            self._output = self._plain_pid.compute(setpoint, process_value)
        elif strategy == ControlStrategy.SINGLE_LOOP_PID:
            self._output = self._single_loop_pid.compute(setpoint, process_value)
        elif strategy == ControlStrategy.FEEDFORWARD_FB:
            self._output = self._feedforward_fb.compute(setpoint, process_value, disturbance)
        elif strategy == ControlStrategy.CASCADE:
            if inner_pv is not None:
                self._output = self._cascade.compute(setpoint, process_value, inner_pv)
        elif strategy == ControlStrategy.CASCADE_FF:
            if inner_pv is not None:
                self._output = self._cascade_ff.compute(setpoint, process_value, inner_pv, disturbance)

        return self._output

    def set_strategy(self, strategy: ControlStrategy):
        """切换控制策略"""
        if strategy != self._strategy:
            # 跟踪当前输出，实现无扰动切换
            current_output = self._output
            self._track_all(current_output)
            self._strategy = strategy

    def set_mode(self, mode: ControlMode):
        """切换手动/自动模式"""
        if mode == ControlMode.MANUAL and self._mode == ControlMode.AUTO:
            self._manual_output = self._output
        elif mode == ControlMode.AUTO and self._mode == ControlMode.MANUAL:
            self._track_all(self._manual_output)
        self._mode = mode

    def set_manual_output(self, value: float):
        """设置手动输出值"""
        self._manual_output = value

    def _track_all(self, output: float):
        """所有控制器跟踪指定输出值"""
        self._plain_pid.track_output(output)
        self._single_loop_pid.track_output(output)
        self._feedforward_fb.track_output(output)
        self._cascade.track_output(output)
        self._cascade_ff.track_output(output)

    def reset_all(self):
        """重置所有控制器积分"""
        self._plain_pid.reset()
        self._single_loop_pid.reset()
        self._feedforward_fb.reset()
        self._cascade.reset()
        self._cascade_ff.reset()
        self._output = 0.0

    def update_pid_params(self, kp: float = None, ti: float = None, td: float = None):
        """更新单回路PID参数"""
        for ctrl in [self._plain_pid, self._single_loop_pid, self._feedforward_fb.pid]:
            if kp is not None:
                ctrl.kp = kp
            if ti is not None:
                ctrl.ti = ti
            if td is not None:
                ctrl.td = td

    def update_cascade_outer_params(self, kp: float = None, ti: float = None, td: float = None):
        """更新串级外环参数"""
        for ctrl in [self._cascade, self._cascade_ff]:
            ctrl.update_outer_params(kp, ti, td)

    def update_cascade_inner_params(self, kp: float = None, ti: float = None, td: float = None):
        """更新串级内环参数"""
        for ctrl in [self._cascade, self._cascade_ff]:
            ctrl.update_inner_params(kp, ti, td)

    @property
    def strategy(self) -> ControlStrategy:
        return self._strategy

    @property
    def mode(self) -> ControlMode:
        return self._mode

    @property
    def output(self) -> float:
        return self._output

    @property
    def plain_pid(self) -> SimplePIDController:
        return self._plain_pid

    @property
    def single_loop_pid(self) -> PIDController:
        return self._single_loop_pid

    @property
    def feedforward_fb(self) -> FeedforwardFeedbackController:
        return self._feedforward_fb

    @property
    def cascade(self) -> CascadeController:
        return self._cascade

    @property
    def cascade_ff(self) -> CascadeWithFeedforward:
        return self._cascade_ff
