"""
UI配置管理模块 - 负责配置的加载、保存和管理
"""
import hashlib
from typing import TypedDict, List
from PySide6.QtCore import QSettings
from i18n import i18n


class FeedbackResult(TypedDict):
    logs: str
    interactive_feedback: str


class FeedbackConfig(TypedDict):
    run_command: str
    execute_automatically: bool
    suffix_mode: str  # "force", "smart", "none"
    button_size: str  # "small", "medium", "large", "custom"
    custom_button_width: int
    custom_button_height: int
    visible_buttons: List[int]  # 显示的按钮索引列表
    language: str  # "zh_CN", "en_US"
    use_base64_transmission: bool  # 是否启用Base64传输
    base64_target_size_kb: int  # Base64目标大小（KB）


class UIConfigManager:
    """UI配置管理器"""
    
    def __init__(self, project_directory: str):
        self.project_directory = project_directory
        self.settings = QSettings("InteractiveFeedbackMCP", "InteractiveFeedbackMCP")
        self.project_group_name = get_project_settings_group(project_directory)
        
    def load_config(self) -> FeedbackConfig:
        """加载配置"""
        # Load general UI settings for the main window (geometry, state)
        self.settings.beginGroup("MainWindow_General")
        geometry = self.settings.value("geometry")
        window_state = self.settings.value("windowState")
        self.settings.endGroup()
        
        # Load project-specific settings
        self.settings.beginGroup(self.project_group_name)
        config = FeedbackConfig(
            run_command=self.settings.value("run_command", "", type=str),
            execute_automatically=self.settings.value("execute_automatically", False, type=bool),
            suffix_mode=self.settings.value("suffix_mode", "force", type=str),
            button_size=self.settings.value("button_size", "medium", type=str),
            custom_button_width=self.settings.value("custom_button_width", 120, type=int),
            custom_button_height=self.settings.value("custom_button_height", 40, type=int),
            visible_buttons=self.settings.value("visible_buttons", [], type=list),
            language=self.settings.value("language", "zh_CN", type=str),
            use_base64_transmission=self.settings.value("use_base64_transmission", True, type=bool),
            base64_target_size_kb=self.settings.value("base64_target_size_kb", 30, type=int)
        )
        self.settings.endGroup()
        
        return config, geometry, window_state
    
    def save_config(self, config: FeedbackConfig):
        """保存配置"""
        self.settings.beginGroup(self.project_group_name)
        self.settings.setValue("run_command", config["run_command"])
        self.settings.setValue("execute_automatically", config["execute_automatically"])
        self.settings.setValue("suffix_mode", config["suffix_mode"])
        self.settings.setValue("button_size", config["button_size"])
        self.settings.setValue("custom_button_width", config["custom_button_width"])
        self.settings.setValue("custom_button_height", config["custom_button_height"])
        self.settings.setValue("visible_buttons", config["visible_buttons"])
        self.settings.setValue("language", config["language"])
        self.settings.setValue("use_base64_transmission", config["use_base64_transmission"])
        self.settings.setValue("base64_target_size_kb", config["base64_target_size_kb"])
        self.settings.endGroup()
    
    def save_window_geometry(self, geometry, window_state):
        """保存窗口几何信息"""
        self.settings.beginGroup("MainWindow_General")
        if geometry:
            self.settings.setValue("geometry", geometry)
        if window_state:
            self.settings.setValue("windowState", window_state)
        self.settings.endGroup()
    
    def save_command_section_visibility(self, visible: bool):
        """保存命令区域可见性"""
        self.settings.beginGroup(self.project_group_name)
        self.settings.setValue("commandSectionVisible", visible)
        self.settings.endGroup()
    
    def load_command_section_visibility(self) -> bool:
        """加载命令区域可见性"""
        self.settings.beginGroup(self.project_group_name)
        visible = self.settings.value("commandSectionVisible", False, type=bool)
        self.settings.endGroup()
        return visible
    
    def load_quick_responses(self):
        """加载快捷回复配置"""
        self.settings.beginGroup(self.project_group_name)
        saved_responses = self.settings.value("quick_responses", [], type=list)
        self.settings.endGroup()
        return saved_responses
    
    def save_quick_responses(self, responses):
        """保存快捷回复配置"""
        self.settings.beginGroup(self.project_group_name)
        self.settings.setValue("quick_responses", responses)
        self.settings.endGroup()


# 默认按钮模式定义（统一管理，避免重复）
DEFAULT_BUTTON_PATTERNS = [
    # RIPER-5按钮特征
    ("RESEARCH", "请进入RESEARCH模式", "Please enter RESEARCH mode"),
    ("INNOVATE", "请进入INNOVATE模式", "Please enter INNOVATE mode"),
    ("PLAN", "请进入PLAN模式", "Please enter PLAN mode"),
    ("EXECUTE", "请进入EXECUTE模式", "Please enter EXECUTE mode"),
    ("REVIEW", "请进入REVIEW模式", "Please enter REVIEW mode"),
    
    # 其他默认按钮特征
    ("完成所有清单", "继续完成剩余的所有清单", "Complete all remaining checklist"),
    ("智能执行清单", "继续执行剩余的清单项", "Execute remaining checklist"),
    ("执行下一项", "继续执行下一项清单项", "Execute next checklist"),
    ("总结生成规则文件", "同时生成或更新两种规则文件", "Generate or update both rule file formats"),
    ("看起来不错", "看起来不错", "LGTM"),
    ("需要小调整", "基本方向正确", "Good direction"),
    ("完成", "", ""),
    ("深度分析问题", "请进入RESEARCH模式", "Please enter RESEARCH mode"),
    ("创新解决方案", "请进入INNOVATE模式", "Please enter INNOVATE mode"),
    ("制定实施计划", "请进入PLAN模式", "Please enter PLAN mode"),
    ("执行计划步骤", "请进入EXECUTE模式", "Please enter EXECUTE mode"),
    ("验证最终结果", "请进入REVIEW模式", "Please enter REVIEW mode"),
]

def is_default_button(button_text: str, response_text: str) -> bool:
    """统一的默认按钮判断函数"""
    for pattern in DEFAULT_BUTTON_PATTERNS:
        if (pattern[0] in button_text or 
            pattern[1] in response_text or 
            pattern[2] in response_text):
            return True
    return False

def get_project_settings_group(project_dir: str) -> str:
    """
    根据项目目录生成设置组名称
    使用目录路径的哈希值来确保唯一性，同时保持可读性
    """
    # 使用项目目录的绝对路径创建哈希
    dir_hash = hashlib.md5(project_dir.encode('utf-8')).hexdigest()[:8]
    
    # 获取项目目录名称（用于可读性）
    import os
    dir_name = os.path.basename(project_dir.rstrip(os.sep))
    
    # 组合成设置组名称
    return f"Project_{dir_name}_{dir_hash}"


def get_default_config() -> FeedbackConfig:
    """获取默认配置"""
    return FeedbackConfig(
        run_command="",
        execute_automatically=False,
        suffix_mode="force",
        button_size="medium",
        custom_button_width=120,
        custom_button_height=40,
        visible_buttons=[],
        language="zh_CN",
        use_base64_transmission=True,
        base64_target_size_kb=30
    ) 