import json
import os
import re
import yaml
from jinja2 import Environment, FileSystemLoader
from pkg.calender.calendar_api import CalendarAPI
from pkg.sqlite.sqlite import get_db
from models.llm_client import create_llm_client
from pkg.log.log import get_logger

logger = get_logger()

# 从配置文件读取模板路径
def _get_template_dir():
    """从配置文件读取模板目录路径"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "app.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    base_path = config['prompt']['path']
    calendar_dir = config['prompt'].get('calendar', 'calendar')
    template_version = config['prompt'].get('template_version', 'default')
    
    # 如果是相对路径，则基于项目根目录
    if not os.path.isabs(base_path):
        project_root = os.path.dirname(os.path.dirname(__file__))
        base_path = os.path.join(project_root, base_path)
    
    template_dir = os.path.join(base_path, calendar_dir, template_version)
    return template_dir

# 初始化Jinja2环境
_template_dir = _get_template_dir()
_jinja_env = Environment(loader=FileSystemLoader(_template_dir))


def _load_template(template_name: str) -> str:
    """
    加载并渲染模板文件（无变量）
    
    Args:
        template_name: 模板文件名（不含.j2后缀）
        
    Returns:
        str: 渲染后的模板内容
    """
    template = _jinja_env.get_template(f"{template_name}.j2")
    return template.render()

def get_calander_info(year: int, month: int, day: int, force_refresh: bool = False) -> str:
    """
    获取黄历信息
    优先从SQLite数据库获取，如果获取不到则从API获取并保存到数据库
    
    Args:
        year: 年份
        month: 月份
        day: 日期
        force_refresh: 是否强制从API获取最新数据，忽略缓存。默认为False
        
    Returns:
        str: 黄历信息的JSON字符串
    """
    try:
        # 构建日期字符串，格式为 YYYY-MM-DD
        date_str = f"{year}-{month:02d}-{day:02d}"
        
        db = get_db()
        
        # 如果强制刷新，跳过数据库查询，直接从API获取
        if force_refresh:
            logger.info(f"强制刷新，从API获取最新黄历信息: {date_str}")
            api = CalendarAPI()
            
            # 获取日维度数据信息
            day_info = api.get_day_calendar(year, month, day)
            logger.info(f"日维度-{year}年{month}月{day}日: {json.dumps(day_info, ensure_ascii=False)}")
            # 保存到数据库
            db.save_day_calendar(date_str, day_info)
            
            # 获取小时维度数据
            hour_info = api.get_hour_calendar(year, month, day)
            logger.info(f"小时维度-{year}年{month}月{day}日: {json.dumps(hour_info, ensure_ascii=False)}")
            # 保存到数据库
            db.save_hour_calendar(date_str, hour_info)
            
            # 合并信息并转换为JSON字符串
            calendar_data = {
                "day_info": day_info,
                "hour_info": hour_info
            }
            return json.dumps(calendar_data, ensure_ascii=False, indent=2)
        
        # 从数据库获取数据
        day_info = db.get_day_calendar(date_str)
        hour_info = db.get_hour_calendar(date_str)
        
        # 如果数据库中有数据，直接返回
        if day_info and hour_info:
            logger.info(f"从数据库获取黄历信息: {date_str}")
            calendar_data = {
                "day_info": day_info,
                "hour_info": hour_info
            }
            return json.dumps(calendar_data, ensure_ascii=False, indent=2)
        
        # 如果数据库中没有数据，从API获取
        logger.info(f"数据库中没有数据，从API获取: {date_str}")
        api = CalendarAPI()
        
        # 获取日维度数据信息
        if not day_info:
            day_info = api.get_day_calendar(year, month, day)
            # 将数据写入日志
            logger.info(f"日维度-{year}年{month}月{day}日: {json.dumps(day_info, ensure_ascii=False)}")
            # 保存到数据库
            db.save_day_calendar(date_str, day_info)
        
        # 获取小时维度数据
        if not hour_info:
            hour_info = api.get_hour_calendar(year, month, day)
            # 将数据写入日志
            logger.info(f"小时维度-{year}年{month}月{day}日: {json.dumps(hour_info, ensure_ascii=False)}")
            # 保存到数据库
            db.save_hour_calendar(date_str, hour_info)
        
        # 合并信息并转换为JSON字符串
        calendar_data = {
            "day_info": day_info,
            "hour_info": hour_info
        }
        
        return json.dumps(calendar_data, ensure_ascii=False, indent=2)
    except Exception as e:
        raise Exception(f"获取数据失败: {str(e)}")


def answer_question(question: str, force_refresh: bool = False) -> str:
    """
    回答问题
    
    Args:
        question: 用户问题（应该已经通过parse_question处理，包含具体日期）
        force_refresh: 是否强制从API获取最新数据，忽略缓存。默认为False
        
    Returns:
        str: 回答内容
    """
    try:
        # 从问题中提取日期（YYYY-MM-DD格式）
        date_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', question)
        if not date_match:
            # 如果没有找到日期，尝试其他格式
            date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', question)
            if not date_match:
                return "无法从问题中提取日期信息，请确保问题中包含具体日期（如2025-12-01）。"
        
        year = int(date_match.group(1))
        month = int(date_match.group(2))
        day = int(date_match.group(3))
        
        # 如果未指定force_refresh，则从问题中检测
        if not force_refresh:
            force_refresh_keywords = ["最新", "刷新", "重新获取", "更新", "重新拉取", "强制刷新", "重新查询"]
            force_refresh = any(keyword in question for keyword in force_refresh_keywords)
        
        # 获取黄历信息
        calendar_info = get_calander_info(year, month, day, force_refresh=force_refresh)
        
        # 判断是否需要关注时辰信息
        need_hour_info = any(keyword in question for keyword in ["时辰", "几点", "什么时候", "时间", "小时", "吉时", "面试"])
        
        # 从模板文件加载系统提示词
        system_prompt = _load_template("system_prompt")
        
        # 从模板文件加载并渲染用户提示词
        user_template = _jinja_env.get_template("user_prompt.j2")
        user_prompt = user_template.render(
            year=year,
            month=month,
            day=day,
            calendar_info=calendar_info,
            question=question,
            need_hour_info=need_hour_info
        )
        
        # 调用大模型
        llm = create_llm_client(provider="deepseek")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        # answer = llm.chat(messages, model="GLM-4-Flash-250414", temperature=0.7)
        answer = llm.chat(messages, model="deepseek-r1-250528", temperature=0.7)

        return answer
        
    except Exception as e:
        return f"处理问题时出错：{str(e)}"
