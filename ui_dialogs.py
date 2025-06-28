"""
UI对话框模块 - 包含所有的对话框类
"""
import os
import math
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, 
                             QRadioButton, QLineEdit, QListWidget, QListWidgetItem, 
                             QPushButton, QTextEdit, QProgressBar, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal
from i18n import i18n
from cleanup_temp_images import cleanup_temp_images, get_temp_images_dir


class QuickResponseEditDialog(QDialog):
    """快捷按钮编辑对话框"""
    
    def __init__(self, quick_responses, parent=None):
        super().__init__(parent)
        self.quick_responses = quick_responses.copy()
        self.parent_ui = parent
        self.setWindowTitle(i18n.t("edit_quick_buttons_dialog"))
        self.setModal(True)
        self.resize(600, 500)
        
        # 存储控件引用以便后续更新文本
        self.info_label = None
        self.size_group = None
        self.language_group = None
        self.add_button = None
        self.delete_button = None
        self.move_up_button = None
        self.move_down_button = None
        self.reset_button = None
        self.ok_button = None
        self.cancel_button = None
        self.width_label = None
        self.height_label = None
        
        layout = QVBoxLayout(self)
        
        # 说明标签
        self.info_label = QLabel(i18n.t("edit_instruction"))
        layout.addWidget(self.info_label)
        
        # 按钮尺寸设置区域
        self.size_group = QGroupBox(i18n.t("button_size_settings"))
        size_layout = QHBoxLayout(self.size_group)
        
        self.size_small = QRadioButton(i18n.t("small"))
        self.size_medium = QRadioButton(i18n.t("medium"))
        self.size_large = QRadioButton(i18n.t("large"))
        self.size_custom = QRadioButton(i18n.t("custom"))
        
        # 根据父窗口配置设置初始状态
        if self.parent_ui:
            button_size = self.parent_ui.config.get("button_size", "medium")
            if button_size == "small":
                self.size_small.setChecked(True)
            elif button_size == "large":
                self.size_large.setChecked(True)
            elif button_size == "custom":
                self.size_custom.setChecked(True)
            else:
                self.size_medium.setChecked(True)
        else:
            self.size_medium.setChecked(True)
        
        # 自定义尺寸输入
        self.custom_width = QLineEdit()
        self.custom_width.setPlaceholderText(i18n.t("placeholder_width"))
        self.custom_width.setMaximumWidth(60)
        self.custom_height = QLineEdit()
        self.custom_height.setPlaceholderText(i18n.t("placeholder_height"))
        self.custom_height.setMaximumWidth(60)
        
        if self.parent_ui:
            self.custom_width.setText(str(self.parent_ui.config.get("custom_button_width", 120)))
            self.custom_height.setText(str(self.parent_ui.config.get("custom_button_height", 40)))
        
        size_layout.addWidget(self.size_small)
        size_layout.addWidget(self.size_medium)
        size_layout.addWidget(self.size_large)
        size_layout.addWidget(self.size_custom)
        self.width_label = QLabel(i18n.t("width") + ":")
        size_layout.addWidget(self.width_label)
        size_layout.addWidget(self.custom_width)
        self.height_label = QLabel(i18n.t("height") + ":")
        size_layout.addWidget(self.height_label)
        size_layout.addWidget(self.custom_height)
        size_layout.addStretch()
        
        layout.addWidget(self.size_group)
        
        # 语言设置区域
        self.language_group = QGroupBox(i18n.t("language_settings"))
        language_layout = QHBoxLayout(self.language_group)
        
        self.language_zh = QRadioButton(i18n.t("chinese"))
        self.language_en = QRadioButton(i18n.t("english"))
        
        # 根据父窗口配置设置初始状态
        if self.parent_ui:
            current_language = self.parent_ui.config.get("language", "zh_CN")
            if current_language == "en_US":
                self.language_en.setChecked(True)
            else:
                self.language_zh.setChecked(True)
        else:
            self.language_zh.setChecked(True)
        
        language_layout.addWidget(self.language_zh)
        language_layout.addWidget(self.language_en)
        language_layout.addStretch()
        
        layout.addWidget(self.language_group)
        
        # 列表显示当前快捷按钮
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._edit_item)
        layout.addWidget(self.list_widget)
        
        # 按钮行
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton(i18n.t("add"))
        self.add_button.clicked.connect(self._add_item)
        button_layout.addWidget(self.add_button)
        
        self.delete_button = QPushButton(i18n.t("delete"))
        self.delete_button.clicked.connect(self._delete_item)
        button_layout.addWidget(self.delete_button)
        
        # 添加上移和下移按钮
        self.move_up_button = QPushButton(i18n.t("move_up"))
        self.move_up_button.clicked.connect(self._move_item_up)
        button_layout.addWidget(self.move_up_button)
        
        self.move_down_button = QPushButton(i18n.t("move_down"))
        self.move_down_button.clicked.connect(self._move_item_down)
        button_layout.addWidget(self.move_down_button)
        
        self.reset_button = QPushButton(i18n.t("reset_to_default"))
        self.reset_button.clicked.connect(self._reset_to_default)
        button_layout.addWidget(self.reset_button)
        
        button_layout.addStretch()
        
        self.ok_button = QPushButton(i18n.t("ok"))
        self.ok_button.clicked.connect(self._save_and_accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton(i18n.t("cancel"))
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self._populate_list()
    
    def _update_buttons_for_language_change(self):
        """在编辑对话框中智能更新按钮以适应语言切换"""
        if self.parent_ui and hasattr(self.parent_ui, 'button_manager'):
            # 使用父窗口的方法来更新按钮
            updated_buttons = []
            has_changes = False
            
            # 获取当前语言的默认配置
            current_defaults = self.parent_ui.button_manager.get_smart_default_responses(self.parent_ui.config)
            
            for i, (button_text, response_text) in enumerate(self.quick_responses):
                # 检查这个按钮是否是默认按钮
                is_default_button = self.parent_ui.button_manager.is_default_button(button_text, response_text, i)
                
                if is_default_button and i < len(current_defaults):
                    # 如果是默认按钮，更新为新语言的文本
                    new_button_text, new_response_text = current_defaults[i]
                    updated_buttons.append((new_button_text, new_response_text))
                    if button_text != new_button_text or response_text != new_response_text:
                        has_changes = True
                else:
                    # 如果是自定义按钮，保持原样
                    updated_buttons.append((button_text, response_text))
            
            # 如果有变化，更新按钮配置
            if has_changes:
                self.quick_responses = updated_buttons
    
    def _refresh_ui_text(self):
        """刷新界面文本以适应语言变化"""
        self.setWindowTitle(i18n.t("edit_quick_buttons_dialog"))
        
        if self.info_label:
            self.info_label.setText(i18n.t("edit_instruction"))
        
        if self.size_group:
            self.size_group.setTitle(i18n.t("button_size_settings"))
        
        if self.language_group:
            self.language_group.setTitle(i18n.t("language_settings"))
        
        if self.size_small:
            self.size_small.setText(i18n.t("small"))
        if self.size_medium:
            self.size_medium.setText(i18n.t("medium"))
        if self.size_large:
            self.size_large.setText(i18n.t("large"))
        if self.size_custom:
            self.size_custom.setText(i18n.t("custom"))
        
        if self.language_zh:
            self.language_zh.setText(i18n.t("chinese"))
        if self.language_en:
            self.language_en.setText(i18n.t("english"))
        
        if self.width_label:
            self.width_label.setText(i18n.t("width") + ":")
        if self.height_label:
            self.height_label.setText(i18n.t("height") + ":")
        
        if self.custom_width:
            self.custom_width.setPlaceholderText(i18n.t("placeholder_width"))
        if self.custom_height:
            self.custom_height.setPlaceholderText(i18n.t("placeholder_height"))
        
        if self.add_button:
            self.add_button.setText(i18n.t("add"))
        if self.delete_button:
            self.delete_button.setText(i18n.t("delete"))
        if self.move_up_button:
            self.move_up_button.setText(i18n.t("move_up"))
        if self.move_down_button:
            self.move_down_button.setText(i18n.t("move_down"))
        if self.reset_button:
            self.reset_button.setText(i18n.t("reset_to_default"))
        if self.ok_button:
            self.ok_button.setText(i18n.t("ok"))
        if self.cancel_button:
            self.cancel_button.setText(i18n.t("cancel"))
    
    def _populate_list(self):
        """填充列表"""
        self.list_widget.clear()
        visible_buttons = []
        if self.parent_ui:
            visible_buttons = self.parent_ui.config.get("visible_buttons", list(range(len(self.quick_responses))))
        
        for index, (button_text, response_text) in enumerate(self.quick_responses):
            item = QListWidgetItem(f"{button_text} → {response_text[:50]}{'...' if len(response_text) > 50 else ''}")
            item.setData(Qt.ItemDataRole.UserRole, (button_text, response_text, index))
            
            # 设置复选框状态
            if index in visible_buttons:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
                
            self.list_widget.addItem(item)
    
    def _edit_item(self, item):
        """编辑选中的项目"""
        button_text, response_text, index = item.data(Qt.ItemDataRole.UserRole)
        dialog = QuickResponseItemDialog(button_text, response_text, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_button_text, new_response_text = dialog.get_values()
            self.quick_responses[index] = (new_button_text, new_response_text)
            self._populate_list()
    
    def _add_item(self):
        """添加新项目"""
        dialog = QuickResponseItemDialog("", "", self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            button_text, response_text = dialog.get_values()
            self.quick_responses.append((button_text, response_text))
            self._populate_list()
    
    def _delete_item(self):
        """删除选中的项目"""
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            del self.quick_responses[current_row]
            self._populate_list()
    
    def _move_item_up(self):
        """上移选中的项目"""
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            # 交换位置
            self.quick_responses[current_row], self.quick_responses[current_row - 1] = \
                self.quick_responses[current_row - 1], self.quick_responses[current_row]
            self._populate_list()
            self.list_widget.setCurrentRow(current_row - 1)
    
    def _move_item_down(self):
        """下移选中的项目"""
        current_row = self.list_widget.currentRow()
        if current_row >= 0 and current_row < len(self.quick_responses) - 1:
            # 交换位置
            self.quick_responses[current_row], self.quick_responses[current_row + 1] = \
                self.quick_responses[current_row + 1], self.quick_responses[current_row]
            self._populate_list()
            self.list_widget.setCurrentRow(current_row + 1)
    
    def _reset_to_default(self):
        """重置为默认配置"""
        if not self.parent_ui:
            return
            
        # 检查是否有自定义按钮
        has_custom = False
        default_responses = self.parent_ui._get_smart_default_responses()
        
        # 简单检查：如果按钮数量不同，或者内容不匹配，则认为有自定义
        if len(self.quick_responses) != len(default_responses):
            has_custom = True
        else:
            for i, (button_text, response_text) in enumerate(self.quick_responses):
                if i < len(default_responses):
                    default_button, default_response = default_responses[i]
                    if button_text != default_button or response_text != default_response:
                        has_custom = True
                        break
        
        # 如果有自定义按钮，显示选择对话框
        if has_custom:
            # 创建自定义选择对话框
            choice_dialog = QMessageBox(self)
            choice_dialog.setWindowTitle(i18n.t("reset_options"))
            choice_dialog.setText(i18n.t("reset_options_message"))
            choice_dialog.setInformativeText(i18n.t("reset_options_info"))
            
            # 添加三个选择按钮
            reset_defaults_only = choice_dialog.addButton(i18n.t("reset_defaults_only"), QMessageBox.ButtonRole.ActionRole)
            reset_all = choice_dialog.addButton(i18n.t("reset_all_buttons"), QMessageBox.ButtonRole.ActionRole)
            cancel_button = choice_dialog.addButton(i18n.t("cancel"), QMessageBox.ButtonRole.RejectRole)
            
            choice_dialog.setDefaultButton(reset_defaults_only)
            choice_dialog.exec()
            
            clicked_button = choice_dialog.clickedButton()
            
            if clicked_button == cancel_button:
                return
            elif clicked_button == reset_defaults_only:
                # 只重置默认按钮，保留自定义按钮
                self._reset_defaults_only(default_responses)
                return
            elif clicked_button == reset_all:
                # 继续执行完全重置
                pass
            else:
                return
        
        # 执行重置
        # 清理保存的快捷按钮配置
        if hasattr(self.parent_ui, 'settings') and hasattr(self.parent_ui, 'project_group_name'):
            self.parent_ui.settings.beginGroup(self.parent_ui.project_group_name)
            self.parent_ui.settings.remove("quick_responses")  # 删除保存的快捷按钮配置
            self.parent_ui.settings.endGroup()
        
        # 清理config_manager中的配置
        if hasattr(self.parent_ui, 'config_manager'):
            self.parent_ui.config_manager.save_quick_responses([])  # 清空保存的配置
        
        # 标记没有自定义配置
        if hasattr(self.parent_ui, '_has_custom_buttons'):
            self.parent_ui._has_custom_buttons = False
        
        # 获取默认配置
        self.quick_responses = default_responses.copy()
        
        # 强制更新父窗口的快捷按钮配置
        self.parent_ui.quick_responses = self.quick_responses.copy()
        
        # 重置可见按钮配置为全部显示
        if hasattr(self.parent_ui, 'config'):
            self.parent_ui.config["visible_buttons"] = list(range(len(self.quick_responses)))
        
        # 重新填充列表显示
        self._populate_list()
        
        # 重置按钮尺寸为默认
        self.size_medium.setChecked(True)
        self.custom_width.setText("120")
        self.custom_height.setText("40")
        
        # 立即刷新主界面的按钮显示
        if hasattr(self.parent_ui, 'button_core_manager'):
            self.parent_ui.button_core_manager.refresh_quick_response_buttons()
    
    def _reset_defaults_only(self, default_responses):
        """只重置默认按钮，保留自定义按钮"""
        if not self.parent_ui:
            return
            
        # 分离默认按钮和自定义按钮
        custom_buttons = []
        default_count = len(default_responses)
        
        # 保留超出默认数量的自定义按钮
        if len(self.quick_responses) > default_count:
            for i in range(default_count, len(self.quick_responses)):
                custom_buttons.append(self.quick_responses[i])
        
        # 构建新的按钮列表：默认按钮 + 自定义按钮
        self.quick_responses = default_responses.copy() + custom_buttons
        
        # 更新父窗口配置
        self.parent_ui.quick_responses = self.quick_responses.copy()
        
        # 保存配置（保持自定义按钮标志）
        self.parent_ui._save_quick_responses()
        
        # 更新可见按钮配置
        if hasattr(self.parent_ui, 'config'):
            self.parent_ui.config["visible_buttons"] = list(range(len(self.quick_responses)))
        
        # 重新填充列表显示
        self._populate_list()
        
        # 重置按钮尺寸为默认
        self.size_medium.setChecked(True)
        self.custom_width.setText("120")
        self.custom_height.setText("40")
        
        # 立即刷新主界面的按钮显示
        if hasattr(self.parent_ui, 'button_core_manager'):
            self.parent_ui.button_core_manager.refresh_quick_response_buttons()
    
    def _save_and_accept(self):
        """保存并接受"""
        if self.parent_ui:
            # 更新父窗口配置
            self.parent_ui.quick_responses = self.quick_responses.copy()
            
            # 保存快捷按钮配置
            self.parent_ui._save_quick_responses()
            
            # 更新按钮尺寸配置
            if self.size_small.isChecked():
                self.parent_ui.config["button_size"] = "small"
            elif self.size_large.isChecked():
                self.parent_ui.config["button_size"] = "large"
            elif self.size_custom.isChecked():
                self.parent_ui.config["button_size"] = "custom"
                try:
                    self.parent_ui.config["custom_button_width"] = int(self.custom_width.text())
                    self.parent_ui.config["custom_button_height"] = int(self.custom_height.text())
                except ValueError:
                    # 如果输入无效，使用默认值
                    self.parent_ui.config["custom_button_width"] = 120
                    self.parent_ui.config["custom_button_height"] = 40
            else:
                self.parent_ui.config["button_size"] = "medium"
            
            # 更新语言配置
            if self.language_en.isChecked():
                old_language = self.parent_ui.config.get("language", "zh_CN")
                self.parent_ui.config["language"] = "en_US"
                if old_language != "en_US":
                    # 语言发生变化，切换语言并更新按钮
                    i18n.set_language("en_US")
                    self._update_buttons_for_language_change()
                    self._refresh_ui_text()
                    if hasattr(self.parent_ui, '_refresh_ui_text'):
                        self.parent_ui._refresh_ui_text()
            else:
                old_language = self.parent_ui.config.get("language", "zh_CN")
                self.parent_ui.config["language"] = "zh_CN"
                if old_language != "zh_CN":
                    # 语言发生变化，切换语言并更新按钮
                    i18n.set_language("zh_CN")
                    self._update_buttons_for_language_change()
                    self._refresh_ui_text()
                    if hasattr(self.parent_ui, '_refresh_ui_text'):
                        self.parent_ui._refresh_ui_text()
            
            # 更新可见按钮配置
            visible_buttons = []
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    visible_buttons.append(i)
            self.parent_ui.config["visible_buttons"] = visible_buttons
            
            # 保存配置
            if hasattr(self.parent_ui, 'config_manager'):
                self.parent_ui.config_manager.save_config(self.parent_ui.config)
            
            # 刷新UI
            if hasattr(self.parent_ui, 'button_manager'):
                self.parent_ui.button_manager.clear_layout_cache()
            
            # 刷新快捷按钮显示
            if hasattr(self.parent_ui, 'button_core_manager'):
                self.parent_ui.button_core_manager.refresh_quick_response_buttons()
            
        self.accept()


class QuickResponseItemDialog(QDialog):
    """快捷按钮项目编辑对话框"""
    
    def __init__(self, button_text, response_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(i18n.t("edit_quick_button"))
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # 按钮文本输入
        layout.addWidget(QLabel(i18n.t("button_text")))
        self.button_text_edit = QLineEdit(button_text)
        layout.addWidget(self.button_text_edit)
        
        # 反馈内容输入
        layout.addWidget(QLabel(i18n.t("feedback_content")))
        self.response_text_edit = QTextEdit(response_text)
        self.response_text_edit.setMaximumHeight(80)
        layout.addWidget(self.response_text_edit)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton(i18n.t("ok"))
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton(i18n.t("cancel"))
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def get_values(self):
        """获取输入的值"""
        return self.button_text_edit.text(), self.response_text_edit.toPlainText()


class CleanupThread(QThread):
    """清理线程"""
    finished = Signal(dict)
    
    def __init__(self, days_old):
        super().__init__()
        self.days_old = days_old
    
    def run(self):
        """执行清理"""
        result = cleanup_temp_images(self.days_old, dry_run=False)
        self.finished.emit(result)


class TempImagesCleanupDialog(QDialog):
    """临时图片清理对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(i18n.t("cleanup_temp_images"))
        self.setModal(True)
        self.resize(500, 300)
        self.cleanup_thread = None
        self.setup_ui()
        self.refresh_info()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 信息区域
        info_group = QGroupBox(i18n.t("temp_images_info"))
        info_layout = QVBoxLayout(info_group)
        
        self.path_label = QLabel()
        self.count_label = QLabel()
        self.size_label = QLabel()
        
        info_layout.addWidget(self.path_label)
        info_layout.addWidget(self.count_label)
        info_layout.addWidget(self.size_label)
        
        layout.addWidget(info_group)
        
        # 清理选项
        options_group = QGroupBox(i18n.t("cleanup_options"))
        options_layout = QVBoxLayout(options_group)
        
        days_layout = QHBoxLayout()
        days_layout.addWidget(QLabel(i18n.t("cleanup_days_old")))
        self.days_spin = QLineEdit("7")
        self.days_spin.setMaximumWidth(60)
        days_layout.addWidget(self.days_spin)
        days_layout.addWidget(QLabel(i18n.t("days")))
        days_layout.addStretch()
        
        options_layout.addLayout(days_layout)
        layout.addWidget(options_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 结果区域
        self.result_text = QTextEdit()
        self.result_text.setMaximumHeight(100)
        self.result_text.setVisible(False)
        layout.addWidget(self.result_text)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton(i18n.t("refresh"))
        self.refresh_button.clicked.connect(self.refresh_info)
        button_layout.addWidget(self.refresh_button)
        
        self.cleanup_button = QPushButton(i18n.t("start_cleanup"))
        self.cleanup_button.clicked.connect(self.start_cleanup)
        button_layout.addWidget(self.cleanup_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton(i18n.t("close"))
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def refresh_info(self):
        """刷新信息"""
        temp_dir = get_temp_images_dir()
        self.path_label.setText(f"{i18n.t('temp_directory')}: {temp_dir}")
        
        if os.path.exists(temp_dir):
            files = [f for f in os.listdir(temp_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            total_size = 0
            for file in files:
                file_path = os.path.join(temp_dir, file)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
            
            self.count_label.setText(f"{i18n.t('file_count')}: {len(files)}")
            self.size_label.setText(f"{i18n.t('total_size')}: {self.format_size(total_size)}")
        else:
            self.count_label.setText(f"{i18n.t('file_count')}: 0")
            self.size_label.setText(f"{i18n.t('total_size')}: 0 B")
    
    def start_cleanup(self):
        """开始清理"""
        try:
            days_old = int(self.days_spin.text())
        except ValueError:
            QMessageBox.warning(self, i18n.t("error"), i18n.t("invalid_days_input"))
            return
        
        self.cleanup_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        
        # 启动清理线程
        self.cleanup_thread = CleanupThread(days_old)
        self.cleanup_thread.finished.connect(self.display_result)
        self.cleanup_thread.start()
    
    def display_result(self, result):
        """显示清理结果"""
        self.cleanup_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.result_text.setVisible(True)
        
        # 格式化结果文本
        result_text = []
        if result.get('success', False):
            result_text.append(i18n.t("cleanup_success"))
            result_text.append(f"{i18n.t('deleted_files')}: {result.get('deleted_count', 0)}")
            result_text.append(f"{i18n.t('freed_space')}: {self.format_size(result.get('freed_size', 0))}")
            
            if result.get('errors'):
                result_text.append(f"\n{i18n.t('errors')}:")
                for error in result['errors']:
                    result_text.append(f"- {error}")
        else:
            result_text.append(i18n.t("cleanup_failed"))
            if result.get('error'):
                result_text.append(f"{i18n.t('error')}: {result['error']}")
        
        self.result_text.setPlainText('\n'.join(result_text))
        
        # 刷新信息
        self.refresh_info()
    
    def format_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}" 