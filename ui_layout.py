"""
UI布局模块 - 负责创建和管理UI界面布局
"""
import os
import sys
from functools import partial
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QTextEdit, QGroupBox,
    QRadioButton, QComboBox, QMenu
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase

from i18n import i18n
from clipboard_image_widget import ClipboardImageWidget
from ui_utils import FeedbackTextEdit


class UILayoutManager:
    """UI布局管理器"""
    
    def __init__(self, parent_ui):
        self.parent_ui = parent_ui
    
    def create_ui(self):
        """创建主UI界面"""
        central_widget = QWidget()
        self.parent_ui.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建各个UI区域
        self._create_command_toggle_button(layout)
        self._create_command_section(layout)
        self._create_feedback_section(layout)
        self._create_contact_label(layout)
        
        return central_widget
    
    def _create_command_toggle_button(self, layout):
        """创建命令区域切换按钮"""
        self.parent_ui.toggle_command_button = QPushButton("Show Command Section")
        self.parent_ui.toggle_command_button.clicked.connect(self.parent_ui._toggle_command_section)
        layout.addWidget(self.parent_ui.toggle_command_button)
    
    def _create_command_section(self, layout):
        """创建命令执行区域"""
        self.parent_ui.command_group = QGroupBox("Command")
        command_layout = QVBoxLayout(self.parent_ui.command_group)

        # 工作目录标签
        self._create_working_directory_label(command_layout)
        
        # 命令输入行
        self._create_command_input_row(command_layout)
        
        # 自动执行和保存配置行
        self._create_auto_execute_row(command_layout)
        
        # 控制台区域
        self._create_console_section(command_layout)

        self.parent_ui.command_group.setVisible(False)
        layout.addWidget(self.parent_ui.command_group)
    
    def _create_working_directory_label(self, layout):
        """创建工作目录标签"""
        formatted_path = self._format_windows_path(self.parent_ui.project_directory)
        self.parent_ui.working_dir_label = QLabel(f"{i18n.t('working_directory')}: {formatted_path}")
        layout.addWidget(self.parent_ui.working_dir_label)
    
    def _create_command_input_row(self, layout):
        """创建命令输入行"""
        command_input_layout = QHBoxLayout()
        
        self.parent_ui.command_entry = QLineEdit()
        self.parent_ui.command_entry.setText(self.parent_ui.config["run_command"])
        self.parent_ui.command_entry.returnPressed.connect(self.parent_ui.event_manager.run_command)
        self.parent_ui.command_entry.textChanged.connect(self.parent_ui.settings_manager.update_config_from_ui)
        
        self.parent_ui.run_button = QPushButton("&Run")
        self.parent_ui.run_button.clicked.connect(self.parent_ui.event_manager.run_command)

        command_input_layout.addWidget(self.parent_ui.command_entry)
        command_input_layout.addWidget(self.parent_ui.run_button)
        layout.addLayout(command_input_layout)
    
    def _create_auto_execute_row(self, layout):
        """创建自动执行和保存配置行"""
        auto_layout = QHBoxLayout()
        
        self.parent_ui.auto_check = QCheckBox("Execute automatically on next run")
        self.parent_ui.auto_check.setChecked(self.parent_ui.config.get("execute_automatically", False))
        self.parent_ui.auto_check.stateChanged.connect(self.parent_ui.settings_manager.update_config_from_ui)

        # 工具菜单按钮
        self.parent_ui.tools_button = QPushButton(i18n.t("tools_menu"))
        self.parent_ui.tools_button.setToolTip(i18n.t("tools_menu_tooltip"))
        self.parent_ui.tools_button.clicked.connect(self._show_tools_menu)

        self.parent_ui.save_button = QPushButton(i18n.t("save_configuration"))
        self.parent_ui.save_button.clicked.connect(self.parent_ui.settings_manager.save_config)

        auto_layout.addWidget(self.parent_ui.auto_check)
        auto_layout.addStretch()
        auto_layout.addWidget(self.parent_ui.tools_button)
        auto_layout.addWidget(self.parent_ui.save_button)
        layout.addLayout(auto_layout)
    
    def _create_console_section(self, layout):
        """创建控制台区域"""
        console_group = QGroupBox("Console")
        console_layout_internal = QVBoxLayout(console_group)
        console_group.setMinimumHeight(200)

        # 日志文本区域
        self.parent_ui.log_text = QTextEdit()
        self.parent_ui.log_text.setReadOnly(True)
        font = QFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
        font.setPointSize(9)
        self.parent_ui.log_text.setFont(font)
        console_layout_internal.addWidget(self.parent_ui.log_text)

        # 清除按钮
        button_layout = QHBoxLayout()
        self.parent_ui.clear_button = QPushButton("&Clear")
        self.parent_ui.clear_button.clicked.connect(self.parent_ui.clear_logs)
        button_layout.addStretch()
        button_layout.addWidget(self.parent_ui.clear_button)
        console_layout_internal.addLayout(button_layout)
        
        layout.addWidget(console_group)
    
    def _create_feedback_section(self, layout):
        """创建反馈区域"""
        self.parent_ui.feedback_group = QGroupBox("Feedback")
        feedback_layout = QVBoxLayout(self.parent_ui.feedback_group)

        # 描述标签
        self._create_description_label(feedback_layout)
        
        # 快捷按钮区域
        self._create_quick_response_buttons(feedback_layout)
        
        # 反馈文本区域
        self._create_feedback_text_area(feedback_layout)
        
        # 剪贴板图片组件
        self._create_clipboard_image_widget(feedback_layout)
        
        # 图片传输选项
        self._create_image_transmission_options(feedback_layout)
        
        # 反馈后缀选项
        self._create_feedback_suffix_options(feedback_layout)
        
        # 提交按钮
        self._create_submit_button(feedback_layout)
        
        # 设置反馈区域布局
        self._setup_feedback_layout(feedback_layout)
        
        layout.addWidget(self.parent_ui.feedback_group)
    
    def _create_description_label(self, layout):
        """创建描述标签"""
        self.parent_ui.description_label = QLabel(self.parent_ui.prompt)
        self.parent_ui.description_label.setWordWrap(True)
        layout.addWidget(self.parent_ui.description_label)
    
    def _create_quick_response_buttons(self, layout):
        """创建快捷按钮区域"""
        # 确保完全清理之前的按钮
        if hasattr(self.parent_ui, 'quick_response_buttons'):
            for button in self.parent_ui.quick_response_buttons:
                button.deleteLater()
        
        quick_response_widget = QWidget()
        quick_response_layout = QGridLayout(quick_response_widget)
        quick_response_layout.setSpacing(4)
        quick_response_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建快捷回复按钮
        self.parent_ui.quick_response_buttons = []
        button_size = self.parent_ui._get_button_size()
        visible_buttons = self.parent_ui.config.get("visible_buttons", list(range(len(self.parent_ui.quick_responses))))
        
        # 计算按钮布局
        visible_count = len([i for i in range(len(self.parent_ui.quick_responses)) if i in visible_buttons])
        buttons_per_row = self._calculate_buttons_per_row(visible_count)
        
        # 创建按钮
        row = 0
        col = 0
        
        for index, (button_text, response_text) in enumerate(self.parent_ui.quick_responses):
            if index in visible_buttons:
                button = QPushButton(button_text)
                button.setMinimumHeight(button_size["height"] - 5)
                button.setMaximumHeight(button_size["height"])
                button.setMinimumWidth(button_size["width"])
                button.clicked.connect(partial(self.parent_ui._on_quick_response_clicked, response_text))
                self.parent_ui.quick_response_buttons.append(button)
                quick_response_layout.addWidget(button, row, col)
                
                col += 1
                if col >= buttons_per_row:
                    col = 0
                    row += 1
        
        # 添加编辑和清理按钮
        self._add_control_buttons(quick_response_layout, button_size, buttons_per_row, row, col)
        
        layout.addWidget(quick_response_widget)
    
    def _calculate_buttons_per_row(self, visible_count):
        """计算每行显示的按钮数量"""
        if visible_count <= 4:
            return visible_count
        elif visible_count <= 8:
            return 4
        elif visible_count <= 12:
            return 4
        else:
            return 5
    
    def _add_control_buttons(self, layout, button_size, buttons_per_row, row, col):
        """添加控制按钮（编辑按钮）"""
        # 编辑按钮
        edit_button = QPushButton("⚙️")
        edit_button.setMinimumHeight(button_size["height"] - 5)
        edit_button.setMaximumHeight(button_size["height"])
        edit_button.setMinimumWidth(int(button_size["width"] * 0.6))
        edit_button.setMaximumWidth(int(button_size["width"] * 0.8))
        edit_button.setToolTip("编辑快捷按钮")
        edit_button.clicked.connect(self.parent_ui._edit_quick_responses)
        
        # 计算按钮位置
        max_row = row if col > 0 else max(0, row - 1)
        max_col = buttons_per_row - 1
        layout.addWidget(edit_button, max_row, max_col + 1)
    
    def _create_feedback_text_area(self, layout):
        """创建反馈文本区域"""
        self.parent_ui.feedback_text = FeedbackTextEdit()
        font_metrics = self.parent_ui.feedback_text.fontMetrics()
        row_height = font_metrics.height()
        padding = (self.parent_ui.feedback_text.contentsMargins().top() + 
                  self.parent_ui.feedback_text.contentsMargins().bottom() + 3)
        self.parent_ui.feedback_text.setMinimumHeight(4 * row_height + padding)
        self.parent_ui.feedback_text.setPlaceholderText(i18n.t("placeholder_feedback"))
        layout.addWidget(self.parent_ui.feedback_text)
    
    def _create_clipboard_image_widget(self, layout):
        """创建剪贴板图片组件"""
        self.parent_ui.clipboard_image_widget = ClipboardImageWidget()
        self.parent_ui.clipboard_image_widget.images_changed.connect(self.parent_ui.event_manager.on_images_changed)
        layout.addWidget(self.parent_ui.clipboard_image_widget)
        
        # 设置主窗口焦点策略
        self.parent_ui.setFocusPolicy(Qt.StrongFocus)
    
    def _create_image_transmission_options(self, layout):
        """创建图片传输选项"""
        self.parent_ui.image_transmission_group = QGroupBox(i18n.t("image_transmission_options"))
        transmission_layout = QHBoxLayout(self.parent_ui.image_transmission_group)
        transmission_layout.setContentsMargins(6, 6, 6, 6)
        transmission_layout.setSpacing(8)
        
        self.parent_ui.base64_checkbox = QCheckBox(i18n.t("enable_base64_transmission"))
        self.parent_ui.base64_checkbox.setToolTip(i18n.t("base64_transmission_tooltip"))
        self.parent_ui.base64_checkbox.toggled.connect(self.parent_ui.settings_manager.update_base64_config)
        
        self.parent_ui.size_limit_label = QLabel(i18n.t("target_size"))
        self.parent_ui.size_limit_combo = QComboBox()
        self.parent_ui.size_limit_combo.addItems(["30KB", "50KB", "80KB", "100KB"])
        self.parent_ui.size_limit_combo.setCurrentText("30KB")
        self.parent_ui.size_limit_combo.currentTextChanged.connect(self.parent_ui.settings_manager.update_base64_config)
        
        transmission_layout.addWidget(self.parent_ui.base64_checkbox)
        transmission_layout.addWidget(self.parent_ui.size_limit_label)
        transmission_layout.addWidget(self.parent_ui.size_limit_combo)
        transmission_layout.addStretch()
        
        layout.addWidget(self.parent_ui.image_transmission_group)
    
    def _create_feedback_suffix_options(self, layout):
        """创建反馈后缀选项"""
        self.parent_ui.suffix_group = QGroupBox(i18n.t("feedback_suffix_options"))
        suffix_layout = QHBoxLayout(self.parent_ui.suffix_group)
        suffix_layout.setContentsMargins(6, 6, 6, 6)
        suffix_layout.setSpacing(8)
        
        self.parent_ui.suffix_radio_force = QRadioButton(i18n.t("force_mcp_call"))
        self.parent_ui.suffix_radio_force.setToolTip(i18n.t("force_mcp_tooltip"))
        self.parent_ui.suffix_radio_force.toggled.connect(self.parent_ui.settings_manager.update_suffix_config)
        
        self.parent_ui.suffix_radio_smart = QRadioButton(i18n.t("smart_judgment"))
        self.parent_ui.suffix_radio_smart.setToolTip(i18n.t("smart_judgment_tooltip"))
        self.parent_ui.suffix_radio_smart.toggled.connect(self.parent_ui.settings_manager.update_suffix_config)
        
        self.parent_ui.suffix_radio_none = QRadioButton(i18n.t("no_special_append"))
        self.parent_ui.suffix_radio_none.setToolTip(i18n.t("no_append_tooltip"))
        self.parent_ui.suffix_radio_none.toggled.connect(self.parent_ui.settings_manager.update_suffix_config)
        
        suffix_layout.addWidget(self.parent_ui.suffix_radio_force)
        suffix_layout.addWidget(self.parent_ui.suffix_radio_smart)
        suffix_layout.addWidget(self.parent_ui.suffix_radio_none)
        suffix_layout.addStretch()
        
        layout.addWidget(self.parent_ui.suffix_group)
        
        # 设置初始状态
        self._set_suffix_initial_state()
    
    def _set_suffix_initial_state(self):
        """设置后缀选项的初始状态"""
        if self.parent_ui.config["suffix_mode"] == "force":
            self.parent_ui.suffix_radio_force.setChecked(True)
        elif self.parent_ui.config["suffix_mode"] == "smart":
            self.parent_ui.suffix_radio_smart.setChecked(True)
        else:
            self.parent_ui.suffix_radio_none.setChecked(True)
    
    def _create_submit_button(self, layout):
        """创建提交按钮"""
        self.parent_ui.submit_button = QPushButton(i18n.t("send_feedback"))
        self.parent_ui.submit_button.clicked.connect(self.parent_ui.feedback_logic_manager.submit_feedback)
        layout.addWidget(self.parent_ui.submit_button)
    
    def _setup_feedback_layout(self, layout):
        """设置反馈区域布局"""
        layout.setSpacing(6)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # 设置最小高度
        self.parent_ui.feedback_group.setMinimumHeight(
            self.parent_ui.description_label.sizeHint().height() + 
            35 +  # 快捷按钮高度
            self.parent_ui.feedback_text.minimumHeight() + 
            self.parent_ui.suffix_group.sizeHint().height() +
            self.parent_ui.submit_button.sizeHint().height() + 
            layout.spacing() * 3 +
            layout.contentsMargins().top() + 
            layout.contentsMargins().bottom() + 
            10
        )
    
    def _create_contact_label(self, layout):
        """创建联系信息标签"""
        contact_label = QLabel('Need to improve? Contact Fábio Ferreira on <a href="https://x.com/fabiomlferreira">X.com</a> or visit <a href="https://dotcursorrules.com/">dotcursorrules.com</a>')
        contact_label.setOpenExternalLinks(True)
        contact_label.setAlignment(Qt.AlignCenter)
        contact_label.setStyleSheet("font-size: 9pt; color: #cccccc;")
        layout.addWidget(contact_label)
    
    def _format_windows_path(self, path: str) -> str:
        """格式化Windows路径"""
        if sys.platform == "win32":
            path = path.replace("/", "\\")
            if len(path) >= 2 and path[1] == ":" and path[0].isalpha():
                path = path[0].upper() + path[1:]
        return path
    
    def set_base64_initial_state(self):
        """设置base64传输选项的初始状态"""
        self.parent_ui.base64_checkbox.setChecked(self.parent_ui.config["use_base64_transmission"])
        self.parent_ui.size_limit_combo.setCurrentText(f"{self.parent_ui.config['base64_target_size_kb']}KB")
    
    def _show_tools_menu(self):
        """显示工具菜单"""
        menu = QMenu(self.parent_ui)
        
        # 临时文件清理
        cleanup_action = menu.addAction("🗑️ " + i18n.t("cleanup_temp_images"))
        cleanup_action.triggered.connect(self.parent_ui.event_manager.cleanup_temp_images)
        
        # 可以在这里添加更多工具选项
        # separator = menu.addSeparator()
        # other_action = menu.addAction("🔧 其他工具")
        
        # 在按钮下方显示菜单
        button_pos = self.parent_ui.tools_button.mapToGlobal(self.parent_ui.tools_button.rect().bottomLeft())
        menu.exec(button_pos) 