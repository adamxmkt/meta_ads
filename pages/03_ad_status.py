"""
广告状态页面
显示广告状态统计和管理信息
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.queries import AdQueries


st.set_page_config(
    page_title="广告状态",
    page_icon="📢",
    layout="wide"
)

st.title("📢 广告状态")

st.markdown("---")

# 获取广告状态摘要
st.subheader("📊 广告状态统计")

ad_status = AdQueries.get_ad_status_summary()

if ad_status is not None and not ad_status.empty:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 广告状态饼图
        fig_status = px.pie(
            ad_status,
            values="ad_count",
            names="status",
            title="广告状态分布",
            labels={"ad_count": "广告数量", "status": "状态"}
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # 状态统计表格
        st.dataframe(
            ad_status.rename(columns={"status": "状态", "ad_count": "广告数量"}),
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # 广告状态条形图
    st.subheader("📈 广告状态条形图")
    
    fig_bar = px.bar(
        ad_status,
        x="status",
        y="ad_count",
        title="各状态广告数量",
        labels={"status": "状态", "ad_count": "广告数量"},
        color="ad_count",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    
    # 获取账户列表
    st.subheader("🏢 广告账户信息")
    
    accounts = AdQueries.get_account_list()
    
    if accounts is not None and not accounts.empty:
        st.dataframe(
            accounts.rename(columns={
                "id": "账户 ID",
                "ad_account_id": "广告账户 ID",
                "account_name": "账户名称",
                "currency": "货币",
                "timezone_name": "时区",
                "account_status_text": "账户状态",
                "is_active": "是否活跃"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("暂无账户信息")

else:
    st.warning("未能加载广告状态数据")

st.markdown("---")

# 帮助信息
st.subheader("ℹ️ 帮助信息")

help_text = """
### 广告状态说明

- **ACTIVE**: 广告正在运行中
- **PAUSED**: 广告已暂停
- **ARCHIVED**: 广告已归档
- **DELETED**: 广告已删除

### 账户状态说明

- **ACTIVE**: 账户处于活跃状态
- **DISABLED**: 账户已禁用
- **UNSETTLED**: 账户未结算

如有任何问题，请联系管理员。
"""

st.markdown(help_text)
