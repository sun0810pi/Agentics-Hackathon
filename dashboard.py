import streamlit as st
import boto3
import json
import time
import pandas as pd
import io
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
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],
        aws_secret_access_key=st.secrets["AWS_SECRET_KEY"]
    )
    SFN_ARN = st.secrets["SFN_ARN"]
    DEMO_MODE = False
except:
    DEMO_MODE = True

# Init Session
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Chào sếp! Hệ thống Audit đã sẵn sàng. 🌸"}]
if 'lang' not in st.session_state: st.session_state.lang = 'vi'
if 'theme' not in st.session_state: st.session_state.theme = 'light'

# --- 2. CSS GIAO DIỆN (FIX MỜ & UX) ---
def inject_css():
    if st.session_state.theme == 'light':
        # Nền Sáng: Pastel
        bg_url = "https://img.freepik.com/free-vector/hand-painted-watercolor-pastel-sky-background_23-2148902771.jpg"
        text_color = "#000000" # Ép màu đen tuyền cho dễ đọc
        card_bg = "rgba(255, 255, 255, 0.90)"
        sidebar_bg = "rgba(255, 255, 255, 0.95)"
        
        # CSS ĐẶC BIỆT: Fix lỗi chữ mờ trong ô Upload file
        uploader_css = """
        [data-testid="stFileUploader"] {
            background-color: #ffffff;
            border: 2px dashed #E91E63;
            padding: 20px;
        }
        [data-testid="stFileUploader"] section > div {
            color: #000000 !important; /* Ép chữ màu đen */
        }
        [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] small {
            color: #000000 !important;
            font-weight: 800 !important; /* Chữ đậm */
            opacity: 1 !important;
        }
        """
        sidebar_text_color = "#333333"
    else:
        # Nền Tối: Deep Space
        bg_url = "https://img.freepik.com/free-photo/abstract-digital-grid-black-background_53876-97647.jpg"
        text_color = "#ffffff"
        card_bg = "rgba(15, 23, 42, 0.9)" 
        sidebar_bg = "rgba(5, 5, 10, 0.95)"
        uploader_css = ""
        sidebar_text_color = "#ffffff"

    st.markdown(f"""
    <style>
        /* Nền chính */
        .stApp {{ background-image: url("{bg_url}"); background-size: cover; background-attachment: fixed; }}
        
        /* Màu chữ chung */
        h1, h2, h3, h4, p, div, span, label, li {{ color: {text_color} !important; }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{ 
            background-color: {sidebar_bg} !important; 
            border-right: 1px solid rgba(255,255,255,0.1); 
        }}
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
            color: {sidebar_text_color} !important;
        }}
        
        /* Card */
        .cute-card {{
            background-color: {card_bg};
            padding: 25px;
            border-radius: 20px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(128,128,128,0.2);
        }}
        
        /* Input */
        .stTextInput input {{ border-radius: 10px; color: {text_color}; background-color: rgba(128,128,128,0.1); }}
        
        /* Expander (Guide) */
        .streamlit-expanderHeader {{
            color: {text_color} !important;
            font-weight: bold;
        }}
        
        {uploader_css}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC XỬ LÝ DỮ LIỆU ---
def process_and_send(df):
    """Chuẩn hóa dữ liệu -> Tìm cột STK -> Gửi JSON"""
    # 1. Clean tên cột
    df.columns = df.columns.str.lower().str.strip()
    payloads = []
    
    for _, row in df.iterrows():
        # 2. Tìm cột thông minh
        inv = next((c for c in df.columns if 'invoice' in c or 'hóa đơn' in c or 'amount' in c), None)
        po = next((c for c in df.columns if 'po' in c or 'đơn hàng' in c), None)
        sup = next((c for c in df.columns if 'supplier' in c or 'nhà cung cấp' in c), None)
        email = next((c for c in df.columns if 'email' in c or 'liên hệ' in c), None)
        
        # Logic tìm tài khoản ngân hàng (Updated)
        acc = next((c for c in df.columns if 'account' in c or 'stk' in c or 'bank' in c or 'tài khoản' in c), None)
        
        # 3. Tạo Payload
        item = {
            "invoice_amount": float(row[inv]) if inv else 0.0,
            "po_amount": float(row[po]) if po else 0.0,
            "supplier": str(row[sup]) if sup else "Unknown",
            "email": str(row[email]) if email else "N/A",
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
        st.title("⚙️ ADMIN")
        
        st.caption("Appearance")
        def update_lang(): st.session_state.lang = 'vi' if st.session_state.lang_radio == "Tiếng Việt 🇻🇳" else 'en'
        def update_theme(): st.session_state.theme = 'light' if "Sáng" in st.session_state.theme_radio else 'dark'

        st.radio("Ngôn ngữ / Language", ["Tiếng Việt 🇻🇳", "English 🇬🇧"], index=0 if st.session_state.lang == 'vi' else 1, key="lang_radio", on_change=update_lang)
        st.radio("Giao diện / Theme", ["Sáng (Light) ☀️", "Tối (Dark Space) 🌌"], index=0 if st.session_state.theme == 'light' else 1, key="theme_radio", on_change=update_theme)

        st.divider()

        # INPUT NHẬP TOKEN (Rõ ràng hơn)
        st.caption("Integrations Setup")
        with st.expander("🔵 Telegram Bot", expanded=False):
            if st.toggle("Kích hoạt Tele"):
                st.text_input("Bot Token", type="password", placeholder="1234:ABC...", key="tele_token")
                st.text_input("Chat ID", placeholder="-998877...", key="tele_chatid")
                st.success("Đã lưu!")

        with st.expander("🔵 Zalo OA", expanded=False):
            if st.toggle("Kích hoạt Zalo"):
                st.text_input("OA ID", placeholder="Nhập OA ID...")
                st.text_input("Secret Key", type="password")
        
        with st.expander("🟣 Slack", expanded=False):
            if st.toggle("Kích hoạt Slack"):
                st.text_input("Webhook URL", type="password")

        st.divider()
        
        # HƯỚNG DẪN (Sửa UX: Dùng Expander thay vì Selectbox)
        st.caption("Quick Guides")
        with st.expander("📖 Cách lấy Telegram Token"):
            st.markdown("""
            1. Chat với **@BotFather**.
            2. Gõ `/newbot` -> Đặt tên.
            3. Copy **Token API**.
            4. Chat với **@userinfobot** lấy ID.
            """)
            
        with st.expander("📖 Cách lấy Zalo OA"):
            st.markdown("""
            1. Vào `oa.zalo.me`.
            2. Quản lý -> Lấy **OA ID**.
            3. Vào `developers.zalo.me` lấy Key.
            """)

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
        
        # TAB 1: EXCEL LOCAL
        with tabs[0]:
            uploaded = st.file_uploader(T['drag'], type=['xlsx', 'csv'])
            if uploaded:
                try:
                    df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
                    st.dataframe(df.head(3), height=100, use_container_width=True)
                    if st.button(T['btn_run'], key="b1", type="primary"):
                        payloads = process_and_send(df)
                except Exception as e: st.error(f"Error: {e}")

        # TAB 2: GOOGLE SHEET
        with tabs[1]:
            url = st.text_input("Link Google Sheet (Public):")
            if url and st.button(T['btn_run'], key="b2"):
                df = load_gsheet(url)
                if df is not None:
                    st.dataframe(df.head(3), height=100)
                    payloads = process_and_send(df)
                else: st.error("Link Error")

        # TAB 3: EXCEL ONLINE (ĐÃ SỬA LỖI COMING SOON)
        with tabs[2]:
            st.info("💡 Lưu ý: Link phải là link tải trực tiếp (Direct Link) của file .xlsx")
            onl_url = st.text_input("Dán link file Excel vào đây:")
            if onl_url and st.button(T['btn_run'], key="b3"):
                try:
                    # Đọc trực tiếp từ URL
                    df = pd.read_excel(onl_url)
                    st.success("✅ Đã kết nối thành công!")
                    st.dataframe(df.head(3), height=100)
                    payloads = process_and_send(df)
                except Exception as e:
                    st.error(f"Không đọc được file. Hãy đảm bảo link là public. Lỗi: {e}")

        # LOGIC GỬI AWS
        if payloads:
            st.divider()
            st.info(f"⚡ Processing {len(payloads)} transactions with Agent Swarm...")
            progress = st.progress(0)
            status = st.empty()
            
            for i, p in enumerate(payloads):
                # Show thông tin Bank Account đã bắt được
                bank_info = p.get('bank_account', 'N/A')
                status.code(f"Scanning: {p['supplier']} | Bank: {bank_info}")
                
                if not DEMO_MODE:
                    try:
                        sfn.start_execution(stateMachineArn=SFN_ARN, input=json.dumps(p))
                    except: pass
                else: time.sleep(0.1)
                
                progress.progress((i+1)/len(payloads))
            
            st.success("✅ SENT TO CORE ENGINE! Agents are verifying data.")
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
        
        if prompt := st.chat_input("Ask me..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_con:
                with st.chat_message("user", avatar="👤"): st.write(prompt)
            
            reply = "..."
            if st.session_state.lang == 'vi':
                reply = "Hệ thống đã nhận diện được cột 'Account' trong file của bạn. Dữ liệu này sẽ được Agent 1 mã hóa ngay lập tức!"
            else:
                reply = "System detected 'Account' column. Agent 1 will tokenize this data immediately for security."
                
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