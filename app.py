"""
Meta Ads 分析仪表板 - 简化版本
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from utils.queries import AdQueries


st.set_page_config(
    page_title="Meta Ads Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def safe_metric(label, value, default="N/A"):
    """安全地显示指标"""
    try:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            st.metric(label, default)
        else:
            st.metric(label, value)
    except Exception as e:
        st.metric(label, default)


def main():
    """主函数"""
    
    st.sidebar.title("📊 Meta Ads Dashboard")
    st.sidebar.markdown("---")
    
    # 日期范围选择
    st.sidebar.subheader("📅 时间范围")
    date_range = st.sidebar.selectbox(
        "选择时间范围",
        ["最近 7 天", "最近 30 天", "最近 90 天", "自定义"],
        key="date_range"
    )
    
    end_date = datetime.now().date()
    if date_range == "最近 7 天":
        start_date = end_date - timedelta(days=7)
    elif date_range == "最近 30 天":
        start_date = end_date - timedelta(days=30)
    elif date_range == "最近 90 天":
        start_date = end_date - timedelta(days=90)
    else:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("开始日期", end_date - timedelta(days=30))
        with col2:
            end_date = st.date_input("结束日期", end_date)
    
    # 账户选择
    st.sidebar.subheader("🏢 广告账户")
    accounts_df = AdQueries.get_account_list()
    
    if accounts_df is not None and not accounts_df.empty:
        account_options = ["全部账户"] + accounts_df["account_name"].tolist()
        selected_account = st.sidebar.selectbox("选择账户", account_options)
        
        if selected_account != "全部账户":
            account_id = accounts_df[accounts_df["account_name"] == selected_account]["id"].values[0]
        else:
            account_id = None
    else:
        st.sidebar.warning("无法加载账户列表")
        account_id = None
    
    st.sidebar.markdown("---")
    
    # 主内容区域
    st.title("📊 Meta Ads 分析仪表板")
    st.markdown(f"**时间范围**: {start_date} 至 {end_date}")
    
    # 获取数据
    daily_perf = AdQueries.get_daily_performance(
        str(start_date),
        str(end_date),
        account_id
    )
    
    if daily_perf is not None and not daily_perf.empty:
        st.success("✅ 数据加载成功")
        
        # 关键指标
        st.subheader("📈 关键指标")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_spend = daily_perf["total_spend"].sum()
            safe_metric("总支出", f"${float(total_spend):,.2f}" if total_spend > 0 else "$0.00")
        
        with col2:
            total_impressions = daily_perf["total_impressions"].sum()
            safe_metric("总展示数", f"{int(total_impressions):,}" if total_impressions > 0 else "0")
        
        with col3:
            total_clicks = daily_perf["total_clicks"].sum()
            safe_metric("总点击数", f"{int(total_clicks):,}" if total_clicks > 0 else "0")
        
        with col4:
            avg_cpm = daily_perf["cpm"].mean()
            safe_metric("平均 CPM", f"${float(avg_cpm):.2f}" if avg_cpm > 0 else "$0.00")
        
        st.markdown("---")
        
        # 数据表格
        st.subheader("📋 详细数据")
        st.dataframe(
            daily_perf.sort_values("report_date", ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("⚠️ 未能加载数据，请检查时间范围或数据库连接")


if __name__ == "__main__":
    main()
