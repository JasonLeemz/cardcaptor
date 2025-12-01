"""
测试模型对话功能
测试各个模型是否能够正常进行问答对话
"""
import os
import pytest
from dotenv import load_dotenv

from models.llm_client import create_llm_client


class TestModelChat:
    """模型对话测试类"""
    # 加载环境变量
    load_dotenv(dotenv_path="configs/.env")

    def test_deepseek_chat(self):
        """测试DeepSeek模型对话"""
        # 检查是否有API密钥
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            pytest.skip("未设置DEEPSEEK_API_KEY环境变量，跳过测试")

        # 创建客户端
        client = create_llm_client("deepseek")

        # 构建消息
        messages = [
            {"role": "user", "content": "你好，请简单介绍一下你自己。"}
        ]

        # 发送请求
        response = client.chat(messages,model="deepseek-r1-250528")

        # 验证响应
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        print(f"\nDeepSeek回复: {response}")

    def test_zhipu_chat(self):
        """测试智谱AI模型对话"""
        # 检查是否有API密钥
        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            pytest.skip("未设置ZHIPU_API_KEY环境变量，跳过测试")

        # 创建客户端
        client = create_llm_client("zhipu")

        # 构建消息
        messages = [
            {"role": "user", "content": "你好，请简单介绍一下你自己。"}
        ]

        # 发送请求
        response = client.chat(messages, model="GLM-4-Flash-250414")

        # 验证响应
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        print(f"\n智谱AI回复: {response}")

    def test_qwen_chat(self):
        """测试通义千问模型对话"""
        # 检查是否有API密钥
        api_key = os.getenv("QWEN_API_KEY")
        if not api_key:
            pytest.skip("未设置QWEN_API_KEY环境变量，跳过测试")

        # 创建客户端
        client = create_llm_client("qwen")

        # 构建消息
        messages = [
            {"role": "user", "content": "你好，请简单介绍一下你自己。"}
        ]

        # 发送请求
        response = client.chat(messages, model="qwen_72b")

        # 验证响应
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        print(f"\n通义千问回复: {response}")

    def test_doubao_chat(self):
        """测试豆包模型对话"""
        # 检查是否有API密钥
        api_key = os.getenv("DOUBAO_API_KEY")
        if not api_key:
            pytest.skip("未设置DOUBAO_API_KEY环境变量，跳过测试")

        # 创建客户端
        client = create_llm_client("doubao")

        # 构建消息
        messages = [
            {"role": "user", "content": "你好，请简单介绍一下你自己。"}
        ]

        # 发送请求
        response = client.chat(messages)

        # 验证响应
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        print(f"\n豆包回复: {response}")

    def test_deepseek_multi_turn_chat(self):
        """测试DeepSeek多轮对话"""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            pytest.skip("未设置DEEPSEEK_API_KEY环境变量，跳过测试")

        client = create_llm_client("deepseek")

        # 第一轮对话
        messages = [
            {"role": "user", "content": "1+1等于几？"}
        ]
        response1 = client.chat(messages)
        assert response1 is not None
        assert isinstance(response1, str)
        print(f"\n第一轮问题: 1+1等于几？")
        print(f"第一轮回复: {response1}")

        # 第二轮对话（多轮对话）
        messages.append({"role": "assistant", "content": response1})
        messages.append({"role": "user", "content": "那2+2呢？"})
        response2 = client.chat(messages)
        assert response2 is not None
        assert isinstance(response2, str)
        print(f"\n第二轮问题: 那2+2呢？")
        print(f"第二轮回复: {response2}")

    def test_zhipu_multi_turn_chat(self):
        """测试智谱AI多轮对话"""
        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            pytest.skip("未设置ZHIPU_API_KEY环境变量，跳过测试")

        client = create_llm_client("zhipu")

        # 第一轮对话
        messages = [
            {"role": "user", "content": "1+1等于几？"}
        ]
        response1 = client.chat(messages)
        assert response1 is not None
        assert isinstance(response1, str)
        print(f"\n第一轮问题: 1+1等于几？")
        print(f"第一轮回复: {response1}")

        # 第二轮对话（多轮对话）
        messages.append({"role": "assistant", "content": response1})
        messages.append({"role": "user", "content": "那2+2呢？"})
        response2 = client.chat(messages)
        assert response2 is not None
        assert isinstance(response2, str)
        print(f"\n第二轮问题: 那2+2呢？")
        print(f"第二轮回复: {response2}")
