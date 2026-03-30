"""
数据库连接模块
用于管理 MySQL 数据库连接和查询
"""

import pymysql
import pandas as pd
from typing import Optional, List, Dict, Any
import streamlit as st


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
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=10
            )
            return connection
        except pymysql.Error as e:
            st.error(f"❌ 数据库连接失败: {e}")
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
            st.error(f"❌ 查询执行失败: {e}")
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
            st.error(f"❌ 查询执行失败: {e}")
            return None


def get_db_connection() -> DatabaseConnection:
    """
    获取数据库连接对象
    从 Streamlit Secrets 读取配置
    """
    try:
        # 直接从 st.secrets 读取数据库配置
        host = st.secrets.get("database_host") or st.secrets.get("host")
        user = st.secrets.get("database_user") or st.secrets.get("user")
        password = st.secrets.get("database_password") or st.secrets.get("password")
        database = st.secrets.get("database_name") or st.secrets.get("database")
        
        # 如果上面的方式都不行，尝试读取 [database] 表
        if not all([host, user, password, database]):
            try:
                db_section = st.secrets["database"]
                host = db_section.get("host") or host
                user = db_section.get("user") or user
                password = db_section.get("password") or password
                database = db_section.get("database") or database
            except (KeyError, TypeError):
                pass
        
        # 验证所有必要的字段都已配置
        if not all([host, user, password, database]):
            missing = []
            if not host:
                missing.append("host")
            if not user:
                missing.append("user")
            if not password:
                missing.append("password")
            if not database:
                missing.append("database")
            
            st.error(
                f"❌ 数据库配置不完整！\n\n"
                f"缺少以下字段：{', '.join(missing)}\n\n"
                f"请在 Streamlit Cloud 的 Settings → Secrets 中添加：\n\n"
                f"```\n"
                f"[database]\n"
                f"host = \"203.55.176.41\"\n"
                f"user = \"fb_ads_admin\"\n"
                f"password = \"your_password\"\n"
                f"database = \"facebook_ads_data\"\n"
                f"```"
            )
            raise ValueError(f"数据库配置不完整，缺少字段：{missing}")
        
        return DatabaseConnection(
            host=host,
            user=user,
            password=password,
            database=database
        )
    
    except Exception as e:
        st.error(f"❌ 数据库配置读取失败：{str(e)}")
        raise
