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
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from main_window import MainWindow

def resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if getattr(sys, 'frozen', False):
        # Nuitka 或 PyInstaller 打包后
        base_path = sys._MEIPASS
    else:
        # 未打包，正常运行
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    app = QApplication(sys.argv)

    # 设置应用程序图标
    icon_path = resource_path("resources/icon.ico")
    app.setWindowIcon(QIcon(icon_path))

    # 加载样式表
    style_path = resource_path("styles/style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"样式表未找到：{style_path}")

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
