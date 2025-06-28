"""
反馈业务逻辑模块 - 负责反馈提交和处理的核心业务逻辑
"""
import os
import json
import subprocess
import sys
from typing import Optional

from i18n import i18n
from ui_config import FeedbackResult


class FeedbackLogicManager:
    """反馈业务逻辑管理器"""
    
    def __init__(self, parent_ui):
        self.parent_ui = parent_ui
    
    def submit_feedback(self):
        """提交反馈"""
        feedback_text = self.parent_ui.feedback_text.toPlainText().strip()
        
        # 处理上传的图片
        if hasattr(self.parent_ui, 'uploaded_images') and self.parent_ui.uploaded_images:
            feedback_text += self._process_uploaded_images()
        
        # 根据选择的后缀选项追加相应内容
        if feedback_text:
            feedback_text += self._get_feedback_suffix()
        
        self.parent_ui.feedback_result = FeedbackResult(
            logs="".join(self.parent_ui.log_buffer),
            interactive_feedback=feedback_text,
        )
        self.parent_ui.close()
    
    def _process_uploaded_images(self):
        """处理上传的图片"""
        # 检查是否启用base64传输
        use_base64 = self.parent_ui.config.get("use_base64_transmission", False)
        
        if use_base64:
            return self._process_base64_images()
        else:
            return self._process_path_images()
    
    def _process_base64_images(self):
        """处理base64传输的图片"""
        image_info = "\n\n[附件图片 - Base64优化传输]:\n"
        
        for i, img_data in enumerate(self.parent_ui.uploaded_images, 1):
            if img_data.get('success'):
                image_path = self._get_image_path(img_data)
                
                if image_path:
                    base64_result = self._generate_optimized_base64(image_path)
                    
                    if base64_result and base64_result.get('success'):
                        image_info += f"图片{i}: {base64_result['base64']}\n"
                        image_info += f"优化信息: 原始{base64_result['original_size']} → 优化{base64_result['optimized_size']}, "
                        image_info += f"大小{base64_result['file_size_kb']}KB, 压缩比{base64_result['compression_ratio']}\n\n"
                    else:
                        # base64生成失败，回退到路径模式
                        image_info += f"图片{i}路径: {image_path}\n"
                        image_info += f"图片{i}信息: {img_data.get('original_info', {})}\n"
                        image_info += f"注意: Base64优化失败，请直接查看路径文件\n\n"
        
        image_info += "[处理指令]: 以上图片已通过优化Base64传输，请分析图片内容并处理用户反馈。\n"
        return image_info
    
    def _process_path_images(self):
        """处理路径传输的图片"""
        image_info = "\n\n[附件图片 - 请先解析图片内容再处理反馈]:\n"
        
        for i, img_data in enumerate(self.parent_ui.uploaded_images, 1):
            if img_data.get('success'):
                image_path = self._get_image_path(img_data)
                if image_path:
                    if 'original_path' in img_data:
                        image_info += f"图片{i}路径: {img_data['original_path']}\n"
                    elif 'clipboard_path' in img_data:
                        image_info += f"图片{i}路径(剪贴板): {img_data['clipboard_path']}\n"
                    elif 'processed_path' in img_data:
                        image_info += f"图片{i}路径(处理后): {img_data['processed_path']}\n"
                    
                    image_info += f"图片{i}信息: {img_data.get('original_info', {})}\n\n"
        
        image_info += "[处理指令]: 请先查看并分析上述图片内容，然后结合图片信息处理用户的反馈内容。\n"
        return image_info
    
    def _get_image_path(self, img_data):
        """获取图片路径"""
        if 'original_path' in img_data:
            return img_data['original_path']
        elif 'clipboard_path' in img_data:
            return img_data['clipboard_path']
        elif 'processed_path' in img_data:
            return img_data['processed_path']
        return None
    
    def _generate_optimized_base64(self, image_path):
        """生成优化的base64"""
        try:
            from image_handler import ImageHandler
            handler = ImageHandler()
            
            # 智能判断图片类型
            use_case = 'ui_screenshot'  # 默认为UI截图
            if 'clipboard' in str(image_path):
                use_case = 'ui_screenshot'
            
            # 使用配置中的目标大小
            target_size = self.parent_ui.config.get("base64_target_size_kb", 50)
            return handler.get_optimized_base64(image_path, target_size)
        except Exception as e:
            return None
    
    def _get_feedback_suffix(self):
        """获取反馈后缀"""
        if self.parent_ui.suffix_radio_force.isChecked():
            return i18n.t("suffix_force")
        elif self.parent_ui.suffix_radio_smart.isChecked():
            return i18n.t("suffix_smart")
        # suffix_radio_none 不追加任何内容
        return ""
    
    def on_quick_response_clicked(self, response_text: str):
        """处理快捷回复按钮点击事件"""
        self.parent_ui.feedback_text.setPlainText(response_text)
        # 自动提交反馈（会自动应用后缀选项）
        self.submit_feedback()
    
    def run_feedback_ui_process(self) -> Optional[FeedbackResult]:
        """运行反馈UI进程并获取结果"""
        from PySide6.QtWidgets import QApplication
        from ui_utils import get_dark_mode_palette
        
        app = QApplication.instance() or QApplication()
        app.setPalette(get_dark_mode_palette(app))
        app.setStyle("Fusion")
        
        result = self.parent_ui.run()

        # 在获得结果后调用interactive-feedback-mcp等待用户反馈
        if result and result.get("interactive_feedback"):
            print("正在调用interactive-feedback-mcp等待您的反馈...")
            mcp_result = self._call_interactive_feedback_mcp(
                self.parent_ui.project_directory, 
                "用户反馈已提交，等待进一步指示"
            )
            
            # 如果MCP返回了额外的反馈，可以合并到结果中
            if mcp_result and mcp_result.get("interactive_feedback"):
                original_feedback = result["interactive_feedback"]
                additional_feedback = mcp_result["interactive_feedback"]
                if additional_feedback.strip():  # 只有在有额外反馈时才合并
                    result["interactive_feedback"] = f"{original_feedback}\n\n[额外反馈]: {additional_feedback}"

        return result
    
    def _call_interactive_feedback_mcp(self, project_directory: str, summary: str):
        """调用interactive-feedback-mcp等待用户反馈"""
        try:
            # 构建MCP调用命令
            mcp_command = [
                sys.executable, "-c",
                f"""
import json
import sys
try:
    # 模拟MCP interactive_feedback调用
    print("MCP Interactive Feedback Started")
    print(f"Project: {project_directory}")
    print(f"Summary: {summary}")
    print("等待用户反馈...")
    
    # 这里应该是实际的MCP调用逻辑
    # 暂时用输入等待来模拟
    user_input = input("请输入反馈（按Enter结束）: ")
    
    result = {{
        "logs": "MCP调用完成",
        "interactive_feedback": user_input
    }}
    
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({{"error": str(e)}}))
"""
            ]
            
            # 执行MCP调用
            process = subprocess.Popen(
                mcp_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                try:
                    result = json.loads(stdout.strip().split('\n')[-1])
                    return result
                except:
                    return {"logs": stdout, "interactive_feedback": ""}
            else:
                print(f"MCP调用失败: {stderr}")
                return {"logs": stderr, "interactive_feedback": ""}
                
        except Exception as e:
            print(f"调用interactive-feedback-mcp时出错: {e}")
            return {"logs": str(e), "interactive_feedback": ""} 