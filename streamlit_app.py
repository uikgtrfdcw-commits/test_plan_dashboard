import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import re

# 设置网页标题
st.set_page_config(page_title="🚀 任务进度实时看板", layout="wide")
st.title("🚀 任务进度实时看板")

def get_gspread_client():
    """
    授权并连接 Google Sheets（带 Base64 容错处理）
    """
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        if "gcp_service_account" not in st.secrets:
            st.error("未检测到 Secrets 配置，请在 Streamlit 后台设置 [gcp_service_account]")
            st.stop()
            
        # 复制字典防止修改原始只读对象
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        # --- 🛡️ 核心修复逻辑：彻底清理 Base64 杂质 ---
        pk = str(creds_dict["private_key"])
        header = "-----BEGIN PRIVATE KEY-----"
        footer = "-----END PRIVATE KEY-----"
        
        if header in pk and footer in pk:
            # 1. 提取 Header 和 Footer 之间的核心编码内容
            content = pk.split(header)[1].split(footer)[0]
            # 2. 移除所有空白符（空格、换行、回车）以及字面量的 \n 字符
            # 这一步会干掉那个导致 65 字符报错的“多余字符”
            clean_body = re.sub(r'\s+', '', content).replace("\\n", "")
            # 3. 重新拼装为标准的、无杂质的 PEM 格式
            creds_dict["private_key"] = f"{header}\n{clean_body}\n{footer}\n"
        # ----------------------------------------------

        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    
    except Exception as e:
        st.error(f"授权失败，请检查配置: {str(e)}")
        st.stop()

def load_data():
    """
    从 Google Sheets 加载数据
    """
    try:
        client = get_gspread_client()
        # 确保您的 Google Sheet 名字叫 test-plan-dashboard
        sheet = client.open("test-plan-dashboard").get_worksheet(0)
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"同步失败，请检查配置: {str(e)}")
        return None

# 执行页面渲染逻辑
df = load_data()

if df is not None:
    if df.empty:
        st.warning("表格内容为空，请在 Google Sheet 中添加数据。")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        if st.button("🔄 手动刷新数据"):
            st.cache_data.clear()
            st.rerun()

with st.sidebar:
    st.markdown("### 📊 指挥中心说明")
    st.info("已启用 v2.1 自动纠错授权引擎")
    st.markdown("---")
    st.write("状态: 云端运行中")
