"""
Base classes for AI providers

该模块定义了AI提供商的抽象基类和消息模型:

核心抽象类:
- AIProvider: 所有AI提供商的抽象基类

消息模型:
- MessageRole: 消息角色枚举(SYSTEM, USER, ASSISTANT)
- MessageContentType: 内容类型枚举(TEXT, IMAGE_URL)
- ImageContent: 图片内容模型
- TextContent: 文本内容模型
- AIMessage: AI消息模型，支持多模态
- AIResponse: AI响应模型

设计模式:
- 抽象基类: 定义统一接口
- Pydantic模型: 数据验证和序列化
- 策略模式: 支持多种AI提供商
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator, Union
from pydantic import BaseModel
from enum import Enum


class MessageRole(str, Enum):
    """AI对话中的消息角色枚举
    
    定义了对话中不同角色的消息:
    - SYSTEM: 系统消息，设置AI行为和约束
    - USER: 用户消息，用户输入
    - ASSISTANT: 助手消息，AI生成的回复
    """
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class MessageContentType(str, Enum):
    """消息内容类型枚举，支持多模态输入
    
    定义了消息内容的类型:
    - TEXT: 纯文本内容
    - IMAGE_URL: 图片URL内容
    """
    TEXT = "text"
    IMAGE_URL = "image_url"


class ImageContent(BaseModel):
    """图片内容模型，用于多模态消息
    
    属性:
        type: 内容类型，默认为IMAGE_URL
        image_url: 图片URL字典，包含url键
    """
    type: MessageContentType = MessageContentType.IMAGE_URL
    image_url: Dict[str, str]  # {"url": "data:image/jpeg;base64,..." or "http://..."}


class TextContent(BaseModel):
    """文本内容模型，用于多模态消息
    
    属性:
        type: 内容类型，默认为TEXT
        text: 文本内容字符串
    """
    type: MessageContentType = MessageContentType.TEXT
    text: str


class AIMessage(BaseModel):
    """AI消息模型，支持多模态内容
    
    统一的对话消息格式，支持:
    - 简单字符串内容
    - 混合文本和图片内容
    
    属性:
        role: 消息角色
        content: 消息内容(字符串或内容块列表)
        name: 可选的说话者名称
    """
    role: MessageRole
    content: Union[str, List[Union[TextContent, ImageContent]]]  # Support both simple string and multimodal content
    name: Optional[str] = None


class AIResponse(BaseModel):
    """AI响应模型
    
    统一的AI响应格式，包含:
    - content: 生成的文本内容
    - model: 使用的模型名称
    - usage: token使用统计
    - finish_reason: 完成原因
    - metadata: 额外元数据
    """
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = {}


class AIProvider(ABC):
    """AI提供商抽象基类
    
    定义了所有AI提供商必须实现的统一接口:
    - chat_completion: 聊天补全
    - text_completion: 文本补全
    - stream_chat_completion: 流式聊天补全(可选)
    - stream_text_completion: 流式文本补全(可选)
    
    设计要点:
    - 抽象基类确保一致性
    - 默认实现提供回退行为
    - 配置驱动初始化
    """
    
    def __init__(self, config: Dict[str, Any]):
        """初始化AI提供商
        
        参数:
            config: 提供商配置字典
        """
        self.config = config
        self.model = config.get("model", "unknown")
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AIResponse:
        """生成聊天补全
        
        参数:
            messages: 对话消息历史列表
            **kwargs: 其他参数(temperature, max_tokens等)
            
        返回:
            AIResponse对象
        """
        pass
    
    @abstractmethod
    async def text_completion(
        self,
        prompt: str,
        **kwargs
    ) -> AIResponse:
        """生成文本补全
        
        参数:
            prompt: 提示词
            **kwargs: 其他参数
            
        返回:
            AIResponse对象
        """
        pass
    
    async def stream_chat_completion(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天补全(可选实现)
        
        默认实现返回完整响应，支持提供商重写优化
        
        参数:
            messages: 对话消息历史列表
            **kwargs: 其他参数
            
        返回:
            生成器，逐块产出内容
        """
        # Default implementation: return full response at once
        # 默认实现：一次性返回完整响应
        response = await self.chat_completion(messages, **kwargs)
        yield response.content
    
    async def stream_text_completion(
        self,
        prompt: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式文本补全(可选实现)
        
        默认实现返回完整响应，支持提供商重写优化
        
        参数:
            prompt: 提示词
            **kwargs: 其他参数
            
        返回:
            生成器，逐块产出内容
        """
        # Default implementation: return full response at once
        # 默认实现：一次性返回完整响应
        response = await self.text_completion(prompt, **kwargs)
        yield response.content
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息
        
        返回不包含敏感信息的模型配置
        
        返回:
            包含模型信息的字典
        """
        return {
            "model": self.model,
            "provider": self.__class__.__name__,
            "config": {k: v for k, v in self.config.items() if "key" not in k.lower()}
        }
    
    def _calculate_usage(self, prompt: str, response: str) -> Dict[str, int]:
        """计算token使用量(简化版)
        
        参数:
            prompt: 输入提示词
            response: 响应文本
            
        返回:
            使用量统计字典
        """
        # Simplified calculation - 简化计算
        prompt_tokens = len(prompt.split())
        completion_tokens = len(response.split())
        
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }
    
    def _merge_config(self, **kwargs) -> Dict[str, Any]:
        """Merge provider config with request parameters"""
        merged = self.config.copy()
        merged.update(kwargs)
        return merged
