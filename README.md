# 大学课表生成日历工具

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 目录

- [简介](#简介)
- [功能特性](#功能特性)
- [使用方法](#使用方法)
- [导入到 iOS 和 Android 设备日历的教程](#导入到-ios-和-android-设备日历的教程)
- [贡献指南](#贡献指南)
- [许可证](#许可证)
- [致谢](#致谢)

## 简介

**大学课表生成日历工具**是一款桌面应用程序，帮助大学生将课程表转换为日历格式，便于在各类日历应用中查看和管理课程安排。

## 功能特性

- **课程管理**：添加、编辑和删除课程信息，包括课程名称、时间、地点、教师等。
- **课表导入**：支持从 Excel、CSV 等格式导入课程表。
- **日历生成**：一键生成符合 iCalendar 标准的 `.ics` 日历文件。
- **界面美观**：采用现代化的用户界面，简洁易用。
- **跨平台支持**：可在 Windows、macOS 和 Linux 系统上运行。

## 使用方法

1. **运行应用程序**

   - 双击可执行文件 `课程表生成工具.exe`（Windows）或相应的应用程序文件（macOS/Linux）启动程序。

2. **添加课程**

   - 点击“添加课程”按钮，填写课程信息，包括名称、时间、地点、教师等。

3. **编辑课程**

   - 在课程列表中，选择要编辑的课程，点击“编辑”按钮，修改课程信息。

4. **删除课程**

   - 在课程列表中，选择要删除的课程，点击“删除”按钮，确认删除。

5. **生成日历**

   - 添加完所有课程后，点击“生成日历”按钮，选择保存位置，即可生成 `.ics` 格式的日历文件。

## 导入到 iOS 和 Android 设备日历的教程

### **在 iOS 设备上导入日历**

1. **通过邮件发送 .ics 文件**

   - 将生成的 `.ics` 文件发送到您的邮箱。

2. **在 iOS 设备上打开邮件**

   - 使用 iPhone 或 iPad 打开邮件，找到包含 `.ics` 文件的邮件。

3. **打开 .ics 文件**

   - 点击附件中的 `.ics` 文件。

4. **添加到日历**

   - 在弹出的窗口中，点击“添加到日历”。

5. **选择日历**

   - 选择要添加到的日历（例如默认日历或新建日历），然后点击“添加”。

### **在 Android 设备上导入日历**

**方法一：通过 Google 日历导入**

1. **在电脑上登录 Google 日历**

   - 访问 [Google 日历](https://calendar.google.com/) 并使用您的 Google 账号登录。

2. **导入 .ics 文件**

   - 点击页面右上角的齿轮图标，选择“设置”。
   - 在左侧菜单中，选择“导入和导出”。
   - 在“导入”部分，点击“从电脑选择文件”，选择生成的 `.ics` 文件。
   - 选择要导入的日历，点击“导入”按钮。

3. **在 Android 设备上同步**

   - 确保您的 Android 设备已登录同一 Google 账号，并打开了日历同步功能。
   - 等待同步完成，课程安排将显示在 Google 日历应用中。

**方法二：使用第三方应用直接导入**

1. **将 .ics 文件传输到 Android 设备**

   - 通过 USB、蓝牙、邮件或云存储将 `.ics` 文件传输到您的 Android 设备。

2. **安装支持 .ics 导入的日历应用**

   - 在 Google Play 商店中搜索并安装支持导入 .ics 文件的日历应用，如 [ICS Importer](https://play.google.com/store/apps/details?id=tv.redwarp.icsimporter)。

3. **使用应用导入 .ics 文件**

   - 打开已安装的应用，按照提示选择并导入 `.ics` 文件。

4. **查看日历**

   - 打开您的日历应用，检查课程安排是否已成功导入。

## 贡献指南

欢迎任何形式的贡献！您可以：

- 提交问题（Issue）或功能请求。
- 修复错误并提交拉取请求（Pull Request）。
- 优化代码或添加新功能。

请在提交前确保：

- 代码风格一致，注释清晰。
- 详细描述您的更改内容。

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 致谢

- 感谢所有为本项目做出贡献的开发者。
- 感谢 [PySide6](https://www.qt.io/qt-for-python) 和 [icalendar](https://icalendar.readthedocs.io/en/latest/) 项目的支持。