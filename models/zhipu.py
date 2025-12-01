"""
智谱AI（GLM）API客户端
"""
import os
from typing import Optional, Dict, List
from openai import OpenAI
from models.llm_client import LLMClient


class ZhipuClient(LLMClient):
    """智谱AI（GLM）API客户端"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化智谱AI客户端
        
        Args:
            api_key: API密钥，如果为None则从环境变量ZHIPU_API_KEY获取
            base_url: API基础URL，如果为None则从环境变量ZHIPU_BASE_URL获取，否则使用默认值
        """
        super().__init__(api_key, base_url)
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("ZHIPU_API_KEY", "")
        
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
        
        if not self.api_key:
            raise ValueError("需要设置ZHIPU_API_KEY环境变量或传入api_key参数")
        
        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> str:
        """
        发送聊天请求到智谱AI API
        
        Args:
            messages: 消息列表
            model: 模型名称，如果为None则从环境变量ZHIPU_LLM_MODEL获取，默认glm-4
            **kwargs: 其他参数
            
        Returns:
            str: 模型回复内容
        """
        if model is None:
            model = os.getenv("ZHIPU_LLM_MODEL", "glm-4")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"调用智谱AI API时出错: {str(e)}")