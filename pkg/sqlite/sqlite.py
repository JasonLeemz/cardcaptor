"""
SQLite数据库操作模块
用于缓存黄历信息，避免重复调用API
"""
import sqlite3
import json
import os
import errno
from contextlib import contextmanager
from typing import Dict, Optional
from datetime import datetime


def _get_logger():
    """延迟获取logger，避免模块导入时的错误"""
    try:
        from pkg.log.log import get_logger
        return get_logger(None)
    except Exception:
        import logging
        return logging.getLogger(__name__)


def ensure_dir(path):
    """确保目录存在，如果不存在则创建"""
    if path and not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise e


def get_local_timestamp() -> str:
    """
    获取本地时间戳字符串（格式：YYYY-MM-DD HH:MM:SS）
    
    Returns:
        str: 本地时间戳字符串
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class SQLiteDB:
    """SQLite数据库操作类"""
    
    def __init__(self, db_path: str = "data/calendar.db"):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径，默认为 data/calendar.db
        """
        self.db_path = db_path
        self.logger = _get_logger()
        self._ensure_db_dir()
        self._init_connection()
        self._init_tables()
        self.logger.info(f"SQLite数据库初始化完成: {self.db_path}")
    
    def _ensure_db_dir(self):
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            ensure_dir(db_dir)
    
    def _init_connection(self):
        """
        初始化数据库连接
        测试连接是否正常
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("SELECT 1")
            conn.close()
            self.logger.debug("数据库连接测试成功")
        except Exception as e:
            self.logger.error(f"数据库连接初始化失败: {str(e)}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        获取数据库连接的上下文管理器
        自动处理事务提交和回滚
        
        Yields:
            sqlite3.Connection: 数据库连接对象
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            _get_logger().error(f"数据库操作失败: {str(e)}")
            raise
        finally:
            conn.close()
    
    def _init_tables(self):
        """初始化数据库表结构"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 创建日维度黄历信息表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS day_calendar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, -- id 主键自增
                    date TEXT UNIQUE NOT NULL,             -- date 日期格式，唯一键，不允许为空
                    data TEXT,                             -- data 数据 json格式 (SQLite 没有原生JSON类型，通常用TEXT存储)
                    create_time TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL, -- create_time 默认当前时间，不允许为空
                    update_time TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL  -- update_time 最后更新时间，默认当前时间，不允许为空
                    )
                """)
                
                # 创建小时维度黄历信息表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS hour_calendar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, -- id 主键自增
                    date TEXT UNIQUE NOT NULL,             -- date 日期格式，唯一键，不允许为空
                    data TEXT,                             -- data 数据 json格式 (SQLite 没有原生JSON类型，通常用TEXT存储)
                    create_time TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL, -- create_time 默认当前时间，不允许为空
                    update_time TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL  -- update_time 最后更新时间，默认当前时间，不允许为空
                    )
                """)
                
                # 创建唯一索引以提高查询性能并确保数据唯一性
                cursor.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_day_calendar_date 
                    ON day_calendar(date)
                """)
                
                cursor.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_hour_calendar_date 
                    ON hour_calendar(date) 
                """)
                
                conn.commit()
                self.logger.debug("数据库表结构初始化完成")
        except Exception as e:
            self.logger.error(f"初始化数据库表失败: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """
        测试数据库连接是否正常
        
        Returns:
            bool: 连接是否正常
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            self.logger.error(f"数据库连接测试失败: {str(e)}")
            return False
    
    def get_day_calendar(self, date: str) -> Optional[Dict]:
        """
        从数据库获取日维度黄历信息
        
        Args:
            date: 日期字符串，格式为 YYYY-MM-DD
            
        Returns:
            Optional[Dict]: 如果存在则返回数据字典，否则返回 None
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM day_calendar WHERE date = ?",
                    (date,)
                )
                row = cursor.fetchone()
                if row:
                    data_str = row["data"]
                    return json.loads(data_str) if data_str else None
                return None
        except Exception as e:
            self.logger.error(f"查询日维度黄历信息失败: {str(e)}")
            return None
    
    def save_day_calendar(self, date: str, data: Dict) -> bool:
        """
        保存日维度黄历信息到数据库
        
        Args:
            date: 日期字符串，格式为 YYYY-MM-DD
            data: 黄历数据字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 检查记录是否已存在
                cursor.execute("SELECT update_time FROM day_calendar WHERE date = ?", (date,))
                existing_row = cursor.fetchone()
                old_update_time = existing_row["update_time"] if existing_row else None
                
                data_str = json.dumps(data, ensure_ascii=False)
                current_time = get_local_timestamp()
                
                # 使用 INSERT ... ON CONFLICT 语法，更新时保留 create_time，只更新 update_time
                cursor.execute(
                    """INSERT INTO day_calendar (date, data, create_time, update_time) 
                       VALUES (?, ?, ?, ?)
                       ON CONFLICT(date) DO UPDATE SET 
                           data = excluded.data,
                           update_time = excluded.update_time""",
                    (date, data_str, current_time, current_time)
                )
                
                if old_update_time:
                    self.logger.info(f"更新日维度黄历信息: {date}, 旧时间: {old_update_time}, 新时间: {current_time}")
                else:
                    self.logger.info(f"新增日维度黄历信息: {date}, 时间: {current_time}")
                return True
        except Exception as e:
            self.logger.error(f"保存日维度黄历信息失败: {str(e)}")
            return False
    
    def get_hour_calendar(self, date: str) -> Optional[Dict]:
        """
        从数据库获取小时维度黄历信息
        
        Args:
            date: 日期字符串，格式为 YYYY-MM-DD
            
        Returns:
            Optional[Dict]: 如果存在则返回数据字典，否则返回 None
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM hour_calendar WHERE date = ?",
                    (date,)
                )
                row = cursor.fetchone()
                if row:
                    data_str = row["data"]
                    return json.loads(data_str) if data_str else None
                return None
        except Exception as e:
            self.logger.error(f"查询小时维度黄历信息失败: {str(e)}")
            return None
    
    def save_hour_calendar(self, date: str, data: Dict) -> bool:
        """
        保存小时维度黄历信息到数据库
        
        Args:
            date: 日期字符串，格式为 YYYY-MM-DD
            data: 黄历数据字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 检查记录是否已存在
                cursor.execute("SELECT update_time FROM hour_calendar WHERE date = ?", (date,))
                existing_row = cursor.fetchone()
                old_update_time = existing_row["update_time"] if existing_row else None
                
                data_str = json.dumps(data, ensure_ascii=False)
                current_time = get_local_timestamp()
                
                # 使用 INSERT ... ON CONFLICT 语法，更新时保留 create_time，只更新 update_time
                cursor.execute(
                    """INSERT INTO hour_calendar (date, data, create_time, update_time) 
                       VALUES (?, ?, ?, ?)
                       ON CONFLICT(date) DO UPDATE SET 
                           data = excluded.data,
                           update_time = excluded.update_time""",
                    (date, data_str, current_time, current_time)
                )
                
                if old_update_time:
                    self.logger.info(f"更新小时维度黄历信息: {date}, 旧时间: {old_update_time}, 新时间: {current_time}")
                else:
                    self.logger.info(f"新增小时维度黄历信息: {date}, 时间: {current_time}")
                return True
        except Exception as e:
            self.logger.error(f"保存小时维度黄历信息失败: {str(e)}")
            return False


# 单例模式的数据库实例
_db_instance: Optional[SQLiteDB] = None


def get_db(db_path: str = "data/calendar.db") -> SQLiteDB:
    """
    获取数据库实例（单例模式）
    
    Args:
        db_path: 数据库文件路径，默认为 data/calendar.db
        
    Returns:
        SQLiteDB: 数据库实例
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = SQLiteDB(db_path)
    return _db_instance


def init_db(db_path: str = "data/calendar.db") -> SQLiteDB:
    """
    初始化数据库连接
    
    Args:
        db_path: 数据库文件路径，默认为 data/calendar.db
        
    Returns:
        SQLiteDB: 数据库实例
    """
    return get_db(db_path)

