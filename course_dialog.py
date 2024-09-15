"""
===========================
@Time : 2024/9/15 下午6:39
@Author : Entropy.Xu
@File : course_dialog.py
@Software: PyCharm
============================
"""
# course_dialog.py

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTimeEdit
from PyQt6.QtCore import Qt
from datetime import datetime

class CourseDialog(QDialog):
    """
    课程添加对话框
    """
    def __init__(self, parent=None, day=None, period=None, default_start_time=None, default_end_time=None):
        super().__init__(parent)
        self.setWindowTitle("添加课程")
        self.day = day
        self.period = period
        self.default_start_time = default_start_time
        self.default_end_time = default_end_time
        self.initUI()

    def initUI(self):
        """
        初始化对话框界面
        """
        layout = QVBoxLayout()

        # 课程名称输入
        self.name_label = QLabel("课程名称:")
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_edit)

        # 地点输入
        self.location_label = QLabel("地点:")
        self.location_edit = QLineEdit()
        layout.addWidget(self.location_label)
        layout.addWidget(self.location_edit)

        # 重复周数输入
        self.weeks_label = QLabel("重复周数（例如：1,3-5,9）:")
        self.weeks_edit = QLineEdit()
        layout.addWidget(self.weeks_label)
        layout.addWidget(self.weeks_edit)

        # 开始时间输入，使用 QTimeEdit
        self.start_time_label = QLabel("开始时间（hh:mm）:")
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm")
        if self.default_start_time:
            try:
                start_time = datetime.strptime(self.default_start_time, "%H:%M").time()
                self.start_time_edit.setTime(start_time)
            except ValueError:
                pass  # 保持默认值
        layout.addWidget(self.start_time_label)
        layout.addWidget(self.start_time_edit)

        # 结束时间输入，使用 QTimeEdit
        self.end_time_label = QLabel("结束时间（hh:mm）:")
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("HH:mm")
        if self.default_end_time:
            try:
                end_time = datetime.strptime(self.default_end_time, "%H:%M").time()
                self.end_time_edit.setTime(end_time)
            except ValueError:
                pass  # 保持默认值
        layout.addWidget(self.end_time_label)
        layout.addWidget(self.end_time_edit)

        # 保存按钮
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.accept)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def getData(self):
        """
        获取用户输入的数据
        """
        return {
            'name': self.name_edit.text(),
            'location': self.location_edit.text(),
            'weeks': self.weeks_edit.text(),
            'start_time': self.start_time_edit.time().toString("HH:mm"),
            'end_time': self.end_time_edit.time().toString("HH:mm")
        }
