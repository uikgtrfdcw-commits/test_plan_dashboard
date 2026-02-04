import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
import base64

# 版本号更新
VERSION = "v2.7 (Enhanced UI)"
st.set_page_config(page_title="🚀 任务进度实时看板", layout="wide")

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if "gcp_json_b64" not in st.secrets:
            st.error("未检测到 gcp_json_b64 配置")
            st.stop()
        b64_str = st.secrets["gcp_json_b64"]
        json_bytes = base64.b64decode(b64_str)
        creds_info = json.loads(json_bytes.decode('utf-8'))
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"授权失败: {str(e)}")
        st.stop()

def load_data():
    try:
        client = get_gspread_client()
        SHEET_NAME = "Test plan" 
        spreadsheet = client.open(SHEET_NAME)
        worksheet = spreadsheet.get_worksheet(0)
        return pd.DataFrame(worksheet.get_all_records())
    except Exception as e:
        st.error(f"同步失败: {str(e)}")
        return None

# --- 页面主逻辑 ---
st.title("🚀 任务进度实时看板")

df = load_data()

if df is not None:
    if df.empty:
        st.info("表格目前是空的，请在 Google Sheet 中填入数据。")
    else:
        # 使用 Streamlit 的高级列配置进行美化
        st.data_editor(
            df,
            column_config={
                "状态": st.column_config.SelectboxColumn(
                    "任务状态",
                    help="任务的当前进展情况",
                    options=["待开始", "进行中", "已完成"],
                    required=True,
                ),
                # 如果你的表格有“进度”列且是 0-1 之间的小数，可以使用进度条
                "进度": st.column_config.ProgressColumn(
                    "进度 (%)",
                    format="%.0f",
                    min_value=0,
                    max_value=100,
                ),
            },
            hide_index=True,
            use_container_width=True,
            disabled=df.columns, # 目前仅作为展示，锁定编辑功能
        )
        
        # 底部操作区
        col1, col2 = st.columns([1, 8])
        with col1:
            if st.button("🔄 刷新"):
                st.cache_data.clear()
                st.rerun()
        with col2:
            st.caption(f"最后同步时间: {pd.Timestamp.now().strftime('%H:%M:%S')} | 版本: {VERSION}")

with st.sidebar:
    st.markdown("### 📊 统计概览")
    if df is not None and not df.empty and "状态" in df.columns:
        done_count = len(df[df["状态"] == "已完成"])
        total_count = len(df)
        st.metric("任务完成率", f"{int(done_count/total_count*100) if total_count > 0 else 0}%")
        st.progress(done_count/total_count if total_count > 0 else 0.0)
    st.markdown("---")
    st.info("数据源: Google Sheet (Test plan)")
