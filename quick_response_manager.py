"""
快捷按钮管理模块 - 负责快捷按钮的创建、布局和管理
"""
import os
from functools import partial
from typing import List, Tuple, Dict, Any
from PySide6.QtWidgets import QPushButton, QGridLayout, QWidget
from PySide6.QtCore import QTimer
from i18n import i18n


class QuickResponseManager:
    """快捷按钮管理器"""
    
    def __init__(self, parent_ui):
        self.parent_ui = parent_ui
        self.quick_response_buttons = []
        
        # 性能优化基础设施
        self._ui_update_cache = {}  # 缓存布局计算结果
        self._delayed_layout_timer = None  # 延迟布局更新定时器
        self._is_batch_updating = False  # 批量更新状态标志
        self._pending_layout_update = False  # 待处理的布局更新标志
        
        # 性能监控
        self._performance_stats = {
            "button_rebuilds": 0,
            "incremental_updates": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "batch_updates": 0
        }
        
    def get_default_quick_responses(self, config):
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

    def get_smart_default_responses(self, config):
        """获取统一的默认快捷按钮（不区分项目类型）"""
        # 统一提供默认配置，不再根据项目类型区分
        return self.get_default_quick_responses(config)

    def _extract_mode_rules_from_cursor_rule(self):
        """从RIPER-5-cursor-rule.txt文件中提取模式规则"""
        cursor_rule_path = os.path.join(os.path.dirname(__file__), "RIPER-5-cursor-rule.txt")
        mode_rules = {}
        
        if not os.path.exists(cursor_rule_path):
            return mode_rules
        
        try:
            with open(cursor_rule_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找各个模式的规则
            modes = ["RESEARCH", "INNOVATE", "PLAN", "EXECUTE", "REVIEW"]
            
            for mode in modes:
                # 查找模式标题
                mode_start = content.find(f"### 模式{modes.index(mode)+1}: {mode}")
                if mode_start == -1:
                    mode_start = content.find(f"模式{modes.index(mode)+1}: {mode}")
                
                if mode_start != -1:
                    # 查找下一个模式的开始位置
                    next_mode_start = len(content)
                    for next_mode in modes[modes.index(mode)+1:]:
                        next_start = content.find(f"### 模式{modes.index(next_mode)+1}: {next_mode}", mode_start + 1)
                        if next_start == -1:
                            next_start = content.find(f"模式{modes.index(next_mode)+1}: {next_mode}", mode_start + 1)
                        if next_start != -1:
                            next_mode_start = min(next_mode_start, next_start)
                    
                    # 提取模式内容
                    mode_content = content[mode_start:next_mode_start]
                    
                    # 构建模式指令
                    mode_instruction = f"请进入{mode}模式，严格按照以下规则执行：\n\n{mode_content.strip()}"
                    mode_rules[mode] = mode_instruction
        
        except Exception:
            # 如果读取失败，返回默认的模式指令
            for mode in ["RESEARCH", "INNOVATE", "PLAN", "EXECUTE", "REVIEW"]:
                mode_rules[mode] = f"请进入{mode}模式并按照RIPER-5协议执行。"
        
        return mode_rules

    def get_button_size(self, config):
        """根据配置获取按钮尺寸"""
        button_size = config.get("button_size", "medium")
        
        if button_size == "small":
            return {"width": 100, "height": 30}
        elif button_size == "large":
            return {"width": 150, "height": 45}
        elif button_size == "custom":
            return {
                "width": config.get("custom_button_width", 120),
                "height": config.get("custom_button_height", 40)
            }
        else:  # medium (default)
            return {"width": 120, "height": 40}

    def get_layout_cache_key(self, config, quick_responses):
        """生成布局缓存键"""
        visible_buttons = config.get("visible_buttons", [])
        button_size = config.get("button_size", "medium")
        custom_width = config.get("custom_button_width", 120)
        custom_height = config.get("custom_button_height", 40)
        
        return f"{len(visible_buttons)}_{button_size}_{custom_width}_{custom_height}_{len(quick_responses)}"

    def get_cached_button_layout(self, config, quick_responses):
        """获取缓存的按钮布局计算结果"""
        cache_key = self.get_layout_cache_key(config, quick_responses)
        
        if cache_key not in self._ui_update_cache:
            self._performance_stats["cache_misses"] += 1
            # 计算布局参数
            visible_buttons = config.get("visible_buttons", list(range(len(quick_responses))))
            visible_count = len([i for i in range(len(quick_responses)) if i in visible_buttons])
            
            # 智能布局计算
            if visible_count <= 4:
                buttons_per_row = visible_count
            elif visible_count <= 8:
                buttons_per_row = 4
            elif visible_count <= 12:
                buttons_per_row = 4
            else:
                buttons_per_row = 5
            
            button_size = self.get_button_size(config)
            
            # 缓存结果
            self._ui_update_cache[cache_key] = {
                "visible_count": visible_count,
                "buttons_per_row": buttons_per_row,
                "button_size": button_size,
                "visible_buttons": visible_buttons.copy()
            }
        else:
            self._performance_stats["cache_hits"] += 1
        
        return self._ui_update_cache[cache_key]

    def clear_layout_cache(self):
        """清理布局缓存"""
        self._ui_update_cache.clear()

    def create_quick_response_buttons(self, quick_response_widget, config, quick_responses, on_click_callback):
        """创建快捷回复按钮"""
        quick_response_layout = quick_response_widget.layout()
        
        # 获取布局信息
        layout_info = self.get_cached_button_layout(config, quick_responses)
        button_size = layout_info["button_size"]
        visible_buttons = layout_info["visible_buttons"]
        buttons_per_row = layout_info["buttons_per_row"]
        
        # 清除现有按钮
        for button in self.quick_response_buttons:
            button.deleteLater()
        self.quick_response_buttons.clear()
        
        # 清除布局中的所有项目
        while quick_response_layout.count() > 0:
            child = quick_response_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        row = 0
        col = 0
        
        for index, (button_text, response_text) in enumerate(quick_responses):
            if index in visible_buttons:
                button = QPushButton(button_text)
                button.setMinimumHeight(button_size["height"] - 5)
                button.setMaximumHeight(button_size["height"])
                button.setMinimumWidth(button_size["width"])
                button.clicked.connect(partial(on_click_callback, response_text))
                self.quick_response_buttons.append(button)
                quick_response_layout.addWidget(button, row, col)
                
                col += 1
                if col >= buttons_per_row:
                    col = 0
                    row += 1
        
        return row, col, button_size

    def need_full_button_rebuild(self, layout_info):
        """检查是否需要完全重建按钮"""
        # 如果按钮数量发生变化，需要重建
        if len(self.quick_response_buttons) != layout_info["visible_count"]:
            return True
        
        # 如果按钮尺寸发生变化，需要重建
        if hasattr(self, '_last_button_size'):
            if self._last_button_size != layout_info["button_size"]:
                return True
        else:
            self._last_button_size = layout_info["button_size"]
            return True
        
        return False

    def update_buttons_incrementally(self, quick_response_widget, layout_info):
        """增量更新按钮（仅更新文本和状态）"""
        self._performance_stats["incremental_updates"] += 1
        
        # 更新按钮文本
        for i, button in enumerate(self.quick_response_buttons):
            if i < len(self.parent_ui.quick_responses):
                button_text, _ = self.parent_ui.quick_responses[i]
                if button.text() != button_text:
                    button.setText(button_text)
        
        return True

    def get_performance_stats(self):
        """获取性能统计信息（用于调试）"""
        return self._performance_stats.copy()

    def is_default_button(self, button_text, response_text, index):
        """判断按钮是否为默认按钮"""
        from ui_config import is_default_button
        return is_default_button(button_text, response_text) 