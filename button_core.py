"""
按钮核心逻辑模块 - 负责快捷按钮的刷新、重建和增量更新
"""
from functools import partial
from PySide6.QtWidgets import QPushButton, QGridLayout


class ButtonCoreManager:
    """按钮核心逻辑管理器"""
    
    def __init__(self, parent_ui):
        self.parent_ui = parent_ui
        self._last_button_size = None
    
    def refresh_quick_response_buttons(self):
        """刷新快捷按钮UI（优化版本 - 增量更新）"""
        # 防止初始化期间重复调用
        if getattr(self.parent_ui, '_is_initializing', False):
            return
            
        def update_buttons():
            # 获取缓存的布局信息
            layout_info = self.parent_ui.quick_response_manager.get_cached_button_layout(
                self.parent_ui.config, self.parent_ui.quick_responses
            )
            
            # 获取快捷按钮widget
            feedback_layout = self.parent_ui.feedback_group.layout()
            quick_response_widget = None
            
            # 找到快捷按钮widget（第二个widget，第一个是描述标签）
            for i in range(feedback_layout.count()):
                item = feedback_layout.itemAt(i)
                if item and item.widget() and isinstance(item.widget().layout(), QGridLayout):
                    quick_response_widget = item.widget()
                    break
            
            if not quick_response_widget:
                return False
                
            # 检查是否需要完全重建（布局参数改变）
            if self._need_full_button_rebuild(layout_info):
                return self._rebuild_all_buttons(quick_response_widget, layout_info)
            else:
                return self._update_buttons_incrementally(quick_response_widget, layout_info)
        
        # 使用批量更新
        self.parent_ui.performance_manager.batch_ui_updates(update_buttons)
    
    def _need_full_button_rebuild(self, layout_info):
        """检查是否需要完全重建按钮"""
        # 如果按钮数量发生变化，需要重建
        if len(self.parent_ui.quick_response_buttons) != layout_info["visible_count"]:
            return True
        
        # 如果按钮尺寸发生变化，需要重建
        if hasattr(self, '_last_button_size'):
            if self._last_button_size != layout_info["button_size"]:
                return True
        else:
            self._last_button_size = layout_info["button_size"]
            return True
        
        return False
    
    def _rebuild_all_buttons(self, quick_response_widget, layout_info):
        """完全重建所有按钮"""
        self.parent_ui.performance_manager.increment_stat("button_rebuilds")
        quick_response_layout = quick_response_widget.layout()
        
        # 清除现有按钮
        for button in self.parent_ui.quick_response_buttons:
            button.deleteLater()
        self.parent_ui.quick_response_buttons.clear()
        
        # 清除布局中的所有项目
        while quick_response_layout.count() > 0:
            child = quick_response_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # 重新创建快捷按钮
        button_size = layout_info["button_size"]
        visible_buttons = layout_info["visible_buttons"]
        buttons_per_row = layout_info["buttons_per_row"]
        
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
        
        # 重新添加编辑按钮（固定在右下角）
        edit_button = QPushButton("⚙️")
        edit_button.setMinimumHeight(button_size["height"] - 5)
        edit_button.setMaximumHeight(button_size["height"])
        edit_button.setMinimumWidth(int(button_size["width"] * 0.4))
        edit_button.setMaximumWidth(int(button_size["width"] * 0.5))
        edit_button.setToolTip("编辑快捷按钮")
        edit_button.clicked.connect(self.parent_ui._edit_quick_responses)
        
        # 计算编辑按钮应该放置的位置（右下角）
        max_row = row if col > 0 else max(0, row - 1)
        max_col = buttons_per_row - 1
        quick_response_layout.addWidget(edit_button, max_row, max_col + 1)
        
        # 更新缓存的按钮尺寸
        self._last_button_size = button_size
        
        return True
    
    def _update_buttons_incrementally(self, quick_response_widget, layout_info):
        """增量更新按钮（仅更新文本和可见性）"""
        self.parent_ui.performance_manager.increment_stat("incremental_updates")
        visible_buttons = layout_info["visible_buttons"]
        
        # 更新现有按钮的文本
        visible_index = 0
        for index, (button_text, response_text) in enumerate(self.parent_ui.quick_responses):
            if index in visible_buttons and visible_index < len(self.parent_ui.quick_response_buttons):
                button = self.parent_ui.quick_response_buttons[visible_index]
                if button.text() != button_text:
                    button.setText(button_text)
                    # 重新连接信号（如果响应文本改变了）
                    button.clicked.disconnect()
                    button.clicked.connect(partial(self.parent_ui._on_quick_response_clicked, response_text))
                visible_index += 1
        
        return True
    
    def adjust_window_size(self):
        """调整窗口大小以适应新的按钮配置（优化版本）"""
        def adjust_size():
            # 使用缓存的布局信息
            layout_info = self.parent_ui.quick_response_manager.get_cached_button_layout(
                self.parent_ui.config, self.parent_ui.quick_responses
            )
            button_size = layout_info["button_size"]
            visible_count = layout_info["visible_count"]
            buttons_per_row = layout_info["buttons_per_row"]
            
            # 更新反馈组的最小高度
            self.parent_ui.feedback_group.setMinimumHeight(
                self.parent_ui.description_label.sizeHint().height() + 
                button_size["height"] + 15 +  # 按钮高度加边距
                self.parent_ui.feedback_text.minimumHeight() + 
                80 +  # 后缀选项组的大概高度
                40 +  # 提交按钮高度
                60    # 额外边距
            )
            
            # 计算窗口宽度（包含编辑按钮）
            actual_buttons_per_row = min(buttons_per_row, visible_count)
            estimated_width = max(800, actual_buttons_per_row * (button_size["width"] + 10) + 100)
            
            # 让窗口根据内容自动调整大小
            self.parent_ui.adjustSize()
            
            # 设置新的窗口大小
            current_size = self.parent_ui.size()
            new_width = max(estimated_width, current_size.width())
            new_height = max(500, current_size.height())
            
            # 调整窗口大小
            self.parent_ui.resize(new_width, new_height)
            
            # 居中显示窗口
            self._center_window()
            
            return True
        
        # 使用批量更新和延迟布局更新
        self.parent_ui.performance_manager.batch_ui_updates(adjust_size)
        self.parent_ui.performance_manager.schedule_layout_update()
    
    def _center_window(self):
        """将窗口居中显示"""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.parent_ui.geometry()
        x = (screen.width() - window_geometry.width()) // 2
        y = (screen.height() - window_geometry.height()) // 2
        self.parent_ui.move(x, y) 