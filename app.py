"""
Meta Ads 分析仪表板 - 简化版本
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.queries import AdQueries


st.set_page_config(
    page_title="Meta Ads Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def safe_convert_to_float(value):
    """安全地将值转换为浮点数"""
    try:
        if value is None or pd.isna(value):
            return 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def safe_convert_to_int(value):
    """安全地将值转换为整数"""
    try:
        if value is None or pd.isna(value):
            return 0
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def safe_metric(label, value, format_type="number"):
    """安全地显示指标"""
    try:
        if format_type == "currency":
            value_float = safe_convert_to_float(value)
            st.metric(label, f"${value_float:,.2f}")
        elif format_type == "integer":
            value_int = safe_convert_to_int(value)
            st.metric(label, f"{value_int:,}")
        else:
            st.metric(label, value)
    except Exception as e:
        st.metric(label, "N/A")


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
    
    account_id = None
    if accounts_df is not None and not accounts_df.empty:
        account_options = ["全部账户"] + accounts_df["account_name"].tolist()
        selected_account = st.sidebar.selectbox("选择账户", account_options)
        
        if selected_account != "全部账户":
            account_id = accounts_df[accounts_df["account_name"] == selected_account]["id"].values[0]
    else:
        st.sidebar.warning("⚠️ 无法加载账户列表")
    
    st.sidebar.markdown("---")
    
    # 主内容区域
    st.title("📊 Meta Ads 分析仪表板")
    st.markdown(f"**时间范围**: {start_date} 至 {end_date}")
    
    # 获取数据
    with st.spinner("📊 正在加载数据..."):
        daily_perf = AdQueries.get_daily_performance(
            str(start_date),
            str(end_date),
            account_id
        )
    
    if daily_perf is not None and not daily_perf.empty:
        st.success("✅ 数据加载成功")
        
        # 数据类型转换
        try:
            # 确保所有数值列都是数字类型
            numeric_columns = ["total_spend", "total_impressions", "total_clicks", "cpm"]
            for col in numeric_columns:
                if col in daily_perf.columns:
                    daily_perf[col] = pd.to_numeric(daily_perf[col], errors="coerce")
        except Exception as e:
            st.warning(f"⚠️ 数据类型转换出现问题: {e}")
        
        # 关键指标
        st.subheader("📈 关键指标")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_spend = daily_perf["total_spend"].sum()
            safe_metric("总支出", total_spend, format_type="currency")
        
        with col2:
            total_impressions = daily_perf["total_impressions"].sum()
            safe_metric("总展示数", total_impressions, format_type="integer")
        
        with col3:
            total_clicks = daily_perf["total_clicks"].sum()
            safe_metric("总点击数", total_clicks, format_type="integer")
        
        with col4:
            avg_cpm = daily_perf["cpm"].mean()
            safe_metric("平均 CPM", avg_cpm, format_type="currency")
        
        st.markdown("---")
        
        # 数据表格
        st.subheader("📋 详细数据")
        display_df = daily_perf.sort_values("report_date", ascending=False).copy()
        
        # 格式化显示
        if "total_spend" in display_df.columns:
            display_df["total_spend"] = display_df["total_spend"].apply(lambda x: f"${safe_convert_to_float(x):,.2f}")
        if "cpm" in display_df.columns:
            display_df["cpm"] = display_df["cpm"].apply(lambda x: f"${safe_convert_to_float(x):.2f}")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # 数据统计
        st.subheader("📊 数据统计")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("数据行数", len(daily_perf))
        
        with col2:
            st.metric("日期范围", f"{daily_perf['report_date'].min()} 至 {daily_perf['report_date'].max()}")
        
        with col3:
            st.metric("平均每日支出", f"${safe_convert_to_float(daily_perf['total_spend'].mean()):,.2f}")
    
    else:
        st.warning("⚠️ 未能加载数据")
        st.info("请检查：")
        st.write("1. 时间范围是否正确")
        st.write("2. 数据库连接是否正常")
        st.write("3. 选定的账户是否有数据")


if __name__ == "__main__":
    main()
