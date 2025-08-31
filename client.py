# -*- coding: utf-8 -*-
import sys
import socket
import threading
import platform
import requests
import datetime
import json
import os
import re
import base64
import io

import markdown
import matplotlib.pyplot as plt
from pygments.formatters import HtmlFormatter
from pygments import styles

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextBrowser, QTextEdit, QDialog, QFormLayout, QMessageBox,
    QDialogButtonBox, QCheckBox, QSpinBox, QComboBox, QSplitter, QToolBar
)
from PyQt6.QtCore import pyqtSignal, QObject, Qt
from PyQt6.QtGui import QFont, QIcon, QAction

# --- Pygments CSS 生成 ---
# 为亮色主题生成 'nord' 样式的 CSS
LIGHT_PYGMENTS_CSS = HtmlFormatter(style='nord', nobackground=True).get_style_defs('.codehilite')
# 为暗色主题生成 'nord-darker' 样式的 CSS
DARK_PYGMENTS_CSS = HtmlFormatter(style='nord-darker', nobackground=True).get_style_defs('.codehilite')

# 亮色UI样式表
LIGHT_STYLESHEET = f"""
    QWidget {{
        background-color: #F5F5F5;
        color: #2E3440;
        font-family: "微软雅黑", "Segoe UI", "Arial";
        font-size: 11pt;
    }}
    #ConnectionWindow, #SettingsDialog, #MarkdownPreviewDialog {{
        background-color: #ECEFF4;
    }}
    QLabel {{
        color: #2E3440;
        background-color: transparent;
    }}
    QLineEdit, QTextEdit, QTextBrowser, QSpinBox, QComboBox {{
        background-color: #FFFFFF;
        border: 1px solid #D8DEE9;
        border-radius: 5px;
        padding: 5px;
        color: #2E3440;
    }}
    /* 为聊天记录和预览窗口中的表格添加样式 */
    QTextBrowser table {{
        border: 1px solid #D8DEE9;
        border-collapse: collapse;
        margin: 4px 0;
    }}
    QTextBrowser th, QTextBrowser td {{
        border: 1px solid #D8DEE9;
        padding: 6px;
    }}
    QTextBrowser th {{
        background-color: #E5E9F0;
    }}
    /* 代码块基础样式 */
    QTextBrowser .codehilite {{
        background: #ECEFF4;
        border-radius: 5px;
        padding: 8px;
        margin: 4px 0;
        overflow: auto;
    }}
    QTextBrowser .codehilite pre {{
        background: transparent;
        border: none;
        padding: 0;
        margin: 0;
    }}
    QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 1px solid #5E81AC;
    }}
    QPushButton {{
        background-color: #5E81AC;
        color: #ECEFF4;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        min-height: 20px;
    }}
    QPushButton:hover {{
        background-color: #81A1C1;
    }}
    QPushButton:pressed {{
        background-color: #88C0D0;
    }}
    QTextBrowser {{
        border-radius: 5px;
    }}
    QSplitter::handle {{
        background-color: #D8DEE9;
    }}
    QSplitter::handle:vertical {{
        height: 4px;
    }}
    QSplitter::handle:horizontal {{
        width: 4px;
    }}
    QSplitter::handle:hover {{
        background-color: #B4BCC8;
    }}
    QToolBar {{
        background-color: #ECEFF4;
        border: none;
        padding: 1px;
    }}
    QToolBar QToolButton {{
        font-weight: bold;
        background-color: #ECEFF4;
        border: 1px solid #ECEFF4;
        border-radius: 4px;
        padding: 4px;
        margin: 1px;
    }}
    QToolBar QToolButton:hover {{
        background-color: #D8DEE9;
        border: 1px solid #B4BCC8;
    }}
    QToolBar QToolButton:pressed {{
        background-color: #B4BCC8;
    }}
    QScrollBar:vertical {{
        border: none;
        background: #ECEFF4;
        width: 10px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: #B4BCC8;
        min-height: 20px;
        border-radius: 5px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        border: none;
        background: #ECEFF4;
        height: 10px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: #B4BCC8;
        min-width: 20px;
        border-radius: 5px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    {LIGHT_PYGMENTS_CSS}
"""

# 暗色UI样式表
DARK_STYLESHEET = f"""
    QWidget {{
        background-color: #2E3440;
        color: #D8DEE9;
        font-family: "微软雅黑", "Segoe UI", "Arial";
        font-size: 11pt;
    }}
    #ConnectionWindow, #SettingsDialog, #MarkdownPreviewDialog {{
        background-color: #3B4252;
    }}
    QLabel {{
        color: #E5E9F0;
        background-color: transparent;
    }}
    QLineEdit, QTextEdit, QTextBrowser, QSpinBox {{
        background-color: #434C5E;
        border: 1px solid #4C566A;
        border-radius: 5px;
        padding: 5px;
        color: #ECEFF4;
    }}
    /* 为聊天记录和预览窗口中的表格添加样式 */
    QTextBrowser table {{
        border: 1px solid #4C566A;
        border-collapse: collapse;
        margin: 4px 0;
    }}
    QTextBrowser th, QTextBrowser td {{
        border: 1px solid #4C566A;
        padding: 6px;
    }}
    QTextBrowser th {{
        background-color: #434C5E;
    }}
    /* 代码块基础样式 */
    QTextBrowser .codehilite {{
        background: #3B4252;
        border-radius: 5px;
        padding: 8px;
        margin: 4px 0;
        overflow: auto;
    }}
    QTextBrowser .codehilite pre {{
        background: transparent;
        border: none;
        padding: 0;
        margin: 0;
    }}
    QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {{
        border: 1px solid #88C0D0;
    }}
    QPushButton {{
        background-color: #5E81AC;
        color: #ECEFF4;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        min-height: 20px;
    }}
    QPushButton:hover {{
        background-color: #81A1C1;
    }}
    QPushButton:pressed {{
        background-color: #88C0D0;
    }}
    QTextBrowser {{
        border-radius: 5px;
    }}
    QSplitter::handle {{
        background-color: #4C566A;
    }}
    QSplitter::handle:vertical {{
        height: 4px;
    }}
    QSplitter::handle:horizontal {{
        width: 4px;
    }}
    QSplitter::handle:hover {{
        background-color: #5E81AC;
    }}
    QToolBar {{
        background-color: #3B4252;
        border: none;
        padding: 1px;
    }}
    QToolBar QToolButton {{
        font-weight: bold;
        color: #ECEFF4;
        background-color: #3B4252;
        border: 1px solid #3B4252;
        border-radius: 4px;
        padding: 4px;
        margin: 1px;
    }}
    QToolBar QToolButton:hover {{
        background-color: #4C566A;
        border: 1px solid #5E81AC;
    }}
    QToolBar QToolButton:pressed {{
        background-color: #5E81AC;
    }}
    QScrollBar:vertical {{
        border: none;
        background: #3B4252;
        width: 10px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: #5E81AC;
        min-height: 20px;
        border-radius: 5px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        border: none;
        background: #3B4252;
        height: 10px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: #5E81AC;
        min-width: 20px;
        border-radius: 5px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    {DARK_PYGMENTS_CSS}
"""

CONFIG_FILE = "clientconfig.json"

def get_hh_mm_ss() -> str:
    """返回 HH:MM:SS 格式的时间字符串"""
    return datetime.datetime.now().strftime("%H:%M:%S")

def latex_to_svg_data_uri(latex_string: str, is_display_style: bool, is_dark_theme: bool) -> str:
    """使用 Matplotlib 将 LaTeX 字符串转换为 SVG 图像的 Data URI"""
    try:
        # Matplotlib 的 mathtext 需要将公式包裹在 $ 中
        clean_latex = f"${latex_string}$"
        
        fig = plt.figure(figsize=(0.01, 0.01))
        color = 'white' if is_dark_theme else 'black'
        fig.text(0, 0, clean_latex, usetex=False, fontsize=12, color=color)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='svg', bbox_inches='tight', pad_inches=0.1, transparent=True)
        plt.close(fig)

        svg_data = buffer.getvalue()
        base64_data = base64.b64encode(svg_data).decode('utf-8')

        # 对于行内公式，使用 CSS 使其与文本垂直对齐
        style = "vertical-align: middle;" if not is_display_style else ""
        
        # 对于块级公式，将其包裹在 div 中以实现居中
        if is_display_style:
            return f'<div align="center"><img style="{style}" src="data:image/svg+xml;base64,{base64_data}" /></div>'
        else:
            return f'<img style="{style}" src="data:image/svg+xml;base64,{base64_data}" />'

    except Exception as e:
        print(f"LaTeX 渲染失败 '{latex_string}': {e}")
        return f'<code style="color: red;">{latex_string}</code>'

def markdown_to_html_with_latex(text: str, is_dark_theme: bool) -> str:
    """将包含 LaTeX 的 Markdown 文本转换为 HTML"""
    
    # 用于替换 LaTeX 的回调函数
    def replacer(match):
        # 确定是块级公式还是行内公式
        if match.group(1):  # 块级 $$...$$
            latex_content = match.group(1)
            is_display = True
        else:  # 行内 $...$
            latex_content = match.group(2)
            is_display = False
        
        if not latex_content.strip():
            return match.group(0)

        return latex_to_svg_data_uri(latex_content, is_display, is_dark_theme)

    # 正则表达式：优先匹配块级公式 $$...$$，然后匹配行内公式 $...$
    # re.DOTALL 使 '.' 可以匹配换行符，用于多行块级公式
    # re.M 使 `^` 和 `$` 匹配行的开始和结束
    # 负向先行断言 `(?!\$)` 确保我们匹配的 $...$ 不是以 $$ 开头的
    latex_pattern = re.compile(r'\$\$(.*?)\$\$|\$(?!\$)(.*?)\$', re.DOTALL)
    
    # 先替换所有 LaTeX 公式
    text_with_images = latex_pattern.sub(replacer, text)
    
    # 然后将处理过的文本交给 markdown 库
    # 配置 markdown 扩展
    extensions = [
        'tables', 
        'fenced_code', 
        'sane_lists', 
        'codehilite'
    ]
    extension_configs = {
        'codehilite': {
            'guess_lang': False,
            'use_pygments_style': False # 强制使用 CSS 类而不是内联样式
        }
    }
    return markdown.markdown(
        text_with_images, 
        extensions=extensions, 
        extension_configs=extension_configs
    )


class Communicate(QObject):
    """用于跨线程通信的信号类"""
    msg_received = pyqtSignal(str)
    connection_failed = pyqtSignal(str)
    connection_lost = pyqtSignal(str)

class ChatClient(QWidget):
    def __init__(self):
        super().__init__()
        self.socket = None
        self.username = ""
        self.server_ip = "127.0.0.1"
        self.server_port = "8080"
        self.theme = "Light"
        self.font = QFont("微软雅黑", 11)
        self.bell_enabled = False
        
        self.load_config()
        self.apply_theme()

        self.comm = Communicate()
        self.comm.msg_received.connect(self.display_message)
        self.comm.connection_lost.connect(self.handle_connection_lost)
        
        self.chat_win = None
        self.create_connection_window()

    def apply_theme(self):
        """应用当前主题样式表"""
        is_dark = self.theme == "Dark"
        stylesheet = DARK_STYLESHEET if is_dark else LIGHT_STYLESHEET
        QApplication.instance().setStyleSheet(stylesheet)
        # 如果聊天窗口已创建，更新实时预览
        if hasattr(self, 'msg_entry'):
            self.update_live_preview()

    def load_config(self):
        """从文件加载配置"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.username = config.get("username", "")
                    self.server_ip = config.get("server_ip", "127.0.0.1")
                    self.server_port = config.get("server_port", "8080")
                    self.theme = config.get("theme", "Light")
                    font_family = config.get("font_family", "微软雅黑")
                    font_size = config.get("font_size", 11)
                    self.font = QFont(font_family, font_size)
                    self.bell_enabled = config.get("bell_enabled", False)
            except (json.JSONDecodeError, KeyError):
                self.save_config()
        else:
            self.save_config()

    def save_config(self):
        """保存当前配置到文件"""
        config = {
            "username": self.username,
            "server_ip": self.server_ip,
            "server_port": self.server_port,
            "theme": self.theme,
            "font_family": self.font.family(),
            "font_size": self.font.pointSize(),
            "bell_enabled": self.bell_enabled
        }
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"无法保存配置: {e}")

    def create_connection_window(self):
        """创建连接窗口"""
        self.setObjectName("ConnectionWindow")
        self.setWindowTitle("连接到服务器")
        self.setGeometry(300, 300, 350, 250)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("加入聊天")
        title.setFont(QFont("微软雅黑", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        self.ip_entry = QLineEdit(self.server_ip)
        self.port_entry = QLineEdit(self.server_port)
        self.user_entry = QLineEdit(self.username)
        self.user_entry.setPlaceholderText("输入你的昵称")
        
        form_layout.addRow("服务器IP:", self.ip_entry)
        form_layout.addRow("端口:", self.port_entry)
        form_layout.addRow("用户名:", self.user_entry)
        layout.addLayout(form_layout)

        connect_btn = QPushButton("连接")
        connect_btn.clicked.connect(self.connect_to_server)
        layout.addWidget(connect_btn)
        layout.addStretch()

        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel("提示: Ctrl+Enter 发送消息", alignment=Qt.AlignmentFlag.AlignCenter))
        CURRENT_VERSION = "v1.2.0"
        # try:
        #     NEWEST_VERSION = requests.get("https://www.bopid.cn/chat/newest_version_client.html").content.decode()
        # except Exception:
        #     NEWEST_VERSION = "UNKNOWN"
        # info_layout.addWidget(QLabel(f"版本: {CURRENT_VERSION} (最新: {NEWEST_VERSION})", alignment=Qt.AlignmentFlag.AlignCenter))
        info_layout.addWidget(QLabel(f"当前版本: {CURRENT_VERSION}", alignment=Qt.AlignmentFlag.AlignCenter))
        
        layout.addLayout(info_layout)
        
        self.setLayout(layout)
        self.show()

    def connect_to_server(self):
        """连接到服务器"""
        self.server_ip = self.ip_entry.text()
        self.server_port = self.port_entry.text()
        self.username = self.user_entry.text()

        if not self.username:
            QMessageBox.critical(self, "错误", "用户名不能为空")
            return
        
        if not self.server_port.isdigit():
            QMessageBox.critical(self, "错误", "端口必须是数字")
            return

        try:
            port = int(self.server_port)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_ip, port))
            
            # 设置 TCP Keep-Alive (仅限 Windows)
            if platform.system() == "Windows":
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
                self.socket.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 180 * 1000, 30 * 1000))
            
            self.save_config()
            self.hide()
            self.create_chat_window()
            
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            QMessageBox.critical(self, "连接错误", f"无法连接到服务器:\n{e}")
            self.socket = None

    def create_chat_window(self):
        """创建聊天窗口"""
        self.chat_win = QWidget()
        self.chat_win.setWindowTitle(f"聊天室 - {self.username}")
        self.chat_win.setGeometry(100, 100, 800, 600)
        
        main_layout = QVBoxLayout(self.chat_win)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        v_splitter = QSplitter(Qt.Orientation.Vertical)

        self.chat_browser = QTextBrowser()
        self.chat_browser.setFont(self.font)
        v_splitter.addWidget(self.chat_browser)

        input_area_container = QWidget()
        input_area_layout = QVBoxLayout(input_area_container)
        input_area_layout.setContentsMargins(0, 5, 0, 0)
        input_area_layout.setSpacing(5)

        self.toolbar = QToolBar("Formatting")
        self.toolbar.setMovable(False)
        input_area_layout.addWidget(self.toolbar)

        bold_action = QAction("B", self)
        bold_action.setToolTip("加粗 (Ctrl+B)")
        bold_action.setShortcut("Ctrl+B")
        bold_action.triggered.connect(lambda: self.format_text("**"))
        self.toolbar.addAction(bold_action)

        italic_action = QAction("I", self)
        italic_action.setToolTip("斜体 (Ctrl+I)")
        italic_action.setShortcut("Ctrl+I")
        italic_action.triggered.connect(lambda: self.format_text("*"))
        self.toolbar.addAction(italic_action)

        code_action = QAction("`...`", self)
        code_action.setToolTip("行内代码")
        code_action.triggered.connect(lambda: self.format_text("`"))
        self.toolbar.addAction(code_action)
        
        latex_action = QAction("$...$", self)
        latex_action.setToolTip("行内公式")
        latex_action.triggered.connect(lambda: self.format_text("$"))
        self.toolbar.addAction(latex_action)

        h_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.msg_entry = QTextEdit()
        self.msg_entry.setFont(self.font)
        self.msg_entry.setPlaceholderText("在此输入 Markdown 文本...")
        self.msg_entry.installEventFilter(self)
        
        self.live_preview = QTextBrowser()
        self.live_preview.setFont(self.font)
        self.live_preview.setPlaceholderText("Markdown 实时预览")

        h_splitter.addWidget(self.msg_entry)
        h_splitter.addWidget(self.live_preview)
        h_splitter.setSizes([400, 400])
        input_area_layout.addWidget(h_splitter)

        self.msg_entry.textChanged.connect(self.update_live_preview)

        bottom_button_layout = QHBoxLayout()
        send_btn = QPushButton("发送")
        send_btn.clicked.connect(self.send_message)
        
        setting_btn = QPushButton("设置")
        setting_btn.clicked.connect(self.open_settings)

        bottom_button_layout.addStretch()
        bottom_button_layout.addWidget(setting_btn)
        bottom_button_layout.addWidget(send_btn)
        input_area_layout.addLayout(bottom_button_layout)
        
        v_splitter.addWidget(input_area_container)
        v_splitter.setSizes([400, 200])
        main_layout.addWidget(v_splitter)
        
        self.chat_win.closeEvent = self.on_closing
        self.chat_win.show()

    def update_live_preview(self):
        """更新Markdown实时预览窗口"""
        markdown_text = self.msg_entry.toPlainText()
        is_dark = self.theme == "Dark"
        html = markdown_to_html_with_latex(markdown_text, is_dark)
        self.live_preview.setHtml(html)

    def format_text(self, wrapper):
        """为选中文本添加或移除Markdown包装符"""
        cursor = self.msg_entry.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            if selected_text.startswith(wrapper) and selected_text.endswith(wrapper):
                cursor.insertText(selected_text[len(wrapper):-len(wrapper)])
            else:
                cursor.insertText(f"{wrapper}{selected_text}{wrapper}")
        else:
            cursor.insertText(f"{wrapper}{wrapper}")
            cursor.movePosition(cursor.MoveOperation.PreviousCharacter, n=len(wrapper))
            self.msg_entry.setTextCursor(cursor)

    def eventFilter(self, obj, event):
        """事件过滤器，用于捕获 QTextEdit 的 Ctrl+Enter"""
        if obj is self.msg_entry and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    def open_settings(self):
        """打开设置窗口"""
        dialog = QDialog(self.chat_win)
        dialog.setObjectName("SettingsDialog")
        dialog.setWindowTitle("设置")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)

        theme_layout = QFormLayout()
        theme_combo = QComboBox()
        theme_combo.addItems(["Light", "Dark"])
        theme_combo.setCurrentText(self.theme)
        theme_layout.addRow("主题:", theme_combo)
        layout.addLayout(theme_layout)
        
        font_layout = QFormLayout()
        font_name_entry = QLineEdit(self.font.family())
        font_size_spinbox = QSpinBox()
        font_size_spinbox.setRange(8, 72)
        font_size_spinbox.setValue(self.font.pointSize())
        font_layout.addRow("字体:", font_name_entry)
        font_layout.addRow("大小:", font_size_spinbox)
        layout.addLayout(font_layout)
        
        bell_check = QCheckBox("启用新消息提示音")
        bell_check.setChecked(self.bell_enabled)
        if platform.system() != "Windows":
            bell_check.setDisabled(True)
            bell_check.setToolTip("仅在 Windows 上受支持")
        layout.addWidget(bell_check)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec():
            try:
                self.theme = theme_combo.currentText()
                self.apply_theme()

                font_name = font_name_entry.text()
                font_size = font_size_spinbox.value()
                self.font = QFont(font_name, font_size)
                self.bell_enabled = bell_check.isChecked()
                
                self.chat_browser.setFont(self.font)
                self.msg_entry.setFont(self.font)
                self.live_preview.setFont(self.font)

                self.save_config()
            except Exception as e:
                QMessageBox.critical(dialog, "错误", f"应用设置失败: {e}")

    def send_message(self):
        """发送消息"""
        message = self.msg_entry.toPlainText().strip()
        if not message or not self.socket:
            return
            
        full_msg_raw = f"{self.username}: {message}"
        try:
            self.socket.send(full_msg_raw.encode("utf-8"))
            
            my_msg_color = "#5E81AC" if self.theme == "Light" else "#88C0D0"
            is_dark = self.theme == "Dark"
            html_message = markdown_to_html_with_latex(message, is_dark)
            
            # 移除外层 <p> 标签以避免 append 产生多余间距
            if html_message.startswith("<p>") and html_message.endswith("</p>"):
                html_message = html_message[3:-4]

            self.display_message(f"<font color='{my_msg_color}'>[{get_hh_mm_ss()}] {self.username}:</font><br>{html_message}")
            self.msg_entry.clear()
        except Exception as e:
            QMessageBox.critical(self.chat_win, "发送错误", f"消息发送失败:\n{e}")

    def receive_messages(self):
        """接收消息的线程函数"""
        while self.socket:
            try:
                message_raw = self.socket.recv(1024).decode("utf-8")
                if not message_raw:
                    self.comm.connection_lost.emit("服务器已关闭连接。")
                    break
                
                if message_raw.startswith(f"{self.username}:"):
                    continue

                if ":" in message_raw:
                    parts = message_raw.split(":", 1)
                    sender = parts[0]
                    content_md = parts[1].strip()
                    
                    is_dark = self.theme == "Dark"
                    content_html = markdown_to_html_with_latex(content_md, is_dark)

                    # 移除外层 <p> 标签以避免 append 产生多余间距
                    if content_html.startswith("<p>") and content_html.endswith("</p>"):
                        content_html = content_html[3:-4]

                    other_msg_color = "#005500" if self.theme == "Light" else "#A3BE8C"
                    full_message = f"<font color='{other_msg_color}'>[{get_hh_mm_ss()}] {sender}:</font><br>{content_html}"
                else:
                    sys_msg_color = "#D08770" if self.theme == "Light" else "#EBCB8B"
                    full_message = f"<font color='{sys_msg_color}'>[{get_hh_mm_ss()}] {message_raw}</font>"

                self.comm.msg_received.emit(full_message)
                
                if self.bell_enabled:
                    self.play_notification_sound()
            except (socket.error, ConnectionResetError) as e:
                self.comm.connection_lost.emit(f"与服务器的连接已断开: {e}")
                break
            except Exception:
                pass

    def display_message(self, message):
        """在聊天框中显示消息"""
        self.chat_browser.append(message)
        self.chat_browser.verticalScrollBar().setValue(self.chat_browser.verticalScrollBar().maximum())

    def handle_connection_lost(self, reason):
        """处理连接断开"""
        if self.chat_win and self.chat_win.isVisible():
            QMessageBox.warning(self.chat_win, "连接断开", reason)
            self.chat_win.close()
        self.socket = None

    def play_notification_sound(self):
        """播放提示音"""
        try:
            system = platform.system()
            if system == "Windows":
                import winsound
                winsound.Beep(1000, 200)
            elif system == "Darwin":
                os.system("afplay /System/Library/Sounds/Ping.aiff >/dev/null 2>&1 &")
            else:
                os.system("paplay /usr/share/sounds/freedesktop/stereo/message.oga >/dev/null 2>&1 &")
        except Exception:
            pass

    def on_closing(self, event):
        """关闭窗口时的处理"""
        self.save_config()
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
        self.socket = None
        event.accept()
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = ChatClient()
    sys.exit(app.exec())
