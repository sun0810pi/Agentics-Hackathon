import streamlit as st
import boto3
import json
import time
import pandas as pd # Import thêm để hiển thị bảng nếu cần

# --- CẤU HÌNH GIAO DIỆN (Phải đầu tiên) ---
st.set_page_config(
    page_title="Fintech Shield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS TÙY CHỈNH CHO ĐẸP ---
st.markdown("""
<style>
    /* Tô màu tiêu đề chính */
    .main-header {
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF914D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    /* Làm nổi bật khung kết quả */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: #00C897 !important;
    }
    /* Viền nhẹ cho form */
    [data-testid="stForm"] {
        border: 1px solid #ddd;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: Thông tin dự án ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2345/2345338.png", width=120)
    st.title("🛡️ Fintech Shield")
    st.caption("Hệ thống kiểm toán tự động bằng AI Multi-Agent")
    st.markdown("---")
    st.markdown("### 👨‍💻 Team Agentics")
    st.info("Dự án Hackathon 2026. Sử dụng AWS Step Functions và LLM để phát hiện gian lận tài chính.")
    st.markdown("---")
    st.write("🔴 Trạng thái hệ thống: **Online**")


# --- KẾT NỐI AWS (Giữ nguyên logic cũ) ---
try:
    sfn = boto3.client(
        'stepfunctions',
        region_name='ap_southeast_1',
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],
        aws_secret_access_key=st.secrets["AWS_SECRET_KEY"]
    )
    SFN_ARN = st.secrets["SFN_ARN"]
    aws_connected = True
except:
    aws_connected = False


# --- GIAO DIỆN CHÍNH ---
# Tiêu đề dùng HTML tùy chỉnh cho đẹp
st.markdown('<p class="main-header">🚀 TRUNG TÂM ĐIỀU HÀNH KIỂM TOÁN AI</p>', unsafe_allow_html=True)
st.markdown("#### 🧠 Luồng xử lý: Data Masking ➡️ AI Phân tích rủi ro ➡️ Blockchain Log")
st.divider()

# Chia cột tỷ lệ 4:6 để phần kết quả rộng hơn chút
col1, col2 = st.columns([4, 6], gap="large")

with col1:
    st.subheader("📋 Thông tin Giao dịch đầu vào")
    with st.form("input_form"):
        # Dùng cột trong form để gọn hơn
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            invoice_amt = st.number_input("💰 Tiền Hóa đơn (VNĐ)", value=55000000, step=1000000)
            supplier = st.text_input("🏢 Nhà cung cấp", value="Tech Solutions Co.")
            tax_id = st.text_input("🔢 Mã số thuế", value="0312345678")
        with f_col2:
            po_amt = st.number_input("📑 Tiền Đơn hàng PO (VNĐ)", value=50000000, step=1000000)
            email = st.text_input("📧 Email liên hệ (Sẽ che)", value="contact@techsol.vn")
            note = st.text_input("📝 Ghi chú ngắn", value="Thanh toán HĐ tháng 10")
        
        st.markdown("---")
        # Nút submit to và nổi bật
        submitted = st.form_submit_button("🔥 KÍCH HOẠT ĐỘI QUÂN AI 🔥", type="primary", use_container_width=True)

with col2:
    st.subheader("📡 Trạng thái & Kết quả Phân tích (Real-time)")
    # Container để chứa kết quả, tạo khung viền
    result_container = st.container(border=True)
    
    with result_container:
        status_box = st.empty() # Khung loading

        if not aws_connected:
             st.warning("⚠️ Chưa kết nối AWS Secrets. Vui lòng cấu hình trên Streamlit Cloud để chạy thật.")

        if submitted and aws_connected:
            # 1. Chuẩn bị Input
            input_payload = {
                "invoice_amount": invoice_amt, "po_amount": po_amt,
                "supplier": supplier, "email": email,
                "tax_id": tax_id, "note": note
            }
            
            # 2. Gọi AWS Step Functions
            try:
                status_box.markdown("### 🔄 Đang khởi động workflow trên AWS Cloud...")
                # Tạo hiệu ứng loading đẹp hơn
                with st.spinner('⚡ Các AI Agent đang chạy đua vũ trang... Vui lòng đợi...'):
                    response = sfn.start_execution(
                        stateMachineArn=SFN_ARN,
                        input=json.dumps(input_payload)
                    )
                    execution_arn = response['executionArn']
                    
                    # 3. Vòng lặp chờ kết quả (Polling)
                    while True:
                        status = sfn.describe_execution(executionArn=execution_arn)
                        state = status['status']
                        
                        if state == 'SUCCEEDED':
                            status_box.empty() # Xóa loading
                            st.balloons() # Bắn pháo hoa chúc mừng
                            
                            st.success("✅ QUY TRÌNH HOÀN TẤT! Đã có kết quả đánh giá.")
                            
                            # Lấy output và xử lý
                            output_str = status['output']
                            output_json = json.loads(output_str)
                            
                            # --- PHẦN HIỂN THỊ KẾT QUẢ "MÀU MÈ" ---
                            st.divider()
                            st.markdown("### 🎯 Tổng hợp Đánh giá")

                            # Giả sử output_json trả về có các trường này (Bạn cần điều chỉnh theo output thật của Agent 5)
                            # Ví dụ output_json = {"risk_score": 85, "status": "HIGH RISK", "reason": "PO lệch Invoice quá lớn", "masked_email": "c***@techsol.vn"}
                            
                            # Fake data để demo giao diện (XÓA ĐOẠN NÀY KHI CHẠY THẬT NẾU JSON CỦA BẠN ĐỦ DỮ LIỆU)
                            if "risk_score" not in output_json:
                                output_json["risk_score"] = 15 if abs(invoice_amt - po_amt) < 1000000 else 85
                                output_json["status"] = "AN TOÀN" if output_json["risk_score"] < 30 else "RỦI RO CAO"
                                output_json["reason"] = "Chênh lệch PO/Invoice chấp nhận được." if output_json["risk_score"] < 30 else "Cảnh báo: Chênh lệch số tiền lớn!"

                            
                            # Hiển thị bằng thẻ Metric (Nhìn chuyên nghiệp hơn)
                            m1, m2, m3 = st.columns(3)
                            with m1:
                                st.metric("Điểm Rủi ro (Risk Score)", f"{output_json.get('risk_score', 0)}/100", delta="-Thấp là tốt" if output_json.get('risk_score', 0) < 50 else "+Cao là nguy hiểm", delta_color="inverse")
                            with m2:
                                status_text = output_json.get('status', 'Unknown')
                                st.metric("Kết luận cuối cùng", status_text)
                            with m3:
                                # Ví dụ hiển thị một dữ liệu đã được che
                                st.metric("Email đã Masking", output_json.get('masked_email', 'e***@***.vn'))
                            
                            st.markdown(f"**📌 Lý do chính:** *{output_json.get('reason', 'Không có chi tiết')}*")

                            with st.expander("🔍 Xem chi tiết dữ liệu JSON gốc (Cho Dev)"):
                                st.json(output_json)
                            break
                            
                        elif state in ['FAILED', 'TIMED_OUT', 'ABORTED']:
                            status_box.error(f"❌ Quy trình thất bại trên AWS. Trạng thái: {state}")
                            break
                        
                        time.sleep(2) # Chờ 2s check lại
                        
            except Exception as e:
                status_box.error(f"Lỗi hệ thống: {str(e)}")
        elif not submitted:
            status_box.info("👈 Nhập dữ liệu bên trái và bấm Kích hoạt để bắt đầu.")