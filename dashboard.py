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
    initial_sidebar_state="collapsed"
)

# Khởi tạo Session State
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'theme' not in st.session_state: st.session_state.theme = 'light'
if 'lang' not in st.session_state: st.session_state.lang = 'vi'
if 'messages' not in st.session_state: 
    st.session_state.messages = [{"role": "assistant", "content": "Chào sếp! Hệ thống Audit đã sẵn sàng. 🌸"}]
if 'integrations' not in st.session_state:
    st.session_state.integrations = {"tele": False, "zalo": False}

# --- 2. CSS ĐỘNG (THAY NỀN THEO THEME) ---
def inject_css():
    # URL ẢNH NỀN (Thay đổi theo theme)
    # Light: Pastel Sky Art
    bg_light = "https://img.freepik.com/free-vector/hand-painted-watercolor-pastel-sky-background_23-2148902771.jpg"
    # Dark: Elegant Dark Wave
    bg_dark = "https://img.freepik.com/free-vector/gradient-black-background-with-wavy-lines_23-2149151159.jpg"
    
    # Chọn màu dựa trên Theme hiện tại
    if st.session_state.theme == 'light':
        current_bg = bg_light
        text_color = "#333333"
        card_bg = "rgba(255, 255, 255, 0.85)"
        sidebar_bg = "rgba(255, 255, 255, 0.9)"
        sidebar_text = "#000000"
    else:
        current_bg = bg_dark
        text_color = "#ffffff"
        card_bg = "rgba(20, 20, 30, 0.85)"
        sidebar_bg = "rgba(0, 0, 0, 0.8)"
        sidebar_text = "#ffffff"

    st.markdown(f"""
    <style>
        /* NỀN TOÀN TRANG */
        .stApp {{
            background-image: url("{current_bg}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}

        /* SIDEBAR */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255,255,255,0.1);
        }}
        /* Chỉnh màu chữ trong Sidebar */
        [data-testid="stSidebar"] * {{
            color: {sidebar_text} !important;
        }}

        /* CARD CONTAINER */
        .cute-card {{
            background-color: {card_bg};
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            margin-bottom: 20px;
        }}

        /* TEXT COLOR FIX */
        h1, h2, h3, p, div, label, span {{
            color: {text_color};
        }}
        
        /* INPUT FIELDS */
        .stTextInput input {{
            background-color: {card_bg} !important;
            color: {text_color} !important;
            border-radius: 10px;
        }}

        /* BUTTON */
        .stButton button {{
            border-radius: 25px;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: 0.3s;
        }}
        .stButton button:hover {{
            transform: translateY(-2px);
        }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. MÀN HÌNH LOGIN ---
def login_screen():
    inject_css()
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown('<div class="cute-card" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown("<h1 style='color: #E91E63;'>🌸 FinTech Audit Hub</h1>", unsafe_allow_html=True)
        st.write("Đăng nhập hệ thống quản trị")
        
        user = st.text_input("Tài khoản", placeholder="admin")
        pwd = st.text_input("Mật khẩu", type="password", placeholder="123")
        
        if st.button("🚀 Vào Dashboard", type="primary", use_container_width=True):
            if user == "admin" and pwd == "123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Sai mật khẩu (Thử admin/123)")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. DASHBOARD CHÍNH ---
def main_dashboard():
    # Quan trọng: Load CSS ngay đầu hàm để áp dụng theme
    inject_css() 
    
    # Từ điển ngôn ngữ
    T = {
        'vi': {'title': "Trung Tâm Kiểm Toán AI", 'sub': "Hệ thống đối soát tự động", 'tab1': "Tải Excel", 'tab2': "Google Sheet", 'tab3': "Excel Online", 'chat': "Trợ Lý Guru 🌸"},
        'en': {'title': "AI Audit Hub", 'sub': "Automated Reconciliation System", 'tab1': "Upload Excel", 'tab2': "Google Sheet", 'tab3': "Excel Online", 'chat': "Guru Assistant 🌸"}
    }
    cur_lang = T[st.session_state.lang]

    # --- SIDEBAR (ĐÃ KHÔI PHỤC) ---
    with st.sidebar:
        st.title("⚙️ Cài đặt / Admin")
        
        # 1. Chọn Ngôn ngữ (Sửa lỗi logic cũ)
        lang_idx = 0 if st.session_state.lang == 'vi' else 1
        lang_sel = st.radio("Ngôn ngữ / Language", ["Tiếng Việt 🇻🇳", "English 🇬🇧"], index=lang_idx)
        st.session_state.lang = 'vi' if "Việt" in lang_sel else 'en'
        
        # 2. Chọn Theme (Background đổi theo cái này)
        theme_idx = 0 if st.session_state.theme == 'light' else 1
        theme_sel = st.radio("Giao diện / Theme", ["Sáng (Xuân) 🌸", "Tối (Cyber) 🌙"], index=theme_idx)
        
        # Logic đổi theme và reload trang để ăn CSS mới
        new_theme = 'light' if "Sáng" in theme_sel else 'dark'
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun()
        
        st.divider()
        
        # 3. Integrations
        st.subheader("🔗 Kết nối Bot")
        
        # Tele
        tele_on = st.toggle("Telegram Bot", value=st.session_state.integrations['tele'])
        if tele_on: 
            st.text_input("API Token", type="password")
            st.caption("✅ Connected: @AuditBot")
        st.session_state.integrations['tele'] = tele_on
        
        # Zalo
        zalo_on = st.toggle("Zalo OA", value=st.session_state.integrations['zalo'])
        if zalo_on: st.caption("⏳ Pending Approval...")
        st.session_state.integrations['zalo'] = zalo_on
        
        st.divider()
        if st.button("🚪 Đăng xuất"):
            st.session_state.logged_in = False
            st.rerun()

    # --- MAIN CONTENT ---
    st.markdown(f"<h1 style='text-align: center; color: #E91E63; font-family: sans-serif;'>✿ {cur_lang['title']} ✿</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; opacity: 0.8;'>{cur_lang['sub']}</p>", unsafe_allow_html=True)

    c_left, c_right = st.columns([1.5, 1])

    # CỘT TRÁI
    with c_left:
        st.markdown('<div class="cute-card">', unsafe_allow_html=True)
        
        # Thông báo trạng thái Bot
        if st.session_state.integrations['tele']:
            st.info("📢 Bot Telegram đang theo dõi hệ thống.")

        tabs = st.tabs([f"📂 {cur_lang['tab1']}", f"🌱 {cur_lang['tab2']}", f"☁️ {cur_lang['tab3']}"])
        
        with tabs[0]: # Excel
            st.file_uploader("Kéo thả file .xlsx / .csv", type=['xlsx', 'csv'])
            if st.button("🚀 Xử lý ngay", key="btn1", type="primary"):
                with st.status("Processing...", expanded=True):
                    time.sleep(1)
                    st.write("Reading data...")
                    time.sleep(1)
                    st.write("Sending to AWS...")
                st.success("Done! Check chat log.")
        
        with tabs[1]: # GSheet
            st.text_input("Link Google Sheet:")
            st.button("🚀 Đồng bộ", key="btn2")
            
        with tabs[2]: # Excel Online
            st.text_input("Link Excel Online:")
            st.button("🚀 Kết nối", key="btn3")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Log Box
        st.markdown('<div class="cute-card" style="min-height: 200px;">', unsafe_allow_html=True)
        st.subheader("📠 System Logs")
        st.code(f"[{datetime.now().strftime('%H:%M')}] System Ready.\n[{datetime.now().strftime('%H:%M')}] Theme: {st.session_state.theme}\n[{datetime.now().strftime('%H:%M')}] Waiting for inputs...", language="bash")
        st.markdown('</div>', unsafe_allow_html=True)

    # CỘT PHẢI
    with c_right:
        st.markdown('<div class="cute-card" style="height: 600px; display: flex; flex-direction: column;">', unsafe_allow_html=True)
        st.subheader(f"💬 {cur_lang['chat']}")
        
        chat_con = st.container(height=450)
        with chat_con:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"], avatar="🌸" if msg["role"]=="assistant" else "👤"):
                    st.write(msg["content"])
        
        if prompt := st.chat_input("Nhập tin nhắn..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_con:
                with st.chat_message("user", avatar="👤"): st.write(prompt)
            
            # Bot trả lời
            reply = "Dạ em nghe sếp ơi..."
            if "bot" in prompt.lower(): reply = "Dạ em đã kết nối bot rồi ạ, yên tâm nha!"
            elif "file" in prompt.lower(): reply = "Sếp cứ up file lên đi, em cân hết!"
            
            time.sleep(0.5)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with chat_con:
                with st.chat_message("assistant", avatar="🌸"): st.write(reply)

        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. LOGIC CHẠY ---
if st.session_state.logged_in:
    main_dashboard()
else:
    login_screen()