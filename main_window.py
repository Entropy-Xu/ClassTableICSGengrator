"""
===========================
@Time : 2024/9/15 下午6:09
@Author : Entropy.Xu
@File : main_window.py
@Software: PyCharm
============================
"""
# main_window.py
import os
import platform
import json
from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
    QPushButton, QMessageBox, QHBoxLayout, QHeaderView, QDateEdit, QLabel,
    QCalendarWidget, QDialog, QFileDialog, QLineEdit, QMenu, QInputDialog
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QDate, QItemSelectionModel

from course_dialog import CourseDialog
from utils import format_weeks, parse_weeks_input, get_time_from_period
from icalendar import Calendar, Event, Alarm


class MainWindow(QMainWindow):
    """主窗口类，负责显示课表表格和生成 ICS 文件"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("大学课表生成日历工具")
        self.resize(1400, 900)
        self.courses = []
        self.copied_courses = []  # 用于存储复制的课程
        self.periods = self.get_periods()
        self.ics_file_path = None  # 保存生成的 ICS 文件路径
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
        self.first_day_edit.setDate(QDate.currentDate())
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
        self.table.cellDoubleClicked.connect(self.cell_double_clicked)

        # 启用自定义上下文菜单
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

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

        # 设置焦点策略，确保键盘事件可以被捕获
        self.table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        layout.addWidget(self.table)

    def setup_generate_button(self, layout):
        """设置生成 ICS 按钮和打开文件夹按钮"""
        self.ics_button = QPushButton("生成 ICS 文件")
        self.ics_button.clicked.connect(self.generate_ics)

        self.open_folder_button = QPushButton("打开文件夹")
        self.open_folder_button.clicked.connect(self.open_folder)
        self.open_folder_button.setEnabled(False)  # 初始状态不可用

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.ics_button)
        button_layout.addWidget(self.open_folder_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_C:
                self.copy_cells()
            elif event.key() == Qt.Key.Key_V:
                self.paste_cells()
        elif event.key() == Qt.Key.Key_Delete:
            self.delete_selected_courses()
        else:
            super().keyPressEvent(event)

    def copy_cells(self):
        """复制选定的单元格中的课程信息"""
        selected_ranges = self.table.selectedRanges()
        self.copied_courses = []

        for selected_range in selected_ranges:
            for row in range(selected_range.topRow(), selected_range.bottomRow() + 1):
                for column in range(selected_range.leftColumn(), selected_range.rightColumn() + 1):
                    if column == 0:
                        continue  # 跳过节次列

                    item = self.table.item(row, column)
                    if item and item.text():
                        # 找到对应的课程数据
                        for course in self.courses:
                            if course['day'] == column - 1 and course['period'] == row:
                                self.copied_courses.append(course.copy())

    def paste_cells(self):
        """将复制的课程信息粘贴到选定的单元格"""
        if not self.copied_courses:
            return  # 没有复制的课程，直接返回

        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return  # 没有选定的单元格，直接返回

        # 假设只粘贴到第一个选定区域的左上角
        target_row = selected_ranges[0].topRow()
        target_column = selected_ranges[0].leftColumn()

        if target_column == 0:
            return  # 不能粘贴到节次列

        # 计算偏移量
        row_offset = target_row - self.copied_courses[0]['period']
        column_offset = target_column - (self.copied_courses[0]['day'] + 1)

        # 粘贴课程
        new_courses = []
        for course in self.copied_courses:
            new_period = course['period'] + row_offset
            new_day = course['day'] + column_offset

            if new_period < 0 or new_period >= len(self.periods) or new_day < 0 or new_day > 6:
                continue  # 超出表格范围，跳过

            # 检查是否有重复的课程
            if any(c for c in self.courses if c['day'] == new_day and c['period'] == new_period and c['name'] == course['name']):
                continue  # 已存在相同课程，跳过

            new_course = course.copy()
            new_course['period'] = new_period
            new_course['day'] = new_day

            # 获取新的开始时间和结束时间
            new_start_time, new_end_time = get_time_from_period(self.periods[new_period])
            new_course['start_time'] = new_start_time
            new_course['end_time'] = new_end_time

            new_courses.append(new_course)

        if new_courses:
            self.courses.extend(new_courses)
            self.refresh_table()

    def delete_selected_courses(self):
        """删除选定的单元格中的课程"""
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return  # 没有选定的单元格，直接返回

        for selected_range in selected_ranges:
            for row in range(selected_range.topRow(), selected_range.bottomRow() + 1):
                for column in range(selected_range.leftColumn(), selected_range.rightColumn() + 1):
                    if column == 0:
                        continue  # 跳过节次列

                    day = column - 1
                    period = row

                    # 获取单元格中的课程名称
                    item = self.table.item(row, column)
                    if not item:
                        continue

                    # 提取所有课程名称
                    courses_in_cell = item.text().split('\n')
                    course_names = [c.split('(')[0] for c in courses_in_cell]

                    # 从 courses 列表中删除对应的课程
                    self.courses = [
                        course for course in self.courses
                        if not (course['day'] == day and course['period'] == period and course['name'] in course_names)
                    ]

        # 更新表格显示
        self.refresh_table()

    def show_context_menu(self, pos):
        """显示右键上下文菜单"""
        index = self.table.indexAt(pos)
        row = index.row()
        column = index.column()
        if row < 0 or column < 0:
            return  # 点击位置不在有效的单元格上

        menu = QMenu()

        if column == 0:
            pass  # 可以根据需要在节次列添加其他选项
        else:
            item = self.table.item(row, column)
            if item and item.text():
                delete_action = QAction("删除课程", self)
                delete_action.triggered.connect(lambda: self.delete_course(row, column))
                menu.addAction(delete_action)

        # 添加复制和粘贴选项
        copy_action = QAction("复制课程", self)
        copy_action.triggered.connect(self.copy_cells)
        menu.addAction(copy_action)

        paste_action = QAction("粘贴课程", self)
        paste_action.triggered.connect(self.paste_cells)
        menu.addAction(paste_action)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def delete_course(self, row, column):
        """删除指定单元格中的课程"""
        day = column - 1
        period = row

        # 获取单元格中的课程名称
        item = self.table.item(row, column)
        if not item:
            return

        # 如果单元格中有多个课程，需要用户选择要删除的课程
        courses_in_cell = item.text().split('\n')
        if len(courses_in_cell) > 1:
            # 当单元格中有多个课程时，弹出选择对话框
            selected_course, ok = QInputDialog.getItem(
                self,
                "选择课程",
                "请选择要删除的课程：",
                courses_in_cell,
                editable=False
            )
            if not ok:
                return
        else:
            selected_course = courses_in_cell[0]

        # 提取课程名称
        course_name = selected_course.split('(')[0]

        # 从 courses 列表中删除对应的课程
        self.courses = [
            course for course in self.courses
            if not (course['day'] == day and course['period'] == period and course['name'] == course_name)
        ]

        # 更新表格显示
        self.refresh_table()

    def cell_double_clicked(self, row, column):
        if column == 0:
            # 双击节次列，编辑时间范围
            self.edit_period_time(row)
        else:
            # 双击课程单元格，添加或编辑课程
            self.add_course(row, column)

    def edit_period_time(self, row):
        """编辑节次时间范围"""
        period_str = self.periods[row]
        # 提取当前的节次名称和时间范围
        try:
            period_name, time_range = period_str.split('\n')
            start_time_str, end_time_str = time_range.split('-')
        except ValueError:
            QMessageBox.warning(self, "错误", "节次信息格式不正确，无法编辑时间。")
            return

        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle(f"编辑{period_name}时间")
        layout = QVBoxLayout()

        # 开始时间输入
        start_time_label = QLabel("开始时间 (HH:MM):")
        start_time_edit = QLineEdit(start_time_str)
        layout.addWidget(start_time_label)
        layout.addWidget(start_time_edit)

        # 结束时间输入
        end_time_label = QLabel("结束时间 (HH:MM):")
        end_time_edit = QLineEdit(end_time_str)
        layout.addWidget(end_time_label)
        layout.addWidget(end_time_edit)

        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        # 连接信号
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        if dialog.exec():
            new_start_time = start_time_edit.text().strip()
            new_end_time = end_time_edit.text().strip()
            # 验证时间格式
            if self.validate_time_format(new_start_time) and self.validate_time_format(new_end_time):
                # 更新 periods 列表
                self.periods[row] = f"{period_name}\n{new_start_time}-{new_end_time}"
                # 更新表格中的显示
                item = QTableWidgetItem(self.periods[row])
                item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, 0, item)
                # 更新课程中对应的时间
                self.update_courses_time(row, new_start_time, new_end_time)
            else:
                QMessageBox.warning(self, "输入错误", "时间格式不正确，请输入 HH:MM 格式的时间。")

    def validate_time_format(self, time_str):
        """验证时间格式是否为 HH:MM"""
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False

    def update_courses_time(self, period_row, new_start_time, new_end_time):
        """更新课程数据中对应节次的时间"""
        for course in self.courses:
            if course['period'] == period_row:
                course['start_time'] = new_start_time
                course['end_time'] = new_end_time

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
                QMessageBox.warning(self, "输入错误", "周数格式不正确或为空。")
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

        semester_start = self.first_day_edit.date().toPython()

        for course in self.courses:
            self.add_course_events(cal, course, semester_start)

        self.save_ics_file(cal)

    def add_course_events(self, cal, course, semester_start):
        """添加课程事件到日历"""
        task_weeks = course['weeks']
        day = course['day']
        start_time, end_time = self.get_course_times(course)
        if start_time is None or end_time is None:
            return

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
            # 使用 QFileDialog 让用户选择保存位置
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存 ICS 文件",
                os.path.expanduser("~/course_schedule.ics"),
                "ICS Files (*.ics)"
            )
            if not file_path:
                return  # 用户取消保存

            with open(file_path, 'wb') as f:
                f.write(cal.to_ical())

            QMessageBox.information(self, "成功", f"ICS 文件已生成！路径：{file_path}")

            # 保存成功后，更新保存的文件路径
            self.ics_file_path = file_path

            # 启用“打开文件夹”按钮
            self.open_folder_button.setEnabled(True)

        except Exception as e:
            QMessageBox.warning(self, "错误", f"生成 ICS 文件失败: {e}")

    def open_folder(self):
        """打开包含 ICS 文件的文件夹"""
        if self.ics_file_path:
            file_dir = os.path.dirname(self.ics_file_path)
            try:
                if platform.system() == "Windows":
                    os.startfile(file_dir)
                elif platform.system() == "Darwin":  # macOS
                    os.system(f'open "{file_dir}"')
                else:  # Linux 和其他系统
                    os.system(f'xdg-open "{file_dir}"')
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法打开文件夹: {e}")
        else:
            QMessageBox.warning(self, "错误", "请先生成 ICS 文件。")

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
        # 仅清除课程数据，保留节次列（第一列）
        for row in range(self.table.rowCount()):
            for column in range(1, self.table.columnCount()):
                self.table.setItem(row, column, None)

        for row, period in enumerate(self.periods):
            # 更新节次列的显示（防止时间修改后未更新）
            item = QTableWidgetItem(period)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 0, item)

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
