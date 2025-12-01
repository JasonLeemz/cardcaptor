"""
大模型客户端模块
支持多种大模型API
"""
from typing import Optional, Dict, List


class LLMClient:
    """大模型客户端基类"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
    
    def chat(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 模型名称（如果为None，将使用默认模型）
            **kwargs: 其他参数
            
        Returns:
            str: 模型回复内容
        """
        raise NotImplementedError


def create_llm_client(provider: str = "openai", **kwargs) -> LLMClient:
    """
    创建LLM客户端工厂函数
    
    Args:
        provider: 提供商名称，可选: "openai", "qwen", "zhipu", "deepseek", "doubao"
        **kwargs: 传递给客户端的参数
        
    Returns:
        LLMClient: LLM客户端实例
    """
    provider_lower = provider.lower()
    
    if provider_lower == "qwen":
        from models.qianwen import QwenClient
        return QwenClient(**kwargs)
    elif provider_lower == "zhipu":
        from models.zhipu import ZhipuClient
        return ZhipuClient(**kwargs)
    elif provider_lower == "deepseek":
        from models.deepseek import DeepSeekClient
        return DeepSeekClient(**kwargs)
    elif provider_lower == "doubao":
        from models.doubao import DoubaoClient
        return DoubaoClient(**kwargs)
    else:
        raise ValueError(
            f"不支持的提供商: {provider}，"
            f"支持的提供商: ['qwen', 'zhipu', 'deepseek', 'doubao']"
        )

