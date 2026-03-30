"""
数据库连接模块
用于管理 MySQL 数据库连接和查询
"""

import pymysql
import pandas as pd
from typing import Optional, List, Dict, Any
import streamlit as st
from functools import lru_cache


class DatabaseConnection:
    """MySQL 数据库连接类"""
    
    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        charset: str = 'utf8mb4'
    ):
        """
        初始化数据库连接参数
        
        Args:
            host: 数据库主机地址
            user: 数据库用户名
            password: 数据库密码
            database: 数据库名称
            charset: 字符集
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
    
    def get_connection(self):
        """获取数据库连接"""
        try:
            connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset,
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except pymysql.Error as e:
            st.error(f"数据库连接失败: {e}")
            return None
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> Optional[List[Dict[str, Any]]]:
        """
        执行查询并返回结果
        
        Args:
            query: SQL 查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        connection = self.get_connection()
        if connection is None:
            return None
        
        try:
            with connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                result = cursor.fetchall()
            connection.close()
            return result
        except pymysql.Error as e:
            st.error(f"查询执行失败: {e}")
            return None
    
    def query_to_dataframe(self, query: str, params: Optional[tuple] = None) -> Optional[pd.DataFrame]:
        """
        执行查询并返回 DataFrame
        
        Args:
            query: SQL 查询语句
            params: 查询参数
            
        Returns:
            Pandas DataFrame
        """
        connection = self.get_connection()
        if connection is None:
            return None
        
        try:
            df = pd.read_sql(query, connection, params=params)
            connection.close()
            return df
        except Exception as e:
            st.error(f"查询执行失败: {e}")
            return None


@st.cache_resource
def get_db_connection() -> DatabaseConnection:
    """
    获取缓存的数据库连接对象
    使用 Streamlit 的缓存来避免重复创建连接
    """
    # 从 Streamlit secrets 读取数据库配置
    db_config = st.secrets.get("database", {})
    
    # 如果没有配置，使用默认值
    if not db_config:
        db_config = {
            "host": "203.55.176.41",
            "user": "fb_ads_admin",
            "password": "ILqTmJb0Xaq7uxS6UulVoXgBZl8ytqcP",
            "database": "facebook_ads_data"
        }
    
    return DatabaseConnection(
        host=db_config.get("host"),
        user=db_config.get("user"),
        password=db_config.get("password"),
        database=db_config.get("database")
    )
