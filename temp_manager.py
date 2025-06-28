#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时文件管理模块
统一管理 interactive-feedback-mcp 的临时图片文件
"""

import os
from typing import Optional
from config import TEMP_DIR_NAME, CLIPBOARD_FILE_PREFIX, DEFAULT_IMAGE_EXTENSION


class TempManager:
    """临时文件管理器"""
    
    # 使用配置文件中的常量
    TEMP_DIR_NAME = TEMP_DIR_NAME
    
    def __init__(self):
        self._temp_dir = None
    
    @property
    def temp_dir(self) -> str:
        """获取临时目录路径"""
        if self._temp_dir is None:
            self._temp_dir = os.path.join(os.path.expanduser('~'), self.TEMP_DIR_NAME)
        return self._temp_dir
    
    def ensure_temp_dir(self) -> str:
        """确保临时目录存在，如果不存在则创建"""
        temp_dir = self.temp_dir
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
    
    def get_temp_file_path(self, filename: str) -> str:
        """获取临时文件的完整路径"""
        self.ensure_temp_dir()
        return os.path.join(self.temp_dir, filename)
    
    def generate_temp_filename(self, prefix: str = 'temp', suffix: str = DEFAULT_IMAGE_EXTENSION) -> str:
        """生成临时文件名"""
        import time
        timestamp = int(time.time() * 1000)
        return f'{prefix}_{timestamp}{suffix}'
    
    def cleanup_temp_dir(self, days_old: int = 7, dry_run: bool = False) -> dict:
        """
        清理临时目录中的旧文件
        
        Args:
            days_old: 清理多少天前的文件
            dry_run: 是否为预览模式
            
        Returns:
            清理结果统计
        """
        from datetime import datetime, timedelta
        
        temp_dir = self.temp_dir
        if not os.path.exists(temp_dir):
            return {
                'status': 'no_directory',
                'message': f'临时目录不存在: {temp_dir}',
                'deleted_files': 0,
                'total_size': 0
            }
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        deleted_files = []
        total_size = 0
        
        try:
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                
                if not os.path.isfile(file_path):
                    continue
                
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_mtime < cutoff_date:
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    
                    if not dry_run:
                        os.remove(file_path)
                    
                    deleted_files.append({
                        'name': filename,
                        'path': file_path,
                        'size': file_size,
                        'mtime': file_mtime.strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        except Exception as e:
            return {
                'status': 'error',
                'message': f'清理过程中出错: {str(e)}',
                'deleted_files': 0,
                'total_size': 0
            }
        
        return {
            'status': 'success',
            'message': f'{"预览" if dry_run else "清理"}完成',
            'deleted_files': len(deleted_files),
            'total_size': total_size,
            'files': deleted_files,
            'temp_dir': temp_dir
        }


# 全局实例
temp_manager = TempManager()

# 便捷函数
def get_temp_images_dir() -> str:
    """获取临时图片目录路径"""
    return temp_manager.temp_dir

def ensure_temp_images_dir() -> str:
    """确保临时图片目录存在"""
    return temp_manager.ensure_temp_dir()

def get_temp_file_path(filename: str) -> str:
    """获取临时文件路径"""
    return temp_manager.get_temp_file_path(filename)

def generate_clipboard_filename() -> str:
    """生成剪贴板图片文件名"""
    return temp_manager.generate_temp_filename(CLIPBOARD_FILE_PREFIX, DEFAULT_IMAGE_EXTENSION) 