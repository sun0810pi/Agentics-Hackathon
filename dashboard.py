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
        # aws_access_key_id="...",    <-- Điền key nếu chạy local
        # aws_secret_access_key="...",
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],
        aws_secret_access_key=st.secrets["AWS_SECRET_KEY"]
    )
    SFN_ARN = st.secrets["SFN_ARN"]
    DEMO_MODE = False
except:
    DEMO_MODE = True

# Init State
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Chào sếp! Hệ thống Audit đã sẵn sàng. Gửi file để em soi lỗi cho! 🌸"}]
if 'integrations' not in st.session_state: st.session_state.integrations = {"tele": False, "zalo": False}

# --- 2. HÀM CSS ĐỘNG ---
def inject_css():
    theme = st.session_state.get("theme_radio", "Sáng (Light) ☀️")
    if "Sáng" in theme:
        bg_url = "https://img.freepik.com/free-vector/hand-painted-watercolor-pastel-sky-background_23-2148902771.jpg"
        text_color = "#333333"
        card_bg = "rgba(255, 255, 255, 0.95)"
        sidebar_bg = "rgba(255, 255, 255, 0.95)"
        verdict_ok = "#d4edda"
        verdict_bad = "#f8d7da"
    else:
        bg_url = "https://img.freepik.com/free-photo/abstract-luxury-gradient-blue-background-smooth-dark-blue-with-black-vignette_1258-48251.jpg"
        text_color = "#ffffff"
        card_bg = "rgba(20, 25, 40, 0.9)"
        sidebar_bg = "rgba(10, 10, 15, 0.95)"
        verdict_ok = "rgba(40, 167, 69, 0.3)"
        verdict_bad = "rgba(220, 53, 69, 0.3)"

    st.markdown(f"""
    <style>
        .stApp {{ background-image: url("{bg_url}"); background-size: cover; background-attachment: fixed; }}
        h1, h2, h3, p, div, span, label, li {{ color: {text_color} !important; }}
        [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; }}
        .cute-card {{ background-color: {card_bg}; padding: 25px; border-radius: 15px; margin-bottom: 20px; backdrop-filter: blur(5px); box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid rgba(128,128,128,0.1); }}
        .stTextInput input {{ border-radius: 10px; }}
        
        /* Style cho kết quả Audit */
        .audit-pass {{ background-color: {verdict_ok}; padding: 15px; border-radius: 10px; border-left: 5px solid #28a745; margin-top: 10px; }}
        .audit-fail {{ background-color: {verdict_bad}; padding: 15px; border-radius: 10px; border-left: 5px solid #dc3545; margin-top: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC XỬ LÝ (PROCESSING) ---
def process_data_frame(df):
    df.columns = df.columns.str.lower().str.strip()
    payloads = []
    for _, row in df.iterrows():
        inv = next((c for c in df.columns if 'invoice' in c or 'hóa đơn' in c or 'amount' in c), None)
        po = next((c for c in df.columns if 'po' in c or 'đơn hàng' in c), None)
        sup = next((c for c in df.columns if 'supplier' in c or 'nhà cung cấp' in c), None)
        email = next((c for c in df.columns if 'email' in c or 'liên hệ' in c), None)
        tax = next((c for c in df.columns if 'tax' in c or 'thuế' in c), None)

        item = {
            "invoice_amount": float(row[inv]) if inv else 0.0,
            "po_amount": float(row[po]) if po else 0.0,
            "supplier": str(row[sup]) if sup else "Unknown Supplier",
            "email": str(row[email]) if email else "N/A",
            "tax_id": str(row[tax]) if tax else "000000"
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

# --- 4. HÀM GỌI AWS & CHỜ KẾT QUẢ (POLLING) ---
def run_audit_flow(payload):
    """Gửi JSON -> Chờ Step Function chạy xong -> Lấy kết quả về"""
    if DEMO_MODE:
        time.sleep(1.5)
        # Giả lập kết quả trả về từ 3 Agent
        return {
            "supplier_token": "TOK_VINFAST...",
            "audit_status": "APPROVED" if payload['invoice_amount'] == payload['po_amount'] else "REJECTED",
            "risk_level": "LOW" if payload['invoice_amount'] == payload['po_amount'] else "HIGH",
            "ai_analysis": "✅ AI xác nhận: Dữ liệu khớp hoàn toàn." if payload['invoice_amount'] == payload['po_amount'] else "🚨 AI Cảnh báo: Chênh lệch số tiền lớn. Nghi vấn gian lận.",
            "ai_recommendation": "Cho phép thanh toán." if payload['invoice_amount'] == payload['po_amount'] else "Phong tỏa giao dịch ngay lập tức."
        }

    # 1. Start Execution
    try:
        response = sfn.start_execution(
            stateMachineArn=SFN_ARN,
            input=json.dumps(payload)
        )
        execution_arn = response['executionArn']
        
        # 2. Polling (Vòng lặp chờ kết quả)
        while True:
            status_res = sfn.describe_execution(executionArn=execution_arn)
            status = status_res['status']
            
            if status == 'SUCCEEDED':
                # Lấy Output cuối cùng (Từ Agent 3 trả về)
                output_str = status_res['output']
                return json.loads(output_str)
            elif status in ['FAILED', 'TIMED_OUT', 'ABORTED']:
                return {"error": "Quy trình thất bại trên AWS."}
            
            time.sleep(0.5) # Chờ 0.5s rồi check lại
    except Exception as e:
        return {"error": str(e)}

# --- 5. DASHBOARD CHÍNH ---
def main_dashboard():
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Cài Đặt")
        lang = st.radio("Ngôn ngữ", ["Tiếng Việt 🇻🇳", "English 🇬🇧"], key="lang_radio")
        theme = st.radio("Chế độ", ["Sáng (Light) ☀️", "Tối (Dark) 🌙"], key="theme_radio")
        st.divider()
        st.subheader("🔗 Kết Nối")
        st.toggle("Telegram Bot", key="tele_tog")
        st.divider()
        st.subheader("📖 Hướng Dẫn")
        guide = st.selectbox("Chọn:", ["-- Xem --", "Lấy Token Tele"])
        if guide == "Lấy Token Tele": st.info("Chat @BotFather -> /newbot")
        st.divider()
        if st.button("🚪 Đăng xuất"):
            st.session_state.logged_in = False
            st.rerun()

    inject_css()
    
    st.markdown(f"<h1 style='text-align: center; color: #E91E63;'>✿ TRUNG TÂM KIỂM TOÁN AI ✿</h1>", unsafe_allow_html=True)

    col_L, col_R = st.columns([1.5, 1])

    # CỘT TRÁI: NHẬP LIỆU & KẾT QUẢ CHI TIẾT
    with col_L:
        st.markdown('<div class="cute-card">', unsafe_allow_html=True)
        tabs = st.tabs(["📂 Upload Excel", "🌱 Google Sheet", "☁️ Excel Online"])
        
        df_to_process = None
        
        with tabs[0]:
            uploaded = st.file_uploader("Kéo thả file .xlsx / .csv", type=['xlsx', 'csv'])
            if uploaded:
                try: df_to_process = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
                except: st.error("Lỗi file")
        with tabs[1]:
            url = st.text_input("Link Sheet (Public):")
            if url: df_to_process = load_gsheet(url)
            
        # NÚT CHẠY & HIỂN THỊ KẾT QUẢ (PHẦN QUAN TRỌNG NHẤT)
        if df_to_process is not None:
            st.dataframe(df_to_process.head(3), height=100, use_container_width=True)
            
            if st.button("🚀 KÍCH HOẠT HỆ THỐNG AGENT", type="primary", use_container_width=True):
                payloads = process_data_frame(df_to_process)
                
                st.divider()
                st.subheader("📡 KẾT QUẢ ĐỐI SOÁT (REAL-TIME)")
                
                # Thanh tiến trình tổng
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Container chứa kết quả
                result_container = st.container()

                for i, p in enumerate(payloads):
                    status_text.markdown(f"**Đang xử lý giao dịch của: {p['supplier']}...**")
                    
                    # GỌI HÀM CHẠY THẬT (Chờ kết quả về)
                    result = run_audit_flow(p)
                    
                    # HIỂN THỊ KẾT QUẢ ĐẸP MẮT
                    with result_container:
                        with st.expander(f"Giao dịch #{i+1}: {p['supplier']} - ${p['invoice_amount']:,.0f}", expanded=True):
                            
                            if "error" in result:
                                st.error(result["error"])
                            else:
                                c1, c2 = st.columns([1, 3])
                                
                                # Cột 1: Trạng thái (APPROVED / REJECTED)
                                with c1:
                                    status = result.get('audit_status', 'UNKNOWN')
                                    risk = result.get('risk_level', 'UNKNOWN')
                                    
                                    if status == "APPROVED":
                                        st.markdown(f"""
                                        <div style="text-align:center; padding:10px; background:#d4edda; border-radius:10px; border:2px solid #28a745;">
                                            <h2 style="color:#28a745; margin:0;">✅ PASS</h2>
                                            <p style="margin:0; color:#155724;">Rủi ro: {risk}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"""
                                        <div style="text-align:center; padding:10px; background:#f8d7da; border-radius:10px; border:2px solid #dc3545;">
                                            <h2 style="color:#dc3545; margin:0;">🚫 REJECT</h2>
                                            <p style="margin:0; color:#721c24;">Rủi ro: {risk}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                
                                # Cột 2: Lời giải thích của AI (Agent 3)
                                with c2:
                                    st.markdown(f"**🤖 AI Phân tích:** {result.get('ai_analysis', 'N/A')}")
                                    st.markdown(f"**💡 Khuyến nghị:** _{result.get('ai_recommendation', 'N/A')}_")
                                    st.caption(f"Token ID: {result.get('supplier_token', 'N/A')}")

                    progress_bar.progress((i + 1) / len(payloads))
                
                status_text.success("🎉 Đã hoàn tất kiểm tra toàn bộ hồ sơ!")
                st.balloons()
                
        st.markdown('</div>', unsafe_allow_html=True)

    # CỘT PHẢI: CHATBOT
    with col_R:
        st.markdown('<div class="cute-card" style="height: 700px; display: flex; flex-direction: column;">', unsafe_allow_html=True)
        st.subheader("💬 Trợ Lý AI")
        chat_con = st.container(height=550)
        with chat_con:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"], avatar="🤖" if msg["role"]=="assistant" else "👤"):
                    st.write(msg["content"])
        
        if prompt := st.chat_input("Hỏi về kết quả vừa rồi..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_con:
                with st.chat_message("user", avatar="👤"): st.write(prompt)
            
            # Logic trả lời giả lập AI
            reply = "Dạ, sếp xem chi tiết ở cột bên trái nhé. AI đã phân tích kỹ từng giao dịch rồi ạ!"
            if "lỗi" in prompt.lower() or "reject" in prompt.lower():
                reply = "Các giao dịch bị Reject thường do lệch số tiền giữa Hóa đơn và PO. Agent 3 đánh giá rủi ro cao nên chặn lại ạ."
            
            time.sleep(0.5)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with chat_con:
                with st.chat_message("assistant", avatar="🤖"): st.write(reply)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 6. LOGIN ---
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