"""
UI工具模块 - 包含通用UI工具函数和自定义组件
"""
import os
import sys
import subprocess
import signal
from typing import Optional
from PySide6.QtWidgets import QApplication, QTextEdit, QWidget
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QColor, QPalette, QKeyEvent
from i18n import i18n


def set_dark_title_bar(widget: QWidget, dark_title_bar: bool) -> None:
    """设置窗口标题栏为暗色模式（Windows特定）"""
    if sys.platform != "win32":
        return
    
    try:
        import ctypes
        from ctypes import wintypes
        
        hwnd = widget.winId()
        
        # 使用DwmSetWindowAttribute设置暗色标题栏
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        value = ctypes.c_int(1 if dark_title_bar else 0)
        
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(value),
            ctypes.sizeof(value)
        )
        
        # Windows特定解决方案：创建临时窗口强制重绘标题栏
        # 这是一个已知的Windows DWM API限制的解决方案，在某些情况下
        # DwmSetWindowAttribute调用后需要强制窗口重绘才能使暗色标题栏生效
        # 参考：https://docs.microsoft.com/en-us/windows/win32/api/dwmapi/nf-dwmapi-dwmsetwindowattribute
        temp_widget = QWidget(None, Qt.WindowType.FramelessWindowHint)
        temp_widget.resize(1, 1)
        temp_widget.move(widget.pos())
        temp_widget.show()
        temp_widget.deleteLater()  # Safe deletion in Qt event loop
        
    except ImportError:
        # 如果无法导入ctypes，跳过设置
        pass
    except Exception:
        # 其他异常也跳过，避免影响主程序
        pass


def get_dark_mode_palette(app: QApplication):
    """获取暗色模式调色板"""
    palette = app.palette()
    
    # 设置暗色主题颜色
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    
    return palette


def kill_tree(process: subprocess.Popen):
    """终止进程树（跨平台）"""
    if sys.platform == "win32":
        # Windows: 使用taskkill命令终止进程树
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                check=False,
                capture_output=True
            )
        except Exception:
            # 如果taskkill失败，尝试直接终止进程
            try:
                process.terminate()
            except Exception:
                pass
    else:
        # Unix/Linux/macOS: 使用进程组终止
        try:
            # 获取进程组ID并发送SIGTERM信号
            pgid = os.getpgid(process.pid)
            os.killpg(pgid, signal.SIGTERM)
        except Exception:
            # 如果进程组终止失败，尝试直接终止进程
            try:
                process.terminate()
            except Exception:
                pass


def get_user_environment() -> dict[str, str]:
    """获取用户环境变量"""
    env = os.environ.copy()
    
    # 在Windows上，确保包含用户的PATH
    if sys.platform == "win32":
        # 获取用户特定的PATH变量
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                user_path, _ = winreg.QueryValueEx(key, "PATH")
                system_path = env.get("PATH", "")
                env["PATH"] = f"{user_path};{system_path}"
        except Exception:
            # 如果无法获取用户PATH，使用系统PATH
            pass
    
    return env


class LogSignals(QObject):
    """日志信号类 - 用于线程安全的日志输出"""
    append_log = Signal(str)


class FeedbackTextEdit(QTextEdit):
    """自定义文本编辑器 - 支持图片粘贴和拖放"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setPlaceholderText(i18n.t("placeholder_feedback"))

    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘事件"""
        # Ctrl+V 粘贴事件
        if event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._handle_paste()
            return
        
        # 其他键盘事件交给父类处理
        super().keyPressEvent(event)

    def _handle_paste(self):
        """处理粘贴事件"""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        # 检查是否包含图片数据
        if mime_data.hasImage():
            # 如果有图片数据，插入图片
            self.insertFromMimeData(mime_data)
        else:
            # 否则执行正常的文本粘贴
            super().insertPlainText(clipboard.text())

    def insertFromMimeData(self, source):
        """处理拖放和粘贴的MIME数据"""
        if source.hasImage():
            # 通知父窗口有图片被粘贴
            parent_window = self.window()
            if hasattr(parent_window, 'clipboard_image_widget'):
                parent_window.clipboard_image_widget.handle_clipboard_image()
        elif source.hasText():
            # 插入文本
            self.insertPlainText(source.text())
        else:
            # 交给父类处理其他类型的数据
            super().insertFromMimeData(source) 