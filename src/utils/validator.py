"""参数校验工具"""

from typing import Optional
from src.config import TempConfig


def validate_pid_params(kp: float, ti: float, td: float) -> Optional[str]:
    """校验PID参数

    Returns:
        错误消息字符串，None表示校验通过
    """
    if kp < TempConfig.KP_MIN:
        return f"Kp 不能为负数（当前值: {kp}）"
    if kp > TempConfig.KP_MAX:
        return f"Kp 超出上限（当前值: {kp}，上限: {TempConfig.KP_MAX}）"
    if ti < TempConfig.TI_MIN:
        return f"Ti 必须大于0（当前值: {ti}）"
    if ti > TempConfig.TI_MAX:
        return f"Ti 超出上限（当前值: {ti}，上限: {TempConfig.TI_MAX}）"
    if td < TempConfig.TD_MIN:
        return f"Td 不能为负数（当前值: {td}）"
    if td > TempConfig.TD_MAX:
        return f"Td 超出上限（当前值: {td}，上限: {TempConfig.TD_MAX}）"
    return None


def validate_temperature(value: float, field_name: str = "温度") -> Optional[str]:
    """校验温度值范围"""
    if not isinstance(value, (int, float)):
        return f"{field_name}必须是数字"
    if value < TempConfig.SV_MIN or value > TempConfig.SV_MAX:
        return f"{field_name}超出范围 [{TempConfig.SV_MIN}, {TempConfig.SV_MAX}]（当前值: {value}）"
    return None


def validate_control_output(value: float, u_min: float, u_max: float,
                            field_name: str = "控制量") -> Optional[str]:
    """校验控制量范围"""
    if value < u_min or value > u_max:
        return f"{field_name}超出范围 [{u_min}, {u_max}]（当前值: {value}）"
    return None


def validate_positive(value: float, field_name: str = "参数") -> Optional[str]:
    """校验正数"""
    if value <= 0:
        return f"{field_name}必须大于0（当前值: {value}）"
    return None


def validate_non_negative(value: float, field_name: str = "参数") -> Optional[str]:
    """校验非负数"""
    if value < 0:
        return f"{field_name}不能为负数（当前值: {value}）"
    return None


def parse_float(text: str, default: float = 0.0) -> float:
    """安全转换字符串为浮点数"""
    try:
        return float(text.strip())
    except (ValueError, AttributeError):
        return default
