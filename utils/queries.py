"""
数据查询模块
包含所有常用的 SQL 查询语句
"""

from typing import Optional
import pandas as pd
from utils.db_connection import get_db_connection


class AdQueries:
    """广告数据查询类"""
    
    @staticmethod
    def get_daily_performance(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        account_id: Optional[int] = None
    ) -> pd.DataFrame:
        """
        获取每日广告表现数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            account_id: 广告账户 ID
            
        Returns:
            DataFrame 包含每日表现数据
        """
        query = """
        SELECT 
            report_date,
            account_id,
            SUM(spend) as total_spend,
            SUM(impressions) as total_impressions,
            SUM(reach) as total_reach,
            SUM(link_clicks) as total_clicks,
            SUM(landing_page_views) as total_landing_page_views,
            SUM(post_engagement) as total_engagement,
            ROUND(SUM(spend) / NULLIF(SUM(impressions), 0) * 1000, 2) as cpm,
            ROUND(SUM(spend) / NULLIF(SUM(link_clicks), 0), 2) as cpc
        FROM fb_ad_insights_daily
        WHERE 1=1
        """
        
        params = []
        
        if start_date:
            query += " AND report_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND report_date <= %s"
            params.append(end_date)
        
        if account_id:
            query += " AND account_id = %s"
            params.append(account_id)
        
        query += " GROUP BY report_date, account_id ORDER BY report_date DESC"
        
        db = get_db_connection()
        return db.query_to_dataframe(query, tuple(params) if params else None)
    
    @staticmethod
    def get_account_list() -> pd.DataFrame:
        """
        获取所有广告账户列表
        
        Returns:
            DataFrame 包含账户信息
        """
        query = """
        SELECT 
            id,
            ad_account_id,
            account_name,
            currency,
            timezone_name,
            account_status_text,
            is_active
        FROM fb_ad_accounts
        ORDER BY account_name
        """
        
        db = get_db_connection()
        return db.query_to_dataframe(query)
    
    @staticmethod
    def get_spending_by_line(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取按产品线的支出数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            DataFrame 包含按产品线的支出
        """
        query = """
        SELECT 
            date,
            line,
            ad_name,
            SUM(spending) as total_spending
        FROM account_line_daily_spending
        WHERE 1=1
        """
        
        params = []
        
        if start_date:
            query += " AND date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= %s"
            params.append(end_date)
        
        query += " GROUP BY date, line, ad_name ORDER BY date DESC, total_spending DESC"
        
        db = get_db_connection()
        return db.query_to_dataframe(query, tuple(params) if params else None)
    
    @staticmethod
    def get_conversion_data(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        account_id: Optional[int] = None
    ) -> pd.DataFrame:
        """
        获取转化数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            account_id: 广告账户 ID
            
        Returns:
            DataFrame 包含转化数据
        """
        query = """
        SELECT 
            report_date,
            action_type,
            action_name,
            SUM(action_count) as total_actions,
            SUM(action_value) as total_value,
            ROUND(AVG(action_value), 2) as avg_value
        FROM fb_ad_insights_daily_conversions
        WHERE 1=1
        """
        
        params = []
        
        if start_date:
            query += " AND report_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND report_date <= %s"
            params.append(end_date)
        
        if account_id:
            query += " AND account_id = %s"
            params.append(account_id)
        
        query += " GROUP BY report_date, action_type, action_name ORDER BY report_date DESC"
        
        db = get_db_connection()
        return db.query_to_dataframe(query, tuple(params) if params else None)
    
    @staticmethod
    def get_ad_status_summary() -> pd.DataFrame:
        """
        获取广告状态摘要
        
        Returns:
            DataFrame 包含广告状态统计
        """
        query = """
        SELECT 
            status,
            COUNT(*) as ad_count
        FROM fb_ads
        WHERE effective_status IS NOT NULL
        GROUP BY status
        ORDER BY ad_count DESC
        """
        
        db = get_db_connection()
        return db.query_to_dataframe(query)
    
    @staticmethod
    def get_top_ads_by_spend(
        limit: int = 10,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取支出最高的广告
        
        Args:
            limit: 返回数量限制
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            DataFrame 包含支出最高的广告
        """
        query = f"""
        SELECT 
            ad.ad_name,
            SUM(insights.spend) as total_spend,
            SUM(insights.impressions) as total_impressions,
            SUM(insights.link_clicks) as total_clicks,
            ROUND(SUM(insights.spend) / NULLIF(SUM(insights.impressions), 0) * 1000, 2) as cpm
        FROM fb_ad_insights_daily insights
        JOIN fb_ads ad ON insights.ad_id = ad.ad_id
        WHERE 1=1
        """
        
        params = []
        
        if start_date:
            query += " AND insights.report_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND insights.report_date <= %s"
            params.append(end_date)
        
        query += f" GROUP BY ad.ad_name ORDER BY total_spend DESC LIMIT {limit}"
        
        db = get_db_connection()
        return db.query_to_dataframe(query, tuple(params) if params else None)
