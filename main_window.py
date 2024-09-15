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
    QPushButton, QMessageBox, QHBoxLayout, QHeaderView, QDateEdit, QMenu, QDialog, QLabel
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QDate
from course_dialog import CourseDialog
from utils import format_weeks
from icalendar import Calendar, Event, Alarm
from datetime import datetime, timedelta
import json

class MainWindow(QMainWindow):
    """
    主窗口类，负责显示课表表格和生成 ICS 文件
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("大学课表生成日历工具")
        self.resize(1400, 900)  # 增大窗口尺寸以适应更多内容
        self.courses = []  # 存储课程信息
        self.periods = [
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
        self.initUI()

    def parse_input(self, input_string):
        """
        解析用户输入的重复周数字符串，将其转换为整数列表
        例如，"1,3-5,9" -> [1,3,4,5,9]
        """
        parts = input_string.split(',')
        result = []

        for part in parts:
            part = part.strip()
            if '-' in part:
                # 处理范围情况
                start, end = part.split('-')
                try:
                    start = int(start)
                    end = int(end)
                    result.extend(range(start, end + 1))
                except ValueError:
                    continue  # 忽略无效的输入
            else:
                # 处理单个数字
                try:
                    result.append(int(part))
                except ValueError:
                    continue  # 忽略无效的输入

        return result

    def initUI(self):
        """
        初始化主窗口界面
        """
        self.createMenu()  # 创建菜单栏

        central_widget = QWidget()
        layout = QVBoxLayout()

        # 添加学期开始日期输入，使用 QDateEdit
        first_day_layout = QHBoxLayout()
        self.first_day_label = QLabel("选择学期第一周的第一天:")
        self.first_day_edit = QDateEdit()
        self.first_day_edit.setDisplayFormat("yyyy-MM-dd")
        self.first_day_edit.setCalendarPopup(True)
        self.first_day_edit.setDate(QDate(2024, 9, 2))  # 默认值
        # 设置 QDateEdit 为只读，禁止手动输入
        self.first_day_edit.lineEdit().setReadOnly(True)
        first_day_layout.addWidget(self.first_day_label)
        first_day_layout.addWidget(self.first_day_edit)
        first_day_layout.addStretch()  # 增加伸缩因子，使组件靠左对齐
        layout.addLayout(first_day_layout)

        # 创建表格
        self.table = QTableWidget(len(self.periods), 8)  # 第一列为节次，后7列为星期一至星期日
        self.table.setHorizontalHeaderLabels(['节次', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'])
        self.table.setVerticalHeaderLabels([])  # 使用自定义的节次列
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setWordWrap(True)  # 启用自动换行
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # 禁止直接编辑单元格

        # 设置节次时间到第一列
        for row, period in enumerate(self.periods):
            item = QTableWidgetItem(period)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # 只读
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item)

        # 连接双击事件，仅限于课程列
        self.table.cellDoubleClicked.connect(self.addCourse)
        layout.addWidget(self.table)

        # 添加生成 ICS 按钮
        self.ics_button = QPushButton("生成 ICS 文件")
        self.ics_button.clicked.connect(self.generateICS)
        # 将按钮居中
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.ics_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def createMenu(self):
        """
        创建菜单栏，添加保存和加载功能
        """
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")

        save_action = QAction("保存课程", self)
        save_action.triggered.connect(self.save_courses_to_json)
        file_menu.addAction(save_action)

        load_action = QAction("加载课程", self)
        load_action.triggered.connect(self.load_courses_from_json)
        file_menu.addAction(load_action)

    def addCourse(self, row, column):
        """
        添加课程到表格
        """
        if column == 0:
            return  # 节次列不可编辑

        day = column - 1  # 0:周一, 1:周二, ..., 6:周日
        period = row  # 0-based index for periods

        # 获取当前节次的默认时间
        period_info = self.periods[row]
        try:
            period_times = period_info.split('\n')[1]
            default_start_time, default_end_time = period_times.split('-')
        except IndexError:
            QMessageBox.warning(self, "错误", f"节次 {row + 1} 的时间格式不正确。")
            return

        # 弹出课程添加对话框
        dialog = CourseDialog(
            self,
            day,
            period,
            default_start_time=default_start_time.strip(),
            default_end_time=default_end_time.strip()
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.getData()
            course_name = data['name'].strip()
            location = data['location'].strip()
            weeks_input = data['weeks'].strip()
            start_time = data['start_time'].strip()
            end_time = data['end_time'].strip()

            if not course_name:
                QMessageBox.warning(self, "输入错误", "课程名称不能为空。")
                return

            # 解析重复周数
            task_weeks = self.parse_input(weeks_input)
            if not task_weeks:
                QMessageBox.warning(self, "输入错误", "重复周数格式不正确或为空。")
                return

            # 格式化周数字符串为范围显示
            weeks_str = format_weeks(task_weeks)

            # 检查是否已存在相同的课程（可选）
            for course in self.courses:
                if course['day'] == day and course['period'] == period and course['name'] == course_name:
                    QMessageBox.warning(self, "重复课程", "该课程已在此节次和星期添加过。")
                    return

            # 更新表格
            current_item = self.table.item(row, column)
            if current_item and current_item.text():
                existing_text = current_item.text()
                # 添加课程信息和周数
                new_text = f"{existing_text}\n{course_name}({location})\n周数: {weeks_str}"
            else:
                new_text = f"{course_name}({location})\n周数: {weeks_str}"
            item = QTableWidgetItem(new_text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, column, item)

            # 调整行高以适应内容
            self.table.resizeRowToContents(row)

            # 存储课程信息
            course = {
                'day': day,
                'period': row,
                'name': course_name,
                'location': location,
                'weeks': task_weeks,
                'start_time': start_time,
                'end_time': end_time
            }
            self.courses.append(course)

    def generateICS(self):
        """
        生成 ICS 文件
        """
        cal = Calendar()
        cal.add('prodid', '-//大学课表生成工具//mxm.dk//')
        cal.add('version', '2.0')

        # 获取学期开始日期
        semester_start_qdate = self.first_day_edit.date()
        semester_start = datetime(
            year=semester_start_qdate.year(),
            month=semester_start_qdate.month(),
            day=semester_start_qdate.day()
        )

        for course in self.courses:
            task_weeks = course['weeks']
            day = course['day']  # 0:周一, 1:周二, ...
            start_time_str = course['start_time']
            end_time_str = course['end_time']

            try:
                start_time = datetime.strptime(start_time_str, "%H:%M").time()
                end_time = datetime.strptime(end_time_str, "%H:%M").time()
            except ValueError:
                QMessageBox.warning(self, "错误", f"课程 {course['name']} 的时间格式错误，请使用 hh:mm 格式。")
                continue

            for week in task_weeks:
                event = Event()
                # 计算课程日期
                event_date = semester_start + timedelta(weeks=week - 1, days=day)
                start_datetime = datetime.combine(event_date.date(), start_time)
                end_datetime = datetime.combine(event_date.date(), end_time)

                event.add('dtstart', start_datetime)
                event.add('dtend', end_datetime)
                event.add('summary', course['name'])
                event.add('location', course['location'])
                duration_minutes = (datetime.combine(datetime.min, end_time) - datetime.combine(datetime.min, start_time)).seconds // 60
                event.add('description', f"持续时间: {duration_minutes} 分钟\n周数: {week}")

                # 添加提醒（提前30分钟）
                alarm = Alarm()
                alarm.add('action', 'DISPLAY')
                alarm.add('description', f"课程 {course['name']} 即将开始")
                alarm.add('trigger', timedelta(minutes=-30))  # 提前30分钟提醒
                event.add_component(alarm)

                cal.add_component(event)

        # 保存 ICS 文件
        try:
            with open('course_schedule.ics', 'wb') as f:
                f.write(cal.to_ical())
            QMessageBox.information(self, "成功", "ICS 文件已生成！路径：course_schedule.ics")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"生成 ICS 文件失败: {e}")

    def save_courses_to_json(self, filename='courses.json'):
        """
        将课程信息保存到 JSON 文件
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.courses, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "成功", f"课程信息已保存到 {filename}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存课程信息失败: {e}")

    def load_courses_from_json(self, filename='courses.json'):
        """
        从 JSON 文件加载课程信息
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.courses = json.load(f)
            # 重新绘制表格
            self.table.clearContents()
            for course in self.courses:
                row = course['period']
                column = course['day'] + 1
                weeks_str = format_weeks(course['weeks'])
                new_text = f"{course['name']}({course['location']})\n周数: {weeks_str}"
                current_item = self.table.item(row, column)
                if current_item and current_item.text():
                    existing_text = current_item.text()
                    new_text = f"{existing_text}\n{new_text}"
                item = QTableWidgetItem(new_text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(row, column, item)
                self.table.resizeRowToContents(row)
            QMessageBox.information(self, "成功", f"课程信息已从 {filename} 加载")
        except FileNotFoundError:
            QMessageBox.warning(self, "错误", f"文件 {filename} 不存在。")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载课程信息失败: {e}")

    def contextMenuEvent(self, event):
        """
        重写右键菜单事件，添加编辑和删除功能
        """
        selected_items = self.table.selectedItems()
        if not selected_items:
            return

        menu = QMenu(self)
        edit_action = menu.addAction("编辑课程")
        delete_action = menu.addAction("删除课程")

        action = menu.exec(self.mapToGlobal(event.pos()))
        if action == edit_action:
            self.editCourse(selected_items[0].row(), selected_items[0].column())
        elif action == delete_action:
            self.deleteCourse(selected_items[0].row(), selected_items[0].column())

    def editCourse(self, row, column):
        """
        编辑选中的课程
        """
        # 获取当前课程信息
        index = None
        for i, course in enumerate(self.courses):
            if course['day'] == (column - 1) and course['period'] == row:
                index = i
                break
        if index is None:
            QMessageBox.warning(self, "错误", "未找到该课程的信息。")
            return

        course = self.courses[index]
        dialog = CourseDialog(
            self,
            day=course['day'],
            period=course['period'],
            default_start_time=course['start_time'],
            default_end_time=course['end_time']
        )
        dialog.name_edit.setText(course['name'])
        dialog.location_edit.setText(course['location'])
        dialog.weeks_edit.setText(','.join(map(str, course['weeks'])))

        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.getData()
            course_name = data['name'].strip()
            location = data['location'].strip()
            weeks_input = data['weeks'].strip()
            start_time = data['start_time'].strip()
            end_time = data['end_time'].strip()

            if not course_name:
                QMessageBox.warning(self, "输入错误", "课程名称不能为空。")
                return

            # 解析重复周数
            task_weeks = self.parse_input(weeks_input)
            if not task_weeks:
                QMessageBox.warning(self, "输入错误", "重复周数格式不正确或为空。")
                return

            # 格式化周数字符串为范围显示
            weeks_str = format_weeks(task_weeks)

            # 更新表格
            new_text = f"{course_name}({location})\n周数: {weeks_str}"
            item = QTableWidgetItem(new_text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, column, item)

            # 调整行高以适应内容
            self.table.resizeRowToContents(row)

            # 更新课程信息
            self.courses[index] = {
                'day': course['day'],
                'period': course['period'],
                'name': course_name,
                'location': location,
                'weeks': task_weeks,
                'start_time': start_time,
                'end_time': end_time
            }

    def deleteCourse(self, row, column):
        """
        删除选中的课程
        """
        # 获取当前课程信息
        index = None
        for i, course in enumerate(self.courses):
            if course['day'] == (column - 1) and course['period'] == row:
                index = i
                break
        if index is None:
            QMessageBox.warning(self, "错误", "未找到该课程的信息。")
            return

        # 删除课程
        del self.courses[index]

        # 更新表格
        self.table.setItem(row, column, QTableWidgetItem(""))
        self.table.resizeRowToContents(row)

        QMessageBox.information(self, "成功", "课程已删除。")

