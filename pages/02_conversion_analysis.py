"""
转化分析页面
分析广告转化数据和转化价值
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils.queries import AdQueries


st.set_page_config(
    page_title="转化分析",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 转化分析")

# 侧边栏配置
st.sidebar.subheader("📅 时间范围")
date_range = st.sidebar.selectbox(
    "选择时间范围",
    ["最近 7 天", "最近 30 天", "最近 90 天", "自定义"],
    key="conversion_date_range"
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
        start_date = st.date_input("开始日期", end_date - timedelta(days=30), key="conversion_start")
    with col2:
        end_date = st.date_input("结束日期", end_date, key="conversion_end")

st.markdown(f"**时间范围**: {start_date} 至 {end_date}")
st.markdown("---")

# 获取转化数据
conversion_data = AdQueries.get_conversion_data(str(start_date), str(end_date))

if conversion_data is not None and not conversion_data.empty:
    # 转化总览
    st.subheader("📊 转化总览")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_actions = conversion_data["total_actions"].sum()
        st.metric("总转化数", f"{int(total_actions):,}")
    
    with col2:
        total_value = conversion_data["total_value"].sum()
        st.metric("转化总价值", f"${total_value:,.2f}")
    
    with col3:
        avg_value = conversion_data["avg_value"].mean()
        st.metric("平均转化价值", f"${avg_value:.2f}")
    
    with col4:
        unique_actions = conversion_data["action_type"].nunique()
        st.metric("转化类型数", f"{unique_actions}")
    
    st.markdown("---")
    
    # 按转化类型统计
    st.subheader("🎯 按转化类型统计")
    
    action_summary = conversion_data.groupby("action_type").agg({
        "total_actions": "sum",
        "total_value": "sum",
        "avg_value": "mean"
    }).reset_index().sort_values("total_actions", ascending=False)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_action_pie = px.pie(
            action_summary,
            values="total_actions",
            names="action_type",
            title="转化类型分布",
            labels={"total_actions": "转化数", "action_type": "转化类型"}
        )
        st.plotly_chart(fig_action_pie, use_container_width=True)
    
    with col2:
        st.dataframe(
            action_summary.rename(columns={
                "action_type": "转化类型",
                "total_actions": "转化数",
                "total_value": "总价值 ($)",
                "avg_value": "平均价值 ($)"
            }),
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # 每日转化趋势
    st.subheader("📈 每日转化趋势")
    
    daily_conversion = conversion_data.groupby("report_date").agg({
        "total_actions": "sum",
        "total_value": "sum"
    }).reset_index().sort_values("report_date")
    
    fig_daily = go.Figure()
    
    fig_daily.add_trace(go.Scatter(
        x=daily_conversion["report_date"],
        y=daily_conversion["total_actions"],
        name="转化数",
        yaxis="y1",
        mode="lines+markers",
        line=dict(color="#636EFA")
    ))
    
    fig_daily.add_trace(go.Scatter(
        x=daily_conversion["report_date"],
        y=daily_conversion["total_value"],
        name="转化价值",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color="#EF553B")
    ))
    
    fig_daily.update_layout(
        title="每日转化数和转化价值",
        xaxis=dict(title="日期"),
        yaxis=dict(title="转化数", titlefont=dict(color="#636EFA"), tickfont=dict(color="#636EFA")),
        yaxis2=dict(title="转化价值 ($)", titlefont=dict(color="#EF553B"), tickfont=dict(color="#EF553B"), overlaying="y", side="right"),
        hovermode="x unified",
        height=500
    )
    
    st.plotly_chart(fig_daily, use_container_width=True)
    
    st.markdown("---")
    
    # 按转化名称统计
    st.subheader("📋 按转化名称统计")
    
    action_name_summary = conversion_data.groupby("action_name").agg({
        "total_actions": "sum",
        "total_value": "sum",
        "avg_value": "mean"
    }).reset_index().sort_values("total_actions", ascending=False).head(20)
    
    fig_action_name = px.bar(
        action_name_summary,
        x="total_actions",
        y="action_name",
        orientation="h",
        title="转化最多的 20 个转化名称",
        labels={"total_actions": "转化数", "action_name": "转化名称"},
        color="total_value",
        color_continuous_scale="Viridis"
    )
    fig_action_name.update_layout(height=600)
    st.plotly_chart(fig_action_name, use_container_width=True)
    
    st.markdown("---")
    
    # 详细数据表格
    st.subheader("📊 详细数据")
    
    detailed_data = conversion_data.rename(columns={
        "report_date": "日期",
        "action_type": "转化类型",
        "action_name": "转化名称",
        "total_actions": "转化数",
        "total_value": "总价值 ($)",
        "avg_value": "平均价值 ($)"
    }).sort_values("日期", ascending=False)
    
    st.dataframe(
        detailed_data,
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("未能加载转化数据")
