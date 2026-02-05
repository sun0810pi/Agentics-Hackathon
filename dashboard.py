import streamlit as st
import pandas as pd
import boto3
import json
import time

# --- CẤU HÌNH AWS ---
# (Nhớ thay key thật của ông vào đây hoặc dùng st.secrets)
AWS_ACCESS_KEY = "AKIA_XXXXX"
AWS_SECRET_KEY = "YYYYYY"
SFN_ARN = "arn:aws:states:ap-southeast-1:110577990896:stateMachine:Agent3_Workflow"
REGION = "ap-southeast-1"

# Kết nối AWS
try:
    sfn = boto3.client(
        'stepfunctions',
        region_name=REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
except:
    st.error("⚠️ Lỗi kết nối AWS. Kiểm tra lại Key.")

# --- HÀM XỬ LÝ GOOGLE SHEET ---
def load_gsheet(url):
    # Hack: Chuyển link edit thành link export csv
    # Link gốc: https://docs.google.com/.../edit?gid=0
    # Link CSV: https://docs.google.com/.../export?format=csv&gid=0
    try:
        if "docs.google.com" in url:
            csv_url = url.replace('/edit#gid=', '/export?format=csv&gid=')
            csv_url = csv_url.replace('/edit?gid=', '/export?format=csv&gid=')
            return pd.read_csv(csv_url)
    except:
        return None
    return None

# --- GIAO DIỆN CHÍNH ---
st.set_page_config(page_title="Fintech Audit Hub", layout="wide", page_icon="⚡")
st.title("⚡ TRUNG TÂM ĐỐI SOÁT TỰ ĐỘNG (AI AGENT)")

# TẠO 3 TAB NHẬP LIỆU
tab1, tab2, tab3 = st.tabs(["📝 Nhập Tay", "📂 Upload Excel", "googlesheets Link Google Sheet"])

payloads = [] # Danh sách các giao dịch cần check

# --- TAB 1: NHẬP TAY ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        inv = st.number_input("Invoice Amount", 50000000)
        po = st.number_input("PO Amount", 50000000)
    with col2:
        sup = st.text_input("Supplier Name", "VinFast")
        email = st.text_input("Email", "acc@vinfast.vn")
    
    if st.button("🚀 Kiểm tra giao dịch này"):
        payloads.append({
            "invoice_amount": inv, "po_amount": po, 
            "supplier": sup, "email": email
        })

# --- TAB 2: UPLOAD EXCEL ---
with tab2:
    uploaded_file = st.file_uploader("Kéo thả file Excel/CSV vào đây", type=['xlsx', 'csv'])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.dataframe(df.head(3)) # Hiện 3 dòng đầu check
            
            if st.button("🚀 Xử lý toàn bộ file Excel"):
                # Chuẩn hóa tên cột và tạo payload
                df.columns = df.columns.str.lower().str.strip()
                # Map tên cột (Giả sử file excel có cột 'invoice', 'po'...)
                for _, row in df.iterrows():
                    payloads.append({
                        "invoice_amount": float(row.get('invoice', 0)),
                        "po_amount": float(row.get('po', 0)),
                        "supplier": str(row.get('supplier', 'Unknown')),
                        "email": str(row.get('email', 'N/A'))
                    })
        except Exception as e:
            st.error(f"Lỗi đọc file: {e}")

# --- TAB 3: GOOGLE SHEET (KILLER FEATURE) ---
with tab3:
    st.info("💡 Mẹo: Nhớ chuyển Google Sheet sang chế độ 'Anyone with the link' can view.")
    sheet_url = st.text_input("Dán link Google Sheet vào đây:")
    
    if sheet_url:
        df_sheet = load_gsheet(sheet_url)
        if df_sheet is not None:
            st.success("✅ Đã kết nối Google Sheet thành công!")
            st.dataframe(df_sheet.head(3))
            
            if st.button("🚀 Đồng bộ & Kiểm tra ngay"):
                df_sheet.columns = df_sheet.columns.str.lower().str.strip()
                for _, row in df_sheet.iterrows():
                    payloads.append({
                        "invoice_amount": float(row.get('invoice', 0)),
                        "po_amount": float(row.get('po', 0)),
                        "supplier": str(row.get('supplier', 'Unknown')),
                        "email": str(row.get('email', 'N/A'))
                    })
        else:
            st.warning("Không đọc được link. Hãy chắc chắn link đúng định dạng.")

# --- XỬ LÝ GỬI ĐI AWS (CHUNG CHO CẢ 3 TAB) ---
if payloads:
    st.divider()
    st.subheader(f"🔄 Đang đẩy {len(payloads)} giao dịch vào Core AI...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, p in enumerate(payloads):
        # GỌI STEP FUNCTION
        try:
            sfn.start_execution(
                stateMachineArn=SFN_ARN,
                input=json.dumps(p)
            )
            status_text.text(f"Đang xử lý: {p['supplier']} - ${p['invoice_amount']}")
            time.sleep(0.1) # Delay nhẹ cho đỡ lag
            progress_bar.progress((i + 1) / len(payloads))
        except Exception as e:
            st.error(f"Lỗi gửi AWS: {e}")
            
    st.success("✅ ĐÃ HOÀN TẤT! HỆ THỐNG AGENT ĐANG CHẠY NGẦM.")
    st.balloons()