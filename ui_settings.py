"""
UI配置设置模块 - 负责配置的加载、保存和管理
"""
import os
import hashlib
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from i18n import i18n
from ui_config import get_project_settings_group


class UISettingsManager:
    """UI配置设置管理器"""
    
    def __init__(self, parent_ui):
        self.parent_ui = parent_ui
    
    def load_settings(self):
        """加载所有设置"""
        # 加载通用UI设置
        self._load_general_settings()
        
        # 加载项目特定设置
        self._load_project_settings()
        
        # 加载base64传输配置
        self._load_base64_settings()
        
        # 构建最终配置
        return self._build_config()
    
    def _load_general_settings(self):
        """加载通用UI设置（几何、状态）"""
        self.parent_ui.settings.beginGroup("MainWindow_General")
        geometry = self.parent_ui.settings.value("geometry")
        if geometry:
            self.parent_ui.restoreGeometry(geometry)
        else:
            self.parent_ui.resize(800, 600)
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - 800) // 2
            y = (screen.height() - 600) // 2
            self.parent_ui.move(x, y)
        
        state = self.parent_ui.settings.value("windowState")
        if state:
            self.parent_ui.restoreState(state)
        self.parent_ui.settings.endGroup()
    
    def _load_project_settings(self):
        """加载项目特定设置"""
        self.parent_ui.settings.beginGroup(self.parent_ui.project_group_name)
        
        self.loaded_run_command = self.parent_ui.settings.value("run_command", "", type=str)
        self.loaded_execute_auto = self.parent_ui.settings.value("execute_automatically", False, type=bool)
        self.loaded_suffix_mode = self.parent_ui.settings.value("suffix_mode", "force", type=str)
        self.loaded_button_size = self.parent_ui.settings.value("button_size", "medium", type=str)
        self.loaded_custom_width = self.parent_ui.settings.value("custom_button_width", 120, type=int)
        self.loaded_custom_height = self.parent_ui.settings.value("custom_button_height", 40, type=int)
        self.loaded_visible_buttons = self.parent_ui.settings.value("visible_buttons", 
                                                                   list(range(len(self.parent_ui.default_quick_responses))), type=list)
        self.loaded_language = self.parent_ui.settings.value("language", "zh_CN", type=str)
        self.command_section_visible = self.parent_ui.settings.value("commandSectionVisible", False, type=bool)
        
        self.parent_ui.settings.endGroup()
    
    def _load_base64_settings(self):
        """加载base64传输配置"""
        self.loaded_use_base64 = self.parent_ui.settings.value("use_base64_transmission", True, type=bool)
        self.loaded_base64_size = self.parent_ui.settings.value("base64_target_size_kb", 30, type=int)
    
    def _build_config(self):
        """构建配置字典"""
        return {
            "run_command": self.loaded_run_command,
            "execute_automatically": self.loaded_execute_auto,
            "suffix_mode": self.loaded_suffix_mode,
            "button_size": self.loaded_button_size,
            "custom_button_width": self.loaded_custom_width,
            "custom_button_height": self.loaded_custom_height,
            "visible_buttons": self.loaded_visible_buttons if self.loaded_visible_buttons else list(range(len(self.parent_ui.default_quick_responses))),
            "language": self.loaded_language,
            "use_base64_transmission": self.loaded_use_base64,
            "base64_target_size_kb": self.loaded_base64_size
        }
    
    def save_config(self):
        """保存所有配置到QSettings"""
        self.parent_ui.settings.beginGroup(self.parent_ui.project_group_name)
        self.parent_ui.settings.setValue("run_command", self.parent_ui.config["run_command"])
        self.parent_ui.settings.setValue("execute_automatically", self.parent_ui.config["execute_automatically"])
        self.parent_ui.settings.setValue("suffix_mode", self.parent_ui.config["suffix_mode"])
        self.parent_ui.settings.setValue("button_size", self.parent_ui.config["button_size"])
        self.parent_ui.settings.setValue("custom_button_width", self.parent_ui.config["custom_button_width"])
        self.parent_ui.settings.setValue("custom_button_height", self.parent_ui.config["custom_button_height"])
        self.parent_ui.settings.setValue("visible_buttons", self.parent_ui.config["visible_buttons"])
        self.parent_ui.settings.setValue("language", self.parent_ui.config["language"])
        self.parent_ui.settings.setValue("use_base64_transmission", self.parent_ui.config["use_base64_transmission"])
        self.parent_ui.settings.setValue("base64_target_size_kb", self.parent_ui.config["base64_target_size_kb"])
        self.parent_ui.settings.endGroup()
        
        if hasattr(self.parent_ui, 'event_manager'):
            self.parent_ui.event_manager.append_log(i18n.t("configuration_saved"))
    
    def update_config_from_ui(self):
        """从UI控件更新配置"""
        self.parent_ui.config["run_command"] = self.parent_ui.command_entry.text()
        self.parent_ui.config["execute_automatically"] = self.parent_ui.auto_check.isChecked()
    
    def update_suffix_config(self):
        """更新后缀模式配置"""
        if self.parent_ui.suffix_radio_force.isChecked():
            self.parent_ui.config["suffix_mode"] = "force"
        elif self.parent_ui.suffix_radio_smart.isChecked():
            self.parent_ui.config["suffix_mode"] = "smart"
        elif self.parent_ui.suffix_radio_none.isChecked():
            self.parent_ui.config["suffix_mode"] = "none"
        
        # 立即保存配置变更
        self.parent_ui.settings.beginGroup(self.parent_ui.project_group_name)
        self.parent_ui.settings.setValue("suffix_mode", self.parent_ui.config["suffix_mode"])
        self.parent_ui.settings.endGroup()
        
        # 记录配置保存日志
        if hasattr(self.parent_ui, 'event_manager'):
            self.parent_ui.event_manager.append_log(f"后缀模式已更新为: {self.parent_ui.config['suffix_mode']}\n")
    
    def update_base64_config(self):
        """更新base64传输配置"""
        self.parent_ui.config["use_base64_transmission"] = self.parent_ui.base64_checkbox.isChecked()
        # 解析目标大小
        size_text = self.parent_ui.size_limit_combo.currentText()
        size_kb = int(size_text.replace("KB", ""))
        self.parent_ui.config["base64_target_size_kb"] = size_kb
    
    def get_command_section_visibility(self):
        """获取命令区域可见性"""
        return self.command_section_visible
    
    def apply_initial_settings(self):
        """应用初始设置"""
        # 设置命令区域可见性
        self.parent_ui.command_group.setVisible(self.command_section_visible)
        if self.command_section_visible:
            self.parent_ui.toggle_command_button.setText("Hide Command Section")
        else:
            self.parent_ui.toggle_command_button.setText("Show Command Section")
        
        # 设置国际化语言
        i18n.set_language(self.loaded_language) 