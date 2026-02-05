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

# KẾT NỐI AWS (QUAN TRỌNG)
try:
    sfn = boto3.client(
        'stepfunctions',
        region_name='ap_southeast_1',
        # Thay key thật vào đây hoặc dùng st.secrets
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],
        aws_secret_access_key=st.secrets["AWS_SECRET_KEY"]
    )
    SFN_ARN = st.secrets["SFN_ARN"]
    DEMO_MODE = False
except:
    DEMO_MODE = True # Tự động chuyển chế độ Demo nếu không có Key

# State
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Chào sếp! Hệ thống Audit đã sẵn sàng. 🌸"}]
if 'integrations' not in st.session_state: st.session_state.integrations = {"tele": False, "zalo": False}

# --- 2. LOGIC XỬ LÝ DỮ LIỆU (PHẦN MỚI THÊM VÀO) ---
def process_and_send(df):
    """Đọc DataFrame -> Chuẩn hóa -> Gửi JSON"""
    df.columns = df.columns.str.lower().str.strip()
    payloads = []
    for _, row in df.iterrows():
        # Tự động map cột thông minh
        inv = next((c for c in df.columns if 'invoice' in c or 'hóa đơn' in c or 'amount' in c), None)
        po = next((c for c in df.columns if 'po' in c or 'đơn hàng' in c), None)
        sup = next((c for c in df.columns if 'supplier' in c or 'nhà cung cấp' in c), None)
        email = next((c for c in df.columns if 'email' in c or 'liên hệ' in c), None)
        
        # Tạo JSON sạch cho Agent 1
        item = {
            "invoice_amount": float(row[inv]) if inv else 0.0,
            "po_amount": float(row[po]) if po else 0.0,
            "supplier": str(row[sup]) if sup else "Unknown Supplier",
            "email": str(row[email]) if email else "N/A"
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

# --- 3. CSS ĐỘNG ---
def inject_css():
    theme = st.session_state.get("theme_radio", "Sáng (Light) ☀️")
    if "Sáng" in theme:
        bg_url = "https://img.freepik.com/free-vector/hand-painted-watercolor-pastel-sky-background_23-2148902771.jpg"
        text_color = "#333333"
        card_bg = "rgba(255, 255, 255, 0.9)"
        sidebar_bg = "rgba(255, 255, 255, 0.95)"
    else:
        bg_url = "https://img.freepik.com/free-photo/abstract-luxury-gradient-blue-background-smooth-dark-blue-with-black-vignette_1258-48251.jpg"
        text_color = "#ffffff"
        card_bg = "rgba(20, 25, 40, 0.9)"
        sidebar_bg = "rgba(10, 10, 15, 0.95)"

    st.markdown(f"""
    <style>
        .stApp {{ background-image: url("{bg_url}"); background-size: cover; background-attachment: fixed; }}
        h1, h2, h3, p, div, span, label, li {{ color: {text_color} !important; }}
        [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; }}
        .cute-card {{ background-color: {card_bg}; padding: 20px; border-radius: 15px; margin-bottom: 20px; backdrop-filter: blur(5px); box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .stTextInput input {{ border-radius: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. DASHBOARD CHÍNH ---
def main_dashboard():
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Cài Đặt")
        lang = st.radio("Ngôn ngữ", ["Tiếng Việt 🇻🇳", "English 🇬🇧"], key="lang_radio")
        theme = st.radio("Chế độ", ["Sáng (Light) ☀️", "Tối (Dark) 🌙"], key="theme_radio")
        st.divider()
        st.subheader("🔗 Kết Nối Bot")
        st.toggle("Telegram Bot", key="tele_tog")
        st.divider()
        st.subheader("📖 Hướng Dẫn")
        guide = st.selectbox("Chọn:", ["-- Xem --", "Lấy Token Tele", "Lấy Token Zalo"])
        if guide == "Lấy Token Tele": st.info("Chat @BotFather -> /newbot")
        st.divider()
        if st.button("🚪 Đăng xuất"):
            st.session_state.logged_in = False
            st.rerun()

    inject_css()
    
    # Main UI
    T = {'vi': "Trung Tâm Kiểm Toán AI", 'en': "AI Audit Hub"}
    cur_title = T['vi'] if "Việt" in lang else T['en']
    st.markdown(f"<h1 style='text-align: center; color: #E91E63;'>✿ {cur_title} ✿</h1>", unsafe_allow_html=True)

    col_L, col_R = st.columns([1.5, 1])

    # CỘT TRÁI: NHẬP LIỆU & GỬI JSON
    with col_L:
        st.markdown('<div class="cute-card">', unsafe_allow_html=True)
        tabs = st.tabs(["📂 Upload Excel", "🌱 Google Sheet", "☁️ Excel Online"])
        
        payloads = [] # Danh sách JSON chờ gửi

        # TAB 1: EXCEL (LOGIC THẬT)
        with tabs[0]:
            uploaded = st.file_uploader("Kéo thả file .xlsx / .csv", type=['xlsx', 'csv'])
            if uploaded:
                try:
                    df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
                    st.dataframe(df.head(3), height=100, use_container_width=True)
                    if st.button("🚀 XỬ LÝ FILE", type="primary", key="btn1"):
                        payloads = process_and_send(df) # <-- GỌI HÀM CHUYỂN JSON Ở ĐÂY
                except Exception as e: st.error(f"Lỗi file: {e}")

        # TAB 2: GOOGLE SHEET (LOGIC THẬT)
        with tabs[1]:
            url = st.text_input("Link Sheet (Public):")
            if url and st.button("🚀 ĐỒNG BỘ", type="primary", key="btn2"):
                df = load_gsheet(url)
                if df is not None:
                    st.dataframe(df.head(3), height=100)
                    payloads = process_and_send(df)
                else: st.error("Lỗi link!")

        # GỬI JSON SANG AWS
        if payloads:
            st.divider()
            st.info(f"⚡ Đang bắn {len(payloads)} dòng dữ liệu sang AWS Agent 1...")
            progress = st.progress(0)
            status = st.empty()
            
            for i, p in enumerate(payloads):
                status.code(f"Sending: {p['supplier']} | ${p['invoice_amount']:,.0f}")
                
                # GỌI AWS AGENT 1
                if not DEMO_MODE:
                    try:
                        sfn.start_execution(stateMachineArn=SFN_ARN, input=json.dumps(p))
                    except Exception as e: st.error(f"Lỗi AWS: {e}")
                else:
                    time.sleep(0.1) # Demo giả lập nếu ko có key
                
                progress.progress((i+1)/len(payloads))
            
            st.success("✅ HOÀN TẤT! Agent 1 đang xử lý.")
            st.balloons()

        st.markdown('</div>', unsafe_allow_html=True)

        # Log Box
        st.markdown('<div class="cute-card" style="min-height: 200px;">', unsafe_allow_html=True)
        st.subheader("📠 Nhật Ký Hoạt Động")
        st.code(f"[{datetime.now().strftime('%H:%M')}] System Ready.\n[{datetime.now().strftime('%H:%M')}] Waiting for tasks...", language="bash")
        st.markdown('</div>', unsafe_allow_html=True)

    # CỘT PHẢI: CHATBOT
    with col_R:
        st.markdown('<div class="cute-card" style="height: 600px; display: flex; flex-direction: column;">', unsafe_allow_html=True)
        st.subheader("💬 Trợ Lý Hướng Dẫn")
        chat_con = st.container(height=450)
        with chat_con:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"], avatar="🤖" if msg["role"]=="assistant" else "👤"):
                    st.write(msg["content"])
        
        if prompt := st.chat_input("Hỏi cách dùng app..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_con:
                with st.chat_message("user", avatar="👤"): st.write(prompt)
            
            reply = "Bạn up file bên trái là mình xử lý nha!"
            if "token" in prompt.lower(): reply = "Xem menu Hướng dẫn bên trái nha."
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
        st.markdown('<div style="background: rgba(255,255,255,0.9); padding: 30px; border-radius: 20px; text-align: center;">', unsafe_allow_html=True)
        st.markdown("<h1 style='color: #E91E63;'>🌸 FinTech Hub</h1>", unsafe_allow_html=True)
        user = st.text_input("Tài khoản", placeholder="admin")
        pwd = st.text_input("Mật khẩu", type="password", placeholder="123")
        if st.button("🚀 Đăng Nhập", type="primary", use_container_width=True):
            if user == "admin" and pwd == "123":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Sai pass!")
        st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.logged_in:
    main_dashboard()
else:
    login_screen()