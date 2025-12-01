"""
黄历API客户端模块
用于获取黄历信息
"""
import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional


class CalendarAPI:
    """黄历API客户端类"""
    
    def __init__(self):
        self.api_base_url = os.getenv("CALENDAR_BASE_URL")
        self.current_ip = None
        self.id = os.getenv("CALENDAR_API_ID", "")
        self.key = os.getenv("CALENDAR_API_KEY", "")
    
    def get_optimal_api_ip(self) -> str:
        """
        获取当前最优API接口地址
        
        Returns:
            str: API的IP地址
        """
        try:
            response = requests.get(self.api_base_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") == 200 and "api" in data:
                # 从api字段中提取IP地址
                api_url = data["api"]
                # 提取IP地址（去除http://和末尾的/）
                ip = api_url.replace("http://", "").replace("https://", "").rstrip("/")
                self.current_ip = ip
                return ip
            else:
                raise Exception(f"获取API地址失败: {data}")
        except Exception as e:
            raise Exception(f"获取最优API地址时出错: {str(e)}")
    
    def ensure_ip(self):
        """确保已获取IP地址"""
        if not self.current_ip:
            self.get_optimal_api_ip()
    
    def get_day_calendar(self, year: int, month: int, day: int) -> Dict:
        """
        获取某一天的黄历信息
        
        Args:
            year: 年份
            month: 月份
            day: 日期
            
        Returns:
            Dict: 黄历信息
        """
        self.ensure_ip()
        
        url = f"http://{self.current_ip}/api/time/getzdday.php"
        params = {
            "id": self.id,
            "key": self.key,
            "nian": year,
            "yue": month,
            "ri": day
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") == 200:
                return data
            else:
                raise Exception(f"获取黄历信息失败: {data}")
        except Exception as e:
            raise Exception(f"获取日期黄历信息时出错: {str(e)}")
    
    def get_hour_calendar(self, year: int, month: int, day: int) -> Dict:
        """
        获取某一天每个时辰的黄历信息
        
        Args:
            year: 年份
            month: 月份
            day: 日期
            
        Returns:
            Dict: 每个时辰的黄历信息
        """
        self.ensure_ip()
        
        url = f"http://{self.current_ip}/api/time/getzddayh.php"
        params = {
            "id": self.id,
            "key": self.key,
            "nian": year,
            "yue": month,
            "ri": day
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") == 200:
                return data
            else:
                raise Exception(f"获取时辰黄历信息失败: {data}")
        except Exception as e:
            raise Exception(f"获取时辰黄历信息时出错: {str(e)}")
