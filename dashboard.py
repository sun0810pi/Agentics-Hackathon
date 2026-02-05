import streamlit as st
import boto3
import json
import time
import pandas as pd
from datetime import datetime

# --- 1. CONFIG & STATE ---
st.set_page_config(
    page_title="Audit Buddy AI",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Khởi tạo State mặc định
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
# Lưu ý: Chúng ta sẽ dùng key của widget để quản lý state tự động
if 'messages' not in st.session_state: 
    st.session_state.messages = [{"role": "assistant", "content": "Chào bạn! Mình là Trợ lý hướng dẫn 🤖. Bạn chưa biết lấy Token Telegram hay Zalo? Hỏi mình nhé!"}]
if 'integrations' not in st.session_state:
    st.session_state.integrations = {"tele": False, "zalo": False, "slack": False}

# --- 2. HÀM CSS ĐỘNG (THEO THEME) ---
def inject_css():
    # Lấy theme từ widget (nếu chưa có thì mặc định Light)
    theme = st.session_state.get("theme_radio", "Sáng (Light) ☀️")
    
    if "Sáng" in theme:
        # Nền Sáng: Mây trời Pastel
        bg_url = "https://img.freepik.com/free-vector/hand-painted-watercolor-pastel-sky-background_23-2148902771.jpg"
        text_color = "#333333"
        card_bg = "rgba(255, 255, 255, 0.9)"
        sidebar_bg = "rgba(255, 255, 255, 0.95)"
        input_bg = "#ffffff"
    else:
        # Nền Tối: Đêm hội (Tối hẳn để tương phản tốt)
        bg_url = "https://img.freepik.com/free-photo/abstract-luxury-gradient-blue-background-smooth-dark-blue-with-black-vignette_1258-48251.jpg"
        text_color = "#ffffff"
        card_bg = "rgba(20, 25, 40, 0.9)"
        sidebar_bg = "rgba(10, 10, 15, 0.95)"
        input_bg = "#2d2d3d"

    st.markdown(f"""
    <style>
        /* NỀN CHÍNH */
        .stApp {{
            background-image: url("{bg_url}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
        
        /* MÀU CHỮ TOÀN BỘ */
        h1, h2, h3, p, div, span, label, li {{
            color: {text_color} !important;
        }}

        /* SIDEBAR */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
            border-right: 1px solid rgba(100,100,100,0.2);
        }}

        /* CARD (KHUNG CHỨA) */
        .cute-card {{
            background-color: {card_bg};
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            backdrop-filter: blur(5px);
            margin-bottom: 20px;
            border: 1px solid rgba(150,150,150,0.2);
        }}

        /* INPUT BOX */
        .stTextInput input, .stFileUploader {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
            border-radius: 8px;
        }}
        
        /* CHAT BUBBLES */
        .stChatMessage {{
            background-color: {card_bg};
            border-radius: 10px;
        }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. MÀN HÌNH LOGIN ---
def login_screen():
    # Gọi CSS mặc định cho màn login
    st.markdown(f"""<style>.stApp {{ background-image: url("https://img.freepik.com/free-vector/hand-painted-watercolor-pastel-sky-background_23-2148902771.jpg"); background-size: cover; }}</style>""", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown('<div style="background: rgba(255,255,255,0.9); padding: 30px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
        st.markdown("<h1 style='color: #E91E63; margin-bottom: 0;'>🌸 FinTech Hub</h1>", unsafe_allow_html=True)
        st.caption("Hệ thống kiểm toán tự động")
        
        user = st.text_input("Tài khoản", placeholder="admin")
        pwd = st.text_input("Mật khẩu", type="password", placeholder="123")
        
        if st.button("🚀 Đăng Nhập", type="primary", use_container_width=True):
            if user == "admin" and pwd == "123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Sai mật khẩu! (Gợi ý: admin / 123)")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. DASHBOARD CHÍNH ---
def main_dashboard():
    
    # --- A. SIDEBAR MENU ---
    with st.sidebar:
        st.title("⚙️ Cài Đặt")
        
        # 1. GIAO DIỆN & NGÔN NGỮ (Dùng key để auto-update state)
        st.subheader("🎨 Giao diện")
        lang = st.radio("Ngôn ngữ", ["Tiếng Việt 🇻🇳", "English 🇬🇧"], key="lang_radio")
        theme = st.radio("Chế độ", ["Sáng (Light) ☀️", "Tối (Dark) 🌙"], key="theme_radio")
        
        st.divider()
        
        # 2. MENU TÍCH HỢP BOT
        st.subheader("🔗 Kết Nối Bot")
        
        with st.expander("Telegram Bot"):
            on_tele = st.toggle("Kích hoạt Tele", value=st.session_state.integrations['tele'])
            if on_tele:
                st.text_input("Bot Token", type="password", placeholder="1234:ABC...")
                st.success("Đã kết nối")
            st.session_state.integrations['tele'] = on_tele
            
        with st.expander("Zalo OA"):
            on_zalo = st.toggle("Kích hoạt Zalo", value=st.session_state.integrations['zalo'])
            if on_zalo:
                st.text_input("OA ID", placeholder="Nhập ID...")
            st.session_state.integrations['zalo'] = on_zalo

        st.divider()
        
        # 3. HƯỚNG DẪN LẤY TOKEN (MENU MỚI)
        st.subheader("📖 Hướng Dẫn")
        guide_opt = st.selectbox("Chọn hướng dẫn:", ["-- Chọn --", "Lấy Token Telegram", "Lấy Token Zalo", "Lấy Token Slack"])
        
        if guide_opt == "Lấy Token Telegram":
            st.info("""
            **Cách lấy Token Telegram:**
            1. Mở Telegram, tìm **@BotFather**.
            2. Chat lệnh `/newbot`.
            3. Đặt tên cho Bot.
            4. BotFather sẽ đưa mã **Token** (dạng `1234:ABC...`).
            5. Copy mã đó dán vào ô bên trên.
            """)
        elif guide_opt == "Lấy Token Zalo":
            st.info("""
            **Cách kết nối Zalo OA:**
            1. Vào `developers.zalo.me`.
            2. Tạo ứng dụng mới.
            3. Vào mục **Official Account**.
            4. Lấy **OA ID** và **Secret Key**.
            """)
        elif guide_opt == "Lấy Token Slack":
             st.info("""
            **Cách lấy Token Slack:**
            1. Vào `api.slack.com/apps`.
            2. Tạo App mới -> Chọn Workspace.
            3. Vào **OAuth & Permissions**.
            4. Copy **Bot User OAuth Token**.
            """)
            
        st.divider()
        if st.button("🚪 Đăng xuất"):
            st.session_state.logged_in = False
            st.rerun()

    # --- B. INJECT CSS SAU KHI SIDEBAR ĐÃ CHỌN THEME ---
    inject_css() 

    # --- C. MAIN CONTENT ---
    
    # Từ điển ngôn ngữ
    is_vi = "Việt" in lang
    T = {
        'title': "Trung Tâm Kiểm Toán AI" if is_vi else "AI Audit Hub",
        'sub': "Hệ thống đối soát tự động đa kênh" if is_vi else "Automated Omni-channel Reconciliation",
        'tab1': "Tải Excel" if is_vi else "Upload Excel",
        'tab2': "Google Sheet",
        'tab3': "Excel Online",
        'chat': "Trợ Lý Hướng Dẫn 🤖" if is_vi else "Support Guide Bot 🤖",
        'drag': "Kéo thả file .xlsx / .csv vào đây" if is_vi else "Drag & Drop .xlsx / .csv here"
    }

    st.markdown(f"<h1 style='text-align: center; color: #E91E63;'>✿ {T['title']} ✿</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; opacity: 0.8;'>{T['sub']}</p>", unsafe_allow_html=True)

    col_L, col_R = st.columns([1.5, 1])

    # CỘT TRÁI: NHẬP LIỆU
    with col_L:
        st.markdown('<div class="cute-card">', unsafe_allow_html=True)
        
        # Tabs
        tab1, tab2, tab3 = st.tabs([f"📂 {T['tab1']}", f"🌱 {T['tab2']}", f"☁️ {T['tab3']}"])
        
        with tab1:
            st.file_uploader(T['drag'], type=['xlsx', 'csv'])
            if st.button("🚀 Run Audit", type="primary"):
                with st.spinner("Processing..."):
                    time.sleep(1.5)
                st.success("Done! Data sent to AWS.")
        
        with tab2:
            st.text_input("Link Google Sheet (Public):")
            st.button("Sync Now")
            
        with tab3:
            st.text_input("Link Excel Online:")
            st.button("Connect")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Log Box
        st.markdown('<div class="cute-card" style="min-height: 200px;">', unsafe_allow_html=True)
        st.subheader("📠 System Logs")
        st.code(f"[INFO] Theme: {theme}\n[INFO] Language: {lang}\n[INFO] Telegram: {'Connected' if st.session_state.integrations['tele'] else 'Disconnected'}", language="bash")
        st.markdown('</div>', unsafe_allow_html=True)

    # CỘT PHẢI: CHATBOT HƯỚNG DẪN
    with col_R:
        st.markdown('<div class="cute-card" style="height: 650px; display: flex; flex-direction: column;">', unsafe_allow_html=True)
        st.subheader(f"💬 {T['chat']}")
        
        # Chat History Container
        chat_con = st.container(height=500)
        with chat_con:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"], avatar="🤖" if msg["role"]=="assistant" else "👤"):
                    st.write(msg["content"])
        
        # Chat Input logic
        if prompt := st.chat_input("Hỏi cách dùng app..."):
            # 1. User Message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_con:
                with st.chat_message("user", avatar="👤"): st.write(prompt)
            
            # 2. Bot Logic (Support Guide)
            reply = ""
            p_lower = prompt.lower()
            
            if "tele" in p_lower or "token" in p_lower:
                reply = "Để lấy Token Telegram: Bạn vào mục 'Cài Đặt' bên trái -> Chọn menu 'Hướng dẫn' -> Chọn 'Lấy Token Telegram' nhé!"
            elif "zalo" in p_lower:
                reply = "Kết nối Zalo cần tạo OA trước. Bạn xem hướng dẫn chi tiết ở cột bên trái nhé."
            elif "excel" in p_lower or "file" in p_lower:
                reply = "Bạn hãy kéo file Excel vào Tab đầu tiên bên trái, sau đó bấm nút 'Run Audit' màu đỏ nhé."
            elif "sheet" in p_lower:
                reply = "Nhớ chia sẻ Google Sheet ở chế độ 'Public' (Ai có link cũng xem được) thì mình mới đọc được nha."
            else:
                reply = "Mình là Bot hướng dẫn. Bạn có thể hỏi: 'Cách lấy token tele', 'Cách up file excel', hoặc xem menu Hướng dẫn bên trái."
            
            # 3. Bot Reply
            time.sleep(0.5)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with chat_con:
                with st.chat_message("assistant", avatar="🤖"): st.write(reply)

        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. RUN APP ---
if st.session_state.logged_in:
    main_dashboard()
else:
    login_screen()