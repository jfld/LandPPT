"""
Pydantic models for API requests and responses

该模块定义了LandPPT API的所有请求和响应模型:

OpenAI兼容模型:
- ChatMessage: 聊天消息
- ChatCompletionRequest: 聊天补全请求
- CompletionRequest: 文本补全请求
- Usage: Token使用统计
- ChatCompletionChoice: 聊天补全选项
- CompletionChoice: 文本补全选项
- ChatCompletionResponse: 聊天补全响应
- CompletionResponse: 文本补全响应

LandPPT特定模型:
- PPTScenario: PPT场景配置
- PPTGenerationRequest: PPT生成请求
- PPTOutline: PPT大纲
- PPTGenerationResponse: PPT生成响应
- TodoStage: TODO阶段
- TodoBoard: TODO看板
- PPTProject: PPT项目

设计特点:
- Pydantic BaseModel用于数据验证
- Field定义用于API文档生成
- 支持默认值和可选字段
"""

from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field
import time
import uuid

# ============================================================================
# OpenAI兼容模型 - OpenAI Compatible Models
# ============================================================================

class ChatMessage(BaseModel):
    """聊天消息模型
    
    属性:
        role: 消息角色 (system/user/assistant)
        content: 消息内容
        name: 说话者名称(可选)
    """
    role: Literal["system", "user", "assistant"] = Field(..., description="The role of the message author")
    content: str = Field(..., description="The content of the message")
    name: Optional[str] = Field(None, description="The name of the author of this message")

class ChatCompletionRequest(BaseModel):
    """聊天补全请求模型
    
    属性:
        model: 使用的模型ID
        messages: 消息历史列表
        temperature: 采样温度(0-2)
        max_tokens: 最大生成token数
        top_p: 核采样参数(0-1)
        n: 生成选项数量
        stream: 是否流式返回
        stop: 停止序列
        presence_penalty: 存在惩罚
        frequency_penalty: 频率惩罚
        user: 用户标识
    """
    model: str = Field(..., description="ID of the model to use")
    messages: List[ChatMessage] = Field(..., description="A list of messages comprising the conversation so far")
    temperature: Optional[float] = Field(1.0, ge=0, le=2, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum number of tokens to generate")
    top_p: Optional[float] = Field(1.0, ge=0, le=1, description="Nucleus sampling parameter")
    n: Optional[int] = Field(1, ge=1, le=128, description="Number of chat completion choices to generate")
    stream: Optional[bool] = Field(False, description="Whether to stream back partial progress")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Up to 4 sequences where the API will stop generating")
    presence_penalty: Optional[float] = Field(0, ge=-2, le=2, description="Presence penalty parameter")
    frequency_penalty: Optional[float] = Field(0, ge=-2, le=2, description="Frequency penalty parameter")
    user: Optional[str] = Field(None, description="A unique identifier representing your end-user")

class CompletionRequest(BaseModel):
    """文本补全请求模型
    
    属性:
        model: 使用的模型ID
        prompt: 提示词
        temperature: 采样温度
        max_tokens: 最大生成token数
        top_p: 核采样参数
        n: 生成选项数量
        stream: 是否流式返回
        stop: 停止序列
        presence_penalty: 存在惩罚
        frequency_penalty: 频率惩罚
        user: 用户标识
    """
    model: str = Field(..., description="ID of the model to use")
    prompt: Union[str, List[str]] = Field(..., description="The prompt(s) to generate completions for")
    temperature: Optional[float] = Field(1.0, ge=0, le=2, description="Sampling temperature")
    max_tokens: Optional[int] = Field(16, gt=0, description="Maximum number of tokens to generate")
    top_p: Optional[float] = Field(1.0, ge=0, le=1, description="Nucleus sampling parameter")
    n: Optional[int] = Field(1, ge=1, le=128, description="Number of completions to generate")
    stream: Optional[bool] = Field(False, description="Whether to stream back partial progress")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Up to 4 sequences where the API will stop generating")
    presence_penalty: Optional[float] = Field(0, ge=-2, le=2, description="Presence penalty parameter")
    frequency_penalty: Optional[float] = Field(0, ge=-2, le=2, description="Frequency penalty parameter")
    user: Optional[str] = Field(None, description="A unique identifier representing your end-user")

class Usage(BaseModel):
    """Token使用统计模型
    
    属性:
        prompt_tokens: 输入token数
        completion_tokens: 输出token数
        total_tokens: 总token数
    """
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionChoice(BaseModel):
    """聊天补全选项模型
    
    属性:
        index: 选项索引
        message: 生成的消息
        finish_reason: 完成原因
    """
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None

class CompletionChoice(BaseModel):
    """文本补全选项模型
    
    属性:
        text: 生成的文本
        index: 选项索引
        finish_reason: 完成原因
    """
    text: str
    index: int
    finish_reason: Optional[str] = None

class ChatCompletionResponse(BaseModel):
    """聊天补全响应模型
    
    属性:
        id: 响应ID
        object: 对象类型
        created: 创建时间戳
        model: 模型ID
        choices: 选项列表
        usage: 使用统计
    """
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:29]}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionChoice]
    usage: Usage

class CompletionResponse(BaseModel):
    """文本补全响应模型
    
    属性:
        id: 响应ID
        object: 对象类型
        created: 创建时间戳
        model: 模型ID
        choices: 选项列表
        usage: 使用统计
    """
    id: str = Field(default_factory=lambda: f"cmpl-{uuid.uuid4().hex[:29]}")
    object: str = "text_completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[CompletionChoice]
    usage: Usage

# ============================================================================
# LandPPT特定模型 - LandPPT Specific Models
# ============================================================================

class PPTScenario(BaseModel):
    """PPT场景配置模型
    
    属性:
        id: 场景ID
        name: 场景名称
        description: 场景描述
        icon: 图标
        template_config: 模板配置
    """
    id: str
    name: str
    description: str
    icon: str
    template_config: Dict[str, Any]

class PPTGenerationRequest(BaseModel):
    """PPT生成请求模型
    
    属性:
        scenario: 场景类型
        topic: 主题
        requirements: 额外需求
        network_mode: 是否使用网络模式
        language: 语言
        uploaded_content: 上传文件内容
        target_audience: 目标受众
        ppt_style: PPT风格
        custom_style_prompt: 自定义风格提示
        description: 描述
        use_file_content: 是否使用文件内容
        file_processing_mode: 文件处理模式
        content_analysis_depth: 内容分析深度
    """
    scenario: str = Field(..., description="PPT scenario type")
    topic: str = Field(..., description="PPT topic/theme")
    requirements: Optional[str] = Field(None, description="Additional requirements")
    network_mode: bool = Field(False, description="Whether to use network mode for enhanced generation")
    language: str = Field("zh", description="Language for the PPT content")
    uploaded_content: Optional[str] = Field(None, description="Content from uploaded files")
    # 目标受众和风格相关参数
    target_audience: Optional[str] = Field(None, description="Target audience for the PPT")
    ppt_style: str = Field("general", description="PPT style: 'general', 'conference', 'custom'")
    custom_style_prompt: Optional[str] = Field(None, description="Custom style prompt")
    description: Optional[str] = Field(None, description="Additional description or requirements")
    # 文件生成相关参数
    use_file_content: bool = Field(False, description="Whether to use uploaded file content for generation")
    file_processing_mode: str = Field("markitdown", description="File processing mode: 'markitdown' or 'magic_pdf'")
    content_analysis_depth: str = Field("standard", description="Content analysis depth: 'fast', 'standard', 'deep'")

class PPTOutline(BaseModel):
    """PPT大纲模型
    
    属性:
        title: 大纲标题
        slides: 幻灯片列表
        metadata: 元数据
    """
    title: str
    slides: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class PPTGenerationResponse(BaseModel):
    """PPT生成响应模型
    
    属性:
        task_id: 任务ID
        status: 状态
        outline: 大纲
        slides_html: HTML幻灯片
        error: 错误信息
    """
    task_id: str
    status: str
    outline: Optional[PPTOutline] = None
    slides_html: Optional[str] = None
    error: Optional[str] = None

# Enhanced Task Management Models - 增强任务管理模型
class TodoStage(BaseModel):
    """TODO阶段模型
    
    属性:
        id: 阶段ID
        name: 阶段名称
        description: 阶段描述
        status: 状态
        progress: 进度
        subtasks: 子任务列表
        result: 结果
        created_at: 创建时间
        updated_at: 更新时间
    """
    id: str
    name: str
    description: str
    status: Literal["pending", "running", "completed", "failed"] = "pending"
    progress: float = 0.0
    subtasks: List[str] = []
    result: Optional[Dict[str, Any]] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

class TodoBoard(BaseModel):
    """TODO看板模型
    
    属性:
        task_id: 任务ID
        title: 标题
        stages: 阶段列表
        current_stage_index: 当前阶段索引
        overall_progress: 总体进度
        created_at: 创建时间
        updated_at: 更新时间
    """
    task_id: str
    title: str
    stages: List[TodoStage]
    current_stage_index: int = 0
    overall_progress: float = 0.0
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

# Project Management Models - 项目管理模型
class PPTProject(BaseModel):
    """PPT项目模型
    
    属性:
        project_id: 项目ID
        title: 标题
        scenario: 场景
        topic: 主题
        requirements: 需求
        status: 状态
        outline: 大纲
        slides_html: HTML幻灯片
        slides_data: 幻灯片数据
        confirmed_requirements: 确认的需求
        project_metadata: 项目元数据
        todo_board: TODO看板
        version: 版本号
        versions: 版本历史
        created_at: 创建时间
        updated_at: 更新时间
    """
    project_id: str
    title: str
    scenario: str
    topic: str
    requirements: Optional[str] = None
    status: Literal["draft", "in_progress", "completed", "archived"] = "draft"
    outline: Optional[Dict[str, Any]] = None  # Changed to Dict for flexibility
    slides_html: Optional[str] = None
    slides_data: Optional[List[Dict[str, Any]]] = None  # Individual slide data
    confirmed_requirements: Optional[Dict[str, Any]] = None  # Confirmed requirements from step 1
    project_metadata: Optional[Dict[str, Any]] = None  # 项目元数据，包括选择的模板ID等
    todo_board: Optional[TodoBoard] = None
    version: int = 1
    versions: List[Dict[str, Any]] = []
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

class ProjectListResponse(BaseModel):
    projects: List[PPTProject]
    total: int
    page: int
    page_size: int

# Enhanced Slide Models
class SlideContent(BaseModel):
    type: Literal["title", "content", "image", "chart", "list", "thankyou", "agenda", "section", "conclusion"]
    title: str
    subtitle: Optional[str] = None
    content: Optional[str] = None
    bullet_points: Optional[List[str]] = None
    image_suggestions: Optional[List[str]] = None
    chart_data: Optional[Dict[str, Any]] = None
    layout: str = "default"
    locked: bool = False

class EnhancedPPTOutline(BaseModel):
    title: str
    slides: List[SlideContent]
    metadata: Dict[str, Any]
    theme_config: Dict[str, Any] = {}

# File Upload Models
class FileUploadResponse(BaseModel):
    filename: str
    size: int
    type: str
    processed_content: str
    extracted_topics: List[str] = []
    suggested_scenarios: List[str] = []
    message: str

class FileOutlineGenerationRequest(BaseModel):
    """从文件生成PPT大纲的请求模型"""
    file_path: str = Field(..., description="Uploaded file path")
    filename: str = Field(..., description="Original filename")
    topic: Optional[str] = Field(None, description="Custom topic override")
    scenario: str = Field("general", description="PPT scenario type")
    requirements: Optional[str] = Field(None, description="Specific requirements from user")
    target_audience: Optional[str] = Field(None, description="Target audience for the PPT")
    language: str = Field("zh", description="Language for the PPT content: 'zh' for Chinese, 'en' for English")
    page_count_mode: str = Field("ai_decide", description="Page count mode: 'ai_decide', 'custom_range', 'fixed'")
    min_pages: Optional[int] = Field(8, description="Minimum pages for custom_range mode")
    max_pages: Optional[int] = Field(15, description="Maximum pages for custom_range mode")
    fixed_pages: Optional[int] = Field(10, description="Fixed page count")
    ppt_style: str = Field("general", description="PPT style: 'general', 'conference', 'custom'")
    custom_style_prompt: Optional[str] = Field(None, description="Custom style prompt")
    file_processing_mode: str = Field("markitdown", description="File processing mode")
    content_analysis_depth: str = Field("standard", description="Content analysis depth")

class FileOutlineGenerationResponse(BaseModel):
    """从文件生成PPT大纲的响应模型"""
    success: bool
    outline: Optional[Dict[str, Any]] = None
    file_info: Optional[Dict[str, Any]] = None
    processing_stats: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: str

# TaskStatus model removed - now using project-based workflow with TodoBoard

# Global Master Template Models
class GlobalMasterTemplateCreate(BaseModel):
    """Request model for creating a global master template"""
    template_name: str = Field(..., description="Template name (must be unique)")
    description: Optional[str] = Field("", description="Template description")
    html_template: str = Field(..., description="HTML template content")
    tags: Optional[List[str]] = Field([], description="Template tags for categorization")
    is_default: Optional[bool] = Field(False, description="Whether this is the default template")
    created_by: Optional[str] = Field("user", description="Creator identifier")


class GlobalMasterTemplateUpdate(BaseModel):
    """Request model for updating a global master template"""
    template_name: Optional[str] = Field(None, description="Template name (must be unique)")
    description: Optional[str] = Field(None, description="Template description")
    html_template: Optional[str] = Field(None, description="HTML template content")
    tags: Optional[List[str]] = Field(None, description="Template tags for categorization")
    is_default: Optional[bool] = Field(None, description="Whether this is the default template")
    is_active: Optional[bool] = Field(None, description="Whether the template is active")


class GlobalMasterTemplateResponse(BaseModel):
    """Response model for global master template"""
    id: int
    template_name: str
    description: str
    preview_image: Optional[str] = None
    tags: List[str]
    is_default: bool
    is_active: bool
    usage_count: int
    created_by: str
    created_at: float
    updated_at: float


class GlobalMasterTemplateDetailResponse(GlobalMasterTemplateResponse):
    """Detailed response model for global master template"""
    html_template: str
    style_config: Optional[Dict[str, Any]] = None


class ReferenceImageData(BaseModel):
    """Reference image data for AI generation"""
    filename: str = Field(..., description="Image filename")
    data: str = Field(..., description="Base64 encoded image data")
    size: int = Field(..., description="File size in bytes")
    type: str = Field(..., description="MIME type")


class GlobalMasterTemplateGenerateRequest(BaseModel):
    """Request model for AI-generated global master template"""
    prompt: str = Field(..., description="AI generation prompt")
    template_name: str = Field(..., description="Template name (must be unique)")
    description: Optional[str] = Field("", description="Template description")
    tags: Optional[List[str]] = Field([], description="Template tags")
    generation_mode: str = Field("text_only", description="Generation mode: text_only, reference_style, exact_replica")
    reference_image: Optional[ReferenceImageData] = Field(None, description="Reference image for multimodal generation")


class TemplateSelectionRequest(BaseModel):
    """Request model for template selection during PPT generation"""
    project_id: str = Field(..., description="Project ID")
    selected_template_id: Optional[int] = Field(None, description="Selected template ID (None for default)")
    template_mode: Optional[Literal["global", "default", "free"]] = Field(
        None,
        description="Template mode: global (selected template), default (system default), free (AI decides)"
    )


class TemplateSelectionResponse(BaseModel):
    """Response model for template selection"""
    success: bool
    message: str
    selected_template: Optional[GlobalMasterTemplateResponse] = None
