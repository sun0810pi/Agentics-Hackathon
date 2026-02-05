import streamlit as st
import boto3
import json
import time
import random
import pandas as pd
import io
from datetime import datetime

# --- 1. CẤU HÌNH TRANG & KẾT NỐI AWS ---
st.set_page_config(
    page_title="Agentics Fintech Core",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Thử kết nối AWS
try:
    # --- THAY KEY THẬT CỦA BẠN VÀO ĐÂY NẾU CHƯA CÓ TRONG SECRETS ---
    # AWS_ACCESS_KEY = "AKIA_..." 
    # AWS_SECRET_KEY = "..."
    # SFN_ARN = "arn:aws:states:..."
    
    sfn = boto3.client(
        'stepfunctions',
        region_name='ap_southeast_1',
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],
        aws_secret_access_key=st.secrets["AWS_SECRET_KEY"]
    )
    SFN_ARN = st.secrets["SFN_ARN"]
    DEMO_MODE = False
except:
    DEMO_MODE = True # Chế độ diễn tập nếu chưa có Key

# --- 2. GIAO DIỆN CYBERPUNK (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'JetBrains Mono', monospace;
        background-color: #0E1117;
        color: #00FFC2;
    }
    
    /* Tabs Styling - Chỉ còn 2 tab nên chỉnh lại cho đẹp */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #0E1117;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        color: #8B949E;
        border-radius: 4px;
        padding: 15px 20px; /* To hơn xíu */
        flex-grow: 1; /* Căn đều */
        text-align: center;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #00FFC2 !important;
        color: #000 !important;
        border-color: #00FFC2 !important;
        font-weight: bold;
    }

    /* Terminal Window */
    .terminal-window {
        background-color: #000000;
        border: 1px solid #333;
        border-left: 4px solid #A020F0;
        padding: 15px;
        font-family: 'Courier New', monospace;
        color: #00FF00;
        height: 450px;
        overflow-y: auto;
        border-radius: 5px;
        box-shadow: inset 0 0 20px rgba(0, 255, 0, 0.1);
    }

    /* Tiêu đề */
    .neon-title {
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #00FFC2, #A020F0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 15px rgba(0, 255, 194, 0.4);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HÀM XỬ LÝ DỮ LIỆU ---
def load_gsheet(url):
    try:
        if "docs.google.com" in url:
            csv_url = url.replace('/edit#gid=', '/export?format=csv&gid=').replace('/edit?gid=', '/export?format=csv&gid=')
            if "export" not in csv_url: csv_url += "/export?format=csv"
            return pd.read_csv(csv_url)
    except: return None

def normalize_data(df):
    """Chuẩn hóa mọi file Excel/CSV về định dạng JSON chuẩn"""
    df.columns = df.columns.str.lower().str.strip()
    payloads = []
    for _, row in df.iterrows():
        # Tự động tìm cột thông minh
        inv = next((c for c in df.columns if 'invoice' in c or 'hóa đơn' in c), None)
        po = next((c for c in df.columns if 'po' in c or 'đơn hàng' in c), None)
        sup = next((c for c in df.columns if 'supplier' in c or 'cung cấp' in c), None)
        email = next((c for c in df.columns if 'email' in c or 'mail' in c), None)
        
        payloads.append({
            "invoice_amount": float(row[inv]) if inv else 0.0,
            "po_amount": float(row[po]) if po else 0.0,
            "supplier": str(row[sup]) if sup else "Unknown",
            "email": str(row[email]) if email else "N/A"
        })
    return payloads

# --- 4. HEADER & KPI ---
st.markdown('<div class="neon-title">/// AGENTICS AUDIT HUB ///</div>', unsafe_allow_html=True)

# KPI Giả lập
k1, k2, k3, k4 = st.columns(4)
k1.metric("SYSTEM STATUS", "ONLINE", "Stable")
k2.metric("LATENCY", f"{random.randint(40, 90)}ms", "-12ms")
k3.metric("AGENTS", "5 ACTIVE", "Ready")
k4.metric("AI CONFIDENCE", "98.5%", "+2%")
st.divider()

# --- 5. MAIN INTERFACE ---
col_left, col_right = st.columns([1.2, 1.8], gap="large")

payloads_queue = [] # Danh sách chờ xử lý

with col_left:
    st.subheader("📥 DATA INGESTION CHANNEL")
    
    # CHỈ CÒN 2 TAB: EXCEL & GOOGLE SHEET
    tab_excel, tab_sheet = st.tabs(["📂 EXCEL UPLOAD (BATCH)", "☁️ GOOGLE SHEET (REAL-TIME)"])
    
    # --- TAB 1: EXCEL ---
    with tab_excel:
        st.markdown("For large volume historical audit logs.")
        uploaded = st.file_uploader("Drop .xlsx / .csv here", type=['xlsx', 'csv'])
        if uploaded:
            try:
                df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
                st.dataframe(df.head(5), height=150, use_container_width=True)
                st.info(f"Detected {len(df)} transactions.")
                
                if st.button(f"🚀 EXECUTE BATCH AUDIT", type="primary", use_container_width=True):
                    payloads_queue = normalize_data(df)
            except Exception as e: st.error(f"Error reading file: {e}")

    # --- TAB 2: GOOGLE SHEET ---
    with tab_sheet:
        st.markdown("For live data sync from branches.")
        st.warning("⚠️ Ensure Sheet link is 'Public/Anyone with link'")
        sheet_url = st.text_input("Paste Google Sheet URL:", placeholder="https://docs.google.com/spreadsheets/d/...")
        
        if sheet_url:
            df_sheet = load_gsheet(sheet_url)
            if df_sheet is not None:
                st.success("✅ Connected to Google Cloud!")
                st.dataframe(df_sheet.head(5), height=150, use_container_width=True)
                
                if st.button(f"🚀 SYNC & AUDIT LIVE DATA", type="primary", use_container_width=True):
                    payloads_queue = normalize_data(df_sheet)
            else:
                st.error("Cannot read Sheet. Check permissions.")

with col_right:
    st.subheader("🖥 SYSTEM CONSOLE")
    terminal = st.empty()
    
    logs = ["[SYSTEM READY] Waiting for data stream...", "> Channel secure.", "> Agent Swarm standby."]
    
    # HÀM LOGGING GIẢ LẬP
    def update_log(msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        logs.append(f"[{timestamp}] > {msg}")
        if len(logs) > 15: logs.pop(0) # Giữ terminal gọn
        log_html = "<br>".join([f"<span style='color:#00FF00'>{l}</span>" for l in logs])
        terminal.markdown(f'<div class="terminal-window">{log_html}</div>', unsafe_allow_html=True)
        time.sleep(0.05) # Chạy nhanh hơn xíu cho Batch lớn

    # --- XỬ LÝ KHI CÓ DỮ LIỆU ---
    if payloads_queue:
        update_log(f"📥 RECEIVED BATCH: {len(payloads_queue)} TRANSACTIONS")
        update_log("🔄 INITIALIZING AGENT WORKFLOW...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, payload in enumerate(payloads_queue):
            sup_id = payload.get('supplier', 'Unknown')
            amt = payload.get('invoice_amount', 0)
            
            # Hiệu ứng Log chạy liên tục kiểu Matrix
            update_log(f"PROCESSING TXN #{i+1}: {sup_id} | ${amt:,.0f}")
            status_text.text(f"Audit Progress: {int((i+1)/len(payloads_queue)*100)}%")
            
            # GỌI AWS THẬT (Hoặc Demo)
            if not DEMO_MODE:
                try:
                    sfn.start_execution(stateMachineArn=SFN_ARN, input=json.dumps(payload))
                    # update_log(f"--> SENT TO AGENT 1 [OK]") # Tắt dòng này cho đỡ spam nếu nhiều
                except Exception as e:
                    update_log(f"--> ERROR: {str(e)}")
            else:
                time.sleep(0.1) # Demo mode delay
            
            progress_bar.progress((i + 1) / len(payloads_queue))
        
        update_log("✅ BATCH COMPLETED. ALL AGENTS FINISHED.")
        update_log("📊 GENERATING FINAL COMPLIANCE REPORT...")
        st.success(f"✅ Đã xử lý xong {len(payloads_queue)} giao dịch! Kiểm tra Slack/Email để xem kết quả.")
        st.balloons()
    
    else:
        # Hiển thị log mặc định
        update_log("Monitoring active channels...")