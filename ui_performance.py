"""
UI性能优化模块 - 负责UI性能优化和缓存管理
"""
from PySide6.QtCore import QTimer


class UIPerformanceManager:
    """UI性能优化管理器"""
    
    def __init__(self, parent_ui):
        self.parent_ui = parent_ui
        
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
    
    def batch_ui_updates(self, func):
        """批量处理UI更新的装饰器方法"""
        if self._is_batch_updating:
            # 如果已经在批量更新中，直接执行
            return func()
            
        self._is_batch_updating = True
        self._performance_stats["batch_updates"] += 1
        self.parent_ui.setUpdatesEnabled(False)
        try:
            result = func()
            return result
        finally:
            self._is_batch_updating = False
            self.parent_ui.setUpdatesEnabled(True)
            # 强制重绘一次
            self.parent_ui.update()
    
    def schedule_layout_update(self):
        """延迟布局更新，避免频繁重计算"""
        self._pending_layout_update = True
        
        if not self._delayed_layout_timer:
            self._delayed_layout_timer = QTimer()
            self._delayed_layout_timer.setSingleShot(True)
            self._delayed_layout_timer.timeout.connect(self._execute_delayed_layout_update)
        
        # 重启定时器，延迟50ms执行
        self._delayed_layout_timer.start(50)
    
    def _execute_delayed_layout_update(self):
        """执行延迟的布局更新"""
        if self._pending_layout_update and not self._is_batch_updating:
            self._pending_layout_update = False
            self._do_layout_update()
    
    def _do_layout_update(self):
        """实际执行布局更新"""
        def update_func():
            self.parent_ui.centralWidget().updateGeometry()
            self.parent_ui.centralWidget().layout().invalidate()
            self.parent_ui.centralWidget().layout().activate()
            return True
        
        return self.batch_ui_updates(update_func)
    

    
    def _get_button_size(self, config):
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
    
    def clear_layout_cache(self):
        """清理布局缓存"""
        self._ui_update_cache.clear()
    
    def get_performance_stats(self):
        """获取性能统计信息（用于调试）"""
        return self._performance_stats.copy()
    
    def log_performance_stats(self):
        """输出性能统计到日志（用于调试）"""
        stats = self.get_performance_stats()
        cache_hit_rate = 0
        if stats["cache_hits"] + stats["cache_misses"] > 0:
            cache_hit_rate = stats["cache_hits"] / (stats["cache_hits"] + stats["cache_misses"]) * 100
        
        perf_log = f"""
=== UI Performance Statistics ===
Button rebuilds: {stats['button_rebuilds']}
Incremental updates: {stats['incremental_updates']}
Cache hits: {stats['cache_hits']}
Cache misses: {stats['cache_misses']}
Cache hit rate: {cache_hit_rate:.1f}%
Batch updates: {stats['batch_updates']}
================================"""
        
        if hasattr(self.parent_ui, '_append_log'):
            self.parent_ui._append_log(perf_log)
    
    def increment_stat(self, stat_name):
        """增加统计计数"""
        if stat_name in self._performance_stats:
            self._performance_stats[stat_name] += 1
    
    @property
    def is_batch_updating(self):
        """获取批量更新状态"""
        return self._is_batch_updating 