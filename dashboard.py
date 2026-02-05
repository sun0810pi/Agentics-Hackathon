import streamlit as st
import boto3
import json
import time

#giao diện web app
st.set_page_config(page_title="Fintech AI Agent", page_icon="🤖", layout="wide")

#KẾT NỐI AWS (Lấy từ Secrets của Streamlit)
try:
    sfn = boto3.client(
        'stepfunctions',
        region_name='ap_southeast_1', # Đổi nếu bạn dùng region khác
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],
        aws_secret_access_key=st.secrets["AWS_SECRET_KEY"]
    )
    # ARN của Step Function (Lấy từ Secrets luôn cho bảo mật)
    SFN_ARN = st.secrets["SFN_ARN"]
except:
    st.warning("⚠️ Chưa cấu hình AWS Secrets. Web đang chạy chế độ Offline.")

# --- GIAO DIỆN CHÍNH ---
st.title("🤖 HỆ THỐNG KIỂM TOÁN TỰ ĐỘNG (AI AGENT)")
st.markdown("### 🚀 Luồng xử lý: Data Masking -> AI Phân tích -> Blockchain Log")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1️⃣ Nhập thông tin giao dịch")
    with st.form("input_form"):
        invoice_amt = st.number_input("Số tiền trên Hóa đơn (Invoice)", value=50000000)
        po_amt = st.number_input("Số tiền trên Đơn hàng (PO)", value=50000000)
        supplier = st.text_input("Tên Nhà cung cấp", value="VinFast Trading")
        email = st.text_input("Email liên hệ (Sẽ được che)", value="ketoan@vinfast.vn")
        tax_id = st.text_input("Mã số thuế", value="0312345678")
        note = st.text_area("Ghi chú", value="Thanh toán đợt 1")
        
        submitted = st.form_submit_button("🚀 Kích hoạt Agent Kiểm toán")

with col2:
    st.subheader("2️⃣ Trạng thái Xử lý (Real-time)")
    status_box = st.empty() # Khung để hiện loading
    result_box = st.container() # Khung hiện kết quả

if submitted:
    # 1. Chuẩn bị Input
    input_payload = {
        "invoice_amount": invoice_amt,
        "po_amount": po_amt,
        "supplier": supplier,
        "email": email,
        "tax_id": tax_id,
        "note": note
    }
    
    # 2. Gọi AWS Step Functions
    try:
        status_box.info("🔄 Đang gửi lệnh tới AWS Cloud...")
        
        response = sfn.start_execution(
            stateMachineArn=SFN_ARN,
            input=json.dumps(input_payload)
        )
        execution_arn = response['executionArn']
        
        # 3. Vòng lặp chờ kết quả (Polling)
        with st.spinner('Các Agent đang chạy đua vũ trang...'):
            while True:
                status = sfn.describe_execution(executionArn=execution_arn)
                state = status['status']
                
                if state == 'SUCCEEDED':
                    status_box.success("✅ QUY TRÌNH HOÀN TẤT!")
                    
                    # Lấy output cuối cùng
                    output_str = status['output']
                    output_json = json.loads(output_str)
                    
                    # Hiển thị đẹp
                    with result_box:
                        st.markdown("---")
                        st.metric(label="Trạng thái cuối cùng", value="APPROVED ✅")
                        st.json(output_json) # Hiện cục JSON cuối cùng từ Agent 5
                    break
                    
                elif state in ['FAILED', 'TIMED_OUT', 'ABORTED']:
                    status_box.error(f"❌ Quy trình thất bại: {state}")
                    break
                
                # Chờ 2 giây rồi check lại
                time.sleep(2)
                
    except Exception as e:
        status_box.error(f"Lỗi hệ thống: {str(e)}")