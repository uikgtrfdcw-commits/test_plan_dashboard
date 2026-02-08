import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = "1jxztmCu0gPYkYna05ZVGnnjGEnaJKKCx5YsF_fraerk"
SHEET1_TITLE = "Sheet1"
ARCHIVE_TITLE = "Archive"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

st.set_page_config(page_title="任务清单", layout="wide")


def _get_gspread_client() -> gspread.Client:
    conn_secrets = dict(st.secrets["connections"]["gsheets"])
    creds = Credentials.from_service_account_info(conn_secrets, scopes=SCOPES)
    return gspread.authorize(creds)


def render_table_with_rowspan(df: pd.DataFrame, title: str) -> None:
    st.subheader(title)
    if df.empty:
        st.info("无数据")
        return
    
    # Build HTML with rowspan for first column
    html = ['<table class="task-table">']
    
    # Header
    html.append('<thead><tr>')
    for col in df.columns:
        html.append(f'<th>{col}</th>')
    html.append('</tr></thead>')
    
    # Body with rowspan
    html.append('<tbody>')
    
    # Calculate rowspan for first column
    first_col = df.iloc[:, 0].tolist()
    i = 0
    while i < len(df):
        curr_val = first_col[i]
        span = 1
        while i + span < len(df) and first_col[i + span] == curr_val:
            span += 1
        
        # First row of the group
        html.append('<tr>')
        html.append(f'<td rowspan="{span}" class="merged-cell">{curr_val}</td>')
        for j in range(1, len(df.columns)):
            html.append(f'<td>{df.iloc[i, j]}</td>')
        html.append('</tr>')
        
        # Remaining rows in the group (skip first column)
        for k in range(1, span):
            html.append('<tr>')
            for j in range(1, len(df.columns)):
                html.append(f'<td>{df.iloc[i + k, j]}</td>')
            html.append('</tr>')
        
        i += span
    
    html.append('</tbody></table>')
    
    st.markdown(
        """
        <style>
        .task-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        .task-table th {
            background-color: #f0f2f6;
            padding: 10px 12px;
            text-align: left;
            font-weight: bold;
            font-size: 15px;
            border: 1px solid #ddd;
        }
        .task-table td {
            padding: 10px 12px;
            border: 1px solid #eee;
            vertical-align: middle;
            text-align: left;
        }
        .task-table .merged-cell {
            background-color: #fafafa;
            font-weight: 500;
            vertical-align: middle;
            text-align: left;
        }
        .task-table tr:hover td {
            background-color: #f5f5f5;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown(''.join(html), unsafe_allow_html=True)


try:
    gc = _get_gspread_client()
    sh = gc.open_by_key(SPREADSHEET_ID)
    
    ws1 = sh.worksheet(SHEET1_TITLE)
    values1 = ws1.get_all_values()
    if values1:
        df1 = pd.DataFrame(values1[1:], columns=values1[0])
        df1.iloc[:, 0] = df1.iloc[:, 0].replace("", pd.NA).ffill().fillna("")
        render_table_with_rowspan(df1, "📋 进行中")
    else:
        st.subheader("📋 进行中")
        st.info("无数据")
    
    st.divider()
    
    ws_archive = sh.worksheet(ARCHIVE_TITLE)
    values_archive = ws_archive.get_all_values()
    if values_archive:
        df_archive = pd.DataFrame(values_archive[1:], columns=values_archive[0])
        df_archive.iloc[:, 0] = df_archive.iloc[:, 0].replace("", pd.NA).ffill().fillna("")
        render_table_with_rowspan(df_archive, "✅ 已完成")
    else:
        st.subheader("✅ 已完成")
        st.info("无数据")

except Exception as e:
    st.error(f"连接失败：{e}")