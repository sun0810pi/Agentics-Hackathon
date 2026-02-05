import streamlit as st
import boto3
import json
import time
import pandas as pd
from datetime import datetime

# --- 1. SETUP & STATE MANAGEMENT (QUAN TRỌNG NHẤT) ---
st.set_page_config(
    page_title="Audit Buddy AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Khởi tạo giá trị mặc định nếu chưa có
if 'theme' not in st.session_state: st.session_state.theme = 'light'
if 'lang' not in st.session_state: st.session_state.lang = 'vi'
if 'messages' not in st.session_state: 
    st.session_state.messages = [{"role": "assistant", "content": "Chào bạn! Mình là AI Audit Buddy 🌸. Gửi file lên đi mình soi lỗi cho!"}]

# --- 2. XỬ LÝ SIDEBAR TRƯỚC (ĐỂ CẬP NHẬT STATE KỊP THỜI) ---
with st.sidebar:
    st.title("⚙️ Cài đặt / Settings")
    
    # Toggle Ngôn ngữ (Dùng on_change để force update)
    lang_opt = st.radio(
        "Ngôn ngữ / Language", 
        ["Tiếng Việt 🇻🇳", "English 🇬🇧"], 
        index=0 if st.session_state.lang == 'vi' else 1,
        key="lang_radio"
    )
    # Cập nhật state ngay lập tức
    st.session_state.lang = 'vi' if "Việt" in lang_opt else 'en'
    
    # Toggle Theme
    theme_opt = st.radio(
        "Giao diện / Theme", 
        ["Sáng (Light) ☀️", "Tối (Dark) 🌙"], 
        index=0 if st.session_state.theme == 'light' else 1,
        key="theme_radio"
    )
    # Cập nhật state ngay lập tức
    st.session_state.theme = 'light' if "Sáng" in theme_opt else 'dark'
    
    st.divider()
    st.info("💡 Tips: Upload file Excel để AI kiểm tra tự động.")

# --- 3. TỪ ĐIỂN NGÔN NGỮ (LẤY THEO STATE ĐÃ UPDATE) ---
TRANS = {
    'vi': {
        'title': "Trung Tâm Kiểm Toán AI",
        'subtitle': "Hệ thống đối soát tự động thông minh & thân thiện",
        'tab_excel': "📂 Tải Excel lên",
        'tab_sheet': "🌱 Google Sheet",
        'tab_onl': "☁️ Excel Online",
        'lbl_drag': "Kéo thả file .xlsx hoặc .csv vào đây nhé",
        'lbl_sheet': "Dán link Google Sheet (Công khai) vào đây",
        'lbl_onl': "Dán link Excel Online / OneDrive (Direct Link)",
        'btn_run': "🚀 Kích Hoạt Kiểm Tra",
        'chat_title': "Trợ Lý Ảo Guru",
        'chat_ph': "Hỏi mình về các giao dịch...",
        'log_title': "Nhật Ký Hệ Thống"
    },
    'en': {
        'title': "AI Audit Hub",
        'subtitle': "Smart & Friendly Automated Reconciliation System",
        'tab_excel': "📂 Upload Excel",
        'tab_sheet': "🌱 Google Sheet",
        'tab_onl': "☁️ Excel Online",
        'lbl_drag': "Drop your .xlsx or .csv file here",
        'lbl_sheet': "Paste Public Google Sheet URL here",
        'lbl_onl': "Paste Excel Online / OneDrive URL",
        'btn_run': "🚀 Start Audit",
        'chat_title': "Guru Assistant",
        'chat_ph': "Ask me about transactions...",
        'log_title': "System Log"
    }
}
T = TRANS[st.session_state.lang]

# --- 4. CSS (XỬ LÝ MÀU SẮC CHUẨN) ---
def inject_css():
    if st.session_state.theme == 'light':
        # CHẾ ĐỘ SÁNG: Nền trắng, Chữ ĐEN
        bg_color = "#ffffff"
        text_color = "#000000" 
        input_bg = "#f0f2f6"
        card_bg = "#f9f9f9"
        border_color = "#cccccc"
    else:
        # CHẾ ĐỘ TỐI: Nền đen, Chữ TRẮNG
        bg_color = "#0e1117"
        text_color = "#ffffff"
        input_bg = "#262730"
        card_bg = "#1f2937"
        border_color = "#4b5563"

    st.markdown(f"""
    <style>
        /* Force màu nền và màu chữ toàn trang */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        /* Chỉnh màu chữ cho các thẻ p, div, label, input */
        p, div, label, h1, h2, h3, span {{
            color: {text_color} !important;
        }}
        
        /* Input text box */
        .stTextInput input {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
        }}
        
        /* Card Container */
        .cute-card {{
            background-color: {card_bg};
            padding: 20px;
            border-radius: 15px;
            border: 1px solid {border_color};
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        /* Tabs Text Color Fix */
        button[data-baseweb="tab"] {{
            color: {text_color} !important;
        }}
        
        /* Chat Input */
        .stChatInput textarea {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
        }}
    </style>
    """, unsafe_allow_html=True)

inject_css()

# --- 5. AWS CONNECTION ---
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

# --- 6. LOGIC XỬ LÝ DỮ LIỆU ---
def normalize_data(df):
    df.columns = df.columns.str.lower().str.strip()
    payloads = []
    for _, row in df.iterrows():
        inv = next((c for c in df.columns if 'invoice' in c or 'hóa đơn' in c), None)
        po = next((c for c in df.columns if 'po' in c or 'đơn hàng' in c), None)
        sup = next((c for c in df.columns if 'supplier' in c or 'cung cấp' in c), None)
        email = next((c for c in df.columns if 'email' in c), None)
        
        payloads.append({
            "invoice_amount": float(row[inv]) if inv else 0.0,
            "po_amount": float(row[po]) if po else 0.0,
            "supplier": str(row[sup]) if sup else "Unknown",
            "email": str(row[email]) if email else "N/A"
        })
    return payloads

def load_gsheet(url):
    try:
        if "docs.google.com" in url:
            csv_url = url.replace('/edit#gid=', '/export?format=csv&gid=').replace('/edit?gid=', '/export?format=csv&gid=')
            if "export" not in csv_url: csv_url += "/export?format=csv"
            return pd.read_csv(csv_url)
    except: return None

# --- 7. GIAO DIỆN CHÍNH (MAIN UI) ---

st.markdown(f"<h1 style='text-align: center; color: #FF4B4B;'>{T['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; opacity: 0.8;'>{T['subtitle']}</p>", unsafe_allow_html=True)

col_left, col_right = st.columns([1.5, 1])

# === CỘT TRÁI: INPUT ===
with col_left:
    st.markdown('<div class="cute-card">', unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs([f"📂 {T['tab_excel']}", f"🌱 {T['tab_sheet']}", f"☁️ {T['tab_onl']}"])
    
    payloads_queue = []

    # TAB 1
    with tab1:
        uploaded = st.file_uploader(T['lbl_drag'], type=['xlsx', 'csv'])
        if uploaded:
            df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
            st.dataframe(df.head(3), use_container_width=True)
            if st.button(T['btn_run'], key="btn_upload", type="primary"):
                payloads_queue = normalize_data(df)

    # TAB 2
    with tab2:
        url = st.text_input(T['lbl_sheet'])
        if url:
            df = load_gsheet(url)
            if df is not None:
                st.dataframe(df.head(3), use_container_width=True)
                if st.button(T['btn_run'], key="btn_sheet", type="primary"):
                    payloads_queue = normalize_data(df)

    # TAB 3
    with tab3:
        onl_url = st.text_input(T['lbl_onl'])
        if onl_url and st.button(T['btn_run'], key="btn_onl", type="primary"):
            try:
                df = pd.read_excel(onl_url) if "xlsx" in onl_url else pd.read_csv(onl_url)
                st.dataframe(df.head(3), use_container_width=True)
                payloads_queue = normalize_data(df)
            except: st.error("Lỗi link!")

    st.markdown('</div>', unsafe_allow_html=True)

    # LOG BOX
    st.subheader(f"📠 {T['log_title']}")
    log_container = st.container(height=200, border=True)
    
    if payloads_queue:
        progress = st.progress(0)
        for i, p in enumerate(payloads_queue):
            msg = f"Processing: {p['supplier']} | ${p['invoice_amount']:,.0f}"
            log_container.write(msg)
            
            if not DEMO_MODE:
                try: sfn.start_execution(stateMachineArn=SFN_ARN, input=json.dumps(p))
                except: pass
            else:
                time.sleep(0.05)
            progress.progress((i+1)/len(payloads_queue))
        st.success("✅ Done!")

# === CỘT PHẢI: CHATBOT ===
with col_right:
    st.markdown('<div class="cute-card">', unsafe_allow_html=True)
    st.subheader(f"💬 {T['chat_title']}")
    
    # Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"]) # Dùng write thay vì markdown để auto màu chữ

    # Chat Input
    if prompt := st.chat_input(T['chat_ph']):
        # User message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Bot logic
        reply = "Mình đang kiểm tra dữ liệu cho bạn... (Demo)"
        if "lỗi" in prompt.lower(): reply = "Có vẻ có lệch số liệu ở file vừa up. Bạn check cột Amount chưa?"
        elif "hello" in prompt.lower() or "chào" in prompt.lower(): reply = "Hello sếp! Cần mình giúp gì không?"
        
        time.sleep(0.5)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)
            
    st.markdown('</div>', unsafe_allow_html=True)