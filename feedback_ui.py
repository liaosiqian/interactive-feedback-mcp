# Interactive Feedback MCP UI
# Developed by Fábio Ferreira (https://x.com/fabiomlferreira)
# Inspired by/related to dotcursorrules.com (https://dotcursorrules.com/)
import os
import sys
import json
import psutil
import argparse
import subprocess
import threading
from typing import Optional
from functools import partial

# 导入国际化和图片组件
from i18n import i18n
from clipboard_image_widget import ClipboardImageWidget

# 导入新的模块化组件
from ui_utils import (
    set_dark_title_bar, get_dark_mode_palette, kill_tree, 
    get_user_environment, LogSignals, FeedbackTextEdit
)
from ui_config import (
    FeedbackResult, FeedbackConfig, UIConfigManager, 
    get_project_settings_group, get_default_config
)
from quick_response_manager import QuickResponseManager
from ui_dialogs import (
    QuickResponseEditDialog, QuickResponseItemDialog, 
    TempImagesCleanupDialog
)
from ui_i18n import UIInternationalization

# 导入新的深度模块化组件
from ui_layout import UILayoutManager
from ui_performance import UIPerformanceManager
from button_core import ButtonCoreManager
from ui_events import UIEventManager
from ui_settings import UISettingsManager
from feedback_logic import FeedbackLogicManager

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QTextEdit, QGroupBox,
    QDialog, QListWidget, QListWidgetItem, QMessageBox, QRadioButton, QSpinBox, QComboBox
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer, QSettings
from PySide6.QtGui import QTextCursor, QIcon, QKeyEvent, QFont, QFontDatabase, QPalette, QColor

# 类型定义已移至 ui_config.py

# 工具函数已移至 ui_utils.py

# 自定义组件已移至 ui_utils.py

class FeedbackUI(QMainWindow):
    def __init__(self, project_directory: str, prompt: str):
        super().__init__()
        self.project_directory = project_directory
        self.prompt = prompt

        self.process: Optional[subprocess.Popen] = None
        self.log_buffer = []
        self.feedback_result = None
        self.log_signals = LogSignals()
        # log_signals连接将在event_manager初始化后设置
        
        # 初始化标志，防止初始化期间重复刷新按钮
        self._is_initializing = True
        
        # 初始化窗口基本设置
        self._setup_window()
        
        # 初始化QSettings
        self.settings = QSettings("InteractiveFeedbackMCP", "InteractiveFeedbackMCP")
        self.project_group_name = get_project_settings_group(self.project_directory)
        
        # 先设置临时的i18n语言（使用默认中文），这样可以正确生成默认按钮
        i18n.set_language("zh_CN")
        
        # 初始化默认快捷按钮
        self.default_quick_responses = self._get_default_quick_responses()
        
        # 加载快捷按钮配置
        self.quick_responses = self._load_quick_responses()
        
        # 初始化自定义按钮标志
        self._has_custom_buttons = False
        
        # 初始化所有管理器
        self._initialize_managers()
        
        # 加载配置
        self.config = self.settings_manager.load_settings()
        
        # 设置国际化语言
        i18n.set_language(self.config["language"])

        # 创建UI
        self.layout_manager.create_ui()
        
        # 设置base64传输选项的初始状态
        self.layout_manager.set_base64_initial_state()
        
        # 确保visible_buttons配置与按钮数量匹配
        self._update_visible_buttons_config()

        # 应用初始设置
        self.settings_manager.apply_initial_settings()

        set_dark_title_bar(self, True)
        
                # 在UI创建后初始化其他管理器（保持兼容性）
        self.quick_response_manager = QuickResponseManager(self)
        self.ui_i18n = UIInternationalization(self)
        
        # 完成初始化，允许按钮刷新
        self._is_initializing = False
        
        # 初始化完成后，根据语言设置更新按钮文本
        self._update_buttons_for_language_change()

        if self.config.get("execute_automatically", False):
            self.event_manager.run_command()
    
    def _setup_window(self):
        """设置窗口基本属性"""
        self.setWindowTitle("Interactive Feedback MCP")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "images", "feedback.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
    
    def _initialize_managers(self):
        """初始化所有管理器"""
        # 配置管理器
        self.config_manager = UIConfigManager(self.project_directory)
        self.settings_manager = UISettingsManager(self)
        
        # 性能管理器
        self.performance_manager = UIPerformanceManager(self)
        
        # UI管理器
        self.layout_manager = UILayoutManager(self)
        self.button_core_manager = ButtonCoreManager(self)
        
        # 事件管理器
        self.event_manager = UIEventManager(self)
        
        # 连接日志信号
        self.log_signals.append_log.connect(self.event_manager.append_log)
        
        # 业务逻辑管理器
        self.feedback_logic_manager = FeedbackLogicManager(self)
        
        # 在UI创建后初始化的管理器（保持兼容性）
        self.quick_response_manager = None
        self.ui_i18n = None

    def _format_windows_path(self, path: str) -> str:
        if sys.platform == "win32":
            # Convert forward slashes to backslashes
            path = path.replace("/", "\\")
            # Capitalize drive letter if path starts with x:\
            if len(path) >= 2 and path[1] == ":" and path[0].isalpha():
                path = path[0].upper() + path[1:]
        return path

    # UI创建方法已移至 ui_layout.py

    def _toggle_command_section(self):
        """切换命令区域可见性 - 委托给事件管理器"""
        self.event_manager.toggle_command_section()

    def _update_config(self):
        """更新配置 - 委托给设置管理器"""
        self.settings_manager.update_config_from_ui()

    def _get_default_quick_responses(self):
        """获取默认快捷按钮列表（统一配置，确保中英文功能对等）"""
        current_language = i18n.language
        
        # 提取完整规则
        mode_rules = self._extract_mode_rules_from_cursor_rule()
        
        # 统一的按钮配置，两种语言功能完全对等
        buttons = [
            # RIPER-5协议模式按钮（两种语言都有）
            (i18n.t("riper_research_full"), mode_rules.get("RESEARCH", i18n.t("riper_research_feedback"))),
            (i18n.t("riper_innovate_full"), mode_rules.get("INNOVATE", i18n.t("riper_innovate_feedback"))),
            (i18n.t("riper_plan_full"), mode_rules.get("PLAN", i18n.t("riper_plan_feedback"))),
            (i18n.t("riper_execute_full"), mode_rules.get("EXECUTE", i18n.t("riper_execute_feedback"))),
            (i18n.t("riper_review_full"), mode_rules.get("REVIEW", i18n.t("riper_review_feedback"))),
            
            # 核心执行策略
            (i18n.t("complete_all_checklist"), i18n.t("complete_all_feedback")),
            (i18n.t("smart_execute_checklist"), i18n.t("smart_execute_feedback")),
            (i18n.t("execute_next_item"), i18n.t("execute_next_feedback")),
            (i18n.t("summarize_to_cursorrule"), i18n.t("summarize_cursorrule_feedback")),
            
            # 常用反馈（统一的三个核心按钮）
            (i18n.t("looks_good"), i18n.t("looks_good_feedback")),
            (i18n.t("needs_adjustment"), i18n.t("needs_adjustment_feedback")),
            (i18n.t("complete"), i18n.t("complete_feedback")),
        ]
        
        return buttons

    def _update_suffix_config(self):
        """更新后缀模式配置 - 委托给设置管理器"""
        self.settings_manager.update_suffix_config()

    def _update_base64_config(self):
        """更新base64传输配置 - 委托给设置管理器"""
        self.settings_manager.update_base64_config()

    def _get_button_size(self):
        """根据配置获取按钮尺寸 - 委托给性能管理器"""
        return self.performance_manager._get_button_size(self.config)
    
    def _batch_ui_updates(self, func):
        """批量处理UI更新 - 委托给性能管理器"""
        return self.performance_manager.batch_ui_updates(func)

    def _submit_feedback(self):
        """提交反馈 - 委托给业务逻辑管理器"""
        self.feedback_logic_manager.submit_feedback()

    def _on_quick_response_clicked(self, response_text: str):
        """处理快捷回复按钮点击 - 委托给业务逻辑管理器"""
        self.feedback_logic_manager.on_quick_response_clicked(response_text)

    def _load_quick_responses(self):
        """加载快捷按钮配置"""
        self.settings.beginGroup(self.project_group_name)
        
        # 尝试加载自定义配置
        saved_responses = self.settings.value("quick_responses", None)
        
        if saved_responses and len(saved_responses) > 0:
            # 标记有自定义配置
            self._has_custom_buttons = True
            self.settings.endGroup()
            return saved_responses
        else:
            # 如果没有保存的配置，生成统一的默认配置
            self._has_custom_buttons = False
            self.settings.endGroup()
            # 直接使用已初始化的默认按钮
            return self.default_quick_responses
    

    
    def _extract_mode_rules_from_cursor_rule(self):
        """从RIPER-5-cursor-rule.txt提取各模式的完整规则"""
        cursor_rule_path = os.path.join(os.path.dirname(__file__), "RIPER-5-cursor-rule.txt")
        
        if not os.path.exists(cursor_rule_path):
            return {}
        
        try:
            with open(cursor_rule_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 定义各模式的规则提取模式
            mode_patterns = {
                "RESEARCH": (
                    r"### 模式1: RESEARCH.*?(?=### 模式2: INNOVATE)",
                    "RESEARCH模式规则"
                ),
                "INNOVATE": (
                    r"### 模式2: INNOVATE.*?(?=### 模式3: PLAN)",
                    "INNOVATE模式规则"
                ),
                "PLAN": (
                    r"### 模式3: PLAN.*?(?=### 模式4: EXECUTE)",
                    "PLAN模式规则"
                ),
                "EXECUTE": (
                    r"### 模式4: EXECUTE.*?(?=### 模式5: REVIEW)",
                    "EXECUTE模式规则"
                ),
                "REVIEW": (
                    r"### 模式5: REVIEW.*?(?=## 关键协议指南)",
                    "REVIEW模式规则"
                )
            }
            
            extracted_rules = {}
            
            for mode, (pattern, description) in mode_patterns.items():
                import re
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    rule_text = match.group(0)
                    # 清理文本，移除过多的空行
                    rule_text = re.sub(r'\n\s*\n\s*\n', '\n\n', rule_text)
                    extracted_rules[mode] = rule_text.strip()
                else:
                    # 如果提取失败，使用备用文本
                    extracted_rules[mode] = f"请严格按照{mode}模式的协议执行，参考RIPER-5-cursor-rule.txt中的详细规则。"
            
            return extracted_rules
            
        except Exception as e:
            # 如果读取失败，返回空字典
            return {}
    
    def _update_visible_buttons_config(self):
        """更新visible_buttons配置以匹配当前按钮数量"""
        current_visible = self.config.get("visible_buttons", [])
        total_buttons = len(self.quick_responses)
        
        # 如果当前配置的可见按钮数量少于总按钮数量，添加新按钮为可见
        if len(current_visible) < total_buttons:
            # 添加缺失的按钮索引
            for i in range(len(current_visible), total_buttons):
                current_visible.append(i)
            
            self.config["visible_buttons"] = current_visible
            
            # 保存更新后的配置
            self.settings.beginGroup(self.project_group_name)
            self.settings.setValue("visible_buttons", current_visible)
            self.settings.endGroup()

    def _get_smart_default_responses(self):
        """获取统一的默认快捷按钮（不区分项目类型）"""
        # 统一提供一份默认配置，不区分项目类型
        return self._get_default_quick_responses()

    def _save_quick_responses(self):
        """保存快捷按钮配置"""
        self.settings.beginGroup(self.project_group_name)
        self.settings.setValue("quick_responses", self.quick_responses)
        self.settings.endGroup()
        
        # 标记用户有自定义配置
        self._has_custom_buttons = True

    def _edit_quick_responses(self):
        """编辑快捷按钮配置（优化版本）"""
        dialog = QuickResponseEditDialog(self.quick_responses, self)
        if dialog.exec() == QDialog.Accepted:
            # 清理缓存（配置可能已更改）
            self.performance_manager.clear_layout_cache()
            
            self.quick_responses = dialog.quick_responses
            self._save_quick_responses()
            
            # 批量执行UI更新
            def update_ui():
                self.button_core_manager.refresh_quick_response_buttons()
                self.settings_manager.save_config()
                self._adjust_window_size()
                return True
            
            self.performance_manager.batch_ui_updates(update_ui)

    def clear_logs(self):
        self.log_buffer = []
        self.log_text.clear()

    def _adjust_window_size(self):
        """调整窗口大小以适应新的按钮配置（优化版本）"""
        def adjust_size():
            # 使用缓存的布局信息
            layout_info = self.quick_response_manager.get_cached_button_layout(
                self.config, self.quick_responses
            )
            button_size = layout_info["button_size"]
            visible_count = layout_info["visible_count"]
            buttons_per_row = layout_info["buttons_per_row"]
            
            # 更新反馈组的最小高度
            self.feedback_group.setMinimumHeight(
                self.description_label.sizeHint().height() + 
                button_size["height"] + 15 +  # 按钮高度加边距
                self.feedback_text.minimumHeight() + 
                80 +  # 后缀选项组的大概高度
                40 +  # 提交按钮高度
                60    # 额外边距
            )
            
            # 计算窗口宽度（包含编辑按钮）
            actual_buttons_per_row = min(buttons_per_row, visible_count)
            estimated_width = max(800, actual_buttons_per_row * (button_size["width"] + 10) + 100)
            
            # 让窗口根据内容自动调整大小
            self.adjustSize()
            
            # 设置新的窗口大小
            current_size = self.size()
            new_width = max(estimated_width, current_size.width())
            new_height = max(500, current_size.height())
            
            # 调整窗口大小
            self.resize(new_width, new_height)
            
            # 居中显示窗口
            self._center_window()
            
            return True
        
        # 使用批量更新和延迟布局更新
        self.performance_manager.batch_ui_updates(adjust_size)
        self.performance_manager.schedule_layout_update()

    def _center_window(self):
        """将窗口居中显示"""
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.geometry()
        x = (screen.width() - window_geometry.width()) // 2
        y = (screen.height() - window_geometry.height()) // 2
        self.move(x, y)

    def _refresh_ui_text(self):
        """刷新界面文本以适应语言变化（优化版本）"""
        def update_text():
            # 更新窗口标题
            self.setWindowTitle(i18n.t("window_title"))
            
            # 更新按钮文本（添加安全检查）
            try:
                if hasattr(self, 'toggle_command_button') and self.toggle_command_button is not None:
                    if self.command_group.isVisible():
                        self.toggle_command_button.setText(i18n.t("hide_command_section"))
                    else:
                        self.toggle_command_button.setText(i18n.t("show_command_section"))
                
                if hasattr(self, 'run_button') and self.run_button is not None:
                    if self.process:
                        self.run_button.setText(i18n.t("stop"))
                    else:
                        self.run_button.setText(i18n.t("run"))
                
                if hasattr(self, 'clear_button') and self.clear_button is not None:
                    self.clear_button.setText(i18n.t("clear"))
                
                if hasattr(self, 'auto_check') and self.auto_check is not None:
                    self.auto_check.setText(i18n.t("execute_automatically"))
                
                if hasattr(self, 'save_button') and self.save_button is not None:
                    self.save_button.setText(i18n.t("save_configuration"))
                
                if hasattr(self, 'tools_button') and self.tools_button is not None:
                    self.tools_button.setText(i18n.t("tools_menu"))
                    self.tools_button.setToolTip(i18n.t("tools_menu_tooltip"))
                
                if hasattr(self, 'submit_button') and self.submit_button is not None:
                    self.submit_button.setText(i18n.t("send_feedback"))
            except RuntimeError:
                # UI对象已被删除，忽略此错误
                pass
            
            try:
                if hasattr(self, 'feedback_text') and self.feedback_text is not None:
                    self.feedback_text.setPlaceholderText(i18n.t("placeholder_feedback"))
                
                if hasattr(self, 'working_dir_label') and self.working_dir_label is not None:
                    formatted_path = self._format_windows_path(self.project_directory)
                    self.working_dir_label.setText(f"{i18n.t('working_directory')}: {formatted_path}")
                
                # 更新组框标题
                if hasattr(self, 'command_group') and self.command_group is not None:
                    self.command_group.setTitle(i18n.t("command"))
                
                if hasattr(self, 'feedback_group') and self.feedback_group is not None:
                    self.feedback_group.setTitle(i18n.t("feedback"))
                
                # 更新反馈后缀选项
                if hasattr(self, 'suffix_group') and self.suffix_group is not None:
                    self.suffix_group.setTitle(i18n.t("feedback_suffix_options"))
                
                if hasattr(self, 'suffix_radio_force') and self.suffix_radio_force is not None:
                    self.suffix_radio_force.setText(i18n.t("force_mcp_call"))
                    self.suffix_radio_force.setToolTip(i18n.t("force_mcp_tooltip"))
                
                if hasattr(self, 'suffix_radio_smart') and self.suffix_radio_smart is not None:
                    self.suffix_radio_smart.setText(i18n.t("smart_judgment"))
                    self.suffix_radio_smart.setToolTip(i18n.t("smart_judgment_tooltip"))
                
                if hasattr(self, 'suffix_radio_none') and self.suffix_radio_none is not None:
                    self.suffix_radio_none.setText(i18n.t("no_special_append"))
                    self.suffix_radio_none.setToolTip(i18n.t("no_append_tooltip"))
                
                # 更新图片传输选项区域
                if hasattr(self, 'image_transmission_group') and self.image_transmission_group is not None:
                    self.image_transmission_group.setTitle(i18n.t("image_transmission_options"))
                
                if hasattr(self, 'base64_checkbox') and self.base64_checkbox is not None:
                    self.base64_checkbox.setText(i18n.t("enable_base64_transmission"))
                    self.base64_checkbox.setToolTip(i18n.t("base64_transmission_tooltip"))
                
                if hasattr(self, 'size_limit_label') and self.size_limit_label is not None:
                    self.size_limit_label.setText(i18n.t("target_size"))
            except RuntimeError:
                # UI对象已被删除，忽略此错误
                pass
            
            # 更新默认快捷按钮列表
            self.default_quick_responses = self._get_default_quick_responses()
            
            # 智能语言切换：只更新默认按钮，保留自定义按钮
            self._update_buttons_for_language_change()
            
            return True
        
        # 使用批量更新避免多次重绘
        self.performance_manager.batch_ui_updates(update_text)

    def _update_buttons_for_language_change(self):
        """智能更新按钮以适应语言切换：强制更新所有默认按钮"""
        # 如果正在初始化，跳过按钮更新避免重复
        if getattr(self, '_is_initializing', False):
            return
            
        # 获取当前语言的默认按钮配置
        current_defaults = self._get_default_quick_responses()
        
        # 检查是否有自定义按钮配置
        if not hasattr(self, '_has_custom_buttons') or not self._has_custom_buttons:
            # 如果没有自定义配置，直接使用新语言的默认配置
            self.quick_responses = current_defaults
            self.performance_manager.clear_layout_cache()
            if not getattr(self, '_is_initializing', False):
                self.button_core_manager.refresh_quick_response_buttons()
            return
        
        # 如果有自定义配置，需要智能合并
        updated_buttons = []
        has_changes = False
        
        # 保守策略：重新生成所有默认按钮，只保留明确的自定义按钮
        default_count = len(current_defaults)
        
        # 首先添加当前语言的所有默认按钮
        for i, (button_text, response_text) in enumerate(current_defaults):
            updated_buttons.append((button_text, response_text))
            # 检查是否与现有按钮不同
            if i < len(self.quick_responses):
                old_button_text, old_response_text = self.quick_responses[i]
                if button_text != old_button_text or response_text != old_response_text:
                    has_changes = True
            else:
                has_changes = True
        
        # 然后添加超出默认数量的自定义按钮
        if len(self.quick_responses) > default_count:
            for i in range(default_count, len(self.quick_responses)):
                button_text, response_text = self.quick_responses[i]
                # 检查是否为明确的自定义按钮（不匹配任何默认模式）
                if not self._is_default_button(button_text, response_text, i):
                    updated_buttons.append((button_text, response_text))
        
        # 如果有变化，更新按钮配置
        if has_changes or len(updated_buttons) != len(self.quick_responses):
            self.quick_responses = updated_buttons
            self.performance_manager.clear_layout_cache()
            if not getattr(self, '_is_initializing', False):
                self.button_core_manager.refresh_quick_response_buttons()
            # 注意：这里不调用 _save_quick_responses() 来避免覆盖用户的自定义配置标记
    
    def _get_default_button_keys(self):
        """获取默认按钮的键名列表，用于语言切换时的映射"""
        return [
            "riper_research_mode", "riper_innovate_mode", "riper_plan_mode", 
            "riper_execute_mode", "riper_review_mode", 
            "riper_research_full", "riper_innovate_full", "riper_plan_full", 
            "riper_execute_full", "riper_review_full",
            "complete_all_checklist", "smart_execute_checklist", "execute_next_item", 
            "regenerate_checklist", "complete_and_record", "looks_good", "needs_adjustment", 
            "reimplemented", "add_comments", "optimize_performance", "fix_issues", "complete", 
            "run_tests", "check_dependencies", "test_interface", "responsive_check", 
            "npm_check", "build_test"
        ]
    
    def _is_default_button(self, button_text, response_text, index):
        """判断按钮是否为默认按钮"""
        from ui_config import is_default_button
        return is_default_button(button_text, response_text)

    def keyPressEvent(self, event):
        """处理键盘事件，支持全局Ctrl+V粘贴图片"""
        if self.event_manager.handle_key_press(event):
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        """处理窗口关闭事件"""
        self.event_manager.handle_close_event(event)
        super().closeEvent(event)

    def run(self) -> FeedbackResult:
        self.show()
        QApplication.instance().exec()

        if self.process:
            kill_tree(self.process)

        if not self.feedback_result:
            return FeedbackResult(logs="".join(self.log_buffer), interactive_feedback="")

        return self.feedback_result

def get_project_settings_group(project_dir: str) -> str:
    # Create a safe, unique group name from the project directory path
    # Using only the last component + hash of full path to keep it somewhat readable but unique
    import hashlib
    basename = os.path.basename(os.path.normpath(project_dir))
    full_hash = hashlib.md5(project_dir.encode('utf-8')).hexdigest()[:8]
    return f"{basename}_{full_hash}"

def _call_interactive_feedback_mcp(project_directory: str, summary: str):
    """调用interactive-feedback-mcp等待用户反馈"""
    try:
        # 导入MCP工具（如果可用）
        import subprocess
        import sys
        import json
        
        # 构建MCP调用命令
        mcp_command = [
            sys.executable, "-c",
            f"""
import json
import sys
try:
    # 模拟MCP interactive_feedback调用
    print("MCP Interactive Feedback Started")
    print(f"Project: {project_directory}")
    print(f"Summary: {summary}")
    print("等待用户反馈...")
    
    # 这里应该是实际的MCP调用逻辑
    # 暂时用输入等待来模拟
    user_input = input("请输入反馈（按Enter结束）: ")
    
    result = {{
        "logs": "MCP调用完成",
        "interactive_feedback": user_input
    }}
    
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({{"error": str(e)}}))
"""
        ]
        
        # 执行MCP调用
        process = subprocess.Popen(
            mcp_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            try:
                result = json.loads(stdout.strip().split('\n')[-1])
                return result
            except:
                return {"logs": stdout, "interactive_feedback": ""}
        else:
            print(f"MCP调用失败: {stderr}")
            return {"logs": stderr, "interactive_feedback": ""}
            
    except Exception as e:
        print(f"调用interactive-feedback-mcp时出错: {e}")
        return {"logs": str(e), "interactive_feedback": ""}

def feedback_ui(project_directory: str, prompt: str, output_file: Optional[str] = None) -> Optional[FeedbackResult]:
    app = QApplication.instance() or QApplication()
    app.setPalette(get_dark_mode_palette(app))
    app.setStyle("Fusion")
    ui = FeedbackUI(project_directory, prompt)
    result = ui.run()

    # 在获得结果后调用interactive-feedback-mcp等待用户反馈
    if result and result.get("interactive_feedback"):
        print("正在调用interactive-feedback-mcp等待您的反馈...")
        mcp_result = _call_interactive_feedback_mcp(project_directory, "用户反馈已提交，等待进一步指示")
        
        # 如果MCP返回了额外的反馈，可以合并到结果中
        if mcp_result and mcp_result.get("interactive_feedback"):
            original_feedback = result["interactive_feedback"]
            additional_feedback = mcp_result["interactive_feedback"]
            if additional_feedback.strip():  # 只有在有额外反馈时才合并
                result["interactive_feedback"] = f"{original_feedback}\n\n[额外反馈]: {additional_feedback}"

    if output_file and result:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
        # Save the result to the output file
        with open(output_file, "w") as f:
            json.dump(result, f)
        return None

    return result

# 对话框类已移至 ui_dialogs.py：
# - QuickResponseEditDialog
# - QuickResponseItemDialog
# - TempImagesCleanupDialog

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the feedback UI")
    parser.add_argument("--project-directory", default=os.getcwd(), help="The project directory to run the command in")
    parser.add_argument("--prompt", default="I implemented the changes you requested.", help="The prompt to show to the user")
    parser.add_argument("--output-file", help="Path to save the feedback result as JSON")
    args = parser.parse_args()

    result = feedback_ui(args.project_directory, args.prompt, args.output_file)
    if result:
        print(f"\nLogs collected: \n{result['logs']}")
        print(f"\nFeedback received:\n{result['interactive_feedback']}")
    sys.exit(0)
