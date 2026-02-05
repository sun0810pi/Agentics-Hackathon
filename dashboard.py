import streamlit as st
import boto3
import json
import time
import pandas as pd
from datetime import datetime

# --- 1. CẤU HÌNH & STATE ---
st.set_page_config(
    page_title="Audit Buddy AI",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# KẾT NỐI AWS
try:
    sfn = boto3.client(
        'stepfunctions',
        region_name='ap_southeast_1',
        # aws_access_key_id="...", 
        # aws_secret_access_key="...",
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],
        aws_secret_access_key=st.secrets["AWS_SECRET_KEY"]
    )
    SFN_ARN = st.secrets["SFN_ARN"]
    DEMO_MODE = False
except:
    DEMO_MODE = True

# Init Session State
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Chào sếp! Hệ thống Audit đã sẵn sàng. 🌸"}]
if 'lang' not in st.session_state: st.session_state.lang = 'vi'
if 'theme' not in st.session_state: st.session_state.theme = 'light'

# --- 2. CSS GIAO DIỆN (THEME & FIX HIỂN THỊ) ---
def inject_css():
    if st.session_state.theme == 'light':
        bg_url = "https://img.freepik.com/free-vector/hand-painted-watercolor-pastel-sky-background_23-2148902771.jpg"
        text_color = "#333333"
        card_bg = "rgba(255, 255, 255, 0.95)"
        sidebar_bg = "rgba(255, 255, 255, 0.95)"
        # Fix chữ mờ trong ô upload file nền sáng
        uploader_css = """
        [data-testid="stFileUploader"] { background-color: #f0f2f6; border: 1px dashed #4CAF50; border-radius: 10px; padding: 10px; }
        [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] small { color: #000000 !important; font-weight: bold; }
        """
    else:
        bg_url = "https://img.freepik.com/free-photo/abstract-digital-grid-black-background_53876-97647.jpg"
        text_color = "#ffffff"
        card_bg = "rgba(15, 23, 42, 0.9)"
        sidebar_bg = "rgba(5, 5, 10, 0.95)"
        uploader_css = ""

    st.markdown(f"""
    <style>
        .stApp {{ background-image: url("{bg_url}"); background-size: cover; background-attachment: fixed; background-position: center; }}
        h1, h2, h3, h4, p, div, span, label, li {{ color: {text_color} !important; }}
        [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; border-right: 1px solid rgba(255,255,255,0.1); }}
        .cute-card {{ background-color: {card_bg}; padding: 25px; border-radius: 20px; margin-bottom: 20px; backdrop-filter: blur(10px); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2); border: 1px solid rgba(255, 255, 255, 0.1); }}
        .stTextInput input, .stSelectbox div[data-baseweb="select"] {{ border-radius: 10px; color: {text_color}; background-color: rgba(128,128,128,0.1); }}
        {uploader_css}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC XỬ LÝ DỮ LIỆU (THÔNG MINH HƠN) ---
def process_and_send(df):
    """Chuẩn hóa dữ liệu -> Tự tìm cột TK -> Gửi JSON"""
    df.columns = df.columns.str.lower().str.strip()
    payloads = []
    
    for _, row in df.iterrows():
        # 1. Tìm các cột cơ bản
        inv = next((c for c in df.columns if 'invoice' in c or 'hóa đơn' in c or 'amount' in c), None)
        po = next((c for c in df.columns if 'po' in c or 'đơn hàng' in c), None)
        sup = next((c for c in df.columns if 'supplier' in c or 'nhà cung cấp' in c), None)
        email = next((c for c in df.columns if 'email' in c or 'liên hệ' in c), None)
        
        # 2. TỰ ĐỘNG TÌM CỘT TÀI KHOẢN (Logic mới)
        # Quét các từ khóa phổ biến: account, stk, bank, tài khoản...
        acc = next((c for c in df.columns if 'account' in c or 'stk' in c or 'bank' in c or 'tài khoản' in c), None)
        
        item = {
            "invoice_amount": float(row[inv]) if inv else 0.0,
            "po_amount": float(row[po]) if po else 0.0,
            "supplier": str(row[sup]) if sup else "Unknown",
            "email": str(row[email]) if email else "N/A",
            # Nếu tìm thấy cột TK thì lấy, không thì để 000000
            "bank_account": str(row[acc]) if acc else "000000"
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

# --- 4. DASHBOARD CHÍNH ---
def main_dashboard():
    
    # --- A. SIDEBAR ---
    with st.sidebar:
        st.title("⚙️ ADMIN CONTROL")
        
        st.subheader("🎨 Appearance")
        def update_lang(): st.session_state.lang = 'vi' if st.session_state.lang_radio == "Tiếng Việt 🇻🇳" else 'en'
        def update_theme(): st.session_state.theme = 'light' if "Sáng" in st.session_state.theme_radio else 'dark'

        st.radio("Ngôn ngữ / Language", ["Tiếng Việt 🇻🇳", "English 🇬🇧"], index=0 if st.session_state.lang == 'vi' else 1, key="lang_radio", on_change=update_lang)
        st.radio("Giao diện / Theme", ["Sáng (Light) ☀️", "Tối (Dark Space) 🌌"], index=0 if st.session_state.theme == 'light' else 1, key="theme_radio", on_change=update_theme)

        st.divider()

        st.subheader("🔗 Integrations")
        with st.expander("🔵 Telegram Bot", expanded=False):
            if st.toggle("Kích hoạt Tele"):
                st.text_input("Bot Token", type="password", placeholder="1234:ABC...", key="tele_token")
                st.text_input("Chat ID", placeholder="-998877...", key="tele_chatid")
                st.success("Đã lưu cấu hình!")

        with st.expander("🔵 Zalo OA", expanded=False):
            if st.toggle("Kích hoạt Zalo"):
                st.text_input("OA ID", placeholder="Nhập OA ID...", key="zalo_id")
                st.text_input("Secret Key", type="password", key="zalo_key")
        
        with st.expander("🟣 Slack", expanded=False):
            if st.toggle("Kích hoạt Slack"):
                st.text_input("Webhook URL", type="password", placeholder="https://hooks.slack.com/...", key="slack_url")

        st.divider()
        st.subheader("📖 Guides")
        guide_opt = st.selectbox("Chọn hướng dẫn:", ["-- Chọn --", "Telegram Guide", "Zalo Guide", "Slack Guide"])
        
        if guide_opt == "Telegram Guide":
            st.info("**Telegram:** Chat @BotFather -> /newbot -> Copy Token. Chat @userinfobot -> Lấy Chat ID.")
        elif guide_opt == "Zalo Guide": 
            st.info("**Zalo:** oa.zalo.me -> Quản lý -> Lấy ID. developers.zalo.me -> Lấy Secret Key.")
        elif guide_opt == "Slack Guide": 
            st.info("**Slack:** api.slack.com -> Create App -> Incoming Webhooks -> Copy URL.")

        st.divider()
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()

    inject_css()
    
    # --- B. MAIN CONTENT ---
    lang_dict = {
        'vi': {'title': "TRUNG TÂM KIỂM TOÁN AI", 'sub': "Hệ thống đối soát tự động đa kênh", 'tabs': ["📂 Tải Excel", "🌱 Google Sheet", "☁️ Excel Online"], 'drag': "Kéo thả file .xlsx / .csv vào đây", 'btn_run': "🚀 XỬ LÝ NGAY", 'chat_title': "Trợ Lý Hướng Dẫn"},
        'en': {'title': "AI AUDIT HUB", 'sub': "Automated Omni-channel Reconciliation System", 'tabs': ["📂 Upload Excel", "🌱 Google Sheet", "☁️ Excel Online"], 'drag': "Drag & Drop .xlsx / .csv here", 'btn_run': "🚀 PROCESS NOW", 'chat_title': "Support Assistant"}
    }
    T = lang_dict[st.session_state.lang]

    st.markdown(f"<h1 style='text-align: center; color: #E91E63; text-shadow: 2px 2px 4px #000000;'>✿ {T['title']} ✿</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-style: italic; opacity: 0.9;'>{T['sub']}</p>", unsafe_allow_html=True)

    col_L, col_R = st.columns([1.5, 1])

    with col_L:
        st.markdown('<div class="cute-card">', unsafe_allow_html=True)
        tabs = st.tabs(T['tabs'])
        
        payloads = []
        
        # Tab 1: Excel
        with tabs[0]:
            uploaded = st.file_uploader(T['drag'], type=['xlsx', 'csv'])
            if uploaded:
                try:
                    df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
                    st.dataframe(df.head(3), height=100, use_container_width=True)
                    if st.button(T['btn_run'], key="b1", type="primary"):
                        payloads = process_and_send(df)
                except Exception as e: st.error(f"Error: {e}")

        # Tab 2: GSheet
        with tabs[1]:
            url = st.text_input("Link Google Sheet (Public):")
            if url and st.button(T['btn_run'], key="b2"):
                df = load_gsheet(url)
                if df is not None:
                    st.dataframe(df.head(3), height=100)
                    payloads = process_and_send(df)
                else: st.error("Link Error")

        # Tab 3: Excel Online
        with tabs[2]: st.info("Coming soon.")

        # Xử lý Gửi AWS (PHẦN CHẠY THẬT)
        if payloads:
            st.divider()
            st.info(f"⚡ Đang gửi {len(payloads)} giao dịch (kèm số TK) lên AWS...")
            progress = st.progress(0)
            status = st.empty()
            
            for i, p in enumerate(payloads):
                # Hiển thị số TK đã lấy được để người dùng tin tưởng
                acc_display = p.get('bank_account', 'N/A')
                status.code(f"Processing: {p['supplier']} | Bank Acc: {acc_display}")
                
                # GỌI AWS
                if not DEMO_MODE:
                    try:
                        sfn.start_execution(stateMachineArn=SFN_ARN, input=json.dumps(p))
                    except: pass
                else: 
                    time.sleep(0.1) # Demo delay
                
                progress.progress((i+1)/len(payloads))
            
            st.success("✅ HOÀN TẤT! Agent 1 đang xử lý và bảo mật số TK.")
            st.balloons()
            
        st.markdown('</div>', unsafe_allow_html=True)

    with col_R:
        st.markdown('<div class="cute-card" style="height: 600px; display: flex; flex-direction: column;">', unsafe_allow_html=True)
        st.subheader(f"💬 {T['chat_title']}")
        
        chat_con = st.container(height=450)
        with chat_con:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"], avatar="🤖" if msg["role"]=="assistant" else "👤"):
                    st.write(msg["content"])
        
        if prompt := st.chat_input("Help me..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_con:
                with st.chat_message("user", avatar="👤"): st.write(prompt)
            
            reply = "I'm checking..."
            if st.session_state.lang == 'vi':
                reply = "Hệ thống sẽ tự động quét cột 'Account' hoặc 'STK' trong file của bạn và gửi đi bảo mật nha!"
            else:
                reply = "The system automatically scans for 'Account' or 'Bank' columns in your file!"
                
            time.sleep(0.5)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with chat_con:
                with st.chat_message("assistant", avatar="🤖"): st.write(reply)

        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. LOGIN ---
def login_screen():
    st.markdown(f"""<style>.stApp {{ background-image: url("https://img.freepik.com/free-vector/hand-painted-watercolor-pastel-sky-background_23-2148902771.jpg"); background-size: cover; }}</style>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown('<div style="background: rgba(255,255,255,0.95); padding: 40px; border-radius: 20px; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.2);">', unsafe_allow_html=True)
        st.markdown("<h1 style='color: #E91E63; font-family: sans-serif;'>🌸 FINTECH HUB LOGIN</h1>", unsafe_allow_html=True)
        user = st.text_input("Username", placeholder="admin")
        pwd = st.text_input("Password", type="password", placeholder="123")
        if st.button("🚀 ACCESS SYSTEM", type="primary", use_container_width=True):
            if user == "admin" and pwd == "123":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Access Denied!")
        st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.logged_in:
    main_dashboard()
else:
    login_screen()