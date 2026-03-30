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
    try:
        # 尝试从 Streamlit secrets 读取数据库配置
        # 处理不同的 Secrets 格式
        
        # 方式 1: 使用字典访问
        if hasattr(st.secrets, "database"):
            db_config = st.secrets["database"]
        else:
            # 方式 2: 使用 get 方法
            db_config = st.secrets.get("database", {})
        
        # 确保 db_config 是字典
        if isinstance(db_config, str):
            st.error(
                "❌ 数据库配置格式错误！\n\n"
                "Secrets 应该是一个表 [database]，而不是字符串。\n\n"
                "正确格式：\n"
                "```\n"
                "[database]\n"
                "host = \"your_host\"\n"
                "user = \"your_user\"\n"
                "password = \"your_password\"\n"
                "database = \"your_database\"\n"
                "```"
            )
            raise ValueError("数据库配置格式错误")
        
        # 如果没有配置，抛出错误
        if not db_config or not isinstance(db_config, dict):
            st.error(
                "❌ 数据库配置未找到！\n\n"
                "请在 Streamlit Cloud 的 Settings → Secrets 中添加：\n\n"
                "```\n"
                "[database]\n"
                "host = \"203.55.176.41\"\n"
                "user = \"fb_ads_admin\"\n"
                "password = \"your_password\"\n"
                "database = \"facebook_ads_data\"\n"
                "```"
            )
            raise ValueError("数据库配置未找到或格式错误")
        
        # 检查必要的字段
        required_fields = ["host", "user", "password", "database"]
        missing_fields = [field for field in required_fields if field not in db_config]
        
        if missing_fields:
            st.error(f"❌ 数据库配置缺少以下字段：{', '.join(missing_fields)}")
            raise ValueError(f"数据库配置缺少字段：{missing_fields}")
        
        return DatabaseConnection(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"]
        )
    
    except Exception as e:
        st.error(f"❌ 数据库连接配置错误：{str(e)}")
        raise
