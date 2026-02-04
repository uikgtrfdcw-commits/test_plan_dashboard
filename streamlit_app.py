import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import re

st.set_page_config(page_title="🚀 任务进度实时看板", layout="wide")
st.title("🚀 任务进度实时看板")

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if "gcp_service_account" not in st.secrets:
            st.error("未检测到 Secrets 配置")
            st.stop()
            
        creds_dict = dict(st.secrets["gcp_service_account"])
        pk = str(creds_dict["private_key"])
        
        # --- 🛡️ v2.2 暴力修复逻辑：剔除所有非 Base64 字符 ---
        # 1. 提取核心：只保留 BEGIN 和 END 之间的部分
        content = pk.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
        
        # 2. 物理剔除：删掉所有换行、空格、反斜杠、字母n
        # 这一步能彻底解决那个“多出来的 1 个字符”
        clean_body = re.sub(r'[^A-Za-z0-9+/=]', '', content)
        
        # 3. 长度补偿：Base64 必须是 4 的倍数
        # 如果长度余 1，说明最后一个字符是多余的杂质，直接扔掉
        if len(clean_body) % 4 == 1:
            clean_body = clean_body[:-1]
            
        # 4. 重新合成标准的 PEM 格式
        creds_dict["private_key"] = f"-----BEGIN PRIVATE KEY-----\n{clean_body}\n-----END PRIVATE KEY-----\n"
        # ----------------------------------------------

        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"授权失败: {str(e)}")
        st.stop()

def load_data():
    try:
        client = get_gspread_client()
        # 注意：请确保你的 Google Sheet 文件名完全匹配 "test-plan-dashboard"
        sheet = client.open("test-plan-dashboard").get_worksheet(0)
        return pd.DataFrame(sheet.get_all_records())
    except Exception as e:
        st.error(f"同步失败: {str(e)}")
        return None

df = load_data()
if df is not None:
    st.dataframe(df, use_container_width=True, hide_index=True)
    if st.button("🔄 刷新数据"):
        st.cache_data.clear()
        st.rerun()
