"""
===========================
@Time : 2024/9/15 下午6:39
@Author : Entropy.Xu
@File : course_dialog.py
@Software: PyCharm
============================
"""
# course_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt

class CourseDialog(QDialog):
    """课程添加和编辑对话框"""

    def __init__(self, parent=None, day=None, period=None):
        super().__init__(parent)
        self.setWindowTitle("添加课程")
        self.day = day
        self.period = period
        self.init_ui()

    def init_ui(self):
        """初始化对话框界面"""
        layout = QVBoxLayout()

        self.name_edit = self.create_line_edit("课程名称:", layout)
        self.location_edit = self.create_line_edit("地点:", layout)
        self.weeks_edit = self.create_line_edit("重复周数（例如：1,3-5,9）:", layout)

        save_button = QPushButton("保存")
        save_button.clicked.connect(self.accept)
        layout.addWidget(save_button)
        self.setLayout(layout)

    @staticmethod
    def create_line_edit(label_text, layout):
        """创建输入框"""
        label = QLabel(label_text)
        edit = QLineEdit()
        layout.addWidget(label)
        layout.addWidget(edit)
        return edit

    def get_data(self):
        """获取用户输入的数据"""
        return {
            'name': self.name_edit.text(),
            'location': self.location_edit.text(),
            'weeks': self.weeks_edit.text()
        }
