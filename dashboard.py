import streamlit as st
import boto3
import json
import time
import pandas as pd
import random
from datetime import datetime

# --- 1. CẤU HÌNH & STATE ---
st.set_page_config(
    page_title="Audit Buddy AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# KẾT NỐI AWS
try:
    sfn = boto3.client(
        'stepfunctions',
        region_name='ap_southeast_1',
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],
        aws_secret_access_key=st.secrets["AWS_SECRET_KEY"]
    )
    SFN_ARN = st.secrets["SFN_ARN"]
    DEMO_MODE = False
except:
    DEMO_MODE = True

# Init State
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "SYSTEM ONLINE. Awaiting Audit Files..."}]
if 'lang' not in st.session_state: st.session_state.lang = 'vi'
if 'theme' not in st.session_state: st.session_state.theme = 'dark' # Mặc định là Cyberpunk

# --- 2. LOGIC XỬ LÝ DỮ LIỆU (THÔNG MINH NHẤT) ---
def process_and_send(df):
    """Đọc DataFrame -> Tìm cột thông minh -> Gửi JSON"""
    # 1. Clean header
    df.columns = df.columns.str.lower().str.strip()
    payloads = []
    
    for _, row in df.iterrows():
        # 2. Auto-map columns
        inv = next((c for c in df.columns if 'invoice' in c or 'hóa đơn' in c or 'amount' in c), None)
        po = next((c for c in df.columns if 'po' in c or 'đơn hàng' in c), None)
        sup = next((c for c in df.columns if 'supplier' in c or 'nhà cung cấp' in c), None)
        email = next((c for c in df.columns if 'email' in c or 'liên hệ' in c), None)
        
        # 3. Logic tìm TÀI KHOẢN NGÂN HÀNG
        acc = next((c for c in df.columns if 'account' in c or 'stk' in c or 'bank' in c or 'tài khoản' in c), None)
        
        item = {
            "invoice_amount": float(row[inv]) if inv else 0.0,
            "po_amount": float(row[po]) if po else 0.0,
            "supplier": str(row[sup]) if sup else "UNKNOWN-ENTITY",
            "email": str(row[email]) if email else "N/A",
            "bank_account": str(row[acc]) if acc else "000000" # <-- Quan trọng
        }
        payloads.append(item)
    return payloads

def load_gsheet(url):
    try:
        if "docs.google.com" in url:
            csv_url = url.replace('/edit#gid=', '/export?format=csv&gid=').replace('/edit?gid=', '/export?format=csv&gid=')
            if "export" not in csv_url: csv_url += "/export?format=csv"
            return pd.read_csv(csv_url)
    except: return None

# --- 3. SIÊU CSS (CHUYỂN ĐỔI 2 PHONG CÁCH) ---
def inject_css():
    # A. PHONG CÁCH CYBERPUNK (DARK)
    if st.session_state.theme == 'dark':
        css = """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;800&display=swap');
            
            .stApp { background-color: #050505; color: #00FF41; font-family: 'JetBrains Mono', monospace; }
            h1, h2, h3 { color: #fff !important; text-shadow: 0 0 10px #00FF41; }
            
            /* Sidebar Matrix */
            [data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #00FF41; }
            [data-testid="stSidebar"] * { color: #00FF41 !important; font-family: 'JetBrains Mono'; }
            
            /* Card Hacker */
            .cute-card {
                background: #000; border: 1px solid #333; border-left: 3px solid #00FF41;
                padding: 20px; box-shadow: 0 0 15px rgba(0, 255, 65, 0.1); margin-bottom: 20px;
            }
            
            /* Input & Button */
            .stTextInput input { background: #111; color: #00FF41; border: 1px solid #333; border-radius: 0px; }
            .stButton button {
                background: transparent; border: 1px solid #00FF41; color: #00FF41;
                border-radius: 0px; font-weight: bold; transition: 0.3s;
            }
            .stButton button:hover { background: #00FF41; color: #000; box-shadow: 0 0 20px #00FF41; }
            
            /* Log Terminal Style */
            .log-entry { font-family: 'Courier New'; font-size: 0.9rem; border-bottom: 1px solid #111; padding: 2px 0; }
        </style>
        """
        
    # B. PHONG CÁCH PASTEL (LIGHT)
    else:
        css = """
        <style>
            .stApp { 
                background-image: url("https://img.freepik.com/free-vector/hand-painted-watercolor-pastel-sky-background_23-2148902771.jpg");
                background-size: cover; font-family: sans-serif;
            }
            h1, h2, h3, p, span, label { color: #333 !important; }
            
            /* Sidebar Cute */
            [data-testid="stSidebar"] { background-color: rgba(255,255,255,0.95) !important; }
            
            /* Card Glassmorphism */
            .cute-card {
                background: rgba(255,255,255,0.85); padding: 25px; border-radius: 20px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1); backdrop-filter: blur(10px);
                margin-bottom: 20px; border: 1px solid rgba(255, 255, 255, 0.18);
            }
            
            /* Input & Button */
            .stTextInput input { border-radius: 15px; border: 1px solid #ddd; }
            .stButton button {
                background: #E91E63; color: white; border-radius: 25px; border: none;
                box-shadow: 0 4px 10px rgba(233, 30, 99, 0.3); transition: 0.3s;
            }
            .stButton button:hover { transform: translateY(-3px); }
            
            /* Fix Uploader Text */
            [data-testid="stFileUploader"] span { color: #000 !important; font-weight: bold; }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)

# --- 4. DASHBOARD CHÍNH ---
def main_dashboard():
    
    # === A. SIDEBAR CÀI ĐẶT ===
    with st.sidebar:
        st.title("⚙️ SYSTEM CONFIG")
        
        # 1. Theme & Lang Logic
        def update_settings():
            st.session_state.lang = 'vi' if "Việt" in st.session_state.lang_sel else 'en'
            st.session_state.theme = 'light' if "Light" in st.session_state.theme_sel else 'dark'

        st.radio("Language / Ngôn ngữ", ["Tiếng Việt 🇻🇳", "English 🇬🇧"], key="lang_sel", on_change=update_settings, index=0 if st.session_state.lang=='vi' else 1)
        st.radio("Interface / Giao diện", ["Dark (Cyberpunk) ⚡", "Light (Pastel) 🌸"], key="theme_sel", on_change=update_settings, index=0 if st.session_state.theme=='dark' else 1)
        
        st.divider()
        
        # 2. Integrations (Bot Config)
        st.subheader("🔗 API Connectors")
        
        with st.expander("🔵 Telegram Bot"):
            if st.toggle("Activate Telegram"):
                st.text_input("Bot Token", type="password", placeholder="1234:ABC...")
                st.text_input("Chat ID", placeholder="-100...")
        
        with st.expander("🔵 Zalo OA"):
            if st.toggle("Activate Zalo"):
                st.text_input("OA ID", placeholder="Ex: 4628...")
                st.text_input("Secret Key", type="password")
                
        with st.expander("🟣 Slack"):
            if st.toggle("Activate Slack"):
                st.text_input("Webhook URL", type="password")

        # 3. Guides
        st.divider()
        st.subheader("📚 Documentation")
        guide = st.selectbox("Select Guide:", ["-- Select --", "Get Tele Token", "Get Zalo ID"])
        if guide == "Get Tele Token": st.info("Chat @BotFather -> /newbot")
        
        if st.button("🔴 LOGOUT SYSTEM"):
            st.session_state.logged_in = False
            st.rerun()

    inject_css()
    
    # === B. MAIN UI ===
    
    # Tiêu đề thay đổi theo Theme
    if st.session_state.theme == 'dark':
        st.markdown('<div style="text-align: center; font-size: 3rem; font-weight: 800; color: #fff; text-shadow: 0 0 20px #00FF41; margin-bottom: 20px;">/// AUDIT CORE V3 ///</div>', unsafe_allow_html=True)
    else:
        st.markdown('<h1 style="text-align: center; color: #E91E63;">✿ TRUNG TÂM KIỂM TOÁN AI ✿</h1>', unsafe_allow_html=True)

    col_L, col_R = st.columns([1.2, 1.8], gap="large")

    # === CỘT TRÁI: DATA INGESTION ===
    with col_L:
        st.markdown('<div class="cute-card">', unsafe_allow_html=True)
        tabs = st.tabs(["📂 UPLOAD", "☁️ GSHEET", "🔗 ONLINE"])
        
        payloads = []
        
        # TAB 1
        with tabs[0]:
            f = st.file_uploader("Drop .xlsx / .csv", type=['xlsx', 'csv'])
            if f:
                try:
                    df = pd.read_csv(f) if f.name.endswith('.csv') else pd.read_excel(f)
                    st.dataframe(df.head(3), height=100)
                    if st.button(">> EXECUTE BATCH", key="b1", type="primary"):
                        payloads = process_and_send(df)
                except Exception as e: st.error(f"Error: {e}")

        # TAB 2
        with tabs[1]:
            url = st.text_input("Google Sheet URL:")
            if url and st.button(">> SYNC DATA", key="b2"):
                df = load_gsheet(url)
                if df is not None:
                    st.dataframe(df.head(3), height=100)
                    payloads = process_and_send(df)
                else: st.error("Link Error")
        
        # TAB 3
        with tabs[2]:
            onl = st.text_input("Direct Excel Link:")
            if onl and st.button(">> FETCH URL", key="b3"):
                try:
                    df = pd.read_excel(onl)
                    st.dataframe(df.head(3), height=100)
                    payloads = process_and_send(df)
                except: st.error("Fetch Error")

        st.markdown('</div>', unsafe_allow_html=True)

    # === CỘT PHẢI: TERMINAL / CHATBOT ===
    with col_R:
        # Giao diện hiển thị (Terminal nếu Dark, Chatbox nếu Light)
        st.markdown('<div class="cute-card" style="height: 600px; overflow-y: auto;">', unsafe_allow_html=True)
        
        # LOGIC CHẠY REAL-TIME
        if payloads:
            st.subheader("🚀 PROCESS EXECUTION")
            
            terminal_placeholder = st.empty()
            logs = []
            progress = st.progress(0)
            
            for i, p in enumerate(payloads):
                # 1. Hiển thị Log chi tiết
                ts = datetime.now().strftime("%H:%M:%S")
                # Lấy số TK đã tìm được để show
                bk = p.get('bank_account', 'N/A')
                
                log_line = f"[{ts}] TXN #{i+1} | SUP: {p['supplier']} | BANK: {bk} -> SENDING..."
                logs.append(log_line)
                
                # Render Log (Màu mè theo theme)
                if st.session_state.theme == 'dark':
                    log_html = "<br>".join([f"<span class='log-entry' style='color: #00FF41'>{l}</span>" for l in logs[-15:]])
                else:
                    log_html = "<br>".join([f"<div style='border-bottom:1px solid #eee; padding:5px;'>{l}</div>" for l in logs[-15:]])
                
                terminal_placeholder.markdown(log_html, unsafe_allow_html=True)
                
                # 2. GỌI AWS THẬT
                if not DEMO_MODE:
                    try:
                        sfn.start_execution(stateMachineArn=SFN_ARN, input=json.dumps(p))
                    except: pass
                else: time.sleep(0.1) # Demo delay
                
                progress.progress((i+1)/len(payloads))
            
            st.success("✅ BATCH COMPLETED. ALL AGENTS ACTIVE.")
            st.balloons()
            
        else:
            # CHẾ ĐỘ CHỜ (IDLE) - Hiện Chatbot
            st.subheader("💬 AI ASSISTANT")
            
            # Chat UI
            chat_box = st.container()
            with chat_box:
                for msg in st.session_state.messages:
                    role_icon = "🤖" if msg["role"] == "assistant" else "👤"
                    st.markdown(f"**{role_icon}:** {msg['content']}")
                    st.markdown("---")
            
            if prompt := st.chat_input("Command Input..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. LOGIN SCREEN ---
def login_screen():
    # Login Style
    if st.session_state.theme == 'dark':
        st.markdown("""<style>.stApp { background-color: #000; color: #00FF41; }</style>""", unsafe_allow_html=True)
        box_style = "border: 2px solid #00FF41; background: #000; color: #00FF41;"
        btn_type = "primary" # Sẽ ăn theo theme dark
    else:
        st.markdown("""<style>.stApp { background-image: url("https://img.freepik.com/free-vector/hand-painted-watercolor-pastel-sky-background_23-2148902771.jpg"); background-size: cover; }</style>""", unsafe_allow_html=True)
        box_style = "background: rgba(255,255,255,0.9); box-shadow: 0 10px 30px rgba(0,0,0,0.1);"
        btn_type = "primary"

    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown(f'<div style="padding: 40px; border-radius: 20px; text-align: center; {box_style}">', unsafe_allow_html=True)
        st.markdown("<h1>ACCESS CONTROL</h1>", unsafe_allow_html=True)
        
        user = st.text_input("IDENTITY", placeholder="admin")
        pwd = st.text_input("PASSCODE", type="password", placeholder="123")
        
        if st.button(">> INITIALIZE LINK", type=btn_type, use_container_width=True):
            if user == "admin" and pwd == "123":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("ACCESS DENIED")
        st.markdown('</div>', unsafe_allow_html=True)

# ENTRY POINT
if st.session_state.logged_in:
    main_dashboard()
else:
    login_screen()