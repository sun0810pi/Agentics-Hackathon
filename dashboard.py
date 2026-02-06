import streamlit as st
import boto3
import json
import time
import pandas as pd
import io
from datetime import datetime

# --- 1. CẤU HÌNH & STATE ---
st.set_page_config(
    page_title="Audit Core V3",
    page_icon="💎",
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

# Init State
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "SYSTEM ONLINE. Ready for audit..."}]
if 'lang' not in st.session_state: st.session_state.lang = 'vi'
if 'theme' not in st.session_state: st.session_state.theme = 'dark' # Mặc định ngầu

# --- 2. LOGIC XỬ LÝ DỮ LIỆU (SMART ENGINE) ---
def process_and_send(df):
    """Chuẩn hóa, kiểm tra lỗi và trả về danh sách hợp lệ + danh sách lỗi"""
    df.columns = df.columns.str.lower().str.strip()
    valid_payloads = []
    error_logs = []
    
    inv_col = next((c for c in df.columns if 'invoice' in c or 'hóa đơn' in c or 'amount' in c), None)
    po_col = next((c for c in df.columns if 'po' in c or 'đơn hàng' in c), None)
    sup_col = next((c for c in df.columns if 'supplier' in c or 'nhà cung cấp' in c), None)

    if not inv_col or not po_col:
        return [], ["❌ Không tìm thấy cột 'Hóa đơn' hoặc 'PO'."]

    for index, row in df.iterrows():
        try:
            inv_val = float(row[inv_col])
            po_val = float(row[po_col])
            if inv_val < 0 or po_val < 0:
                error_logs.append(f"Dòng {index+2}: Số tiền không được âm.")
                continue
            valid_payloads.append({
                "invoice_amount": inv_val,
                "po_amount": po_val,
                "supplier": str(row[sup_col]) if sup_col else "Unknown",
                "row_index": index + 2
            })
        except:
            error_logs.append(f"Dòng {index+2}: Lỗi định dạng số.")
    return valid_payloads, error_logs

def load_gsheet(url):
    try:
        csv_url = url.replace('/edit#gid=', '/export?format=csv&gid=').replace('/edit?gid=', '/export?format=csv&gid=')
        if "export" not in csv_url: csv_url += "/export?format=csv"
        return pd.read_csv(csv_url)
    except: return None

# --- 3. CSS CAO CẤP (GLASSMORPHISM) ---
def inject_css():
    # A. DARK MODE (CYBERPUNK)
    if st.session_state.theme == 'dark':
        bg_url = "https://img.freepik.com/free-photo/abstract-digital-grid-black-background_53876-97647.jpg"
        text_color = "#00FFC2" # Xanh Neon
        card_bg = "rgba(0, 0, 0, 0.7)" # Đen mờ
        sidebar_bg = "rgba(10, 10, 10, 0.9)"
        input_bg = "#111"
        border_color = "#00FFC2"
        
        # CSS Upload file cho nền tối
        upload_fix = """
        [data-testid="stFileUploader"] { background-color: #0a0a0a; border: 1px dashed #00FFC2; }
        [data-testid="stFileUploader"] section > div { color: #fff !important; }
        [data-testid="stFileUploader"] small { color: #888 !important; }
        """
        
    # B. LIGHT MODE (PROFESSIONAL CLEAN)
    else:
        bg_url = "https://img.freepik.com/free-vector/white-abstract-background-design_23-2148825582.jpg"
        text_color = "#1f2937" # Xám đậm
        card_bg = "rgba(255, 255, 255, 0.75)" # Trắng mờ
        sidebar_bg = "rgba(255, 255, 255, 0.95)"
        input_bg = "#f9fafb"
        border_color = "#3b82f6" # Xanh dương
        
        # CSS Upload file cho nền sáng (FIX LỖI MỜ)
        upload_fix = """
        [data-testid="stFileUploader"] { background-color: #f0f9ff; border: 2px dashed #3b82f6; }
        [data-testid="stFileUploader"] section > div, [data-testid="stFileUploader"] div { color: #000000 !important; font-weight: 600; }
        [data-testid="stFileUploader"] small { color: #333 !important; opacity: 1 !important; }
        """

    st.markdown(f"""
    <style>
        /* Import Font xịn */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        .stApp {{
            background-image: url("{bg_url}");
            background-size: cover;
            background-attachment: fixed;
            font-family: 'Inter', sans-serif;
        }}
        
        h1, h2, h3, p, span, label, div {{ color: {text_color} !important; }}
        
        /* Sidebar sang trọng */
        [data-testid="stSidebar"] {{ 
            background-color: {sidebar_bg} !important; 
            border-right: 1px solid rgba(255,255,255,0.1); 
            backdrop-filter: blur(10px);
        }}
        
        /* Card hiệu ứng kính mờ (Glassmorphism) */
        .glass-card {{
            background: {card_bg};
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 20px;
        }}
        
        /* Input Field đẹp */
        .stTextInput input {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
            border: 1px solid {border_color};
            border-radius: 8px;
        }}
        
        /* Nút bấm */
        .stButton button {{
            background: linear-gradient(45deg, {border_color}, #8b5cf6);
            color: white !important;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s;
        }}
        .stButton button:hover {{
            transform: scale(1.02);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        /* Expander (Menu xổ xuống) */
        .streamlit-expanderHeader {{
            background-color: transparent;
            border-radius: 8px;
            color: {text_color} !important;
            font-weight: 600;
        }}
        
        {upload_fix}
    </style>
    """, unsafe_allow_html=True)

# --- 4. DASHBOARD CHÍNH ---
def main_dashboard():
    
    # --- A. SIDEBAR ---
   with st.sidebar:
        st.title("⚙️ CONTROL PANEL")
        def update_ui():
            st.session_state.lang = 'vi' if "Việt" in st.session_state.lang_sel else 'en'
            st.session_state.theme = 'light' if "Light" in st.session_state.theme_sel else 'dark'
        st.radio("Language", ["Tiếng Việt 🇻🇳", "English 🇬🇧"], key="lang_sel", on_change=update_ui, index=0 if st.session_state.lang=='vi' else 1)
        st.radio("Theme", ["Dark (Cyber) ⚡", "Light (Clean) ☀️"], key="theme_sel", on_change=update_ui, index=0 if st.session_state.theme=='dark' else 1)
        st.divider()
        
        # 2. Integrations (Fix lỗi không hiện ô nhập)
        st.caption("Bot Connections")
        
        # Telegram
        with st.expander("🔵 Telegram"):
            tele_active = st.toggle("Enable Telegram")
            if tele_active:
                st.text_input("API Token", type="password", placeholder="1234:ABC...", help="Lấy từ BotFather")
                st.text_input("Chat ID", placeholder="-9988...", help="ID nhóm chat")
        
        # Zalo
        with st.expander("🔵 Zalo OA"):
            zalo_active = st.toggle("Enable Zalo")
            if zalo_active:
                st.text_input("OA ID", placeholder="4628...")
                st.text_input("Secret Key", type="password")

        # Slack
        with st.expander("🟣 Slack"):
            slack_active = st.toggle("Enable Slack")
            if slack_active:
                st.text_input("Webhook URL", type="password", placeholder="https://hooks.slack.com/...")

        st.divider()
        
        # 3. Guides (Dùng Expander thay vì Selectbox -> UX tốt hơn)
        st.caption("Documentation")
        with st.expander("📖 Cách lấy Token Telegram"):
            st.markdown("1. Chat **@BotFather** -> `/newbot`.\n2. Copy Token.\n3. Chat **@userinfobot** lấy ID.")
        
        with st.expander("📖 Cách lấy Zalo Key"):
            st.markdown("1. Vào **oa.zalo.me** lấy OA ID.\n2. Vào **developers.zalo.me** lấy Secret Key.")

        if st.button("🔴 LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()
            
# Trong phần main_dashboard, sau khi gọi hàm validation:
payloads, errors = process_and_send(df)

if errors:
    with st.expander(f"⚠️ Phát hiện {len(errors)} dòng lỗi (Bị loại bỏ)"):
        for err in errors:
            st.warning(err)

if payloads:
    st.success(f"✅ Đã làm sạch {len(payloads)} dòng dữ liệu sẵn sàng gửi AI.")
    # Nút bấm xác nhận gửi lên AWS

    inject_css()
    
    # --- B. MAIN UI ---
    
    
    st.markdown('<h1 style="text-align: center;">AUDIT HUB V4</h1>', unsafe_allow_html=True)
    col_L, col_R = st.columns([1.2, 1.8], gap="medium")

    with col_L:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📂 DATA SOURCE")
        
        f = st.file_uploader("Kéo thả Excel/CSV tại đây", type=['xlsx', 'csv'])
        if f:
            df = pd.read_csv(f) if f.name.endswith('.csv') else pd.read_excel(f)
            st.dataframe(df.head(3), use_container_width=True)
            
            if st.button("🚀 BẮT ĐẦU ĐỐI SOÁT"):
                # CHỈ GỌI KHI CÓ df VÀ BẤM NÚT
                payloads, errors = process_and_send_v2(df)
                
                # Lưu vào session_state để cột bên phải hiển thị
                st.session_state.valid_data = payloads
                st.session_state.error_data = errors
        st.markdown('</div>', unsafe_allow_html=True)

    with col_R:
        st.markdown('<div class="glass-card" style="min-height: 500px;">', unsafe_allow_html=True)
        
        # Hiển thị lỗi nếu có
        if 'error_data' in st.session_state and st.session_state.error_data:
            with st.expander(f"⚠️ Phát hiện {len(st.session_state.error_data)} dòng lỗi"):
                for err in st.session_state.error_data:
                    st.warning(err)
        
        # Xử lý gửi AWS
        if 'valid_data' in st.session_state and st.session_state.valid_data:
            st.success(f"✅ Sẵn sàng xử lý {len(st.session_state.valid_data)} giao dịch.")
            # Thực hiện vòng lặp gửi dữ liệu sfn.start_execution ở đây...
        else:
            st.info("Chờ dữ liệu từ cột bên trái...")
        st.markdown('</div>', unsafe_allow_html=True)
    # Header động
    if st.session_state.theme == 'dark':
        st.markdown('<h1 style="text-align: center; text-shadow: 0 0 20px #00FFC2;">/// AUDIT CORE V4 ///</h1>', unsafe_allow_html=True)
    else:
        st.markdown('<h1 style="text-align: center; color: #1e3a8a !important;">✿ FINANCIAL AUDIT HUB ✿</h1>', unsafe_allow_html=True)

    col_L, col_R = st.columns([1.2, 1.8], gap="medium")

    # === CỘT TRÁI: DATA INPUT ===
    with col_L:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📂 DATA SOURCE")
        
        tabs = st.tabs(["UPLOAD FILE", "GOOGLE SHEET", "DIRECT LINK"])
        payloads = []
        
        # Tab 1: Upload
        with tabs[0]:
            f = st.file_uploader("Excel / CSV", type=['xlsx', 'csv'])
            if f:
                try:
                    df = pd.read_csv(f) if f.name.endswith('.csv') else pd.read_excel(f)
                    st.dataframe(df.head(3), use_container_width=True)
                    if st.button("🚀 EXECUTE BATCH", key="b1"):
                        payloads = process_and_send(df)
                except Exception as e: st.error(f"Error: {e}")

        # Tab 2: GSheet
        with tabs[1]:
            url = st.text_input("Sheet URL (Public):")
            if url and st.button("🚀 SYNC DATA", key="b2"):
                df = load_gsheet(url)
                if df is not None:
                    st.dataframe(df.head(3), use_container_width=True)
                    payloads = process_and_send(df)
                else: st.error("Invalid Link")
        
        # Tab 3: Online Link (Đã fix Coming Soon)
        with tabs[2]:
            onl = st.text_input("Direct .xlsx Link:")
            if onl and st.button("🚀 FETCH", key="b3"):
                try:
                    df = pd.read_excel(onl)
                    st.dataframe(df.head(3), use_container_width=True)
                    payloads = process_and_send(df)
                except: st.error("Fetch Failed")

        st.markdown('</div>', unsafe_allow_html=True)

    # === CỘT PHẢI: CONSOLE / CHAT ===
    with col_R:
        st.markdown('<div class="glass-card" style="height: 650px; overflow-y: auto;">', unsafe_allow_html=True)
        
        # MODE 1: ĐANG CHẠY (LOGS)
        if payloads:
            st.subheader("⚡ PROCESSING LOGS")
            log_container = st.empty()
            logs = []
            bar = st.progress(0)
            
            for i, p in enumerate(payloads):
                ts = datetime.now().strftime("%H:%M:%S")
                bk = p.get('bank_account', 'N/A')
                logs.append(f"[{ts}] TXN #{i+1} | SUP: {p['supplier']} | BANK: {bk} -> SENT")
                
                # Hiển thị log đẹp
                if st.session_state.theme == 'dark':
                    log_html = "<br>".join([f"<span style='color:#00FFC2; font-family:monospace'>{l}</span>" for l in logs[-12:]])
                else:
                    log_html = "<br>".join([f"<div style='border-bottom:1px solid #eee; padding:4px;'>{l}</div>" for l in logs[-12:]])
                
                log_container.markdown(log_html, unsafe_allow_html=True)
                
                # Gửi AWS
                if not DEMO_MODE:
                    try: sfn.start_execution(stateMachineArn=SFN_ARN, input=json.dumps(p))
                    except: pass
                else: time.sleep(0.15)
                
                bar.progress((i+1)/len(payloads))
            
            st.success("✅ BATCH COMPLETED. AGENTS ARE WORKING.")
            st.balloons()
            
        # MODE 2: CHATBOT (KHI RẢNH)
        else:
            st.subheader("💬 AI ASSISTANT")
            
            chat_con = st.container()
            with chat_con:
                for msg in st.session_state.messages:
                    align = "right" if msg["role"] == "user" else "left"
                    bg = "#3b82f6" if msg["role"] == "user" else "rgba(128,128,128,0.2)"
                    st.markdown(f"""
                    <div style="text-align: {align}; margin: 10px 0;">
                        <span style="background: {bg}; padding: 10px 15px; border-radius: 15px; display: inline-block; color: white !important;">
                            {msg['content']}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            
            if prompt := st.chat_input("Ask about transactions..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. LOGIN SCREEN ---
def login_screen():
    # Style riêng cho Login
    if st.session_state.theme == 'dark':
        st.markdown("""<style>.stApp { background-color: #000; }</style>""", unsafe_allow_html=True)
        box_bg = "rgba(0,0,0,0.8)"
        border = "1px solid #00FFC2"
        title_col = "#00FFC2"
    else:
        st.markdown("""<style>.stApp { background-image: url("https://img.freepik.com/free-vector/white-abstract-background-design_23-2148825582.jpg"); background-size: cover; }</style>""", unsafe_allow_html=True)
        box_bg = "rgba(255,255,255,0.9)"
        border = "1px solid #ddd"
        title_col = "#333"

    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background: {box_bg}; padding: 40px; border-radius: 20px; text-align: center; border: {border}; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
            <h1 style="color: {title_col} !important; font-family: sans-serif;">🔒 SECURE LOGIN</h1>
        </div>
        """, unsafe_allow_html=True)
        
        user = st.text_input("Identity", placeholder="admin")
        pwd = st.text_input("Passcode", type="password", placeholder="123")
        
        if st.button("AUTHENTICATE", type="primary", use_container_width=True):
            if user == "admin" and pwd == "123":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Access Denied")

# ENTRY POINT
if st.session_state.logged_in:
    main_dashboard()
else:
    login_screen()