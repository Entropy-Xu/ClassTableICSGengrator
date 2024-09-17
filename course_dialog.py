"""
===========================
@Time : 2024/9/15 下午6:39
@Author : Entropy.Xu
@File : course_dialog.py
@Software: PyCharm
============================
"""
# course_dialog.py

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
class CourseDialog(QDialog):
    def __init__(self, parent=None, day=None, period=None):
        super().__init__(parent)
        self.setWindowTitle("添加课程")
        self.resize(400, 300)

        self.day = day
        self.period = period

        layout = QVBoxLayout()

        # 课程名称
        name_label = QLabel("课程名称:")
        self.name_edit = QLineEdit()
        layout.addWidget(name_label)
        layout.addWidget(self.name_edit)

        # 上课地点
        location_label = QLabel("上课地点:")
        self.location_edit = QLineEdit()
        layout.addWidget(location_label)
        layout.addWidget(self.location_edit)

        # 重复周数
        weeks_label = QLabel("周数 (如: 1-16 或 1,3,5):")
        self.weeks_edit = QLineEdit()
        layout.addWidget(weeks_label)
        layout.addWidget(self.weeks_edit)

        # 按钮
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # 连接信号
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_data(self):
        return {
            'name': self.name_edit.text(),
            'location': self.location_edit.text(),
            'weeks': self.weeks_edit.text(),
            'start_time': None,
            'end_time': None
        }
