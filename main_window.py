"""
===========================
@Time : 2024/9/15 下午6:09
@Author : Entropy.Xu
@File : main_window.py
@Software: PyCharm
============================
"""
# main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
    QPushButton, QMessageBox, QHBoxLayout, QHeaderView, QDateEdit, QMenu, QLabel, QCalendarWidget, QDialog
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QDate
from course_dialog import CourseDialog
from utils import format_weeks, parse_weeks_input, get_time_from_period
from icalendar import Calendar, Event, Alarm
from datetime import datetime, timedelta
import json


class MainWindow(QMainWindow):
    """主窗口类，负责显示课表表格和生成 ICS 文件"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("大学课表生成日历工具")
        self.resize(1400, 900)
        self.courses = []
        self.periods = self.get_periods()
        self.init_ui()

    @staticmethod
    def get_periods():
        """获取节次信息"""
        return [
            "第一节\n8:20-9:05",
            "第二节\n9:10-9:55",
            "第三节\n10:15-11:00",
            "第四节\n11:05-11:50",
            "第五节\n11:55-12:25",
            "第六节\n12:30-13:00",
            "第七节\n13:10-13:55",
            "第八节\n14:00-14:45",
            "第九节\n15:05-15:50",
            "第十节\n15:55-16:40",
            "第十一节\n18:00-18:45",
            "第十二节\n18:50-19:35",
            "第十三节\n19:40-20:25"
        ]

    def init_ui(self):
        """初始化主窗口界面"""
        self.create_menu()
        self.setup_central_widget()

    def create_menu(self):
        """创建菜单栏，添加保存和加载功能"""
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")

        save_action = QAction("保存课程", self)
        save_action.triggered.connect(self.save_courses_to_json)
        file_menu.addAction(save_action)

        load_action = QAction("加载课程", self)
        load_action.triggered.connect(self.load_courses_from_json)
        file_menu.addAction(load_action)

    def setup_central_widget(self):
        """设置中心部件"""
        central_widget = QWidget()
        layout = QVBoxLayout()

        self.setup_first_day_input(layout)
        self.setup_table(layout)
        self.setup_generate_button(layout)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def setup_first_day_input(self, layout):
        """设置学期开始日期输入"""
        first_day_layout = QHBoxLayout()
        first_day_label = QLabel("选择学期第一周的第一天:")
        self.first_day_edit = QDateEdit()
        self.first_day_edit.setDisplayFormat("yyyy-MM-dd")
        self.first_day_edit.setCalendarPopup(True)
        self.first_day_edit.setDate(QDate(2024, 9, 2))
        self.first_day_edit.setMinimumWidth(120)
        self.calendar_button = QPushButton("选择日期")
        self.calendar_button.clicked.connect(self.show_calendar_dialog)
        first_day_layout.addWidget(first_day_label)
        first_day_layout.addWidget(self.first_day_edit)
        first_day_layout.addWidget(self.calendar_button)
        first_day_layout.addStretch()
        layout.addLayout(first_day_layout)

    def show_calendar_dialog(self):
        """显示日历对话框以选择日期"""
        calendar = QCalendarWidget()
        calendar.setGridVisible(True)
        dialog = QDialog(self)
        dialog.setWindowTitle("选择日期")
        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(calendar)
        dialog.setLayout(dialog_layout)
        dialog.resize(400, 300)
        calendar.clicked.connect(lambda date: self.on_date_selected(date, dialog))
        dialog.exec()

    def on_date_selected(self, date, dialog):
        """当在日历中选择日期时更新 QDateEdit"""
        self.first_day_edit.setDate(date)
        dialog.accept()

    def setup_table(self, layout):
        """设置课程表格"""
        self.table = QTableWidget(len(self.periods), 8)
        self.table.setHorizontalHeaderLabels(
            ['节次', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setWordWrap(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # 设置第一列（节次列）的宽度，并固定列宽
        self.table.setColumnWidth(0, 120)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)

        # 其余列均分
        for i in range(1, 8):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        for row, period in enumerate(self.periods):
            item = QTableWidgetItem(period)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 0, item)
            self.table.resizeRowToContents(row)

        self.table.cellDoubleClicked.connect(self.add_course)
        layout.addWidget(self.table)

    def setup_generate_button(self, layout):
        """设置生成 ICS 按钮"""
        self.ics_button = QPushButton("生成 ICS 文件")
        self.ics_button.clicked.connect(self.generate_ics)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.ics_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

    def add_course(self, row, column):
        """添加课程到表格"""
        if column == 0:
            return

        day = column - 1
        period = row

        # 获取节次对应的开始时间和结束时间
        default_start_time, default_end_time = get_time_from_period(self.periods[row])

        dialog = CourseDialog(self, day, period)
        if dialog.exec():
            data = dialog.get_data()
            if not self.validate_course_data(data):
                return

            task_weeks = parse_weeks_input(data['weeks'])
            if not task_weeks:
                QMessageBox.warning(self, "输入错误", "重复周数格式不正确或为空。")
                return

            if self.is_course_duplicate(day, period, data['name']):
                QMessageBox.warning(self, "重复课程", "该课程已在此节次和星期添加过。")
                return

            # 使用根据节次确定的开始时间和结束时间
            data['start_time'] = default_start_time
            data['end_time'] = default_end_time

            self.update_table(row, column, data, task_weeks)
            self.courses.append(self.create_course_dict(day, period, data, task_weeks))

    @staticmethod
    def validate_course_data(data):
        """验证课程数据"""
        if not data['name'].strip():
            QMessageBox.warning(None, "输入错误", "课程名称不能为空。")
            return False
        return True

    def is_course_duplicate(self, day, period, course_name):
        """检查课程是否重复"""
        for course in self.courses:
            if course['day'] == day and course['period'] == period and course['name'] == course_name:
                return True
        return False

    def update_table(self, row, column, data, task_weeks):
        """更新表格显示"""
        weeks_str = format_weeks(task_weeks)
        new_text = f"{data['name']}({data['location']})\n周数: {weeks_str}"
        current_item = self.table.item(row, column)
        if current_item and current_item.text():
            new_text = f"{current_item.text()}\n{new_text}"
        item = QTableWidgetItem(new_text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.table.setItem(row, column, item)
        self.table.resizeRowToContents(row)

    @staticmethod
    def create_course_dict(day, period, data, task_weeks):
        """创建课程字典"""
        return {
            'day': day,
            'period': period,
            'name': data['name'].strip(),
            'location': data['location'].strip(),
            'weeks': task_weeks,
            'start_time': data['start_time'],
            'end_time': data['end_time']
        }

    def generate_ics(self):
        """生成 ICS 文件"""
        cal = Calendar()
        cal.add('prodid', '-//大学课表生成工具//')
        cal.add('version', '2.0')

        semester_start = self.first_day_edit.date().toPyDate()

        for course in self.courses:
            self.add_course_events(cal, course, semester_start)

        self.save_ics_file(cal)

    def add_course_events(self, cal, course, semester_start):
        """添加课程事件到日历"""
        task_weeks = course['weeks']
        day = course['day']
        start_time, end_time = self.get_course_times(course)

        for week in task_weeks:
            event_date = semester_start + timedelta(weeks=week - 1, days=day)
            start_datetime = datetime.combine(event_date, start_time)
            end_datetime = datetime.combine(event_date, end_time)

            event = Event()
            event.add('dtstart', start_datetime)
            event.add('dtend', end_datetime)
            event.add('summary', course['name'])
            event.add('location', course['location'])
            duration_minutes = (end_datetime - start_datetime).seconds // 60
            event.add('description', f"持续时间: {duration_minutes} 分钟\n周数: {week}")

            alarm = Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('description', f"课程 {course['name']} 即将开始")
            alarm.add('trigger', timedelta(minutes=-30))
            event.add_component(alarm)

            cal.add_component(event)

    def get_course_times(self, course):
        """获取课程的开始和结束时间"""
        try:
            start_time = datetime.strptime(course['start_time'], "%H:%M").time()
            end_time = datetime.strptime(course['end_time'], "%H:%M").time()
            return start_time, end_time
        except ValueError:
            QMessageBox.warning(self, "错误", f"课程 {course['name']} 的时间格式错误，请检查节次时间配置。")
            return None, None

    def save_ics_file(self, cal):
        """保存 ICS 文件"""
        try:
            with open('course_schedule.ics', 'wb') as f:
                f.write(cal.to_ical())
            QMessageBox.information(self, "成功", "ICS 文件已生成！路径：course_schedule.ics")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"生成 ICS 文件失败: {e}")

    def save_courses_to_json(self):
        """将课程信息保存到 JSON 文件"""
        try:
            with open('courses.json', 'w', encoding='utf-8') as f:
                json.dump(self.courses, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "成功", "课程信息已保存到 courses.json")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存课程信息失败: {e}")

    def load_courses_from_json(self):
        """从 JSON 文件加载课程信息"""
        try:
            with open('courses.json', 'r', encoding='utf-8') as f:
                self.courses = json.load(f)
            self.refresh_table()
            QMessageBox.information(self, "成功", "课程信息已从 courses.json 加载")
        except FileNotFoundError:
            QMessageBox.warning(self, "错误", "文件 courses.json 不存在。")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载课程信息失败: {e}")

    def refresh_table(self):
        """刷新表格显示"""
        self.table.clearContents()
        for course in self.courses:
            row = course['period']
            column = course['day'] + 1
            weeks_str = format_weeks(course['weeks'])
            new_text = f"{course['name']}({course['location']})\n周数: {weeks_str}"
            current_item = self.table.item(row, column)
            if current_item and current_item.text():
                new_text = f"{current_item.text()}\n{new_text}"
            item = QTableWidgetItem(new_text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, column, item)
            self.table.resizeRowToContents(row)
