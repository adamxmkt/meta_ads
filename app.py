"""
Meta Ads 分析仪表板
主应用程序入口
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from utils.queries import AdQueries


# 页面配置
st.set_page_config(
    page_title="Meta Ads Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    """主函数"""
    
    # 侧边栏配置
    st.sidebar.title("📊 Meta Ads Dashboard")
    st.sidebar.markdown("---")
    
    # 日期范围选择
    st.sidebar.subheader("📅 时间范围")
    date_range = st.sidebar.selectbox(
        "选择时间范围",
        ["最近 7 天", "最近 30 天", "最近 90 天", "自定义"],
        key="date_range"
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
        # 关键指标
        st.subheader("📈 关键指标")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_spend = daily_perf["total_spend"].sum()
            if pd.notna(total_spend):
                st.metric("总支出", f"${float(total_spend):,.2f}")
            else:
                st.metric("总支出", "N/A")
        
        with col2:
            total_impressions = daily_perf["total_impressions"].sum()
            if pd.notna(total_impressions):
                st.metric("总展示数", f"{int(total_impressions):,}")
            else:
                st.metric("总展示数", "N/A")
        
        with col3:
            total_clicks = daily_perf["total_clicks"].sum()
            if pd.notna(total_clicks):
                st.metric("总点击数", f"{int(total_clicks):,}")
            else:
                st.metric("总点击数", "N/A")
        
        with col4:
            avg_cpm = daily_perf["cpm"].mean()
            if pd.notna(avg_cpm):
                st.metric("平均 CPM", f"${float(avg_cpm):.2f}")
            else:
                st.metric("平均 CPM", "N/A")
        
        st.markdown("---")
        
        # 每日支出趋势
        st.subheader("💰 每日支出趋势")
        daily_spend = daily_perf.groupby("report_date")["total_spend"].sum().reset_index()
        daily_spend = daily_spend.sort_values("report_date")
        daily_spend["total_spend"] = daily_spend["total_spend"].astype(float)
        
        fig_spend = px.line(
            daily_spend,
            x="report_date",
            y="total_spend",
            title="每日支出",
            labels={"report_date": "日期", "total_spend": "支出 ($)"},
            markers=True
        )
        fig_spend.update_layout(hovermode="x unified")
        st.plotly_chart(fig_spend, use_container_width=True)
        
        # 展示数和点击数
        st.subheader("📊 展示数和点击数")
        col1, col2 = st.columns(2)
        
        with col1:
            daily_impressions = daily_perf.groupby("report_date")["total_impressions"].sum().reset_index()
            daily_impressions = daily_impressions.sort_values("report_date")
            daily_impressions["total_impressions"] = daily_impressions["total_impressions"].astype(int)
            
            fig_impressions = px.bar(
                daily_impressions,
                x="report_date",
                y="total_impressions",
                title="每日展示数",
                labels={"report_date": "日期", "total_impressions": "展示数"},
                color_discrete_sequence=["#636EFA"]
            )
            st.plotly_chart(fig_impressions, use_container_width=True)
        
        with col2:
            daily_clicks = daily_perf.groupby("report_date")["total_clicks"].sum().reset_index()
            daily_clicks = daily_clicks.sort_values("report_date")
            daily_clicks["total_clicks"] = daily_clicks["total_clicks"].astype(int)
            
            fig_clicks = px.bar(
                daily_clicks,
                x="report_date",
                y="total_clicks",
                title="每日点击数",
                labels={"report_date": "日期", "total_clicks": "点击数"},
                color_discrete_sequence=["#EF553B"]
            )
            st.plotly_chart(fig_clicks, use_container_width=True)
        
        # CPM 和 CPC 分析
        st.subheader("💹 成本指标分析")
        col1, col2 = st.columns(2)
        
        with col1:
            cpm_data = daily_perf.groupby("report_date")[["cpm"]].mean().reset_index()
            cpm_data = cpm_data.sort_values("report_date")
            
            fig_cpm = px.line(
                cpm_data,
                x="report_date",
                y="cpm",
                title="每日平均 CPM",
                labels={"report_date": "日期", "cpm": "CPM ($)"},
                markers=True,
                color_discrete_sequence=["#00CC96"]
            )
            st.plotly_chart(fig_cpm, use_container_width=True)
        
        with col2:
            cpc_data = daily_perf.groupby("report_date")[["cpc"]].mean().reset_index()
            cpc_data = cpc_data.sort_values("report_date")
            
            fig_cpc = px.line(
                cpc_data,
                x="report_date",
                y="cpc",
                title="每日平均 CPC",
                labels={"report_date": "日期", "cpc": "CPC ($)"},
                markers=True,
                color_discrete_sequence=["#AB63FA"]
            )
            st.plotly_chart(fig_cpc, use_container_width=True)
        
        # 数据表格
        st.subheader("📋 详细数据")
        st.dataframe(
            daily_perf.sort_values("report_date", ascending=False),
            use_container_width=True,
            hide_index=True
        )
    
    else:
        st.warning("未能加载数据，请检查数据库连接或时间范围设置")


if __name__ == "__main__":
    main()
