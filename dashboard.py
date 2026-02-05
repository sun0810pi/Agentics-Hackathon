import streamlit as st
import boto3
import json
import time
import pandas as pd
from datetime import datetime

# --- 1. SETUP & STATE MANAGEMENT ---
st.set_page_config(
    page_title="Audit Buddy AI",
    page_icon="🌸", # Đổi icon cho hợp theme
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'theme' not in st.session_state: st.session_state.theme = 'light'
if 'lang' not in st.session_state: st.session_state.lang = 'vi'
if 'messages' not in st.session_state: 
    st.session_state.messages = [{"role": "assistant", "content": "Chào bạn! Mình là AI Audit Buddy 🌸. Gửi file lên đi mình soi lỗi cho!"}]

# --- 2. SIDEBAR (CÀI ĐẶT) ---
with st.sidebar:
    st.title("⚙️ Cài đặt / Settings")
    
    lang_opt = st.radio(
        "Ngôn ngữ / Language", 
        ["Tiếng Việt 🇻🇳", "English 🇬🇧"], 
        index=0 if st.session_state.lang == 'vi' else 1,
        key="lang_radio"
    )
    st.session_state.lang = 'vi' if "Việt" in lang_opt else 'en'
    
    theme_opt = st.radio(
        "Giao diện / Theme", 
        ["Sáng (Tết Nhẹ Nhàng) 🌸", "Tối (Đêm Hội) 🏮"], 
        index=0 if st.session_state.theme == 'light' else 1,
        key="theme_radio"
    )
    st.session_state.theme = 'light' if "Sáng" in theme_opt else 'dark'
    
    st.divider()
    st.image("https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnJ4Ynh6YmZ4Ynh6YmZ4Ynh6YmZ4Ynh6YmZ4Ynh6YmZ4Ynh6YmZ4eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/L3U6p0eL5bF8FfG5Ff/giphy.gif", width=100) # Thêm cái gif cute
    st.info("💡 Tips: Chúc mừng năm mới! Hệ thống đã sẵn sàng.")

# --- 3. LOCALIZATION ---
TRANS = {
    'vi': {
        'title': "Trung Tâm Kiểm Toán AI - Xuân 2026",
        'subtitle': "Hệ thống đối soát tự động thông minh & thân thiện",
        'tab_excel': "📂 Tải Excel lên",
        'tab_sheet': "🌱 Google Sheet",
        'tab_onl': "☁️ Excel Online",
        'lbl_drag': "Kéo thả file .xlsx hoặc .csv vào đây nhé",
        'lbl_sheet': "Dán link Google Sheet (Công khai) vào đây",
        'lbl_onl': "Dán link Excel Online / OneDrive (Direct Link)",
        'btn_run': "🚀 Kích Hoạt Kiểm Tra",
        'chat_title': "Trợ Lý Ảo Guru 🌸",
        'chat_ph': "Hỏi mình về các giao dịch...",
        'log_title': "Nhật Ký Hệ Thống"
    },
    'en': {
        'title': "AI Audit Hub - Spring 2026",
        'subtitle': "Smart & Friendly Automated Reconciliation System",
        'tab_excel': "📂 Upload Excel",
        'tab_sheet': "🌱 Google Sheet",
        'tab_onl': "☁️ Excel Online",
        'lbl_drag': "Drop your .xlsx or .csv file here",
        'lbl_sheet': "Paste Public Google Sheet URL here",
        'lbl_onl': "Paste Excel Online / OneDrive URL",
        'btn_run': "🚀 Start Audit",
        'chat_title': "Guru Assistant 🌸",
        'chat_ph': "Ask me about transactions...",
        'log_title': "System Log"
    }
}
T = TRANS[st.session_state.lang]

# --- 4. CSS (THÊM NỀN TẾT CUTE) ---
def inject_css():
    # Link ảnh nền (Bạn có thể thay bằng link khác)
    # Nền sáng: Hoa văn Tết nhẹ nhàng, màu hồng/đỏ
    bg_url_light = "https://img.freepik.com/free-vector/flat-tet-background_23-2149250000.jpg?w=1380&t=st=1706340000~exp=1706340600~hmac=..." 
    # Nền tối: Đèn lồng, hoa mai trên nền tối
    bg_url_dark = "https://img.freepik.com/free-vector/gradient-tet-background_23-2149266532.jpg?w=1380&t=st=1706340000~exp=1706340600~hmac=..."

    if st.session_state.theme == 'light':
        # CHẾ ĐỘ SÁNG
        text_color = "#4a4a4a" # Màu chữ xám đậm cho dịu
        input_bg = "#fff0f5" # Nền input hồng phấn
        card_bg = "rgba(255, 255, 255, 0.85)" # Card trắng mờ
        border_color = "#ffb6c1" # Viền hồng nhạt
        # Lớp phủ: Màu trắng hồng mờ 85% đè lên ảnh
        bg_overlay = "linear-gradient(rgba(255, 240, 245, 0.85), rgba(255, 240, 245, 0.85))"
        bg_image = bg_url_light
    else:
        # CHẾ ĐỘ TỐI
        text_color = "#e0e0e0"
        input_bg = "#2d1b2d" # Nền input tím tối
        card_bg = "rgba(30, 30, 40, 0.85)" # Card tối mờ
        border_color = "#5a3a5a" # Viền tím
        # Lớp phủ: Màu đen tím mờ 85% đè lên ảnh
        bg_overlay = "linear-gradient(rgba(15, 10, 20, 0.85), rgba(15, 10, 20, 0.85))"
        bg_image = bg_url_dark

    st.markdown(f"""
    <style>
        /* Thiết lập nền chính với lớp phủ */
        .stApp {{
            background-image: {bg_overlay}, url("{bg_image}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            color: {text_color};
        }}
        
        /* Chỉnh màu chữ toàn bộ */
        p, div, label, h1, h2, h3, span, li {{
            color: {text_color} !important;
        }}
        
        /* Input text box */
        .stTextInput input {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
            border: 1px solid {border_color} !important;
            border-radius: 10px;
        }}
        
        /* Card Container (Cute hóa) */
        .cute-card {{
            background-color: {card_bg};
            padding: 25px;
            border-radius: 20px; /* Bo tròn nhiều hơn */
            border: 2px solid {border_color};
            box-shadow: 0 8px 16px rgba(0,0,0,0.1); /* Bóng đổ mềm */
            margin-bottom: 20px;
            backdrop-filter: blur(5px); /* Hiệu ứng mờ kính */
        }}
        
        /* Tabs Text */
        button[data-baseweb="tab"] {{
            color: {text_color} !important;
            font-weight: 600;
        }}
        
        /* Chat Input */
        .stChatInput textarea {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
            border-radius: 15px;
        }}

        /* Nút bấm cute */
        .stButton button {{
            border-radius: 25px !important;
            background-color: {border_color} !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 4px #dbaeb4; /* Hiệu ứng nút nổi 3D nhẹ */
            transition: all 0.2s;
        }}
        .stButton button:hover {{
            transform: translateY(2px);
            box-shadow: 0 2px #dbaeb4;
        }}
        .stButton button:active {{
            transform: translateY(4px);
            box-shadow: none;
        }}

    </style>
    """, unsafe_allow_html=True)

inject_css()

# --- 5. AWS CONNECTION (GIỮ NGUYÊN) ---
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

# --- 6. DATA LOGIC (GIỮ NGUYÊN) ---
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

# --- 7. MAIN UI ---

# Tiêu đề với font chữ dễ thương hơn (nếu có thể load font) hoặc màu sắc
st.markdown(f"<h1 style='text-align: center; color: {'#e91e63' if st.session_state.theme=='light' else '#ff4081'}; font-family: \"Comic Sans MS\", \"Comic Sans\", cursive, sans-serif;'>✿ {T['title']} ✿</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; opacity: 0.8; font-style: italic;'>{T['subtitle']}</p>", unsafe_allow_html=True)

col_left, col_right = st.columns([1.5, 1])

# === CỘT TRÁI ===
with col_left:
    st.markdown('<div class="cute-card">', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs([f"📂 {T['tab_excel']}", f"🌱 {T['tab_sheet']}", f"☁️ {T['tab_onl']}"])
    payloads_queue = []

    with tab1:
        uploaded = st.file_uploader(T['lbl_drag'], type=['xlsx', 'csv'])
        if uploaded:
            df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
            st.dataframe(df.head(3), use_container_width=True)
            if st.button(T['btn_run'], key="btn_upload"): payloads_queue = normalize_data(df)
    with tab2:
        url = st.text_input(T['lbl_sheet'])
        if url:
            df = load_gsheet(url)
            if df is not None:
                st.dataframe(df.head(3), use_container_width=True)
                if st.button(T['btn_run'], key="btn_sheet"): payloads_queue = normalize_data(df)
    with tab3:
        onl_url = st.text_input(T['lbl_onl'])
        if onl_url and st.button(T['btn_run'], key="btn_onl"):
            try:
                df = pd.read_excel(onl_url) if "xlsx" in onl_url else pd.read_csv(onl_url)
                st.dataframe(df.head(3), use_container_width=True)
                payloads_queue = normalize_data(df)
            except: st.error("Lỗi link!")
    st.markdown('</div>', unsafe_allow_html=True)

    # Log Box Cute
    st.subheader(f"📠 {T['log_title']}")
    log_container = st.container(height=200)
    if payloads_queue:
        progress = st.progress(0)
        for i, p in enumerate(payloads_queue):
            log_container.info(f"🌸 Đang xử lý: {p['supplier']} | ${p['invoice_amount']:,.0f}")
            if not DEMO_MODE:
                try: sfn.start_execution(stateMachineArn=SFN_ARN, input=json.dumps(p))
                except: pass
            else: time.sleep(0.05)
            progress.progress((i+1)/len(payloads_queue))
        st.success("✨ Xong luônnnn! Giỏi quá đi! 🎉")
        st.balloons()

# === CỘT PHẢI: CHATBOT ===
with col_right:
    st.markdown('<div class="cute-card">', unsafe_allow_html=True)
    st.subheader(f"💬 {T['chat_title']}")
    
    chat_container = st.container(height=400)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="🌸" if msg["role"]=="assistant" else "👤"):
                st.write(msg["content"])

    if prompt := st.chat_input(T['chat_ph']):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user", avatar="👤"): st.write(prompt)

        reply = "Đợi mình xíu nha..."
        if "lỗi" in prompt.lower(): reply = "Ưm... có vài giao dịch không khớp á. Bạn check cột Amount xem sao nha! 🥺"
        elif "chào" in prompt.lower(): reply = "Dạ chào sếp! Nay sếp muốn soi ai nè? Hehe 🌸"
        
        time.sleep(0.5)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with chat_container:
            with st.chat_message("assistant", avatar="🌸"): st.write(reply)
            
    st.markdown('</div>', unsafe_allow_html=True)