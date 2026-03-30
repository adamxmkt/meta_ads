"""
Meta Ads 分析仪表板 - 调试版本
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.queries import AdQueries


st.set_page_config(
    page_title="Meta Ads Dashboard - Debug",
    page_icon="🐛",
    layout="wide"
)

st.title("🐛 Meta Ads Dashboard - 调试版本")

# 日期范围
end_date = datetime.now().date()
start_date = end_date - timedelta(days=7)

st.write(f"查询日期范围: {start_date} 至 {end_date}")

# 获取账户列表
st.subheader("1️⃣ 账户列表")
accounts_df = AdQueries.get_account_list()
if accounts_df is not None:
    st.write(f"✅ 获取了 {len(accounts_df)} 个账户")
    st.dataframe(accounts_df, use_container_width=True)
else:
    st.error("❌ 无法获取账户列表")

# 获取每日表现数据
st.subheader("2️⃣ 每日表现数据")
daily_perf = AdQueries.get_daily_performance(
    str(start_date),
    str(end_date),
    None
)

if daily_perf is not None:
    st.write(f"✅ 获取了 {len(daily_perf)} 行数据")
    st.write(f"**数据类型:**")
    st.write(daily_perf.dtypes)
    st.write(f"**数据形状:** {daily_perf.shape}")
    st.write(f"**列名:** {list(daily_perf.columns)}")
    st.write(f"**前几行数据:**")
    st.dataframe(daily_perf.head(10), use_container_width=True)
    
    # 尝试转换数据类型
    st.write(f"**数据样本 (原始):**")
    if len(daily_perf) > 0:
        first_row = daily_perf.iloc[0]
        st.write(first_row)
        
        st.write(f"**total_spend 值:** {first_row.get('total_spend', 'NOT FOUND')}")
        st.write(f"**total_spend 类型:** {type(first_row.get('total_spend', 'NOT FOUND'))}")
else:
    st.error("❌ 无法获取每日表现数据")

# 获取支出最高的广告
st.subheader("3️⃣ 支出最高的广告")
top_ads = AdQueries.get_top_ads_by_spend(
    limit=5,
    start_date=str(start_date),
    end_date=str(end_date)
)

if top_ads is not None:
    st.write(f"✅ 获取了 {len(top_ads)} 个广告")
    st.dataframe(top_ads, use_container_width=True)
else:
    st.error("❌ 无法获取支出数据")
