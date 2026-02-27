"""Simple i18n for Vietnamese/English support."""

TRANSLATIONS = {
    "en": {
        # Login
        "app_subtitle": "SWIN Hackathon 2026",
        "sign_in": "Sign In",
        "sign_up": "Sign Up",
        "email": "Email Address",
        "password": "Password",
        "signin_btn": "Sign In →",
        "demo_accounts": "Demo Accounts",
        "email_placeholder": "admin@agentflow.ai",
        "pwd_placeholder": "••••••••",
        "enter_email": "Please enter your email",
        "enter_password": "Please enter your password",
        "invalid_creds": "❌ Invalid credentials",
        "signing_in": "Signing in...",
        "signup_unavailable": "Sign up not available in demo mode.",
        "create_account": "Create Account",
        "full_name": "Full Name",
        "name_placeholder": "John Doe",
        "confirm_password": "Confirm Password",
        "reg_coming_soon": "Registration coming soon",
        # Nav
        "navigation": "Navigation",
        "logout": "Logout",
        "confirm_logout": "Confirm logout?",
        "yes": "Yes", "no": "No",
        # Pages
        "overview": "Overview", "upload": "Upload", "fraud": "Fraud",
        "ml_insights": "ML Insights", "security": "Security",
        "observability": "Observability", "merchant": "Merchant",
        "integrations": "Integrations", "settings": "Settings",
        # Dashboard
        "dashboard_title": "📊 Dashboard Overview",
        "dashboard_subtitle": "Real-time fraud detection insights",
        "backend_demo": "⚠️ Backend unavailable — showing demo data.",
        "kpi_section": "Key Performance Indicators",
        "stats_section": "Processing Statistics",
        "total_processed": "Total Processed",
        "accuracy": "Accuracy",
        "fraud_prevented": "Fraud Prevented",
        "avg_latency": "Avg Latency",
        "approved": "Approved",
        "blocked": "Blocked",
        "pending": "Pending",
        "automation": "Automation Rate",
        # Settings
        "language": "Language",
        "theme": "Theme",
        "dark_mode": "Dark",
        "light_mode": "Light",
    },
    "vi": {
        # Login
        "app_subtitle": "SWIN Hackathon 2026",
        "sign_in": "Đăng Nhập",
        "sign_up": "Đăng Ký",
        "email": "Địa Chỉ Email",
        "password": "Mật Khẩu",
        "signin_btn": "Đăng Nhập →",
        "demo_accounts": "Tài Khoản Demo",
        "email_placeholder": "admin@agentflow.ai",
        "pwd_placeholder": "••••••••",
        "enter_email": "Vui lòng nhập email",
        "enter_password": "Vui lòng nhập mật khẩu",
        "invalid_creds": "❌ Thông tin đăng nhập không đúng",
        "signing_in": "Đang đăng nhập...",
        "signup_unavailable": "Chức năng đăng ký chưa khả dụng trong chế độ demo.",
        "create_account": "Tạo Tài Khoản",
        "full_name": "Họ và Tên",
        "name_placeholder": "Nguyễn Văn A",
        "confirm_password": "Xác Nhận Mật Khẩu",
        "reg_coming_soon": "Chức năng đăng ký sắp ra mắt",
        # Nav
        "navigation": "Điều Hướng",
        "logout": "Đăng Xuất",
        "confirm_logout": "Xác nhận đăng xuất?",
        "yes": "Có", "no": "Không",
        # Pages
        "overview": "Tổng Quan", "upload": "Tải Lên", "fraud": "Gian Lận",
        "ml_insights": "ML Insights", "security": "Bảo Mật",
        "observability": "Giám Sát", "merchant": "Merchant",
        "integrations": "Tích Hợp", "settings": "Cài Đặt",
        # Dashboard
        "dashboard_title": "📊 Tổng Quan Dashboard",
        "dashboard_subtitle": "Thông tin phát hiện gian lận theo thời gian thực",
        "backend_demo": "⚠️ Backend không khả dụng — đang hiển thị dữ liệu demo.",
        "kpi_section": "Chỉ Số Hiệu Suất",
        "stats_section": "Thống Kê Xử Lý",
        "total_processed": "Tổng Xử Lý",
        "accuracy": "Độ Chính Xác",
        "fraud_prevented": "Gian Lận Ngăn Chặn",
        "avg_latency": "Độ Trễ TB",
        "approved": "Đã Duyệt",
        "blocked": "Đã Chặn",
        "pending": "Đang Chờ",
        "automation": "Tự Động Hóa",
        # Settings
        "language": "Ngôn Ngữ",
        "theme": "Giao Diện",
        "dark_mode": "Tối",
        "light_mode": "Sáng",
    }
}

def t(key: str) -> str:
    """Translate key based on current language in session state."""
    import streamlit as st
    lang = st.session_state.get("language", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
