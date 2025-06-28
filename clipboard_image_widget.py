from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QScrollArea, QPushButton, QMessageBox)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QPixmap, QGuiApplication
import os
from typing import List, Dict, Optional
from image_handler import ImageHandler
from i18n import i18n
from temp_manager import ensure_temp_images_dir, generate_clipboard_filename, get_temp_file_path

class ImageProcessingThread(QThread):
    """图片处理线程"""
    finished = Signal(dict)  # 处理完成信号
    progress = Signal(int)   # 进度信号
    
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.image_handler = ImageHandler()
    
    def run(self):
        """处理图片"""
        try:
            self.progress.emit(50)
            result = self.image_handler.process_image(self.file_path)
            self.progress.emit(100)
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({
                'success': False,
                'error': f'处理失败: {str(e)}'
            })

class ImagePreviewWidget(QFrame):
    """图片预览组件"""
    remove_requested = Signal(str)  # 请求删除图片信号
    
    def __init__(self, image_data: dict, parent=None):
        super().__init__(parent)
        self.image_data = image_data
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI - 适应新布局的预览组件"""
        self.setFrameStyle(QFrame.Box)
        self.setFixedSize(45, 45)  # 适中的尺寸
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(1)
        
        # 图片预览 - 适中的尺寸
        self.image_label = QLabel()
        self.image_label.setFixedSize(36, 28)  # 适中尺寸
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ddd;
                background-color: #f9f9f9;
                border-radius: 3px;
            }
        """)
        
        # 设置图片 - 直接从文件路径加载，不使用Base64
        image_path = None
        if 'original_path' in self.image_data:
            image_path = self.image_data['original_path']
        elif 'clipboard_path' in self.image_data:
            image_path = self.image_data['clipboard_path']
        elif 'processed_path' in self.image_data:
            image_path = self.image_data['processed_path']
        
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(34, 26, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
        
        # 删除按钮 - 适中尺寸
        self.remove_btn = QPushButton("×")
        self.remove_btn.setFixedSize(14, 14)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 7px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        self.remove_btn.clicked.connect(self.request_remove)
        
        # 布局
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.remove_btn, alignment=Qt.AlignCenter)
    

    
    def request_remove(self):
        """请求删除图片"""
        self.remove_requested.emit(self.image_data.get('id', ''))

class ClipboardImageWidget(QWidget):
    """剪贴板图片上传组件 - 简化版本，只支持剪贴板粘贴"""
    images_changed = Signal(list)  # 图片列表变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.uploaded_images = []  # 存储上传的图片数据
        self.image_handler = ImageHandler()
        self.processing_thread = None
        self.is_processing = False  # 防止重复处理标志
        self.setup_ui()
        # 设置焦点策略以接收键盘事件
        self.setFocusPolicy(Qt.StrongFocus)
    
    def setup_ui(self):
        """设置UI - 改回垂直布局，但保持紧凑设计"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)  # 减少间距
        
        # 粘贴提示区域 - 紧凑设计，但保持全宽
        self.paste_area = QFrame()
        self.paste_area.setFrameStyle(QFrame.StyledPanel)
        self.paste_area.setStyleSheet("""
            QFrame {
                border: 2px dashed #ccc;
                border-radius: 6px;
                background-color: #fafafa;
                min-height: 40px;
                max-height: 40px;
            }
            QFrame:hover {
                border-color: #007acc;
                background-color: #f0f8ff;
            }
        """)
        
        paste_layout = QHBoxLayout(self.paste_area)
        paste_layout.setContentsMargins(8, 4, 8, 4)
        
        # 粘贴提示文本 - 更简洁
        self.paste_label = QLabel("📋 " + i18n.t("paste_screenshot_hint"))
        self.paste_label.setAlignment(Qt.AlignCenter)
        self.paste_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 12px;
                border: none;
                background: transparent;
            }
        """)
        
        paste_layout.addWidget(self.paste_label)
        
        # 图片预览区域 - 水平滚动，更紧凑
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setFixedHeight(50)  # 进一步减少高度
        self.preview_scroll.setVisible(False)
        self.preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.preview_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.preview_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #fafafa;
            }
        """)
        
        self.preview_widget = QWidget()
        self.preview_layout = QHBoxLayout(self.preview_widget)
        self.preview_layout.setContentsMargins(2, 2, 2, 2)
        self.preview_layout.setSpacing(2)
        self.preview_scroll.setWidget(self.preview_widget)
        
        # 添加到主布局 - 垂直排列
        layout.addWidget(self.paste_area)
        layout.addWidget(self.preview_scroll)
    
    def keyPressEvent(self, event):
        """处理键盘事件（剪贴板粘贴）"""
        if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            self.paste_from_clipboard()
        super().keyPressEvent(event)
    
    def paste_from_clipboard(self):
        """从剪贴板粘贴图片，使用统一的临时目录管理"""
        # 防止重复处理
        if self.is_processing:
            return
        
        self.is_processing = True
        
        try:
            clipboard = QGuiApplication.clipboard()
            mime_data = clipboard.mimeData()
            
            # 统一的剪贴板图片处理逻辑
            image_source = None
            if mime_data.hasImage():
                image_source = clipboard.image()
            elif not clipboard.pixmap().isNull():
                image_source = clipboard.pixmap()
            
            if image_source and not image_source.isNull():
                try:
                    # 使用统一的临时目录管理
                    ensure_temp_images_dir()
                    filename = generate_clipboard_filename()
                    clipboard_path = get_temp_file_path(filename)
                    
                    # 保存图片
                    if image_source.save(clipboard_path, "PNG"):
                        self.process_image(clipboard_path)
                        # 显示成功提示
                        self.paste_label.setText("✅ 已粘贴图片，正在处理...")
                        QTimer.singleShot(2000, lambda: self.paste_label.setText("📋 " + i18n.t("paste_screenshot_hint")))
                    else:
                        QMessageBox.warning(self, i18n.t("warning"), "无法保存剪贴板图片")
                except Exception as e:
                    QMessageBox.warning(self, i18n.t("warning"), f"处理剪贴板图片时出错: {str(e)}")
            else:
                QMessageBox.information(self, i18n.t("info"), i18n.t("no_image_in_clipboard"))
        finally:
            # 延迟重置处理标志，防止快速重复点击
            QTimer.singleShot(500, lambda: setattr(self, 'is_processing', False))
    
    def process_image(self, file_path: str):
        """处理单个图片"""
        if not file_path:
            return
        
        # 创建处理线程
        self.processing_thread = ImageProcessingThread(file_path, self)
        self.processing_thread.finished.connect(self.on_image_processed)
        self.processing_thread.start()
    
    def on_image_processed(self, result: dict):
        """图片处理完成"""
        try:
            if result['success']:
                # 添加唯一ID
                result['id'] = f"clipboard_img_{len(self.uploaded_images)}"
                self.uploaded_images.append(result)
                self.update_preview()
                self.images_changed.emit(self.uploaded_images)
            else:
                # 显示错误信息
                QMessageBox.warning(
                    self, 
                    i18n.t("image_process_error"), 
                    result['error']
                )
            
            # 清理当前线程
            if self.processing_thread:
                self.processing_thread.deleteLater()
                self.processing_thread = None
                
        except Exception as e:
            # 使用更优雅的错误处理：通过UI显示错误而不是控制台输出
            QMessageBox.critical(
                self, 
                i18n.t("error"), 
                f"图片处理过程中发生错误: {str(e)}"
            )
            # 确保线程清理
            if self.processing_thread:
                self.processing_thread.deleteLater()
                self.processing_thread = None
    
    def update_preview(self):
        """更新图片预览"""
        # 清空现有预览
        for i in reversed(range(self.preview_layout.count())):
            child = self.preview_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 添加新的预览
        for image_data in self.uploaded_images:
            preview = ImagePreviewWidget(image_data)
            preview.remove_requested.connect(self.remove_image)
            self.preview_layout.addWidget(preview)
        
        # 添加弹性空间
        self.preview_layout.addStretch()
        
        # 显示/隐藏预览区域
        self.preview_scroll.setVisible(len(self.uploaded_images) > 0)
    
    def remove_image(self, image_id: str):
        """删除图片"""
        self.uploaded_images = [img for img in self.uploaded_images if img.get('id') != image_id]
        self.update_preview()
        self.images_changed.emit(self.uploaded_images)
    
    def get_images_data(self) -> List[Dict]:
        """获取图片数据"""
        return self.uploaded_images
    
    def clear_images(self):
        """清空所有图片"""
        self.uploaded_images.clear()
        self.update_preview()
        self.images_changed.emit(self.uploaded_images)
    
    def _add_image_from_clipboard(self, image):
        """从剪贴板添加图片（供FeedbackTextEdit调用）"""
        if image and not image.isNull():
            try:
                # 使用统一的临时目录管理
                ensure_temp_images_dir()
                filename = generate_clipboard_filename()
                clipboard_path = get_temp_file_path(filename)
                
                # 保存图片
                if image.save(clipboard_path, "PNG"):
                    self.process_image(clipboard_path)
                    # 显示成功提示
                    self.paste_label.setText("✅ 已粘贴图片，正在处理...")
                    QTimer.singleShot(2000, lambda: self.paste_label.setText("📋 " + i18n.t("paste_screenshot_hint")))
                else:
                    QMessageBox.warning(self, i18n.t("warning"), "无法保存剪贴板图片")
            except Exception as e:
                QMessageBox.warning(self, i18n.t("warning"), f"处理剪贴板图片时出错: {str(e)}")
    
    def cleanup(self):
        """清理资源"""
        if self.processing_thread:
            self.processing_thread.deleteLater()
            self.processing_thread = None
    
    def closeEvent(self, event):
        """组件关闭时清理资源"""
        self.cleanup()
        super().closeEvent(event) 