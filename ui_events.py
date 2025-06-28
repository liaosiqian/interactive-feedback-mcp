"""
UI事件处理模块 - 负责处理各种UI事件
"""
import subprocess
import threading
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextCursor

from i18n import i18n
from ui_utils import kill_tree, get_user_environment


class UIEventManager:
    """UI事件处理管理器"""
    
    def __init__(self, parent_ui):
        self.parent_ui = parent_ui
        self.status_timer = None
    
    def append_log(self, text: str):
        """追加日志文本"""
        self.parent_ui.log_buffer.append(text)
        self.parent_ui.log_text.append(text.rstrip())
        cursor = self.parent_ui.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.parent_ui.log_text.setTextCursor(cursor)
    
    def check_process_status(self):
        """检查进程状态"""
        if self.parent_ui.process and self.parent_ui.process.poll() is not None:
            # 进程已终止
            exit_code = self.parent_ui.process.poll()
            self.append_log(f"\n{i18n.t('process_exited')} {exit_code}\n")
            self.parent_ui.run_button.setText("&Run")
            self.parent_ui.process = None
            self.parent_ui.activateWindow()
            self.parent_ui.feedback_text.setFocus()
        
        # 智能调整定时器频率
        # 简化的定时器频率管理：UI更新期间使用较低频率
        if self.status_timer:
            is_updating = (hasattr(self.parent_ui, 'performance_manager') and 
                          self.parent_ui.performance_manager.is_batch_updating)
            optimal_interval = 200 if is_updating else 100
            if self.status_timer.interval() != optimal_interval:
                self.status_timer.setInterval(optimal_interval)
    
    def run_command(self):
        """运行命令"""
        if self.parent_ui.process:
            kill_tree(self.parent_ui.process)
            self.parent_ui.process = None
            self.parent_ui.run_button.setText("&Run")
            return

        # 清除日志缓冲区但保持UI日志可见
        self.parent_ui.log_buffer = []

        command = self.parent_ui.command_entry.text()
        if not command:
            self.append_log(i18n.t("please_enter_command"))
            return

        self.append_log(f"$ {command}\n")
        self.parent_ui.run_button.setText("Sto&p")

        try:
            self.parent_ui.process = subprocess.Popen(
                command,
                shell=True,
                cwd=self.parent_ui.project_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=get_user_environment(),
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="ignore",
                close_fds=True,
            )

            def read_output(pipe):
                for line in iter(pipe.readline, ""):
                    self.parent_ui.log_signals.append_log.emit(line)

            threading.Thread(
                target=read_output,
                args=(self.parent_ui.process.stdout,),
                daemon=True
            ).start()

            threading.Thread(
                target=read_output,
                args=(self.parent_ui.process.stderr,),
                daemon=True
            ).start()

            # 开始进程状态检查
            self.status_timer = QTimer()
            self.status_timer.timeout.connect(self.check_process_status)
            # 使用智能频率
            # 简化的检查间隔：UI更新期间使用较低频率
            is_updating = (hasattr(self.parent_ui, 'performance_manager') and 
                          self.parent_ui.performance_manager.is_batch_updating)
            check_interval = 200 if is_updating else 100
            self.status_timer.start(check_interval)

        except Exception as e:
            self.append_log(f"{i18n.t('error_running_command')}: {str(e)}\n")
            self.parent_ui.run_button.setText("&Run")
    
    def clear_logs(self):
        """清除日志"""
        self.parent_ui.log_buffer = []
        self.parent_ui.log_text.clear()
    
    def toggle_command_section(self):
        """切换命令区域可见性"""
        is_visible = self.parent_ui.command_group.isVisible()
        self.parent_ui.command_group.setVisible(not is_visible)
        if not is_visible:
            self.parent_ui.toggle_command_button.setText("Hide Command Section")
        else:
            self.parent_ui.toggle_command_button.setText("Show Command Section")
        
        # 立即保存此项目的可见性状态
        self.parent_ui.settings.beginGroup(self.parent_ui.project_group_name)
        self.parent_ui.settings.setValue("commandSectionVisible", self.parent_ui.command_group.isVisible())
        self.parent_ui.settings.endGroup()

        # 仅调整窗口高度
        new_height = self.parent_ui.centralWidget().sizeHint().height()
        if self.parent_ui.command_group.isVisible() and self.parent_ui.command_group.layout().sizeHint().height() > 0:
             # 如果命令组变为可见且有内容，确保足够的高度
             min_content_height = (self.parent_ui.command_group.layout().sizeHint().height() + 
                                 self.parent_ui.feedback_group.minimumHeight() + 
                                 self.parent_ui.toggle_command_button.height() + 
                                 self.parent_ui.centralWidget().layout().spacing() * 2)
             new_height = max(new_height, min_content_height)

        current_width = self.parent_ui.width()
        self.parent_ui.resize(current_width, new_height)
    
    def handle_key_press(self, event):
        """处理键盘事件，支持全局Ctrl+V粘贴图片"""
        if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            # 如果反馈文本框没有焦点，则尝试粘贴图片
            if not self.parent_ui.feedback_text.hasFocus():
                # 检查是否已经在处理中，避免重复处理
                if not getattr(self.parent_ui.clipboard_image_widget, 'is_processing', False):
                    self.parent_ui.clipboard_image_widget.paste_from_clipboard()
                event.accept()  # 标记事件已处理
                return True
        return False
    
    def handle_close_event(self, event):
        """处理窗口关闭事件"""
        # 保存主窗口的通用UI设置（几何、状态）
        self.parent_ui.settings.beginGroup("MainWindow_General")
        self.parent_ui.settings.setValue("geometry", self.parent_ui.saveGeometry())
        self.parent_ui.settings.setValue("windowState", self.parent_ui.saveState())
        self.parent_ui.settings.endGroup()

        # 保存项目特定的命令区域可见性（由于toggle中的立即保存，这里稍有冗余，但无害）
        self.parent_ui.settings.beginGroup(self.parent_ui.project_group_name)
        self.parent_ui.settings.setValue("commandSectionVisible", self.parent_ui.command_group.isVisible())
        self.parent_ui.settings.endGroup()

        if self.parent_ui.process:
            kill_tree(self.parent_ui.process)
        
        event.accept()
    
    def on_images_changed(self, images_data):
        """处理图片列表变化"""
        self.parent_ui.uploaded_images = images_data
        # 可以在这里添加额外的逻辑，比如更新UI状态等
    
    def cleanup_temp_images(self):
        """清理临时图片"""
        from ui_dialogs import TempImagesCleanupDialog
        dialog = TempImagesCleanupDialog(self.parent_ui)
        dialog.exec() 