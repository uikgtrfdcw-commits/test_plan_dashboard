import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# 设置网页标题
st.set_page_config(page_title="🚀 任务进度实时看板", layout="wide")
st.title("🚀 任务进度实时看板")

def get_gspread_client():
    """
    授权并连接 Google Sheets
    """
    # 定义授权范围
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        # 从 Streamlit Secrets 读取配置
        if "gcp_service_account" not in st.secrets:
            st.error("未检测到 Secrets 配置，请在 Streamlit Cloud 后台设置 [gcp_service_account]")
            st.stop()
            
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        # --- 核心修复逻辑：处理私钥中的转义和编码问题 ---
        raw_key = creds_dict["private_key"]
        
        # 1. 移除首尾可能存在的空格/回车
        fixed_key = raw_key.strip()
        
        # 2. 如果私钥中包含字面量的 \n (字符串)，将其替换为真正的换行符
        if "\\n" in fixed_key:
            fixed_key = fixed_key.replace("\\n", "\n")
            
        creds_dict["private_key"] = fixed_key
        # ----------------------------------------------

        # 授权
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
        # 打开工作表（确保您的 Google Sheet 名字叫 test-plan-dashboard）
        # 也可以使用 .open_by_key("你的表格ID")
        sheet = client.open("test-plan-dashboard").get_worksheet(0)
        
        # 读取所有记录
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"同步失败，请检查配置: {str(e)}")
        return None

# 执行加载
df = load_data()

if df is not None:
    if df.empty:
        st.warning("表格内容为空，请在 Google Sheet 中添加数据。")
    else:
        # 简单的样式美化
        st.dataframe(
            df, 
            use_container_width=True,
            hide_index=True
        )
        
        # 自动刷新按钮
        if st.button("🔄 手动刷新数据"):
            st.cache_data.clear()
            st.rerun()

# 侧边栏说明
with st.sidebar:
    st.markdown("### 📊 状态说明")
    st.info("数据每 15 分钟自动同步，或点击刷新按钮手动同步。")
    st.markdown("---")
    st.write("版本: v2.0 (Stable)")
