import datetime

from models.llm_client import create_llm_client


def parse_question(question: str) -> str:
    """
    解析用户问题，将相对日期转换为具体日期
    
    Args:
        question: 用户问题
        
    Returns:
        str: 转换后的问题，如果无法识别日期则返回提示信息
    """
    # python获取今天的日期，格式为YYYY-MM-DD
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # 设置提示词，将today替换到提示词中
    system_prompt = f"""你是一个日期转换助手。今天的日期是{today}。

你的任务是将用户问题中的相对日期（如"今天"、"明天"、"后天"、"大后天"等）转换为具体的日期格式（YYYY-MM-DD）。

转换规则：
- 今天 = {today}
- 明天 = 今天的日期 + 1天
- 后天 = 今天的日期 + 2天
- 大后天 = 今天的日期 + 3天
- 昨天 = 今天的日期 - 1天
- 前天 = 今天的日期 - 2天

如果用户问题中包含具体日期（如"2025-12-01"），则保持不变。

如果用户问题中不包含任何日期信息，无法查询黄历，请直接返回："请输入具体的时间日期或相对日期，如2025-12-01或今天、明天等"

请只返回转换后的问题文本，不要添加任何解释或说明。"""

    user_prompt = f"用户问题：{question}\n\n请根据上述规则转换日期并返回转换后的问题。"

    try:
        llm = create_llm_client(provider="deepseek")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        result = llm.chat(messages, model="deepseek-r1-250528", temperature=0.3)
        return result.strip()
    except Exception as e:
        # 如果调用失败，返回错误信息
        return f"处理问题时出错：{str(e)}"
