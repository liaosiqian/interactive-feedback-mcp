#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置常量文件
统一管理 interactive-feedback-mcp 的配置常量
"""

import os

# 临时文件相关配置
TEMP_DIR_NAME = '.interactive_feedback_temp_images'
TEMP_DIR_PATH = os.path.join(os.path.expanduser('~'), TEMP_DIR_NAME)

# 图片处理相关配置
SUPPORTED_IMAGE_FORMATS = {
    'PNG': 'image/png',
    'JPEG': 'image/jpeg', 
    'JPG': 'image/jpeg',
    'GIF': 'image/gif',
    'BMP': 'image/bmp',
    'WEBP': 'image/webp'
}

# 图片大小限制
MAX_FILE_SIZE = 1024 * 1024  # 1MB
MAX_DIMENSION = 2048

# 文件命名模式
CLIPBOARD_FILE_PREFIX = 'clipboard'
TEMP_FILE_PREFIX = 'temp'
DEFAULT_IMAGE_EXTENSION = '.png'

# 清理配置
DEFAULT_CLEANUP_DAYS = 7
CLEANUP_BATCH_SIZE = 100  # 每次清理的最大文件数

# UI配置
DEFAULT_LANGUAGE = 'zh_CN'
AVAILABLE_LANGUAGES = ['zh_CN', 'en_US']

# 应用信息
APP_NAME = 'Interactive Feedback MCP'
APP_VERSION = '1.0.0'
SETTINGS_ORGANIZATION = 'InteractiveFeedbackMCP' 