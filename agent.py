"""
AI Agent核心模块
基于黄历信息回答用户问题，使用大模型进行理解
"""
import re
from typing import Dict, Optional
from calendar_api import CalendarAPI
from models.llm_client import create_llm_client


class CalendarAgent:
    """黄历AI Agent，使用大模型理解黄历信息"""
    
    def __init__(self, llm_provider: str = "openai", llm_model: str = "gpt-3.5-turbo", **llm_kwargs):
        """
        初始化Agent
        
        Args:
            llm_provider: 大模型提供商，可选: "openai", "qwen", "zhipu"
            llm_model: 模型名称
            **llm_kwargs: 传递给LLM客户端的其他参数
        """
        self.api = CalendarAPI()
        try:
            self.llm = create_llm_client(provider=llm_provider, **llm_kwargs)
            self.llm_model = llm_model
        except Exception as e:
            raise ValueError(f"初始化大模型客户端失败: {str(e)}。请确保已设置相应的API密钥环境变量。")
    
    def extract_date_from_question(self, question: str) -> tuple:
        """
        从用户问题中提取日期信息
        
        Args:
            question: 用户问题
            
        Returns:
            tuple: (year, month, day, date_str)
        """
        # 匹配日期关键词
        date_patterns = {
            r"今天|今日": "今天",
            r"明天|明日": "明天",
            r"后天|后日": "后天",
            r"昨天|昨日": "昨天",
            r"(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})[日]?": None  # 具体日期
        }
        
        # 检查相对日期
        for pattern, date_str in date_patterns.items():
            if date_str and re.search(pattern, question):
                year, month, day = self.api.parse_date_string(date_str)
                return year, month, day, date_str
        
        # 检查具体日期
        date_match = re.search(r"(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})[日]?", question)
        if date_match:
            year = int(date_match.group(1))
            month = int(date_match.group(2))
            day = int(date_match.group(3))
            return year, month, day, f"{year}年{month}月{day}日"
        
        # 默认使用今天
        year, month, day = self.api.parse_date_string("今天")
        return year, month, day, "今天"
    
    def format_calendar_info(self, day_info: Dict, hour_info: Optional[Dict] = None) -> str:
        """
        格式化黄历信息，使其易于大模型理解
        
        Args:
            day_info: 日期黄历信息
            hour_info: 时辰黄历信息（可选）
            
        Returns:
            str: 格式化后的黄历信息文本
        """
        info_parts = []
        
        # 基本信息
        info_parts.append(f"日期：{day_info.get('ynian', '')}年{day_info.get('yyue', '')}月{day_info.get('yri', '')}日")
        info_parts.append(f"星期：{day_info.get('xingqi', '')}")
        info_parts.append(f"农历：{day_info.get('nnian', '')}年{day_info.get('nyue', '')}月{day_info.get('nri', '')}")
        info_parts.append(f"节气：{day_info.get('jieqi', '')}（{day_info.get('JIEQIDAYS', '')}天）")
        
        # 干支信息
        info_parts.append(f"年干支：{day_info.get('ganzhinian', '')}")
        info_parts.append(f"月干支：{day_info.get('ganzhiyue', '')}")
        info_parts.append(f"日干支：{day_info.get('ganzhiri', '')}")
        
        # 五行信息
        info_parts.append(f"年五行：{day_info.get('nianwuxing', '')}")
        info_parts.append(f"月五行：{day_info.get('yuewuxing', '')}")
        info_parts.append(f"日五行：{day_info.get('riwuxing', '')}")
        info_parts.append(f"正五行：{day_info.get('ZHENG', '')}")
        
        # 宜忌信息
        yi = day_info.get("yi", "")
        ji = day_info.get("ji", "")
        if yi:
            info_parts.append(f"今日适宜：{yi}")
        if ji:
            info_parts.append(f"今日不宜：{ji}")
        
        # 方位信息
        info_parts.append(f"财神方位：{day_info.get('DAYPOSITIONCAI', '')}")
        info_parts.append(f"喜神方位：{day_info.get('DAYPOSITIONXI', '')}")
        info_parts.append(f"福神方位：{day_info.get('DAYPOSITIONFU', '')}")
        
        # 冲煞信息
        xiangchong = day_info.get("xiangchong", "")
        if xiangchong:
            info_parts.append(f"冲煞：{xiangchong}")
        
        # 吉神凶煞
        jishen = day_info.get("DAYJISHEN", "")
        xiongsha = day_info.get("DAYXIONGSHA", "")
        if jishen:
            info_parts.append(f"吉神：{jishen}")
        if xiongsha:
            info_parts.append(f"凶煞：{xiongsha}")
        
        # 黄道吉日信息
        tianshen = day_info.get("DAYTIANSHEN", "")
        tianshen_type = day_info.get("DAYTIANSHENTYPE", "")
        tianshen_luck = day_info.get("DAYTIANSHENLUCK", "")
        if tianshen:
            info_parts.append(f"天德：{tianshen}（{tianshen_type}，{tianshen_luck}）")
        
        # 值星信息
        zhixing = day_info.get("ZHIXING", "")
        if zhixing:
            info_parts.append(f"值星：{zhixing}")
        
        # 彭祖百忌
        pengzu = day_info.get("pengzu", "")
        if pengzu:
            info_parts.append(f"彭祖百忌：{pengzu}")
        
        # 时辰信息
        if hour_info:
            info_parts.append("\n各时辰详情：")
            shichen_list = ["zi", "chou", "yin", "mao", "chen", "si", "wu", "wei", "shen", "you", "xu", "hai"]
            for sc in shichen_list:
                sc_name = hour_info.get(f"{sc}0", "")
                sc_luck = hour_info.get(f"{sc}1", "")
                sc_time = hour_info.get(f"{sc}2", "")
                sc_shen = hour_info.get(f"{sc}3", "")
                sc_yi = hour_info.get(f"{sc}4", "")
                sc_ji = hour_info.get(f"{sc}5", "")
                
                if sc_name and sc_luck:
                    hour_text = f"{sc_name}时（{sc_time}）：{sc_luck}"
                    if sc_shen:
                        hour_text += f"，{sc_shen}"
                    if sc_yi:
                        hour_text += f"，适宜：{sc_yi}"
                    if sc_ji:
                        hour_text += f"，不宜：{sc_ji}"
                    info_parts.append(hour_text)
        
        return "\n".join(info_parts)
    
    def answer_question(self, question: str) -> str:
        """
        使用大模型回答用户问题，基于黄历信息
        
        Args:
            question: 用户问题
            
        Returns:
            str: 回答内容
        """
        try:
            # 提取日期信息
            year, month, day, date_str = self.extract_date_from_question(question)
            
            # 获取黄历信息
            day_info = self.api.get_day_calendar(year, month, day)
            hour_info = None
            
            # 如果问题涉及时辰，获取时辰信息
            if any(keyword in question for keyword in ["时辰", "几点", "什么时候", "时间", "小时"]):
                hour_info = self.api.get_hour_calendar(year, month, day)
            
            # 格式化黄历信息
            calendar_text = self.format_calendar_info(day_info, hour_info)
            
            # 构建提示词
            system_prompt = """你是一位专业的黄历咨询师，擅长根据黄历信息为用户提供建议和解答。

请根据提供的黄历信息，用专业、友好、易懂的方式回答用户的问题。回答时应该：
1. 基于黄历信息中的宜忌、五行、方位等要素进行分析
2. 提供具体、实用的建议
3. 如果涉及颜色推荐，可以参考五行属性（金-白/银/金，木-绿/青，水-黑/蓝，火-红/粉/紫/橙，土-黄/棕/米）
4. 如果涉及活动建议，要明确指出是否适宜，并说明原因
5. 如果涉及方位，要明确指出具体的方位信息
6. 回答要简洁明了，重点突出

请用中文回答，语气要专业但亲切。"""

            user_prompt = f"""以下是{date_str}（{year}年{month}月{day}日）的黄历信息：

{calendar_text}

用户问题：{question}

请根据上述黄历信息，专业地回答用户的问题。"""
            
            # 调用大模型
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            answer = self.llm.chat(messages, model=self.llm_model, temperature=0.7)
            
            return answer
            
        except Exception as e:
            return f"抱歉，处理您的问题时出现错误：{str(e)}"
