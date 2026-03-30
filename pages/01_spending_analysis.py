"""
支出分析页面
分析按产品线的支出情况和广告支出排行
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils.queries import AdQueries


st.set_page_config(
    page_title="支出分析",
    page_icon="💰",
    layout="wide"
)

st.title("💰 支出分析")

# 侧边栏配置
st.sidebar.subheader("📅 时间范围")
date_range = st.sidebar.selectbox(
    "选择时间范围",
    ["最近 7 天", "最近 30 天", "最近 90 天", "自定义"],
    key="spending_date_range"
)

# 计算日期
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
        start_date = st.date_input("开始日期", end_date - timedelta(days=30), key="spending_start")
    with col2:
        end_date = st.date_input("结束日期", end_date, key="spending_end")

st.markdown(f"**时间范围**: {start_date} 至 {end_date}")
st.markdown("---")

# 按产品线的支出
st.subheader("📊 按产品线的支出")

spending_by_line = AdQueries.get_spending_by_line(str(start_date), str(end_date))

if spending_by_line is not None and not spending_by_line.empty:
    # 按产品线汇总
    line_summary = spending_by_line.groupby("line")["total_spending"].sum().reset_index()
    line_summary = line_summary.sort_values("total_spending", ascending=False)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 产品线支出饼图
        fig_pie = px.pie(
            line_summary,
            values="total_spending",
            names="line",
            title="按产品线的支出分布",
            labels={"total_spending": "支出 ($)", "line": "产品线"}
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # 产品线支出表格
        st.dataframe(
            line_summary.rename(columns={"line": "产品线", "total_spending": "总支出 ($)"}),
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # 按日期和产品线的支出趋势
    st.subheader("📈 按产品线的每日支出趋势")
    
    daily_line_spending = spending_by_line.groupby(["date", "line"])["total_spending"].sum().reset_index()
    daily_line_spending = daily_line_spending.sort_values("date")
    
    fig_line_trend = px.line(
        daily_line_spending,
        x="date",
        y="total_spending",
        color="line",
        title="每日支出趋势（按产品线）",
        labels={"date": "日期", "total_spending": "支出 ($)", "line": "产品线"},
        markers=True
    )
    fig_line_trend.update_layout(hovermode="x unified")
    st.plotly_chart(fig_line_trend, use_container_width=True)
    
    st.markdown("---")
    
    # 支出最高的广告
    st.subheader("🏆 支出最高的广告")
    
    top_ads = AdQueries.get_top_ads_by_spend(limit=15, start_date=str(start_date), end_date=str(end_date))
    
    if top_ads is not None and not top_ads.empty:
        fig_top_ads = px.bar(
            top_ads,
            x="total_spend",
            y="ad_name",
            orientation="h",
            title="支出最高的 15 个广告",
            labels={"total_spend": "总支出 ($)", "ad_name": "广告名称"},
            color="cpm",
            color_continuous_scale="Viridis"
        )
        fig_top_ads.update_layout(height=600)
        st.plotly_chart(fig_top_ads, use_container_width=True)
        
        st.markdown("---")
        
        # 详细表格
        st.subheader("📋 详细数据")
        st.dataframe(
            top_ads.rename(columns={
                "ad_name": "广告名称",
                "total_spend": "总支出 ($)",
                "total_impressions": "展示数",
                "total_clicks": "点击数",
                "cpm": "CPM ($)"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("暂无支出最高的广告数据")
    
    st.markdown("---")
    
    # 原始数据
    st.subheader("📊 原始数据")
    st.dataframe(
        spending_by_line.rename(columns={
            "date": "日期",
            "line": "产品线",
            "ad_name": "广告名称",
            "total_spending": "支出 ($)"
        }).sort_values("日期", ascending=False),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("未能加载支出数据")
