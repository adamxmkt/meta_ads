"""
数据库连接模块
用于管理 MySQL 数据库连接和查询
"""

import pymysql
import pandas as pd
from typing import Optional, List, Tuple, Any
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
            # 使用标准 Cursor，不使用 DictCursor
            connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset,
                connect_timeout=10
            )
            return connection
        except pymysql.Error as e:
            st.error(f"❌ 数据库连接失败: {e}")
            return None
    
    def query_to_dataframe(self, query: str, params: Optional[Tuple] = None) -> Optional[pd.DataFrame]:
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
            with connection.cursor() as cursor:
                # 执行查询
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # 获取列名
                columns = [desc[0] for desc in cursor.description]
                
                # 获取所有数据
                rows = cursor.fetchall()
            
            connection.close()
            
            # 如果没有数据，返回空 DataFrame
            if not rows:
                return pd.DataFrame(columns=columns)
            
            # 转换为 DataFrame
            df = pd.DataFrame(rows, columns=columns)
            
            return df
        
        except Exception as e:
            st.error(f"❌ 查询执行失败: {str(e)}")
            connection.close()
            return None


def get_db_connection() -> DatabaseConnection:
    """
    获取数据库连接对象
    从 Streamlit Secrets 读取配置
    """
    try:
        # 尝试多种方式读取数据库配置
        db_config = None
        
        # 方式 1: 直接读取顶级键
        try:
            if "database_host" in st.secrets:
                db_config = {
                    "host": st.secrets.get("database_host"),
                    "user": st.secrets.get("database_user"),
                    "password": st.secrets.get("database_password"),
                    "database": st.secrets.get("database_name")
                }
        except:
            pass
        
        # 方式 2: 读取 [database] 表
        if not db_config or not all(db_config.values()):
            try:
                db_section = st.secrets.get("database", {})
                if isinstance(db_section, dict):
                    db_config = {
                        "host": db_section.get("host"),
                        "user": db_section.get("user"),
                        "password": db_section.get("password"),
                        "database": db_section.get("database")
                    }
            except:
                pass
        
        # 方式 3: 使用简化的键名
        if not db_config or not all(db_config.values()):
            try:
                db_config = {
                    "host": st.secrets.get("host"),
                    "user": st.secrets.get("user"),
                    "password": st.secrets.get("password"),
                    "database": st.secrets.get("database")
                }
            except:
                pass
        
        # 验证配置
        if not db_config or not all(db_config.values()):
            st.error(
                "❌ 数据库配置未找到！\n\n"
                "请在 Streamlit Cloud 的 Settings → Secrets 中添加：\n\n"
                "```toml\n"
                "[database]\n"
                "host = \"203.55.176.41\"\n"
                "user = \"fb_ads_admin\"\n"
                "password = \"your_password\"\n"
                "database = \"facebook_ads_data\"\n"
                "```"
            )
            raise ValueError("数据库配置未找到")
        
        return DatabaseConnection(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"]
        )
    
    except Exception as e:
        st.error(f"❌ 数据库配置读取失败：{str(e)}")
        raise
