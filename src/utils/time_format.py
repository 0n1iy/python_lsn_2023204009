"""时间格式化工具"""

from datetime import datetime


def get_current_time_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """获取当前时间格式化字符串"""
    return datetime.now().strftime(fmt)


def get_current_time_filename() -> str:
    """获取适合文件名的当前时间字符串"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def format_timestamp(ts: float) -> str:
    """将时间戳格式化为字符串"""
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def format_elapsed(seconds: float) -> str:
    """格式化经过时间"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = seconds % 60
        return f"{minutes}分{secs:.0f}秒"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}时{minutes}分"


def parse_iso_time(iso_str: str) -> datetime:
    """解析ISO格式时间字符串"""
    return datetime.fromisoformat(iso_str)
