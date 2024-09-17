"""
===========================
@Time : 2024/9/15 下午6:40
@Author : Entropy.Xu
@File : main.py
@Software: PyCharm
============================
"""
# main.py
import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow


def main():
    """应用程序的入口点"""
    app = QApplication(sys.argv)

    # 加载 QSS 样式表
    with open("styles/style.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

