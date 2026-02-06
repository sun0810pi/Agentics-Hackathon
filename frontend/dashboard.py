import streamlit as st
import boto3
import json
import time
import pandas as pd
import plotly.express as px
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta
from collections import defaultdict

# --- 1. CẤU HÌNH & STATE ---
st.set_page_config(
    page_title="Audit Core V4 Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# KẾT NỐI AWS
try:
    sfn = boto3.client(
        'stepfunctions',
        region_name='ap-southeast-1',
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],
        aws_secret_access_key=st.secrets["AWS_SECRET_KEY"]
    )
    SFN_ARN = st.secrets["SFN_ARN"]
    DEMO_MODE = False
except:
    DEMO_MODE = True

# Init Enhanced State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "🤖 System initialized. Ready for audit operations."}]
if 'lang' not in st.session_state:
    st.session_state.lang = 'vi'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'transaction_history' not in st.session_state:
    st.session_state.transaction_history = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"
if 'agent_stats' not in st.session_state:
    st.session_state.agent_stats = {
        'agent1': {'processed': 0, 'failed': 0, 'status': 'idle'},
        'agent2': {'processed': 0, 'failed': 0, 'status': 'idle'},
        'agent3': {'processed': 0, 'failed': 0, 'status': 'idle'},
    }

# Integration Config Storage
if 'integrations' not in st.session_state:
    st.session_state.integrations = {
        'telegram': {'enabled': False, 'token': '', 'chat_id': ''},
        'zalo': {'enabled': False, 'oa_id': '', 'secret': ''},
        'slack': {'enabled': False, 'webhook': ''}
    }

# --- 2. TEXT LOCALIZATION ---
TEXTS = {
    'vi': {
        'control_panel': '⚙️ BẢN ĐIỀU KHIỂN',
        'config': 'Cấu hình',
        'language': 'Ngôn ngữ',
        'theme': 'Giao diện',
        'integrations': 'Kết nối Bot',
        'docs': 'Tài liệu',
        'logout': 'ĐĂNG XUẤT',
        'dashboard': 'Tổng quan',
        'upload': 'Tải dữ liệu',
        'history': 'Lịch sử',
        'analytics': 'Phân tích',
        'agents': 'Trạng thái Agents',
    },
    'en': {
        'control_panel': '⚙️ CONTROL PANEL',
        'config': 'Configuration',
        'language': 'Language',
        'theme': 'Theme',
        'integrations': 'Bot Connections',
        'docs': 'Documentation',
        'logout': 'LOGOUT',
        'dashboard': 'Dashboard',
        'upload': 'Data Upload',
        'history': 'History',
        'analytics': 'Analytics',
        'agents': 'Agent Status',
    }
}

def t(key):
    """Get translated text"""
    return TEXTS[st.session_state.lang].get(key, key)

# --- 3. LOGIC XỬ LÝ DỮ LIỆU ---

API_URL = "http://127.0.0.1:8000/api/v1/process-batch"

def send_to_api(payloads):
    try:
        # Gửi request POST sang FastAPI
        response = requests.post(API_URL, json=payloads)
        if response.status_code == 200:
            st.success(f"✅ Đã gửi thành công {len(payloads)} dòng sang hệ thống!")
            return response.json()
        else:
            st.error(f"❌ Lỗi Server: {response.text}")
            return None
    except Exception as e:
        st.error(f"❌ Không kết nối được Backend: {e}")
        return None

def process_and_send(df):
    """Đọc DataFrame -> Tìm cột thông minh -> Gửi JSON"""
    df.columns = df.columns.str.lower().str.strip()
    payloads = []
    
    for _, row in df.iterrows():
        inv = next((c for c in df.columns if 'invoice' in c or 'hóa đơn' in c or 'amount' in c), None)
        po = next((c for c in df.columns if 'po' in c or 'đơn hàng' in c), None)
        sup = next((c for c in df.columns if 'supplier' in c or 'nhà cung cấp' in c), None)
        email = next((c for c in df.columns if 'email' in c or 'liên hệ' in c), None)
        acc = next((c for c in df.columns if 'account' in c or 'stk' in c or 'bank' in c or 'tài khoản' in c), None)
        
        item = {
            "invoice_amount": float(row[inv]) if inv and pd.notna(row[inv]) else 0.0,
            "po_amount": float(row[po]) if po and pd.notna(row[po]) else 0.0,
            "supplier": str(row[sup]) if sup and pd.notna(row[sup]) else "UNKNOWN",
            "email": str(row[email]) if email and pd.notna(row[email]) else "N/A",
            "bank_account": str(row[acc]) if acc and pd.notna(row[acc]) else "000000"
        }
        payloads.append(item)
    return payloads

def load_gsheet(url):
    try:
        if "docs.google.com" in url:
            csv_url = url.replace('/edit#gid=', '/export?format=csv&gid=').replace('/edit?gid=', '/export?format=csv&gid=')
            if "export" not in csv_url:
                csv_url += "/export?format=csv"
            return pd.read_csv(csv_url)
    except:
        return None

def add_transaction_to_history(payload, status, execution_arn=None):
    """Add transaction to history"""
    st.session_state.transaction_history.append({
        'timestamp': datetime.now(),
        'tx_id': payload.get('transaction_id', 'N/A'),
        'supplier': payload.get('supplier', 'UNKNOWN'),
        'invoice_amount': payload.get('invoice_amount', 0),
        'po_amount': payload.get('po_amount', 0),
        'status': status,
        'execution_arn': execution_arn
    })

# --- 4. CSS CAO CẤP ---
def inject_css():
    if st.session_state.theme == 'dark':
        bg_url = "https://img.freepik.com/free-photo/abstract-digital-grid-black-background_53876-97647.jpg"
        text_color = "#00FFC2"
        card_bg = "rgba(0, 0, 0, 0.7)"
        sidebar_bg = "rgba(10, 10, 10, 0.95)"
        input_bg = "#111"
        border_color = "#00FFC2"
        metric_bg = "rgba(0, 255, 194, 0.1)"
        upload_fix = """
        [data-testid="stFileUploader"] { background-color: #0a0a0a; border: 1px dashed #00FFC2; }
        [data-testid="stFileUploader"] section > div { color: #fff !important; }
        """
    else:
        bg_url = "https://img.freepik.com/free-vector/white-abstract-background-design_23-2148825582.jpg"
        text_color = "#1f2937"
        card_bg = "rgba(255, 255, 255, 0.85)"
        sidebar_bg = "rgba(255, 255, 255, 0.95)"
        input_bg = "#f9fafb"
        border_color = "#3b82f6"
        metric_bg = "rgba(59, 130, 246, 0.1)"
        upload_fix = """
        [data-testid="stFileUploader"] { background-color: #f0f9ff; border: 2px dashed #3b82f6; }
        [data-testid="stFileUploader"] section > div { color: #000 !important; font-weight: 600; }
        """

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        .stApp {{
            background-image: url("{bg_url}");
            background-size: cover;
            background-attachment: fixed;
            font-family: 'Inter', sans-serif;
        }}
        
        h1, h2, h3, p, span, label, div {{ color: {text_color} !important; }}
        
        [data-testid="stSidebar"] {{ 
            background-color: {sidebar_bg} !important; 
            border-right: 1px solid rgba(255,255,255,0.1); 
            backdrop-filter: blur(10px);
        }}
        
        .glass-card {{
            background: {card_bg};
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 20px;
        }}
        
        .metric-card {{
            background: {metric_bg};
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid {border_color};
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 36px;
            font-weight: 800;
            color: {border_color} !important;
        }}
        
        .metric-label {{
            font-size: 14px;
            opacity: 0.8;
            margin-top: 5px;
        }}
        
        .stTextInput input {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
            border: 1px solid {border_color};
            border-radius: 8px;
        }}
        
        .stButton button {{
            background: linear-gradient(45deg, {border_color}, #8b5cf6);
            color: white !important;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s;
        }}
        
        .stButton button:hover {{
            transform: scale(1.02);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        .nav-button {{
            width: 100%;
            padding: 12px;
            margin: 5px 0;
            border-radius: 8px;
            border: none;
            background: transparent;
            color: {text_color};
            cursor: pointer;
            transition: all 0.2s;
            text-align: left;
            font-weight: 600;
        }}
        
        .nav-button:hover {{
            background: {metric_bg};
            transform: translateX(5px);
        }}
        
        .nav-button.active {{
            background: linear-gradient(45deg, {border_color}, #8b5cf6);
            color: white !important;
        }}
        
        {upload_fix}
        
        /* Agent status indicators */
        .agent-status {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }}
        
        .status-active {{ background: #10b981; box-shadow: 0 0 10px #10b981; }}
        .status-idle {{ background: #6b7280; }}
        .status-error {{ background: #ef4444; animation: pulse 1s infinite; }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        /* Transaction table */
        .tx-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .tx-table th {{
            background: {metric_bg};
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid {border_color};
        }}
        
        .tx-table td {{
            padding: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        .tx-table tr:hover {{
            background: {metric_bg};
        }}
        
        .status-badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .status-success {{ background: #10b981; color: white; }}
        .status-pending {{ background: #f59e0b; color: white; }}
        .status-failed {{ background: #ef4444; color: white; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. NAVIGATION ---
def render_sidebar_nav():
    """Render sidebar navigation with proper state management"""
    with st.sidebar:
        st.title(t('control_panel'))
        
        # Navigation buttons
        pages = [
            ("📊", t('dashboard')),
            ("📤", t('upload')),
            ("📜", t('history')),
            ("📈", t('analytics')),
            ("🤖", t('agents'))
        ]
        
        for icon, page_name in pages:
            active_class = "active" if st.session_state.current_page == page_name else ""
            if st.button(f"{icon} {page_name}", key=f"nav_{page_name}", use_container_width=True):
                st.session_state.current_page = page_name
                st.rerun()
        
        st.divider()
        
        # Settings
        st.caption(t('config'))
        
        def update_ui():
            st.session_state.lang = 'vi' if "Việt" in st.session_state.lang_sel else 'en'
            st.session_state.theme = 'light' if "Light" in st.session_state.theme_sel else 'dark'
        
        st.radio(
            t('language'),
            ["Tiếng Việt 🇻🇳", "English 🇬🇧"],
            key="lang_sel",
            on_change=update_ui,
            index=0 if st.session_state.lang == 'vi' else 1
        )
        
        st.radio(
            t('theme'),
            ["Dark (Cyber) ⚡", "Light (Clean) ☀️"],
            key="theme_sel",
            on_change=update_ui,
            index=0 if st.session_state.theme == 'dark' else 1
        )
        
        st.divider()
        
        # Integrations
        st.caption(t('integrations'))
        
        with st.expander("🔵 Telegram"):
            tele_enabled = st.toggle(
                "Enable",
                value=st.session_state.integrations['telegram']['enabled'],
                key="tele_toggle"
            )
            if tele_enabled:
                token = st.text_input(
                    "API Token",
                    type="password",
                    value=st.session_state.integrations['telegram']['token'],
                    key="tele_token"
                )
                chat_id = st.text_input(
                    "Chat ID",
                    value=st.session_state.integrations['telegram']['chat_id'],
                    key="tele_chat"
                )
                if st.button("💾 Save Telegram", key="save_tele"):
                    st.session_state.integrations['telegram'] = {
                        'enabled': True,
                        'token': token,
                        'chat_id': chat_id
                    }
                    st.success("✅ Saved!")
        
        with st.expander("🔵 Zalo OA"):
            zalo_enabled = st.toggle(
                "Enable",
                value=st.session_state.integrations['zalo']['enabled'],
                key="zalo_toggle"
            )
            if zalo_enabled:
                oa_id = st.text_input(
                    "OA ID",
                    value=st.session_state.integrations['zalo']['oa_id'],
                    key="zalo_oa"
                )
                secret = st.text_input(
                    "Secret Key",
                    type="password",
                    value=st.session_state.integrations['zalo']['secret'],
                    key="zalo_secret"
                )
                if st.button("💾 Save Zalo", key="save_zalo"):
                    st.session_state.integrations['zalo'] = {
                        'enabled': True,
                        'oa_id': oa_id,
                        'secret': secret
                    }
                    st.success("✅ Saved!")
        
        with st.expander("🟣 Slack"):
            slack_enabled = st.toggle(
                "Enable",
                value=st.session_state.integrations['slack']['enabled'],
                key="slack_toggle"
            )
            if slack_enabled:
                webhook = st.text_input(
                    "Webhook URL",
                    type="password",
                    value=st.session_state.integrations['slack']['webhook'],
                    key="slack_webhook"
                )
                if st.button("💾 Save Slack", key="save_slack"):
                    st.session_state.integrations['slack'] = {
                        'enabled': True,
                        'webhook': webhook
                    }
                    st.success("✅ Saved!")
        
        st.divider()
        
        if st.button(f"🔴 {t('logout')}", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

# --- 6. PAGE: DASHBOARD ---
def page_dashboard():
    inject_css()
    
    if st.session_state.theme == 'dark':
        st.markdown('<h1 style="text-align: center; text-shadow: 0 0 20px #00FFC2;">/// AUDIT CORE V4 PRO ///</h1>', unsafe_allow_html=True)
    else:
        st.markdown('<h1 style="text-align: center; color: #1e3a8a !important;">✿ FINANCIAL AUDIT DASHBOARD ✿</h1>', unsafe_allow_html=True)
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    total_tx = len(st.session_state.transaction_history)
    success_tx = len([t for t in st.session_state.transaction_history if t['status'] == 'SUCCESS'])
    failed_tx = len([t for t in st.session_state.transaction_history if t['status'] == 'FAILED'])
    
    total_amount = sum([t['invoice_amount'] for t in st.session_state.transaction_history])
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{total_tx}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total Transactions</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{success_tx}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">✅ Successful</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{failed_tx}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">❌ Failed</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">${total_amount:,.0f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total Amount</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent Activity
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📋 Recent Transactions")
    
    if st.session_state.transaction_history:
        recent = st.session_state.transaction_history[-10:][::-1]
        
        for tx in recent:
            status_class = {
                'SUCCESS': 'status-success',
                'FAILED': 'status-failed',
                'PENDING': 'status-pending'
            }.get(tx['status'], 'status-pending')
            
            col_a, col_b, col_c, col_d = st.columns([2, 2, 2, 1])
            
            with col_a:
                st.write(f"**{tx['supplier']}**")
            with col_b:
                st.write(f"${tx['invoice_amount']:,.2f}")
            with col_c:
                st.write(tx['timestamp'].strftime("%H:%M:%S %d/%m"))
            with col_d:
                st.markdown(f'<span class="status-badge {status_class}">{tx["status"]}</span>', unsafe_allow_html=True)
            
            st.divider()
    else:
        st.info("No transactions yet. Go to Upload page to start processing.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. PAGE: UPLOAD ---
def page_upload():
    inject_css()
    st.header("📤 Data Upload & Processing")
    
    col_L, col_R = st.columns([1.2, 1.8], gap="medium")
    
    with col_L:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📂 DATA SOURCE")
        
        tabs = st.tabs(["UPLOAD FILE", "GOOGLE SHEET", "DIRECT LINK"])
        payloads = []
        
        with tabs[0]:
            f = st.file_uploader("Excel / CSV", type=['xlsx', 'csv'], key="file_upload")
            if f:
                try:
                    df = pd.read_csv(f) if f.name.endswith('.csv') else pd.read_excel(f)
                    st.dataframe(df.head(5), use_container_width=True)
                    st.info(f"📊 Found {len(df)} records")
                    
                    if st.button("🚀 EXECUTE BATCH", key="exec_file", type="primary"):
                        # 1. Chuyển đổi dữ liệu
                        payloads = process_and_send(df)
                        # 2. Gửi sang FastAPI thật
                        send_to_api(payloads)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with tabs[1]:
            url = st.text_input("Google Sheet URL (Public):")
            if url and st.button("🚀 SYNC DATA", key="exec_gsheet", type="primary"):
                df = load_gsheet(url)
                if df is not None:
                    st.dataframe(df.head(5), use_container_width=True)
                    st.info(f"📊 Found {len(df)} records")
                    payloads = process_and_send(df)
                else:
                    st.error("Invalid Link or sheet not public")
        
        with tabs[2]:
            onl = st.text_input("Direct .xlsx/.csv URL:")
            if onl and st.button("🚀 FETCH", key="exec_link", type="primary"):
                try:
                    if onl.endswith('.csv'):
                        df = pd.read_csv(onl)
                    else:
                        df = pd.read_excel(onl)
                    st.dataframe(df.head(5), use_container_width=True)
                    st.info(f"📊 Found {len(df)} records")
                    payloads = process_and_send(df)
                except Exception as e:
                    st.error(f"Fetch Failed: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_R:
        st.markdown('<div class="glass-card" style="height: 650px; overflow-y: auto;">', unsafe_allow_html=True)
        
        if payloads:
            st.subheader("⚡ PROCESSING LOGS")
            log_container = st.empty()
            logs = []
            bar = st.progress(0)
            
            for i, p in enumerate(payloads):
                ts = datetime.now().strftime("%H:%M:%S")
                logs.append(f"[{ts}] TXN #{i+1} | {p['supplier']} | ${p['invoice_amount']:,.0f} → SENT")
                
                if st.session_state.theme == 'dark':
                    log_html = "<br>".join([f"<span style='color:#00FFC2; font-family:monospace'>{l}</span>" for l in logs[-15:]])
                else:
                    log_html = "<br>".join([f"<div style='border-bottom:1px solid #eee; padding:4px;'>{l}</div>" for l in logs[-15:]])
                
                log_container.markdown(log_html, unsafe_allow_html=True)
                
                # Send to AWS
                execution_arn = None
                status = "SUCCESS"
                if not DEMO_MODE:
                    try:
                        response = sfn.start_execution(
                            stateMachineArn=SFN_ARN,
                            input=json.dumps(p)
                        )
                        execution_arn = response['executionArn']
                    except Exception as e:
                        status = "FAILED"
                        st.error(f"AWS Error: {e}")
                else:
                    time.sleep(0.1)
                
                add_transaction_to_history(p, status, execution_arn)
                bar.progress((i+1)/len(payloads))
            
            st.success(f"✅ BATCH COMPLETED. Processed {len(payloads)} transactions.")
            st.balloons()
        else:
            st.info("👆 Upload data from the left panel to start processing")
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- 8. PAGE: HISTORY ---
def page_history():
    inject_css()
    st.header("📜 Transaction History")
    
    if not st.session_state.transaction_history:
        st.info("No transactions in history yet.")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            ["SUCCESS", "FAILED", "PENDING"],
            default=["SUCCESS", "FAILED", "PENDING"]
        )
    
    with col2:
        search_supplier = st.text_input("Search Supplier", "")
    
    with col3:
        date_filter = st.selectbox("Time Range", ["All", "Last 24h", "Last 7d", "Last 30d"])
    
    # Filter data
    filtered = st.session_state.transaction_history
    
    if status_filter:
        filtered = [t for t in filtered if t['status'] in status_filter]
    
    if search_supplier:
        filtered = [t for t in filtered if search_supplier.lower() in t['supplier'].lower()]
    
    if date_filter != "All":
        now = datetime.now()
        hours = {'Last 24h': 24, 'Last 7d': 168, 'Last 30d': 720}[date_filter]
        cutoff = now - timedelta(hours=hours)
        filtered = [t for t in filtered if t['timestamp'] >= cutoff]
    
    # Display
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write(f"**Showing {len(filtered)} of {len(st.session_state.transaction_history)} transactions**")
    
    # Create DataFrame for display
    df_display = pd.DataFrame(filtered)
    
    if not df_display.empty:
        df_display['timestamp'] = df_display['timestamp'].dt.strftime("%Y-%m-%d %H:%M:%S")
        
        st.dataframe(
            df_display[['timestamp', 'supplier', 'invoice_amount', 'po_amount', 'status']],
            use_container_width=True,
            hide_index=True
        )
        
        # Export
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Export to CSV",
            csv,
            "transaction_history.csv",
            "text/csv",
            key='download-csv'
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 9. PAGE: ANALYTICS ---
def page_analytics():
    inject_css()
    st.header("📈 Analytics & Insights")
    
    if not st.session_state.transaction_history:
        st.info("No data available for analytics yet.")
        return
    
    df = pd.DataFrame(st.session_state.transaction_history)
    
    # Chart 1: Status Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Transaction Status")
        
        status_counts = df['status'].value_counts()
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            color_discrete_sequence=['#10b981', '#ef4444', '#f59e0b']
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#00FFC2' if st.session_state.theme == 'dark' else '#1f2937'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Top Suppliers")
        
        top_suppliers = df.groupby('supplier').agg({
            'invoice_amount': 'sum'
        }).sort_values('invoice_amount', ascending=False).head(10)
        
        fig = px.bar(
            top_suppliers,
            y=top_suppliers.index,
            x='invoice_amount',
            orientation='h',
            color='invoice_amount',
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#00FFC2' if st.session_state.theme == 'dark' else '#1f2937',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chart 2: Transaction Timeline
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Transaction Timeline")
    
    df['date'] = df['timestamp'].dt.date
    timeline = df.groupby('date').size().reset_index(name='count')
    
    fig = px.line(
        timeline,
        x='date',
        y='count',
        markers=True,
        line_shape='spline'
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#00FFC2' if st.session_state.theme == 'dark' else '#1f2937'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 10. PAGE: AGENT STATUS ---
def page_agents():
    inject_css()
    st.header("🤖 Agent Status Monitor")
    
    col1, col2, col3 = st.columns(3)
    
    agents_info = [
        {
            'name': 'Agent 1',
            'role': 'Data Preprocessing',
            'icon': '🔧',
            'tasks': ['PII Masking', 'Data Validation', 'JSON Formatting']
        },
        {
            'name': 'Agent 2',
            'role': 'Transaction Analysis',
            'icon': '🔍',
            'tasks': ['Invoice-PO Comparison', 'Discrepancy Detection', 'Threshold Checking']
        },
        {
            'name': 'Agent 3',
            'role': 'AI Analysis',
            'icon': '🧠',
            'tasks': ['Gemini AI Processing', 'Risk Assessment', 'Report Generation']
        }
    ]
    
    for i, (col, info) in enumerate(zip([col1, col2, col3], agents_info)):
        agent_key = f'agent{i+1}'
        stats = st.session_state.agent_stats[agent_key]
        
        with col:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            
            # Status indicator
            status_class = {
                'active': 'status-active',
                'idle': 'status-idle',
                'error': 'status-error'
            }.get(stats['status'], 'status-idle')
            
            st.markdown(f"""
            <h3>{info['icon']} {info['name']}</h3>
            <p style="opacity: 0.8;">{info['role']}</p>
            <div style="margin: 15px 0;">
                <span class="agent-status {status_class}"></span>
                <span style="text-transform: uppercase; font-weight: 600;">{stats['status']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.metric("Processed", stats['processed'])
            st.metric("Failed", stats['failed'])
            
            with st.expander("📋 Tasks"):
                for task in info['tasks']:
                    st.write(f"• {task}")
            
            st.markdown('</div>', unsafe_allow_html=True)

# --- 11. LOGIN SCREEN ---
def login_screen():
    inject_css()
    
    if st.session_state.theme == 'dark':
        title_col = "#00FFC2"
        box_bg = "rgba(0,0,0,0.8)"
        border = "1px solid #00FFC2"
    else:
        title_col = "#1e3a8a"
        box_bg = "rgba(255,255,255,0.9)"
        border = "1px solid #ddd"
    
    c1, c2, c3 = st.columns([1, 1.5, 1])
    
    
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background: {box_bg}; padding: 40px; border-radius: 20px; text-align: center; border: {border}; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
            <h1 style="color: {title_col} !important;">🔒 SECURE LOGIN</h1>
            <p style="opacity: 0.8;">Audit Core V4 Pro</p>
        </div>
        """, unsafe_allow_html=True)
        
        user = st.text_input("Identity", placeholder="admin")
        pwd = st.text_input("Passcode", type="password", placeholder="***")
        
        if st.button("AUTHENTICATE", type="primary", use_container_width=True):
            if user == "admin" and pwd == "123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Access Denied")

# --- 12. MAIN ROUTER ---
def main():
    if not st.session_state.logged_in:
        login_screen()
        return
    
    render_sidebar_nav()
    
    # Route to pages
    if st.session_state.current_page == t('dashboard') or st.session_state.current_page == "Dashboard":
        page_dashboard()
    elif st.session_state.current_page == t('upload') or st.session_state.current_page == "Data Upload":
        page_upload()
    elif st.session_state.current_page == t('history') or st.session_state.current_page == "History":
        page_history()
    elif st.session_state.current_page == t('analytics') or st.session_state.current_page == "Analytics":
        page_analytics()
    elif st.session_state.current_page == t('agents') or st.session_state.current_page == "Agent Status":
        page_agents()

if __name__ == "__main__":
    main()
