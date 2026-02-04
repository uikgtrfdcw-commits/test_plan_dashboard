import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json

# 修改版本号，确保你能看到页面更新了
VERSION = "v2.3 (Final Fix)"
st.set_page_config(page_title=f"🚀 任务进度看板 {VERSION}", layout="wide")
st.title(f"🚀 任务进度看板 {VERSION}")

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # 直接读取原始 JSON 字符串
        if "gcp_json_raw" not in st.secrets:
            st.error("未检测到 gcp_json_raw 配置，请检查 Secrets。")
            st.stop()
            
        # 使用 json.loads 自动处理所有转义和编码问题，这是最稳的方法
        creds_info = json.loads(st.secrets["gcp_json_raw"])
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"授权失败: {str(e)}")
        st.stop()

def load_data():
    try:
        client = get_gspread_client()
        # 确认你的 Google Sheet 名字叫 test-plan-dashboard
        sheet = client.open("test-plan-dashboard").get_worksheet(0)
        return pd.DataFrame(sheet.get_all_records())
    except Exception as e:
        st.error(f"同步失败: {str(e)}")
        return None

# 渲染逻辑
df = load_data()
if df is not None:
    st.dataframe(df, use_container_width=True, hide_index=True)
    if st.button("🔄 刷新数据"):
        st.cache_data.clear()
        st.rerun()

with st.sidebar:
    st.markdown(f"### 状态: {VERSION}")
    st.info("已切换至 JSON-Raw 授权引擎")
