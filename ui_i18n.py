"""
国际化UI模块 - 负责UI文本刷新和语言切换
"""
from i18n import i18n


class UIInternationalization:
    """UI国际化管理器"""
    
    def __init__(self, parent_ui):
        self.parent_ui = parent_ui
    
    def refresh_ui_text(self):
        """刷新界面文本以适应语言变化"""
        def update_text():
            # 更新窗口标题
            try:
                self.parent_ui.setWindowTitle("Interactive Feedback MCP")
                
                # 更新命令区域
                if hasattr(self.parent_ui, 'command_group') and self.parent_ui.command_group is not None:
                    self.parent_ui.command_group.setTitle(i18n.t("command"))
                
                if hasattr(self.parent_ui, 'run_command_edit') and self.parent_ui.run_command_edit is not None:
                    self.parent_ui.run_command_edit.setPlaceholderText(i18n.t("placeholder_command"))
                
                if hasattr(self.parent_ui, 'execute_checkbox') and self.parent_ui.execute_checkbox is not None:
                    self.parent_ui.execute_checkbox.setText(i18n.t("auto_execute"))
                
                if hasattr(self.parent_ui, 'run_button') and self.parent_ui.run_button is not None:
                    self.parent_ui.run_button.setText(i18n.t("run"))
                
                if hasattr(self.parent_ui, 'clear_button') and self.parent_ui.clear_button is not None:
                    self.parent_ui.clear_button.setText(i18n.t("clear"))
                
                if hasattr(self.parent_ui, 'submit_button') and self.parent_ui.submit_button is not None:
                    self.parent_ui.submit_button.setText(i18n.t("send_feedback"))
            except RuntimeError:
                # UI对象已被删除，忽略此错误
                pass
            
            try:
                if hasattr(self.parent_ui, 'feedback_text') and self.parent_ui.feedback_text is not None:
                    self.parent_ui.feedback_text.setPlaceholderText(i18n.t("placeholder_feedback"))
                
                if hasattr(self.parent_ui, 'working_dir_label') and self.parent_ui.working_dir_label is not None:
                    formatted_path = self.parent_ui._format_windows_path(self.parent_ui.project_directory)
                    self.parent_ui.working_dir_label.setText(f"{i18n.t('working_directory')}: {formatted_path}")
                
                # 更新组框标题
                if hasattr(self.parent_ui, 'command_group') and self.parent_ui.command_group is not None:
                    self.parent_ui.command_group.setTitle(i18n.t("command"))
                
                if hasattr(self.parent_ui, 'feedback_group') and self.parent_ui.feedback_group is not None:
                    self.parent_ui.feedback_group.setTitle(i18n.t("feedback"))
                
                # 更新反馈后缀选项
                if hasattr(self.parent_ui, 'suffix_group') and self.parent_ui.suffix_group is not None:
                    self.parent_ui.suffix_group.setTitle(i18n.t("feedback_suffix_options"))
                
                if hasattr(self.parent_ui, 'suffix_radio_force') and self.parent_ui.suffix_radio_force is not None:
                    self.parent_ui.suffix_radio_force.setText(i18n.t("force_mcp_call"))
                    self.parent_ui.suffix_radio_force.setToolTip(i18n.t("force_mcp_tooltip"))
                
                if hasattr(self.parent_ui, 'suffix_radio_smart') and self.parent_ui.suffix_radio_smart is not None:
                    self.parent_ui.suffix_radio_smart.setText(i18n.t("smart_judgment"))
                    self.parent_ui.suffix_radio_smart.setToolTip(i18n.t("smart_judgment_tooltip"))
                
                if hasattr(self.parent_ui, 'suffix_radio_none') and self.parent_ui.suffix_radio_none is not None:
                    self.parent_ui.suffix_radio_none.setText(i18n.t("no_special_append"))
                    self.parent_ui.suffix_radio_none.setToolTip(i18n.t("no_append_tooltip"))
                
                # 更新图片传输选项区域
                if hasattr(self.parent_ui, 'image_transmission_group') and self.parent_ui.image_transmission_group is not None:
                    self.parent_ui.image_transmission_group.setTitle(i18n.t("image_transmission_options"))
                
                if hasattr(self.parent_ui, 'base64_checkbox') and self.parent_ui.base64_checkbox is not None:
                    self.parent_ui.base64_checkbox.setText(i18n.t("enable_base64_transmission"))
                    self.parent_ui.base64_checkbox.setToolTip(i18n.t("base64_transmission_tooltip"))
                
                if hasattr(self.parent_ui, 'size_limit_label') and self.parent_ui.size_limit_label is not None:
                    self.parent_ui.size_limit_label.setText(i18n.t("target_size"))
            except RuntimeError:
                # UI对象已被删除，忽略此错误
                pass
            
            # 更新默认快捷按钮列表
            if hasattr(self.parent_ui, 'button_manager'):
                self.parent_ui.default_quick_responses = self.parent_ui.button_manager.get_default_quick_responses(self.parent_ui.config)
            
            # 智能语言切换：只更新默认按钮，保留自定义按钮
            self.update_buttons_for_language_change()
            
            return True
        
        # 使用批量更新避免多次重绘
        if hasattr(self.parent_ui, '_batch_ui_updates'):
            self.parent_ui._batch_ui_updates(update_text)
        else:
            update_text()

    def update_buttons_for_language_change(self):
        """智能语言切换：只更新默认按钮，保留自定义按钮"""
        if not hasattr(self.parent_ui, 'button_manager'):
            return
            
        # 获取当前语言的默认按钮配置
        current_defaults = self.parent_ui.button_manager.get_smart_default_responses(self.parent_ui.config)
        
        # 智能更新：只更新默认按钮，保留自定义按钮
        updated_buttons = []
        has_changes = False
        
        for i, (button_text, response_text) in enumerate(self.parent_ui.quick_responses):
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
        
        # 如果有变化，更新按钮配置并刷新UI
        if has_changes:
            self.parent_ui.quick_responses = updated_buttons
            if hasattr(self.parent_ui, 'config_manager'):
                self.parent_ui.config_manager.save_quick_responses(self.parent_ui.quick_responses)
            
            # 清理缓存并刷新按钮
            if hasattr(self.parent_ui, 'button_manager'):
                self.parent_ui.button_manager.clear_layout_cache()
            
            # 刷新快捷按钮UI
            if hasattr(self.parent_ui, '_refresh_quick_response_buttons'):
                self.parent_ui._refresh_quick_response_buttons()

    def get_default_button_keys(self):
        """获取默认按钮的键列表（用于识别哪些是默认按钮）"""
        # 这些是默认按钮的识别特征
        default_keys = [
            # RIPER-5模式按钮
            "riper_research_full", "riper_innovate_full", "riper_plan_full", 
            "riper_execute_full", "riper_review_full",
            
            # 核心执行策略
            "complete_all_checklist", "smart_execute_checklist", "execute_next_item",
            "regenerate_checklist", "summarize_to_cursorrule",
            
            # 常用反馈
            "looks_good", "needs_adjustment", "fix_issues", "complete",
            
            # 项目特定按钮
            "run_tests", "check_dependencies", "test_interface", "responsive_check",
            "npm_check", "build_test"
        ]
        return default_keys 