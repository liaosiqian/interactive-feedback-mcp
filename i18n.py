# -*- coding: utf-8 -*-
"""
国际化支持模块
支持中文、英文等多种语言
"""

class I18n:
    def __init__(self, language="zh_CN"):
        self.language = language
        self.translations = {
            "zh_CN": {
                # 窗口标题
                "window_title": "Interactive Feedback MCP",
                
                # 按钮文本
                "show_command_section": "显示命令区域",
                "hide_command_section": "隐藏命令区域",
                "run": "&运行",
                "stop": "停&止",
                "clear": "&清除",
                "save_configuration": "&保存配置",
                "tools_menu": "🔧 工具",
                "tools_menu_tooltip": "打开工具菜单",
                "cleanup_temp_images": "🗑️ 清理临时图片",
                "send_feedback": "&发送反馈 (Ctrl+Enter)",
                "edit_quick_buttons": "编辑快捷按钮",
                
                # 复选框和标签
                "execute_automatically": "下次运行时自动执行",
                "working_directory": "工作目录",
                "command": "命令",
                "console": "控制台",
                "feedback": "反馈",
                
                # 反馈后缀选项
                "feedback_suffix_options": "反馈后缀选项",
                "force_mcp_call": "强制MCP调用",
                "smart_judgment": "智能判断",
                "no_special_append": "不特别追加",
                "force_mcp_tooltip": "执行完后需要调用interactive-feedback-mcp 等待我的反馈",
                "smart_judgment_tooltip": "执行完后自行判定是否需要调用interactive-feedback-mcp 等待我的反馈",
                "no_append_tooltip": "不在反馈内容后追加任何MCP调用指令",
                

                
                # 快捷按钮
                "complete_all_checklist": "📋 完成所有清单",
                "smart_execute_checklist": "🎯 智能执行清单",
                "execute_next_item": "➡️ 执行下一项",
                # 移除regenerate_checklist（与complete_all_checklist功能重叠）
                # "regenerate_checklist": "🔄 重新生成清单",
                "complete_and_record": "📝 完成并记录",
                "summarize_to_cursorrule": "📋 总结生成规则文件",
                "looks_good": "✅ 看起来不错",
                "needs_adjustment": "🔧 需要小调整",
                # 移除reimplemented和fix_issues（与needs_adjustment功能重叠）
                # "reimplemented": "🔄 重新实现",
                # "fix_issues": "🐛 修复问题",
                "complete": "✨ 完成",
                
                # 对话框
                "edit_quick_buttons_dialog": "编辑快捷按钮",
                "button_size_settings": "按钮尺寸设置",
                "small": "小 (100x30)",
                "medium": "中 (120x40)",
                "large": "大 (150x45)",
                "custom": "自定义",
                "width": "宽",
                "height": "高",
                "add": "添加",
                "delete": "删除",
                "move_up": "上移",
                "move_down": "下移",
                "reset_to_default": "重置为默认",
                "ok": "确定",
                "cancel": "取消",
                "confirm_delete": "确认删除",
                "confirm_delete_message": "确定要删除这个快捷按钮吗？",
                "confirm_reset": "确认重置",
                "confirm_reset_message": "确定要重置为默认快捷按钮吗？这将丢失所有自定义配置。",
                "reset_options": "重置选项",
                "reset_options_message": "检测到您有自定义按钮，请选择重置方式：",
                "reset_options_info": "• 只重置默认按钮：更新默认按钮到最新版本，保留您的自定义按钮\n• 完全重置：删除所有按钮并恢复到默认配置",
                "reset_defaults_only": "只重置默认按钮",
                "reset_all_buttons": "完全重置",
                "edit_instruction": "双击列表项进行编辑，或使用下方按钮添加/删除按钮",
                "button_text": "按钮文本:",
                "feedback_content": "反馈内容:",
                "placeholder_width": "宽度",
                "placeholder_height": "高度",
                "placeholder_feedback": "在此输入您的反馈 (Ctrl+Enter 提交)",
                
                # 消息
                "configuration_saved": "项目配置已保存。\n",
                "please_enter_command": "请输入要运行的命令\n",
                "process_exited": "进程退出，退出码",
                "error_running_command": "运行命令时出错",
                
                # 后缀文本
                "suffix_force": "，执行完后需要调用interactive-feedback-mcp 等待我的反馈",
                "suffix_smart": "，执行完后自行判定是否需要调用interactive-feedback-mcp 等待我的反馈",
                

                
                # RIPER-5协议模式反馈内容
                "riper_research_feedback": "请进入RESEARCH模式，深入分析当前问题，系统性地分解技术组件，识别关键约束和需求，但不提供解决方案建议。执行完后自行判定是否需要调用interactive-feedback-mcp等待我的反馈。",
                "riper_innovate_feedback": "请进入INNOVATE模式，基于研究结果进行头脑风暴，探索多种解决方案，评估各方案的优缺点，但不进行具体规划。执行完后自行判定是否需要调用interactive-feedback-mcp等待我的反馈。",
                "riper_plan_feedback": "请进入PLAN模式，制定详尽的技术规范和实施计划，为每个步骤标记review:true/false，生成完整的检查清单。执行完后自行判定是否需要调用interactive-feedback-mcp等待我的反馈。",
                "riper_execute_feedback": "请进入EXECUTE模式，严格按照计划执行，对review:true的步骤启动MCP交互式反馈，完成后请求确认。执行完后自行判定是否需要调用interactive-feedback-mcp等待我的反馈。",
                "riper_review_feedback": "请进入REVIEW模式，全面验证实施结果与原始需求的一致性，通过MCP interactive_feedback获取最终反馈。执行完后自行判定是否需要调用interactive-feedback-mcp等待我的反馈。",
                
                # RIPER-5完整规则版按钮（通俗易懂版本）
                "riper_research_full": "🔍 深度分析问题",
                "riper_innovate_full": "💡 创新解决方案",
                "riper_plan_full": "📋 制定实施计划",
                "riper_execute_full": "⚡ 执行计划步骤",
                "riper_review_full": "🎯 验证最终结果",
                
                # 快捷按钮反馈内容
                "complete_all_feedback": "继续完成剩余的所有清单，所有清单项完成后需要调用 interactive-feedback-mcp 等待我的反馈",
                "smart_execute_feedback": "继续执行剩余的清单项，按照清单项的情况，决定是否需要调用 interactive-feedback-mcp",
                "execute_next_feedback": "继续执行下一项清单项，执行完后需要调用 interactive-feedback-mcp 等待我的反馈",
                "regenerate_feedback": "重新生成清单项，并更新到markdown文档，生成完后需要调用 interactive-feedback-mcp 等待我的反馈",
                "complete_record_feedback": "继续完成剩余的所有清单项，并且将处理结果记录到markdown文档，所有清单项完成后需要调用 interactive-feedback-mcp 等待我的反馈",
                "summarize_cursorrule_feedback": "请总结当前对话的关键内容，提取核心规则和最佳实践，同时生成或更新项目的两种规则文件：1) 传统的.cursorrules文件（向后兼容）2) 新标准的.cursor/rules/main.mdc文件（推荐格式），确保两种格式内容一致且符合各自的格式规范，执行完后调用interactive-feedback-mcp等待我的反馈",
                "looks_good_feedback": "看起来不错，继续按照当前方向实施。",
                "needs_adjustment_feedback": "基本方向正确，但需要一些小的调整和优化。",
                "reimplemented_feedback": "当前实现不符合预期，请重新分析需求并实现。",

                "fix_issues_feedback": "发现了一些问题，请仔细检查并修复。",
                "complete_feedback": "",
                
                # 编辑对话框新增翻译
                "language_settings": "语言设置",
                "chinese": "中文",
                "english": "English",
                "edit_quick_button": "编辑快捷按钮",
                
                # 图片上传相关文本
                "drag_drop_images": "拖拽图片到此处或点击选择文件",
                "paste_screenshot_hint": "或按 Ctrl+V 粘贴截图",
                "select_images": "选择图片",
                "image_process_error": "图片处理错误",
                "warning": "警告",
                "no_valid_images": "没有找到有效的图片文件",
                "info": "信息",
                "no_image_in_clipboard": "剪贴板中没有图片",
                "image_upload": "图片上传",
                "supported_formats": "支持的格式: PNG, JPG, JPEG, GIF, BMP, WebP",
                "max_size_hint": "最大文件大小: 1MB，超过将自动压缩",
                
                # 图片传输选项相关
                "image_transmission_options": "图片传输选项",
                "enable_base64_transmission": "启用Base64传输",
                "base64_transmission_tooltip": "启用后将图片优化压缩为Base64格式传输，AI可直接识别内容，但会增加token消耗",
                "target_size": "目标大小:",
                
                # 临时图片清理相关
                "cleanup_temp_images_dialog": "清理临时图片",
                "temp_images_info": "临时图片信息",
                "temp_dir_path": "临时目录路径",
                "total_files": "文件总数",
                "total_size": "总大小",
                "cleanup_options": "清理选项",
                "cleanup_days": "清理天数前的文件",
                "cleanup_all": "清理所有文件",
                "preview_mode": "预览模式（不实际删除）",
                "start_cleanup": "开始清理",
                "cleanup_success": "清理完成",
                "cleanup_failed": "清理失败",
                "no_temp_files": "没有临时文件",
            },
            "en_US": {
                # Window title
                "window_title": "Interactive Feedback MCP",
                
                # Button text
                "show_command_section": "Show Command Section",
                "hide_command_section": "Hide Command Section",
                "run": "&Run",
                "stop": "Sto&p",
                "clear": "&Clear",
                "save_configuration": "&Save Configuration",
                "tools_menu": "🔧 Tools",
                "tools_menu_tooltip": "Open tools menu",
                "cleanup_temp_images": "🗑️ Cleanup Temp Images",
                "send_feedback": "&Send Feedback (Ctrl+Enter)",
                "edit_quick_buttons": "Edit Quick Buttons",
                
                # Checkboxes and labels
                "execute_automatically": "Execute automatically on next run",
                "working_directory": "Working directory",
                "command": "Command",
                "console": "Console",
                "feedback": "Feedback",
                
                # Feedback suffix options
                "feedback_suffix_options": "Feedback Suffix Options",
                "force_mcp_call": "Force MCP Call",
                "smart_judgment": "Smart Judgment",
                "no_special_append": "No Special Append",
                "force_mcp_tooltip": "Need to call interactive-feedback-mcp after execution to wait for my feedback",
                "smart_judgment_tooltip": "Determine whether to call interactive-feedback-mcp after execution based on the situation",
                "no_append_tooltip": "Do not append any MCP call instructions after feedback content",
                

                
                # Quick buttons
                "complete_all_checklist": "📋 Complete All Checklist",
                "smart_execute_checklist": "🎯 Smart Execute Checklist",
                "execute_next_item": "➡️ Execute Next Item",
                # 移除regenerate_checklist（与complete_all_checklist功能重叠）
                # "regenerate_checklist": "🔄 Regenerate Checklist",
                "complete_and_record": "📝 Complete and Record",
                "summarize_to_cursorrule": "📋 Generate Rule Files",
                "looks_good": "✅ Looks Good",
                "needs_adjustment": "🔧 Needs Adjustment",
                # 移除reimplemented和fix_issues（与needs_adjustment功能重叠）
                # "reimplemented": "🔄 Re-implement",
                # "fix_issues": "🐛 Fix Issues",
                "complete": "✨ Complete",
                
                # Dialogs
                "edit_quick_buttons_dialog": "Edit Quick Buttons",
                "button_size_settings": "Button Size Settings",
                "small": "Small (100x30)",
                "medium": "Medium (120x40)",
                "large": "Large (150x45)",
                "custom": "Custom",
                "width": "Width",
                "height": "Height",
                "add": "Add",
                "delete": "Delete",
                "move_up": "Move Up",
                "move_down": "Move Down",
                "reset_to_default": "Reset to Default",
                "ok": "OK",
                "cancel": "Cancel",
                "confirm_delete": "Confirm Delete",
                "confirm_delete_message": "Are you sure you want to delete this quick button?",
                "confirm_reset": "Confirm Reset",
                "confirm_reset_message": "Are you sure you want to reset to default quick buttons? This will lose all custom configurations.",
                "reset_options": "Reset Options",
                "reset_options_message": "Custom buttons detected. Please choose reset method:",
                "reset_options_info": "• Reset defaults only: Update default buttons to latest version, keep your custom buttons\n• Reset all: Delete all buttons and restore to default configuration",
                "reset_defaults_only": "Reset Defaults Only",
                "reset_all_buttons": "Reset All",
                "edit_instruction": "Double-click list item to edit, or use buttons below to add/delete buttons",
                "button_text": "Button Text:",
                "feedback_content": "Feedback Content:",
                "placeholder_width": "Width",
                "placeholder_height": "Height",
                "placeholder_feedback": "Enter your feedback here (Ctrl+Enter to submit)",
                
                # Messages
                "configuration_saved": "Configuration saved for this project.\n",
                "please_enter_command": "Please enter a command to run\n",
                "process_exited": "Process exited with code",
                "error_running_command": "Error running command",
                
                # Suffix text
                "suffix_force": ", need to call interactive-feedback-mcp after execution to wait for my feedback",
                "suffix_smart": ", determine whether to call interactive-feedback-mcp after execution based on the situation",
                

                
                # RIPER-5 Protocol Mode Feedback Content
                "riper_research_feedback": "Please enter RESEARCH mode, conduct deep analysis of the current problem, systematically break down technical components, identify key constraints and requirements, but do not provide solution suggestions. Determine whether to call interactive-feedback-mcp after execution based on the situation.",
                "riper_innovate_feedback": "Please enter INNOVATE mode, brainstorm based on research results, explore multiple solutions, evaluate pros and cons of each approach, but do not create specific plans. Determine whether to call interactive-feedback-mcp after execution based on the situation.",
                "riper_plan_feedback": "Please enter PLAN mode, create detailed technical specifications and implementation plans, mark each step with review:true/false, generate complete checklist. Determine whether to call interactive-feedback-mcp after execution based on the situation.",
                "riper_execute_feedback": "Please enter EXECUTE mode, strictly follow the plan, launch MCP interactive feedback for review:true steps, request confirmation after completion. Determine whether to call interactive-feedback-mcp after execution based on the situation.",
                "riper_review_feedback": "Please enter REVIEW mode, comprehensively verify implementation results against original requirements, obtain final feedback through MCP interactive_feedback. Determine whether to call interactive-feedback-mcp after execution based on the situation.",
                
                # RIPER-5 Full Rules Buttons (User-friendly version)
                "riper_research_full": "🔍 Analyze Problem",
                "riper_innovate_full": "💡 Find Solutions",
                "riper_plan_full": "📋 Create Plan",
                "riper_execute_full": "⚡ Execute Steps",
                "riper_review_full": "🎯 Verify Results",
                
                # Quick button feedback content
                "complete_all_feedback": "Complete all remaining checklist items, call interactive-feedback-mcp when done",
                "smart_execute_feedback": "Execute remaining checklist items, call interactive-feedback-mcp if needed",
                "execute_next_feedback": "Execute next checklist item, call interactive-feedback-mcp after completion",
                # 移除regenerate_feedback（功能重叠）
                # "regenerate_feedback": "Regenerate checklist and update markdown, call interactive-feedback-mcp when done",
                "complete_record_feedback": "Complete all items and document results, call interactive-feedback-mcp when finished",
                "summarize_cursorrule_feedback": "Please summarize the key content of current conversation, extract core rules and best practices, and generate or update both rule file formats: 1) Traditional .cursorrules file (backward compatibility) 2) New standard .cursor/rules/main.mdc file (recommended format). Ensure both formats have consistent content and follow their respective format specifications. Call interactive-feedback-mcp after execution for feedback.",
                "looks_good_feedback": "LGTM! Continue as planned.",
                "needs_adjustment_feedback": "Good direction, but needs minor tweaks.",
                # 移除重复的反馈内容
                # "reimplemented_feedback": "Please re-analyze and re-implement.",
                # "fix_issues_feedback": "Fix the issues found.",
                "complete_feedback": "",
                
                # 编辑对话框新增翻译
                "language_settings": "Language Settings",
                "chinese": "中文",
                "english": "English",
                "edit_quick_button": "Edit Quick Button",
                
                # 图片上传相关文本
                "drag_drop_images": "Drag & drop images here or click to select files",
                "paste_screenshot_hint": "or press Ctrl+V to paste screenshot",
                "select_images": "Select Images",
                "image_process_error": "Image Processing Error",
                "warning": "Warning",
                "no_valid_images": "No valid image files found",
                "info": "Information",
                "no_image_in_clipboard": "No image in clipboard",
                "image_upload": "Image Upload",
                "supported_formats": "Supported formats: PNG, JPG, JPEG, GIF, BMP, WebP",
                "max_size_hint": "Max file size: 1MB, larger files will be auto-compressed",
                
                # Image transmission options related
                "image_transmission_options": "Image Transmission Options",
                "enable_base64_transmission": "Enable Base64 Transmission",
                "base64_transmission_tooltip": "When enabled, images will be optimized and compressed to Base64 format for transmission. AI can directly recognize content, but will increase token consumption",
                "target_size": "Target Size:",
                
                # Temp images cleanup related
                "cleanup_temp_images_dialog": "Cleanup Temp Images",
                "temp_images_info": "Temp Images Info",
                "temp_dir_path": "Temp Directory Path",
                "total_files": "Total Files",
                "total_size": "Total Size",
                "cleanup_options": "Cleanup Options",
                "cleanup_days": "Cleanup files older than (days)",
                "cleanup_all": "Cleanup all files",
                "preview_mode": "Preview mode (don't actually delete)",
                "start_cleanup": "Start Cleanup",
                "cleanup_success": "Cleanup Completed",
                "cleanup_failed": "Cleanup Failed",
                "no_temp_files": "No temp files found",
            }
        }
    
    def t(self, key, default=None):
        """获取翻译文本"""
        return self.translations.get(self.language, {}).get(key, default or key)
    
    def set_language(self, language):
        """设置语言"""
        if language in self.translations:
            self.language = language
            return True
        return False
    
    def get_available_languages(self):
        """获取可用语言列表"""
        return list(self.translations.keys())

# 全局国际化实例
i18n = I18n() 