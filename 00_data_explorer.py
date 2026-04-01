"""
数据探索页面 - 显示数据库中所有表的结构和数据样本
"""

import streamlit as st
import pandas as pd
from utils.db_connection import get_db_connection

st.set_page_config(
    page_title="数据探索",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 数据库数据探索")
st.markdown("---")

st.markdown("""
这个页面帮助你了解数据库中的所有表、字段和数据样本。
选择一个表来查看其结构和数据。
""")

st.markdown("---")


def get_all_tables():
    """获取数据库中的所有表"""
    query = """
    SELECT TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_SCHEMA = DATABASE()
    ORDER BY TABLE_NAME
    """
    db = get_db_connection()
    result = db.query_to_dataframe(query)
    if result is not None and not result.empty:
        return result["TABLE_NAME"].tolist()
    return []


def get_table_info(table_name):
    """获取表的列信息"""
    query = f"""
    SELECT 
        COLUMN_NAME,
        COLUMN_TYPE,
        IS_NULLABLE,
        COLUMN_KEY,
        EXTRA
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
    ORDER BY ORDINAL_POSITION
    """
    db = get_db_connection()
    return db.query_to_dataframe(query, (table_name,))


def get_table_row_count(table_name):
    """获取表的行数"""
    query = f"SELECT COUNT(*) as row_count FROM `{table_name}`"
    db = get_db_connection()
    result = db.query_to_dataframe(query)
    if result is not None and not result.empty:
        return result["row_count"].values[0]
    return 0


def get_table_sample(table_name, limit=10):
    """获取表的数据样本"""
    query = f"SELECT * FROM `{table_name}` LIMIT %s"
    db = get_db_connection()
    return db.query_to_dataframe(query, (limit,))


# 获取所有表
tables = get_all_tables()

if not tables:
    st.error("❌ 无法获取表列表，请检查数据库连接")
else:
    st.success(f"✅ 找到 {len(tables)} 个表")
    
    # 表选择
    selected_table = st.selectbox("选择要查看的表", tables)
    
    if selected_table:
        st.markdown(f"## 📊 表: `{selected_table}`")
        
        # 显示行数
        row_count = get_table_row_count(selected_table)
        st.metric("表中的行数", f"{row_count:,}")
        
        # 显示列信息
        st.subheader("📋 表结构（字段信息）")
        table_info = get_table_info(selected_table)
        
        if table_info is not None and not table_info.empty:
            # 格式化显示
            display_info = table_info.copy()
            st.dataframe(display_info, use_container_width=True)
        else:
            st.warning("⚠️ 无法获取表结构信息")
        
        # 显示数据样本
        st.subheader("📊 数据样本（前 10 行）")
        
        sample_data = get_table_sample(selected_table, 10)
        
        if sample_data is not None and not sample_data.empty:
            st.dataframe(sample_data, use_container_width=True)
            
            # 显示数据类型信息
            st.subheader("📈 数据类型统计")
            dtype_info = pd.DataFrame({
                "字段": sample_data.columns,
                "数据类型": [str(dtype) for dtype in sample_data.dtypes]
            })
            st.dataframe(dtype_info, use_container_width=True)
            
            # 显示列统计
            st.subheader("📊 列统计信息")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**数值列统计**")
                numeric_cols = sample_data.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    stats_df = sample_data[numeric_cols].describe().T
                    st.dataframe(stats_df, use_container_width=True)
                else:
                    st.info("ℹ️ 没有数值列")
            
            with col2:
                st.write("**空值统计**")
                null_counts = sample_data.isnull().sum()
                null_df = pd.DataFrame({
                    "字段": null_counts.index,
                    "空值数": null_counts.values,
                    "空值比例": (null_counts.values / len(sample_data) * 100).round(2)
                })
                st.dataframe(null_df, use_container_width=True)
        else:
            st.warning("⚠️ 表中没有数据或无法读取数据")
        
        # 显示所有表列表
        st.markdown("---")
        st.subheader("📚 所有表列表")
        
        tables_info = []
        for table in tables:
            count = get_table_row_count(table)
            tables_info.append({
                "表名": table,
                "行数": f"{count:,}"
            })
        
        tables_df = pd.DataFrame(tables_info)
        st.dataframe(tables_df, use_container_width=True)
