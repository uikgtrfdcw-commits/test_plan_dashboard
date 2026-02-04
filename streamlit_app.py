import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --- 1. 授权逻辑 (通过 Streamlit Secrets) ---
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # 这里的 secrets 对应 Streamlit Cloud 后台设置的键值对
    creds_dict = st.secrets["gcp_service_account"] 
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

# --- 2. 数据读取逻辑 ---
def fetch_data():
    client = get_gspread_client()
    spreadsheet_id = "1jxztmCu0gPYkYna05ZVGnnjGEnaJKKCx5YsF_fraerk"
    sheet = client.open_by_key(spreadsheet_id).sheet1
    # 读取所有数据并转为 DataFrame
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    return df

# --- 3. 网页展示界面 ---
st.set_page_config(page_title="Task Master 2.0", layout="wide")
st.title("🚀 任务进度实时看板")

try:
    df = fetch_data()
    
    # 按大类分组显示
    categories = df['任务大类'].unique()
    for cat in categories:
        st.subheader(f"📍 {cat}")
        cat_df = df[df['任务大类'] == cat][['任务描述', '状态']]
        st.table(cat_df)
        
    st.success(f"最后同步时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

except Exception as e:
    st.error(f"同步失败，请检查配置: {e}")

if st.button('手动刷新数据'):
    st.rerun()
