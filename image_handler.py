import os
import io
from PIL import Image
from typing import Optional
import mimetypes
from config import SUPPORTED_IMAGE_FORMATS, MAX_FILE_SIZE, MAX_DIMENSION

class ImageHandler:
    """图片处理类，支持压缩、格式验证、Base64编码等功能"""
    
    # 使用配置文件中的常量，避免重复定义
    SUPPORTED_FORMATS = SUPPORTED_IMAGE_FORMATS
    MAX_FILE_SIZE = MAX_FILE_SIZE
    MAX_DIMENSION = MAX_DIMENSION
    
    def __init__(self):
        pass
    
    def validate_image_format(self, file_path: str) -> bool:
        """验证图片格式是否支持"""
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            return mime_type in self.SUPPORTED_FORMATS.values()
        except Exception:
            return False
    
    def get_image_info(self, file_path: str) -> Optional[dict]:
        """获取图片信息"""
        try:
            with Image.open(file_path) as img:
                return {
                    'format': img.format,
                    'size': img.size,
                    'mode': img.mode,
                    'file_size': os.path.getsize(file_path)
                }
        except Exception:
            return None
    
    def compress_image(self, file_path: str, max_size: int = MAX_FILE_SIZE) -> Optional[str]:
        """压缩图片到指定大小以下"""
        try:
            with Image.open(file_path) as img:
                # 转换为RGB模式（如果需要）
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 为透明图片创建白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 计算压缩后的尺寸
                width, height = img.size
                if width > self.MAX_DIMENSION or height > self.MAX_DIMENSION:
                    ratio = min(self.MAX_DIMENSION / width, self.MAX_DIMENSION / height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 尝试不同的压缩质量
                for quality in [85, 75, 65, 55, 45, 35, 25]:
                    output = io.BytesIO()
                    img.save(output, format='JPEG', quality=quality, optimize=True)
                    
                    if output.tell() <= max_size:
                        # 保存压缩后的图片
                        compressed_path = file_path.replace('.', '_compressed.')
                        if not compressed_path.endswith(('.jpg', '.jpeg')):
                            compressed_path = os.path.splitext(compressed_path)[0] + '_compressed.jpg'
                        
                        with open(compressed_path, 'wb') as f:
                            f.write(output.getvalue())
                        
                        return compressed_path
                
                # 如果仍然太大，进一步减小尺寸
                for scale in [0.8, 0.6, 0.4, 0.2]:
                    new_width = int(img.size[0] * scale)
                    new_height = int(img.size[1] * scale)
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    output = io.BytesIO()
                    resized_img.save(output, format='JPEG', quality=25, optimize=True)
                    
                    if output.tell() <= max_size:
                        compressed_path = file_path.replace('.', '_compressed.')
                        if not compressed_path.endswith(('.jpg', '.jpeg')):
                            compressed_path = os.path.splitext(compressed_path)[0] + '_compressed.jpg'
                        
                        with open(compressed_path, 'wb') as f:
                            f.write(output.getvalue())
                        
                        return compressed_path
                
                return None  # 无法压缩到目标大小
                
        except Exception as e:
            # 使用更优雅的错误处理：返回None并让调用者处理错误
            # 避免在生产环境中直接输出到控制台
            return None
    
    def get_optimized_base64(self, file_path: str, target_size_kb: int = 50) -> Optional[dict]:
        """
        生成优化的base64数据，平衡文件大小和视觉质量
        
        Args:
            file_path: 图片文件路径
            target_size_kb: 目标文件大小（KB），默认50KB
        
        Returns:
            包含优化base64数据的字典
        """
        try:
            import base64
            
            with Image.open(file_path) as img:
                # 转换为RGB模式
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                original_size = img.size
                target_size_bytes = target_size_kb * 1024
                
                # 智能缩放策略
                scale_factors = [1.0, 0.8, 0.6, 0.5, 0.4, 0.3, 0.25, 0.2]
                quality_levels = [85, 75, 65, 55, 45, 35, 25, 15]
                
                best_result = None
                
                for scale in scale_factors:
                    # 计算新尺寸
                    new_width = int(original_size[0] * scale)
                    new_height = int(original_size[1] * scale)
                    
                    # 确保最小尺寸
                    if new_width < 200 or new_height < 150:
                        continue
                    
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    for quality in quality_levels:
                        output = io.BytesIO()
                        resized_img.save(output, format='JPEG', quality=quality, optimize=True)
                        
                        if output.tell() <= target_size_bytes:
                            # 保存文件大小（在seek之前）
                            file_size_bytes = output.tell()
                            original_file_size = os.path.getsize(file_path)
                            
                            # 生成base64
                            output.seek(0)
                            base64_data = base64.b64encode(output.getvalue()).decode('utf-8')
                            
                            best_result = {
                                'success': True,
                                'base64': f"data:image/jpeg;base64,{base64_data}",
                                'original_size': original_size,
                                'optimized_size': (new_width, new_height),
                                'file_size_bytes': file_size_bytes,
                                'file_size_kb': round(file_size_bytes / 1024, 2),
                                'compression_ratio': round(file_size_bytes / original_file_size, 3) if original_file_size > 0 else 0,
                                'scale_factor': scale,
                                'quality': quality,
                                'original_file_size_kb': round(original_file_size / 1024, 2)
                            }
                            break
                    
                    if best_result:
                        break
                
                if not best_result:
                    return {
                        'success': False,
                        'error': f'无法将图片压缩到{target_size_kb}KB以下'
                    }
                
                return best_result
                
        except Exception as e:
            return {
                'success': False,
                'error': f'生成优化base64时出错: {str(e)}'
            }

    def get_smart_base64(self, file_path: str, use_case: str = 'general') -> Optional[dict]:
        """
        根据使用场景生成智能优化的base64
        
        Args:
            file_path: 图片文件路径
            use_case: 使用场景 ('ui_screenshot', 'diagram', 'text_heavy', 'general')
        
        Returns:
            优化后的base64数据
        """
        # 根据使用场景调整参数
        configs = {
            'ui_screenshot': {
                'target_size_kb': 80,  # UI截图需要更多细节
                'min_width': 400,
                'min_height': 300,
                'prefer_quality': True
            },
            'diagram': {
                'target_size_kb': 60,  # 图表需要清晰度
                'min_width': 300,
                'min_height': 200,
                'prefer_quality': True
            },
            'text_heavy': {
                'target_size_kb': 70,  # 文字图片需要清晰度
                'min_width': 350,
                'min_height': 250,
                'prefer_quality': True
            },
            'general': {
                'target_size_kb': 50,  # 通用场景平衡大小和质量
                'min_width': 250,
                'min_height': 180,
                'prefer_quality': False
            }
        }
        
        config = configs.get(use_case, configs['general'])
        return self.get_optimized_base64(file_path, config['target_size_kb'])
    
    def process_image(self, file_path: str) -> Optional[dict]:
        """处理图片：验证、压缩、编码，同时保留路径信息"""
        try:
            # 验证格式
            if not self.validate_image_format(file_path):
                return {
                    'success': False,
                    'error': '不支持的图片格式'
                }
            
            # 获取图片信息
            info = self.get_image_info(file_path)
            if not info:
                return {
                    'success': False,
                    'error': '无法读取图片文件'
                }
            
            # 检查文件大小
            processed_path = file_path
            if info['file_size'] > self.MAX_FILE_SIZE:
                # 需要压缩
                compressed_path = self.compress_image(file_path)
                if not compressed_path:
                    return {
                        'success': False,
                        'error': '图片太大，无法压缩到1MB以下'
                    }
                processed_path = compressed_path
            
            # 保留原始和处理后的路径信息（不再生成Base64数据）
            result = {
                'success': True,
                'original_info': info,
                'original_path': os.path.abspath(file_path),
                'processed_path': os.path.abspath(processed_path)
            }
            
            # 如果是压缩后的文件，不立即删除，让调用方决定何时清理
            if processed_path != file_path:
                result['needs_cleanup'] = True
                result['temp_file'] = processed_path
            else:
                result['needs_cleanup'] = False
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'处理图片时出错: {str(e)}'
            }
    
    def validate_clipboard_image(self, clipboard_data: bytes) -> bool:
        """验证剪贴板图片数据"""
        try:
            img = Image.open(io.BytesIO(clipboard_data))
            return True
        except Exception:
            return False 