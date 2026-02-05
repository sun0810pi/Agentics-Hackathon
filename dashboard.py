import streamlit as st
import boto3
import json
import time
import pandas as pd
from datetime import datetime

# --- 1. CONFIG & SESSION STATE ---
st.set_page_config(
    page_title="Audit Buddy AI",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed" # Ẩn sidebar lúc login
)

# Init Session State
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'theme' not in st.session_state: st.session_state.theme = 'light'
if 'lang' not in st.session_state: st.session_state.lang = 'vi'
if 'messages' not in st.session_state: 
    st.session_state.messages = [{"role": "assistant", "content": "Chào sếp! Hệ thống Audit đã sẵn sàng. Gửi file để em kiểm tra nhé! 🌸"}]
if 'integrations' not in st.session_state:
    st.session_state.integrations = {"tele": False, "zalo": False, "mess": False}

# --- 2. CSS XỊN (FIX LỖI HIỂN THỊ) ---
def inject_css():
    # Ảnh nền: Dùng ảnh Vector Art cho an toàn & sang trọng
    # Light: Hoa đào vector nền trắng hồng
    bg_light = "https://img.freepik.com/free-vector/hand-painted-watercolor-pastel-sky-background_23-2148902771.jpg"
    # Dark: Abstract Neon tím than
    bg_dark = "https://img.freepik.com/free-vector/dark-gradient-background-with-copy-space_53876-99548.jpg"
    
    current_bg = bg_light if st.session_state.theme == 'light' else bg_dark
    text_color = "#333333" if st.session_state.theme == 'light' else "#ffffff"
    card_bg = "rgba(255, 255, 255, 0.9)" if st.session_state.theme == 'light' else "rgba(30, 30, 40, 0.9)"

    st.markdown(f"""
    <style>
        /* NỀN CHÍNH */
        .stApp {{
            background-image: url("{current_bg}");
            background-size: cover;
            background-attachment: fixed;
        }}

        /* SIDEBAR (FIX CHỮ TRẮNG) */
        [data-testid="stSidebar"] {{
            background-color: rgba(20, 20, 30, 0.85) !important; /* Đen mờ */
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255,255,255,0.1);
        }}
        /* Ép màu chữ trong Sidebar thành Trắng */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] p {{
            color: #ffffff !important;
        }}
        
        /* CARD CONTAINER */
        .cute-card {{
            background-color: {card_bg};
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            margin-bottom: 20px;
        }}

        /* TEXT COLOR MAIN CONTENT */
        .main-content p, .main-content h1, .main-content h2, .main-content h3, .main-content div {{
            color: {text_color} !important;
        }}

        /* BUTTON STYLE */
        .stButton button {{
            border-radius: 30px;
            font-weight: bold;
            transition: transform 0.2s;
        }}
        .stButton button:hover {{
            transform: scale(1.05);
        }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. MÀN HÌNH LOGIN ---
def login_screen():
    inject_css() # Vẫn load CSS nền đẹp
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown('<div class="cute-card" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown("<h1 style='color: #E91E63;'>🌸 FinTech Audit Hub</h1>", unsafe_allow_html=True)
        st.markdown("<h3>Đăng nhập hệ thống</h3>", unsafe_allow_html=True)
        
        username = st.text_input("Tài khoản", placeholder="admin")
        password = st.text_input("Mật khẩu", type="password", placeholder="123")
        
        if st.button("🚀 Đăng Nhập Ngay", type="primary", use_container_width=True):
            if username == "admin" and password == "123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Sai mật khẩu rồi sếp ơi! (Gợi ý: admin/123)")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. MÀN HÌNH DASHBOARD CHÍNH ---
def main_dashboard():
    inject_css() # Load CSS lại khi vào trong
    
    # --- LANGUAGE DICTIONARY ---
    T = {
        'vi': {'title': "Trung Tâm Kiểm Toán AI", 'tab1': "Tải Excel", 'tab2': "Google Sheet", 'tab3': "Excel Online", 'chat': "Trợ Lý Ảo Guru 🌸", 'bot_stt': "Trạng thái Bot"},
        'en': {'title': "AI Audit Hub", 'tab1': "Upload Excel", 'tab2': "Google Sheet", 'tab3': "Excel Online", 'chat': "Guru Assistant 🌸", 'bot_stt': "Bot Status"}
    }[st.session_state.lang]

    # --- SIDEBAR: SETTINGS & INTEGRATIONS ---
    with st.sidebar:
        st.title("⚙️ Cài đặt / Admin")
        
        # 1. Giao diện & Ngôn ngữ
        st.subheader("🎨 Giao diện")
        st.session_state.lang = 'vi' if st.radio("Ngôn ngữ", ["Tiếng Việt 🇻🇳", "English 🇬🇧"]) == "Tiếng Việt 🇻🇳" else 'en'
        st.session_state.theme = 'light' if st.radio("Theme", ["Sáng (Xuân) 🌸", "Tối (Cyber) 🌙"]) == "Sáng (Xuân) 🌸" else 'dark'
        
        st.divider()
        
        # 2. INTEGRATIONS (TÍNH NĂNG MỚI)
        st.subheader("🔗 Kênh Tích Hợp (Bot)")
        st.info("Kết nối AI với các kênh chat của công ty.")
        
        c_tele, c_zalo, c_mess = st.container(), st.container(), st.container()
        
        # Telegram
        with c_tele:
            on_tele = st.toggle("Telegram Bot", value=st.session_state.integrations['tele'])
            if on_tele:
                st.text_input("Token Telegram", type="password", placeholder="1234:ABC-DEF...")
                st.caption("✅ Đã kết nối: @AuditFintechBot")
            st.session_state.integrations['tele'] = on_tele
            
        # Zalo
        with c_zalo:
            on_zalo = st.toggle("Zalo OA", value=st.session_state.integrations['zalo'])
            if on_zalo:
                st.text_input("Zalo OA ID", placeholder="123456789")
                st.caption("⏳ Đang chờ duyệt quyền...")

        # Messenger
        with c_mess:
            st.toggle("Messenger (Facebook)", disabled=True, value=False)
            st.caption("🔜 Coming soon")
            
        st.divider()
        if st.button("🚪 Đăng Xuất"):
            st.session_state.logged_in = False
            st.rerun()

    # --- MAIN UI ---
    st.markdown(f"<h1 style='text-align: center; font-family: sans-serif; color: #E91E63;'>✿ {T['title']} ✿</h1>", unsafe_allow_html=True)

    col_L, col_R = st.columns([1.5, 1])

    # CỘT TRÁI: INPUT DATA
    with col_L:
        st.markdown('<div class="cute-card main-content">', unsafe_allow_html=True)
        
        # Trạng thái Bot Integrations (Hiển thị nhanh)
        if st.session_state.integrations['tele']:
            st.success("🔵 Telegram Bot: Đang trực tuyến (Sẵn sàng bắn cảnh báo)")
        
        tabs = st.tabs([f"📂 {T['tab1']}", f"🌱 {T['tab2']}", f"☁️ {T['tab3']}"])
        
        # Tab Excel
        with tabs[0]:
            st.file_uploader("Kéo thả file vào đây", type=['xlsx', 'csv'])
            if st.button("🚀 Chạy Kiểm Tra", key="b1"):
                with st.status("Đang gọi điệp viên 007...", expanded=True):
                    time.sleep(1)
                    st.write("✅ Đã đọc dữ liệu...")
                    time.sleep(1)
                    st.write("🚀 Đang gửi sang AWS Cloud...")
                st.success("Xong! Check kết quả bên Chat nhé.")

        # Tab Google Sheet
        with tabs[1]:
            st.text_input("Dán link Google Sheet:")
            st.button("🚀 Đồng bộ ngay", key="b2")

        # Tab Excel Online
        with tabs[2]:
            st.text_input("Link OneDrive/Excel Online:")
            st.button("🚀 Kết nối", key="b3")
            
        st.markdown('</div>', unsafe_allow_html=True)

        # Log
        st.markdown('<div class="cute-card main-content" style="min-height: 200px;">', unsafe_allow_html=True)
        st.subheader("📠 System Logs")
        st.code("10:00:01 [INFO] User admin logged in.\n10:00:05 [INFO] Telegram Bot Connected.\n10:05:22 [WAIT] Waiting for file upload...", language="bash")
        st.markdown('</div>', unsafe_allow_html=True)

    # CỘT PHẢI: CHATBOT
    with col_R:
        st.markdown('<div class="cute-card main-content" style="height: 600px; display: flex; flex-direction: column;">', unsafe_allow_html=True)
        st.subheader(f"💬 {T['chat']}")
        
        chat_box = st.container(height=450)
        with chat_box:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"], avatar="🌸" if msg["role"]=="assistant" else "👤"):
                    st.write(msg["content"])
        
        if prompt := st.chat_input("Gõ lệnh vào đây..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_box:
                with st.chat_message("user", avatar="👤"): st.write(prompt)
            
            # Fake response
            reply = "Đợi em xíu..."
            if "tele" in prompt.lower(): reply = "Dạ, em đã bật kết nối Telegram rồi ạ. Có biến là em báo ngay!"
            elif "file" in prompt.lower(): reply = "Sếp cứ up file Excel lên đi, em soi ra lỗi ngay lập tức."
            else: reply = "Dạ rõ sếp! Đang xử lý ạ 🌸"
            
            time.sleep(0.5)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with chat_box:
                with st.chat_message("assistant", avatar="🌸"): st.write(reply)
                
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. LOGIC CHẠY APP ---
if st.session_state.logged_in:
    main_dashboard()
else:
    login_screen()