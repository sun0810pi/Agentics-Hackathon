import streamlit as st
import boto3
import json
import time
import random
import pandas as pd
from datetime import datetime

# --- 1. SETUP STATE & CONFIG ---
st.set_page_config(
    page_title="Audit Buddy AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Khởi tạo Session State (Để lưu trạng thái Chat, Ngôn ngữ, Giao diện)
if 'theme' not in st.session_state: st.session_state.theme = 'light'
if 'lang' not in st.session_state: st.session_state.lang = 'vi'
if 'messages' not in st.session_state: 
    st.session_state.messages = [{"role": "assistant", "content": "Chào bạn! Mình là AI Audit Buddy 🌸. Bạn cần mình giúp kiểm tra giao dịch nào hôm nay?"}]

# --- 2. TỪ ĐIỂN NGÔN NGỮ (LOCALIZATION) ---
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
        'status_ready': "Sẵn sàng nhận nhiệm vụ...",
        'status_proc': "Đang xử lý...",
        'console_title': "Nhật Ký Hoạt Động",
        'chat_title': "Trợ Lý Ảo Guru",
        'chat_ph': "Hỏi mình về các giao dịch bất thường...",
        'kpi_sys': "Hệ Thống",
        'kpi_agent': "AI Agent",
        'kpi_acc': "Độ Chính Xác"
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
        'status_ready': "Ready for tasks...",
        'status_proc': "Processing...",
        'console_title': "Activity Log",
        'chat_title': "Guru Assistant",
        'chat_ph': "Ask me about suspicious transactions...",
        'kpi_sys': "System",
        'kpi_agent': "Active Agents",
        'kpi_acc': "Accuracy"
    }
}
T = TRANS[st.session_state.lang] # Biến tắt để lấy ngôn ngữ hiện tại

# --- 3. CSS (GIAO DIỆN DỄ THƯƠNG & DARK/LIGHT) ---
def inject_css():
    # Màu sắc dựa trên Theme
    if st.session_state.theme == 'light':
        bg_color = "#f8f9fa"
        text_color = "#31333F"
        card_bg = "#ffffff"
        accent = "#FF6B6B" # Màu hồng cam dễ thương
        border = "#e0e0e0"
    else:
        bg_color = "#0e1117"
        text_color = "#e0e0e0"
        card_bg = "#1f2937"
        accent = "#4ADE80" # Màu xanh lá dịu
        border = "#374151"

    st.markdown(f"""
    <style>
        /* Tổng thể */
        .stApp {{ background-color: {bg_color}; color: {text_color}; }}
        
        /* Card Container (Khung bo tròn) */
        .cute-card {{
            background-color: {card_bg};
            padding: 20px;
            border-radius: 15px;
            border: 1px solid {border};
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }}
        
        /* Tiêu đề */
        .main-title {{
            font-family: 'Segoe UI', sans-serif;
            font-weight: 800;
            font-size: 2.5rem;
            color: {accent};
            text-align: center;
            margin-bottom: 5px;
        }}
        
        /* Console Log */
        .log-box {{
            background-color: {card_bg};
            border: 1px dashed {accent};
            border-radius: 10px;
            padding: 10px;
            height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.9rem;
        }}
        
        /* Buttons */
        .stButton button {{
            border-radius: 20px !important;
            font-weight: bold !important;
            border: none !important;
            transition: all 0.3s !important;
        }}
        .stButton button:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
    </style>
    """, unsafe_allow_html=True)

inject_css()

# --- 4. KẾT NỐI AWS ---
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

# --- 5. HÀM XỬ LÝ DATA ---
def normalize_data(df):
    """Chuẩn hóa JSON"""
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

# --- 6. SIDEBAR (CÀI ĐẶT) ---
with st.sidebar:
    st.title("⚙️ Cài đặt / Settings")
    
    # Toggle Ngôn ngữ
    lang_choice = st.radio("Ngôn ngữ / Language", ["Tiếng Việt 🇻🇳", "English 🇬🇧"], horizontal=True)
    if "Việt" in lang_choice: st.session_state.lang = 'vi'
    else: st.session_state.lang = 'en'
    
    # Toggle Theme
    theme_choice = st.radio("Giao diện / Theme", ["Sáng (Cute) ☀️", "Tối (Deep) 🌙"], horizontal=True)
    st.session_state.theme = 'light' if "Sáng" in theme_choice else 'dark'
    
    st.divider()
    
    # KPI Mini
    st.markdown(f"**{T['kpi_sys']}**: ✅ Online")
    st.markdown(f"**{T['kpi_agent']}**: 5 🤖")
    st.metric(T['kpi_acc'], "98.5%", "+2%")
    
    st.divider()
    st.info("💡 Pro tip: Upload file lớn để thấy tốc độ xử lý batch.")

# --- 7. MAIN UI ---

# Header
st.markdown(f'<div class="main-title">{T["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div style="text-align: center; color: gray; margin-bottom: 30px;">{T["subtitle"]}</div>', unsafe_allow_html=True)

col_input, col_chat = st.columns([1.5, 1])

# --- CỘT TRÁI: NHẬP LIỆU ---
with col_input:
    st.markdown(f'<div class="cute-card">', unsafe_allow_html=True)
    
    # 3 Tab Nhập liệu
    tab1, tab2, tab3 = st.tabs([f"📂 {T['tab_excel']}", f"🌱 {T['tab_sheet']}", f"☁️ {T['tab_onl']}"])
    
    payloads_queue = []

    # TAB 1: UPLOAD
    with tab1:
        uploaded = st.file_uploader(T['lbl_drag'], type=['xlsx', 'csv'])
        if uploaded:
            df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
            st.dataframe(df.head(3), height=100, use_container_width=True)
            if st.button(T['btn_run'], key="btn1", type="primary"):
                payloads_queue = normalize_data(df)

    # TAB 2: GOOGLE SHEET
    with tab2:
        url = st.text_input(T['lbl_sheet'])
        if url:
            df = load_gsheet(url)
            if df is not None:
                st.dataframe(df.head(3), height=100)
                if st.button(T['btn_run'], key="btn2", type="primary"):
                    payloads_queue = normalize_data(df)

    # TAB 3: EXCEL ONLINE (Giả lập link trực tiếp)
    with tab3:
        st.info("ℹ️ Excel Online: Copy link 'Direct Download' hoặc 'Embed Link' từ OneDrive.")
        onl_url = st.text_input(T['lbl_onl'])
        if onl_url and st.button(T['btn_run'], key="btn3", type="primary"):
             # Với Hackathon, ta xử lý như một link CSV/Excel public bình thường
             try:
                 df = pd.read_excel(onl_url) if "xlsx" in onl_url else pd.read_csv(onl_url)
                 st.dataframe(df.head(3))
                 payloads_queue = normalize_data(df)
             except:
                 st.error("Không đọc được link. Hãy đảm bảo link là Public Direct Download.")

    st.markdown('</div>', unsafe_allow_html=True)
    
    # KHUNG LOG (CONSOLE)
    st.markdown(f"### 📠 {T['console_title']}")
    log_container = st.empty()
    
    logs = [T['status_ready']]
    
    def update_log(msg):
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
        if len(logs) > 10: logs.pop(0)
        log_html = "<br>".join([f"<div style='border-bottom: 1px solid #eee; padding: 2px;'>{l}</div>" for l in logs])
        log_container.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

    # XỬ LÝ KHI CÓ DATA
    if payloads_queue:
        progress = st.progress(0)
        for i, p in enumerate(payloads_queue):
            sup = p.get('supplier', 'Unknown')
            # Hiệu ứng log chạy
            update_log(f"Processing: {sup} | ${p['invoice_amount']:,.0f}")
            
            if not DEMO_MODE:
                try:
                    sfn.start_execution(stateMachineArn=SFN_ARN, input=json.dumps(p))
                except Exception as e: update_log(f"Err: {e}")
            else:
                time.sleep(0.05) # Demo delay
            
            progress.progress((i+1)/len(payloads_queue))
            time.sleep(0.01)
            
        update_log("✅ DONE! All sent to AWS Agents.")
        st.success("Hoàn thành xuất sắc nhiệm vụ! 🎉")
        st.balloons()

# --- CỘT PHẢI: CHATBOT (PHẦN MỚI) ---
with col_chat:
    st.markdown(f'<div class="cute-card" style="height: 600px; display: flex; flex-direction: column;">', unsafe_allow_html=True)
    st.subheader(f"💬 {T['chat_title']}")
    
    # Container chứa tin nhắn
    chat_container = st.container(height=450)
    
    # Hiển thị lịch sử chat
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Input chat
    if prompt := st.chat_input(T['chat_ph']):
        # 1. Hiện tin nhắn người dùng
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # 2. Logic Bot trả lời (Giả lập thông minh)
        # Sau này ông có thể nối con này vào Agent 3 (Gemini) để trả lời thật
        bot_reply = ""
        if "lỗi" in prompt.lower() or "error" in prompt.lower():
            bot_reply = "Mình thấy có 2 giao dịch bị lệch số liệu hôm nay. Bạn check file báo cáo chưa? 🧐"
        elif "chào" in prompt.lower() or "hello" in prompt.lower():
            bot_reply = "Chào sếp! Chúc sếp một ngày làm việc năng suất nè ✨"
        else:
            bot_reply = f"Mình đã ghi nhận yêu cầu: '{prompt}'. Đang bảo các Agent đi kiểm tra đây ạ... 🏃‍♂️💨"

        # 3. Hiện tin nhắn Bot
        time.sleep(0.5) # Giả vờ suy nghĩ
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(bot_reply)
                
    st.markdown('</div>', unsafe_allow_html=True)