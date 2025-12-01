"""
通义千问API客户端（阿里云）
"""
import os
from typing import Optional, Dict, List
import requests
from models.llm_client import LLMClient


class QwenClient(LLMClient):
    """通义千问API客户端（阿里云）"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化通义千问客户端
        
        Args:
            api_key: API密钥，如果为None则从环境变量QWEN_API_KEY获取
            base_url: API基础URL，如果为None则从环境变量QWEN_BASE_URL获取，否则使用默认值
        """
        super().__init__(api_key, base_url)
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("QWEN_API_KEY", "")
        
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/api/v1")
        
        if not self.api_key:
            raise ValueError("需要设置QWEN_API_KEY环境变量或传入api_key参数")
    
    def chat(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> str:
        """
        发送聊天请求到通义千问API
        
        Args:
            messages: 消息列表
            model: 模型名称，如果为None则从环境变量QWEN_LLM_MODEL获取，默认qwen-turbo
            **kwargs: 其他参数
            
        Returns:
            str: 模型回复内容
        """
        if model is None:
            model = os.getenv("QWEN_LLM_MODEL", "qwen-turbo")
        
        url = f"{self.base_url}/services/aigc/text-generation/generation"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "input": {
                "messages": messages
            },
            **kwargs
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result["output"]["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"调用通义千问API时出错: {str(e)}")

