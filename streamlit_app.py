import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
import base64

# 版本号，确认更新成功
VERSION = "v2.6 (Stable)"
st.set_page_config(page_title=f"🚀 任务进度实时看板", layout="wide")
st.title(f"🚀 任务进度实时看板")

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if "gcp_json_b64" not in st.secrets:
            st.error("未检测到 gcp_json_b64 配置，请检查 Secrets。")
            st.stop()
            
        # 解码 Base64 密钥
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
        # ⚠️ 关键修正：使用机器人扫描出的真实名称
        SHEET_NAME = "Test plan" 
        spreadsheet = client.open(SHEET_NAME)
        worksheet = spreadsheet.get_worksheet(0)
        return pd.DataFrame(worksheet.get_all_records())
    except Exception as e:
        st.error(f"同步失败: {str(e)}")
        return None

# 数据渲染
df = load_data()
if df is not None:
    if df.empty:
        st.info("表格目前是空的，请在 Google Sheet 中填入数据。")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        if st.button("🔄 手动刷新数据"):
            st.cache_data.clear()
            st.rerun()

with st.sidebar:
    st.markdown(f"### 状态: {VERSION}")
    st.success("授权引擎：Base64 (Encoded)")
    st.write(f"连接表格: Test plan")
