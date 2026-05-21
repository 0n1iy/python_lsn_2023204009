"""数据记录器 - 仿真数据记录与历史数据存储"""

import json
import os
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from src.config import Paths


class DataLogger:
    """仿真数据记录器"""

    def __init__(self):
        self._records: List[Dict] = []
        self._session_start = datetime.now()
        self._session_id = self._session_start.strftime("%Y%m%d_%H%M%S")
        Paths.ensure_dirs()

    def record(self, timestamp: float, sv: float, pv: float, u: float,
               disturbance: float, error_val: float):
        """记录一个采样点"""
        self._records.append({
            "time": timestamp,
            "sv": sv,
            "pv": pv,
            "u": u,
            "disturbance": disturbance,
            "error": error_val,
        })

    def save_session(self):
        """保存当前会话数据到文件"""
        if not self._records:
            return

        filename = f"session_{self._session_id}.json"
        filepath = os.path.join(Paths.HISTORY_DATA, filename)

        data = {
            "session_id": self._session_id,
            "start_time": self._session_start.isoformat(),
            "end_time": datetime.now().isoformat(),
            "sample_count": len(self._records),
            "records": self._records,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def clear(self):
        """清空当前会话记录"""
        self._records.clear()

    def get_records(self) -> List[Dict]:
        return self._records

    @property
    def session_id(self) -> str:
        return self._session_id

    @staticmethod
    def list_sessions() -> List[Dict]:
        """列出所有历史会话"""
        sessions = []
        history_dir = Paths.HISTORY_DATA
        if not os.path.exists(history_dir):
            return sessions

        for filename in os.listdir(history_dir):
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(history_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                sessions.append({
                    "session_id": data.get("session_id", filename),
                    "start_time": data.get("start_time", ""),
                    "end_time": data.get("end_time", ""),
                    "sample_count": data.get("sample_count", 0),
                    "filepath": filepath,
                })
            except Exception:
                continue

        sessions.sort(key=lambda x: x["start_time"], reverse=True)
        return sessions

    @staticmethod
    def load_session(filepath: str) -> Optional[Dict]:
        """加载指定会话数据"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    @staticmethod
    def query_by_time_range(start_time: datetime, end_time: datetime) -> List[Dict]:
        """按时间范围查询数据"""
        sessions = DataLogger.list_sessions()
        result = []
        for session in sessions:
            try:
                s_start = datetime.fromisoformat(session["start_time"])
                s_end = datetime.fromisoformat(session["end_time"])
                if s_start <= end_time and s_end >= start_time:
                    data = DataLogger.load_session(session["filepath"])
                    if data:
                        result.append(data)
            except Exception:
                continue
        return result
