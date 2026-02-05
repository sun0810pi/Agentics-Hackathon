import streamlit as st
import pandas as pd
import boto3
import json
import time

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Fintech Audit Core", layout="wide", page_icon="⚡")

# --- CẤU HÌNH AWS (THAY KEY CỦA ÔNG VÀO ĐÂY) ---
# Cách tốt nhất là dùng st.secrets, nhưng để test nhanh ông điền thẳng vào đây cũng được
AWS_ACCESS_KEY = "AKIA_xxxxxxxxx" 
AWS_SECRET_KEY = "yyyyyyyyyyyyyy"
# Copy ARN của Step Function dán vào đây
SFN_ARN = "arn:aws:states:ap-southeast-1:110577990896:stateMachine:Agent3_Workflow" 
REGION = "ap-southeast-1"

# Kết nối AWS Step Functions
try:
    sfn = boto3.client(
        'stepfunctions',
        region_name=REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    is_connected = True
except Exception as e:
    st.error(f"⚠️ Lỗi kết nối AWS: {e}")
    is_connected = False

# --- HÀM XỬ LÝ GOOGLE SHEET (Magic Link) ---
def load_gsheet(url):
    """Biến link Google Sheet thường thành link CSV để tải"""
    try:
        if "docs.google.com" in url:
            # Chiêu hack: Thay /edit thành /export?format=csv
            csv_url = url.replace('/edit#gid=', '/export?format=csv&gid=')
            csv_url = csv_url.replace('/edit?gid=', '/export?format=csv&gid=')
            # Nếu link dạng share ngắn, thêm export vào cuối
            if "export" not in csv_url:
                 csv_url += "/export?format=csv"
            return pd.read_csv(csv_url)
    except Exception as e:
        st.error(f"Không đọc được Google Sheet. Lỗi: {e}")
        return None
    return None

# --- HÀM CHUẨN HÓA DỮ LIỆU (QUAN TRỌNG) ---
def normalize_data(df):
    """Đồng bộ tên cột từ Excel/Sheet thành chuẩn JSON cho Agent 1"""
    # 1. Chuyển hết tên cột về chữ thường, xóa khoảng trắng
    df.columns = df.columns.str.lower().str.strip()
    
    normalized_rows = []
    
    # 2. Duyệt từng dòng và map vào chuẩn
    for _, row in df.iterrows():
        # Tìm cột thông minh: Dù file ghi là "Invoice Value" hay "Tien Hoa Don" cũng ráng bắt
        # Logic: Tìm cột có chữ 'invoice' hoặc lấy mặc định 0
        inv_col = next((c for c in df.columns if 'invoice' in c or 'hóa đơn' in c), None)
        po_col = next((c for c in df.columns if 'po' in c or 'đơn hàng' in c), None)
        sup_col = next((c for c in df.columns if 'supplier' in c or 'cung cấp' in c), None)
        email_col = next((c for c in df.columns if 'email' in c or 'mail' in c), None)
        
        item = {
            "invoice_amount": float(row[inv_col]) if inv_col else 0.0,
            "po_amount": float(row[po_col]) if po_col else 0.0,
            "supplier": str(row[sup_col]) if sup_col else "Unknown",
            "email": str(row[email_col]) if email_col else "N/A"
        }
        normalized_rows.append(item)
        
    return normalized_rows

# --- GIAO DIỆN CHÍNH ---
st.title("⚡ HỆ THỐNG ĐỐI SOÁT TỰ ĐỘNG (MULTI-CHANNEL)")
st.markdown("---")

if not is_connected:
    st.warning("Vui lòng cấu hình AWS Key trong code để chạy.")
    st.stop()

# TẠO TABS
tab_excel, tab_sheet = st.tabs(["📂 UPLOAD EXCEL (Batch)", "☁️ GOOGLE SHEET (Live)"])

payloads_to_send = [] # Chứa danh sách sẽ gửi đi

# === TAB 1: EXCEL / CSV ===
with tab_excel:
    st.subheader("Nhập liệu lô lớn từ File")
    uploaded_file = st.file_uploader("Kéo thả file Excel (.xlsx) hoặc CSV vào đây", type=['xlsx', 'csv'])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_upload = pd.read_csv(uploaded_file)
            else:
                df_upload = pd.read_excel(uploaded_file)
            
            st.dataframe(df_upload.head(3), use_container_width=True)
            st.caption(f"Đã tìm thấy {len(df_upload)} dòng giao dịch.")
            
            if st.button("🚀 Xử lý File này", key="btn_excel"):
                payloads_to_send = normalize_data(df_upload)
                
        except Exception as e:
            st.error(f"Lỗi đọc file: {e}")

# === TAB 2: GOOGLE SHEET ===
with tab_sheet:
    st.subheader("Kết nối dữ liệu thời gian thực")
    st.info("💡 Lưu ý: Google Sheet phải để chế độ **'Anyone with the link'** (Bất kỳ ai có đường liên kết).")
    
    sheet_url = st.text_input("Dán link Google Sheet vào đây:", placeholder="https://docs.google.com/spreadsheets/d/...")
    
    if sheet_url:
        df_sheet = load_gsheet(sheet_url)
        
        if df_sheet is not None:
            st.success("✅ Kết nối thành công!")
            st.dataframe(df_sheet.head(3), use_container_width=True)
            st.caption(f"Đã tìm thấy {len(df_sheet)} dòng giao dịch.")
            
            if st.button("🚀 Đồng bộ & Xử lý ngay", key="btn_sheet"):
                payloads_to_send = normalize_data(df_sheet)

# === PHẦN XỬ LÝ CHUNG (GỬI SANG AWS) ===
if payloads_to_send:
    st.divider()
    st.subheader(f"🔄 Đang kích hoạt Agent cho {len(payloads_to_send)} giao dịch...")
    
    # Thanh tiến trình
    my_bar = st.progress(0)
    status_text = st.empty()
    col_res1, col_res2 = st.columns(2)
    
    success_count = 0
    
    for i, payload in enumerate(payloads_to_send):
        try:
            # GỌI STEP FUNCTIONS
            # Mỗi dòng là 1 lần gọi riêng biệt (Parallel processing)
            response = sfn.start_execution(
                stateMachineArn=SFN_ARN,
                input=json.dumps(payload)
            )
            
            # Cập nhật giao diện
            status_text.text(f"Đang xử lý: {payload['supplier']}...")
            my_bar.progress((i + 1) / len(payloads_to_send))
            success_count += 1
            time.sleep(0.1) # Delay nhẹ để thấy hiệu ứng chạy
            
        except Exception as e:
            st.error(f"Lỗi gửi dòng {i}: {e}")

    my_bar.empty()
    status_text.empty()
    
    st.success(f"✅ ĐÃ HOÀN TẤT! {success_count} Quy trình Audit đang chạy ngầm trên AWS.")
    st.balloons()
    
    # Hiển thị log nhỏ
    with st.expander("Xem chi tiết dữ liệu đã gửi"):
        st.json(payloads_to_send)