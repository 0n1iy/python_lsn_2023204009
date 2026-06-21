"""历史数据查询窗口"""

from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QDateTimeEdit, QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QSplitter, QHeaderView
)
from PyQt6.QtCore import Qt, QDateTime

from src.utils.data_logger import DataLogger
from src.utils.excel_exporter import export_to_excel
from src.ui.plot_widget import HistoryPlotWidget


class HistoryWindow(QDialog):
    """历史数据查询窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._session_data = None
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("历史曲线")
        self.resize(1000, 650)

        layout = QVBoxLayout()

        # 查询控制栏
        ctrl_layout = QHBoxLayout()

        ctrl_layout.addWidget(QLabel("开始时间:"))
        self._start_dt = QDateTimeEdit()
        self._start_dt.setCalendarPopup(True)
        self._start_dt.setDateTime(QDateTime.currentDateTime().addDays(-7))
        self._start_dt.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        ctrl_layout.addWidget(self._start_dt)

        ctrl_layout.addWidget(QLabel("结束时间:"))
        self._end_dt = QDateTimeEdit()
        self._end_dt.setCalendarPopup(True)
        self._end_dt.setDateTime(QDateTime.currentDateTime())
        self._end_dt.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        ctrl_layout.addWidget(self._end_dt)

        self._query_btn = QPushButton("查询")
        self._query_btn.clicked.connect(self._on_query)
        ctrl_layout.addWidget(self._query_btn)

        self._export_btn = QPushButton("导出Excel")
        self._export_btn.clicked.connect(self._on_export)
        self._export_btn.setEnabled(False)
        ctrl_layout.addWidget(self._export_btn)

        ctrl_layout.addStretch()
        layout.addLayout(ctrl_layout)

        # 分割器 - 表格 + 曲线
        splitter = QSplitter(Qt.Orientation.Vertical)

        # 会话列表
        self._session_table = QTableWidget()
        self._session_table.setColumnCount(4)
        self._session_table.setHorizontalHeaderLabels(["会话ID", "开始时间", "结束时间", "采样数"])
        self._session_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._session_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._session_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._session_table.itemSelectionChanged.connect(self._on_session_selected)
        splitter.addWidget(self._session_table)

        # 曲线显示
        self._history_plot = HistoryPlotWidget()
        splitter.addWidget(self._history_plot)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def _on_query(self):
        """查询历史会话"""
        try:
            start = self._start_dt.dateTime().toPyDateTime()
            end = self._end_dt.dateTime().toPyDateTime()

            sessions = DataLogger.query_by_time_range(start, end)

            self._session_table.setRowCount(0)
            for i, session in enumerate(sessions):
                self._session_table.insertRow(i)
                self._session_table.setItem(i, 0,
                    QTableWidgetItem(session.get("session_id", "")))
                self._session_table.setItem(i, 1,
                    QTableWidgetItem(session.get("start_time", "")))
                self._session_table.setItem(i, 2,
                    QTableWidgetItem(session.get("end_time", "")))
                item = QTableWidgetItem()
                item.setData(Qt.ItemDataRole.DisplayRole, session.get("sample_count", 0))
                self._session_table.setItem(i, 3, item)

        except Exception as e:
            QMessageBox.warning(self, "查询失败", f"查询历史数据时出错：{str(e)}")

    def _on_session_selected(self):
        """选择会话后显示曲线"""
        row = self._session_table.currentRow()
        if row < 0:
            return

        session_id = self._session_table.item(row, 0).text()
        sessions = DataLogger.list_sessions()

        for session in sessions:
            if session["session_id"] == session_id:
                data = DataLogger.load_session(session["filepath"])
                if data and "records" in data:
                    self._session_data = data
                    self._history_plot.load_data(data["records"])
                    self._export_btn.setEnabled(True)
                break

    def _on_export(self):
        """导出当前会话数据为Excel"""
        if not self._session_data or "records" not in self._session_data:
            QMessageBox.warning(self, "提示", "请先选择一条会话记录")
            return

        try:
            filepath, _ = QFileDialog.getSaveFileName(
                self, "导出Excel", "", "Excel文件 (*.xlsx)")
            if filepath:
                export_to_excel(self._session_data["records"], filepath)
                QMessageBox.information(self, "导出成功", f"数据已导出到：\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出Excel时出错：{str(e)}")
