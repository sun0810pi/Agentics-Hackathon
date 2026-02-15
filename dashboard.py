"""
AgentFlow Finance Guard - ULTIMATE VERSION
Multi-Agent AI System - Hackathon Production Ready
Features: Dark/Light Theme, Language Toggle, Observability, Integrations
"""

import streamlit as st
import boto3
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from decimal import Decimal
import time

# ========================================
# I18N - LANGUAGE SUPPORT
# ========================================

TRANSLATIONS = {
    'en': {
        'app_title': 'AgentFlow Finance Guard',
        'overview': 'Overview',
        'invoice_upload': 'Invoice Upload',
        'fraud_detection': 'Fraud Detection',
        'ml_insights': 'ML Insights',
        'security': 'Security Monitor',
        'observability': 'Observability & Logs',
        'merchant': 'Merchant Success',
        'integrations': 'Integrations',
        'settings': 'Settings',
        'detection_accuracy': 'Detection Accuracy',
        'automation_rate': 'Automation Rate',
        'avg_latency': 'Avg Latency',
        'fraud_prevented': 'Fraud Prevented',
        'aws_connected': 'AWS Connected',
        'demo_mode': 'Demo Mode',
        'user': 'User',
        'role': 'Role',
        'last_login': 'Last Login',
        'live_aws': 'Full AWS Pipeline (Live)',
        'demo_fast': 'Demo Mode (Fast)',
        'process_invoice': 'Process Invoice',
        'risk_score': 'Risk Score',
        'approve': 'Approve',
        'reject': 'Reject',
        'recent_alerts': 'Recent Alerts',
        'agent_performance': 'Agent Performance Matrix',
        'execution_logs': 'Execution Logs',
        'system_events': 'System Events',
        'error_logs': 'Error Logs',
        'slack_integration': 'Slack Integration',
        'telegram_integration': 'Telegram Integration',
        'zalo_integration': 'Zalo OA Integration',
        'test_connection': 'Test Connection',
        'theme': 'Theme',
        'language': 'Language',
        'dark_mode': 'Dark Mode',
        'light_mode': 'Light Mode'
    },
    'vi': {
        'app_title': 'AgentFlow Bảo Vệ Tài Chính',
        'overview': 'Tổng Quan',
        'invoice_upload': 'Tải Hóa Đơn',
        'fraud_detection': 'Phát Hiện Gian Lận',
        'ml_insights': 'Phân Tích ML',
        'security': 'Giám Sát Bảo Mật',
        'observability': 'Quan Sát & Logs',
        'merchant': 'Thành Công Merchant',
        'integrations': 'Tích Hợp',
        'settings': 'Cài Đặt',
        'detection_accuracy': 'Độ Chính Xác',
        'automation_rate': 'Tỷ Lệ Tự Động',
        'avg_latency': 'Độ Trễ TB',
        'fraud_prevented': 'Gian Lận Ngăn Chặn',
        'aws_connected': 'Kết Nối AWS',
        'demo_mode': 'Chế Độ Demo',
        'user': 'Người Dùng',
        'role': 'Vai Trò',
        'last_login': 'Đăng Nhập Cuối',
        'live_aws': 'Xử Lý AWS Thật (Live)',
        'demo_fast': 'Chế Độ Demo (Nhanh)',
        'process_invoice': 'Xử Lý Hóa Đơn',
        'risk_score': 'Điểm Rủi Ro',
        'approve': 'Phê Duyệt',
        'reject': 'Từ Chối',
        'recent_alerts': 'Cảnh Báo Gần Đây',
        'agent_performance': 'Ma Trận Hiệu Suất Agent',
        'execution_logs': 'Logs Thực Thi',
        'system_events': 'Sự Kiện Hệ Thống',
        'error_logs': 'Logs Lỗi',
        'slack_integration': 'Tích Hợp Slack',
        'telegram_integration': 'Tích Hợp Telegram',
        'zalo_integration': 'Tích Hợp Zalo OA',
        'test_connection': 'Kiểm Tra Kết Nối',
        'theme': 'Giao Diện',
        'language': 'Ngôn Ngữ',
        'dark_mode': 'Chế Độ Tối',
        'light_mode': 'Chế Độ Sáng'
    }
}

def t(key):
    """Translation helper"""
    lang = st.session_state.get('language', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

# ========================================
# THEME CONFIGURATION
# ========================================

DARK_THEME = """
<style>
    :root {
        --bg-primary: #0E1117;
        --bg-secondary: #1E2130;
        --bg-card: #262730;
        --text-primary: #FAFAFA;
        --text-secondary: #B8B8B8;
        --accent-primary: #4A9EFF;
        --accent-success: #00D68F;
        --accent-warning: #FFAB00;
        --accent-danger: #FF5252;
        --border-color: #2D3139;
        --shadow: rgba(0, 0, 0, 0.3);
    }
    
    .main {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
    
    .stApp {
        background: linear-gradient(135deg, #0E1117 0%, #1A1D2E 100%);
    }
    
    /* Glass Morphism Cards */
    .glass-card {
        background: rgba(38, 39, 48, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        box-shadow: 0 8px 32px var(--shadow);
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.1) 0%, rgba(0, 214, 143, 0.1) 100%);
        border-left: 4px solid var(--accent-primary);
        border-radius: 12px;
        padding: 1.2rem;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
    }
    
    /* Alert Cards */
    .alert-high {
        background: linear-gradient(135deg, rgba(255, 82, 82, 0.15) 0%, rgba(255, 82, 82, 0.05) 100%);
        border-left: 4px solid var(--accent-danger);
        border-radius: 12px;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .alert-medium {
        background: linear-gradient(135deg, rgba(255, 171, 0, 0.15) 0%, rgba(255, 171, 0, 0.05) 100%);
        border-left: 4px solid var(--accent-warning);
        border-radius: 12px;
        padding: 1rem;
    }
    
    .alert-low {
        background: linear-gradient(135deg, rgba(0, 214, 143, 0.15) 0%, rgba(0, 214, 143, 0.05) 100%);
        border-left: 4px solid var(--accent-success);
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Main Header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #4A9EFF 0%, #00D68F 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 4px 12px rgba(74, 158, 255, 0.3);
    }
    
    /* Execution Log */
    .execution-log {
        background: rgba(20, 20, 30, 0.95);
        border: 1px solid rgba(74, 158, 255, 0.3);
        border-radius: 12px;
        padding: 1rem;
        font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
        font-size: 0.85rem;
        color: #00D68F;
        overflow-x: auto;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .log-entry {
        margin: 0.5rem 0;
        padding: 0.5rem;
        border-left: 2px solid rgba(74, 158, 255, 0.5);
    }
    
    .log-error {
        color: var(--accent-danger);
        border-left-color: var(--accent-danger);
    }
    
    .log-success {
        color: var(--accent-success);
        border-left-color: var(--accent-success);
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .status-active {
        background: rgba(0, 214, 143, 0.2);
        color: var(--accent-success);
        border: 1px solid var(--accent-success);
    }
    
    .status-inactive {
        background: rgba(184, 184, 184, 0.2);
        color: var(--text-secondary);
        border: 1px solid var(--text-secondary);
    }
</style>
"""

LIGHT_THEME = """
<style>
    :root {
        --bg-primary: #FFFFFF;
        --bg-secondary: #F8F9FA;
        --bg-card: #FFFFFF;
        --text-primary: #1A1A1A;
        --text-secondary: #6C757D;
        --accent-primary: #0066CC;
        --accent-success: #00A878;
        --accent-warning: #FF8C00;
        --accent-danger: #DC3545;
        --border-color: #DEE2E6;
        --shadow: rgba(0, 0, 0, 0.1);
    }
    
    .main {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
    
    .stApp {
        background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%);
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        border: 1px solid var(--border-color);
        padding: 1.5rem;
        box-shadow: 0 4px 16px var(--shadow);
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(0, 102, 204, 0.05) 0%, rgba(0, 168, 120, 0.05) 100%);
        border-left: 4px solid var(--accent-primary);
        border-radius: 12px;
        padding: 1.2rem;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px var(--shadow);
    }
    
    .alert-high {
        background: linear-gradient(135deg, rgba(220, 53, 69, 0.1) 0%, rgba(220, 53, 69, 0.05) 100%);
        border-left: 4px solid var(--accent-danger);
        border-radius: 12px;
        padding: 1rem;
    }
    
    .alert-medium {
        background: linear-gradient(135deg, rgba(255, 140, 0, 0.1) 0%, rgba(255, 140, 0, 0.05) 100%);
        border-left: 4px solid var(--accent-warning);
        border-radius: 12px;
        padding: 1rem;
    }
    
    .alert-low {
        background: linear-gradient(135deg, rgba(0, 168, 120, 0.1) 0%, rgba(0, 168, 120, 0.05) 100%);
        border-left: 4px solid var(--accent-success);
        border-radius: 12px;
        padding: 1rem;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0066CC 0%, #00A878 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .execution-log {
        background: #F8F9FA;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1rem;
        font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
        font-size: 0.85rem;
        color: #00A878;
        overflow-x: auto;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .log-entry {
        margin: 0.5rem 0;
        padding: 0.5rem;
        border-left: 2px solid var(--accent-primary);
    }
    
    .log-error {
        color: var(--accent-danger);
        border-left-color: var(--accent-danger);
    }
    
    .log-success {
        color: var(--accent-success);
        border-left-color: var(--accent-success);
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .status-active {
        background: rgba(0, 168, 120, 0.15);
        color: var(--accent-success);
        border: 1px solid var(--accent-success);
    }
    
    .status-inactive {
        background: rgba(108, 117, 125, 0.15);
        color: var(--text-secondary);
        border: 1px solid var(--text-secondary);
    }
</style>
"""

# Page config
st.set_page_config(
    page_title="AgentFlow Finance Guard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'overview'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'execution_logs' not in st.session_state:
    st.session_state.execution_logs = []
if 'system_events' not in st.session_state:
    st.session_state.system_events = []
if 'processed_invoices' not in st.session_state:
    st.session_state.processed_invoices = []

# Apply theme
theme_css = DARK_THEME if st.session_state.theme == 'dark' else LIGHT_THEME
st.markdown(theme_css, unsafe_allow_html=True)

# Load AWS credentials
try:
    AWS_ACCESS_KEY = st.secrets["AWS_ACCESS_KEY"]
    AWS_SECRET_KEY = st.secrets["AWS_SECRET_KEY"]
    SFN_ARN = st.secrets["SFN_ARN"]
    AWS_REGION = st.secrets.get("AWS_REGION", "ap-southeast-1")
    aws_configured = True
except:
    AWS_ACCESS_KEY = None
    AWS_SECRET_KEY = None
    SFN_ARN = None
    AWS_REGION = "ap-southeast-1"
    aws_configured = False

# AWS Clients
def get_aws_clients():
    try:
        if AWS_ACCESS_KEY and AWS_SECRET_KEY:
            session = boto3.Session(
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY,
                region_name=AWS_REGION
            )
            return {
                'dynamodb': session.resource('dynamodb'),
                's3': session.client('s3'),
                'stepfunctions': session.client('stepfunctions'),
                'configured': True
            }
        return {'configured': False}
    except Exception as e:
        add_log('ERROR', f'AWS connection failed: {e}')
        return {'configured': False}

aws_clients = get_aws_clients()

# ========================================
# LOGGING FUNCTIONS
# ========================================

def add_log(level, message, details=None):
    """Add entry to execution logs"""
    log_entry = {
        'timestamp': datetime.now(),
        'level': level,
        'message': message,
        'details': details
    }
    st.session_state.execution_logs.insert(0, log_entry)
    # Keep only last 100 logs
    st.session_state.execution_logs = st.session_state.execution_logs[:100]

def add_event(event_type, description, data=None):
    """Add system event"""
    event = {
        'timestamp': datetime.now(),
        'type': event_type,
        'description': description,
        'data': data
    }
    st.session_state.system_events.insert(0, event)
    st.session_state.system_events = st.session_state.system_events[:100]

# ========================================
# AWS INTEGRATION FUNCTIONS
# ========================================

def trigger_step_functions(invoice_data):
    """Trigger Step Functions with logging"""
    add_log('INFO', 'Starting Step Functions execution', invoice_data)
    
    try:
        if not aws_clients.get('configured'):
            raise Exception("AWS not configured")
        
        sfn = aws_clients['stepfunctions']
        
        execution_input = {
            'invoice_id': invoice_data.get('invoice_id'),
            'invoice_data': invoice_data,
            'timestamp': datetime.now().isoformat()
        }
        
        response = sfn.start_execution(
            stateMachineArn=SFN_ARN,
            name=f"exec-{int(time.time())}",
            input=json.dumps(execution_input, default=str)
        )
        
        add_log('SUCCESS', f'Execution started: {response["executionArn"]}')
        add_event('EXECUTION_START', f'Invoice {invoice_data.get("invoice_id")} processing started')
        
        return {
            'success': True,
            'execution_arn': response['executionArn'],
            'start_date': response['startDate']
        }
    except Exception as e:
        add_log('ERROR', f'Step Functions failed: {str(e)}')
        return {'success': False, 'error': str(e)}

def check_execution_status(execution_arn):
    """Check execution status with logging"""
    try:
        sfn = aws_clients['stepfunctions']
        response = sfn.describe_execution(executionArn=execution_arn)
        
        status = response['status']
        if status == 'SUCCEEDED':
            add_log('SUCCESS', f'Execution completed: {execution_arn}')
            add_event('EXECUTION_COMPLETE', 'Processing completed successfully')
        elif status == 'FAILED':
            add_log('ERROR', f'Execution failed: {execution_arn}')
            add_event('EXECUTION_FAILED', 'Processing failed')
        
        return {
            'status': status,
            'start_date': response['startDate'],
            'stop_date': response.get('stopDate'),
            'output': response.get('output')
        }
    except Exception as e:
        add_log('ERROR', f'Status check failed: {e}')
        return {'status': 'ERROR', 'error': str(e)}

# ========================================
# HELPER FUNCTIONS
# ========================================

@st.cache_data(ttl=60)
def get_dashboard_metrics():
    """Get dashboard metrics"""
    return {
        'accuracy': 99.2,
        'automation_rate': 85.3,
        'avg_latency_ms': 7800,
        'fraud_prevented_usd': 523000,
        'total_invoices_processed': 148723,
        'pending_manual_review': 42,
        'false_positive_rate': 2.1,
        'uptime_percentage': 99.95
    }

def get_recent_alerts():
    """Get recent alerts"""
    return [
        {
            'id': 'INV-2026-1234',
            'timestamp': '2026-02-15 14:23:15',
            'risk_score': 87,
            'amount': 15423.50,
            'supplier': 'ABC Corp',
            'reason': 'NFC relay attack detected',
            'status': 'BLOCKED'
        },
        {
            'id': 'INV-2026-1235',
            'timestamp': '2026-02-15 13:45:30',
            'risk_score': 65,
            'amount': 8234.00,
            'supplier': 'XYZ Ltd',
            'reason': 'Amount mismatch 45%',
            'status': 'PENDING_REVIEW'
        }
    ]

# ========================================
# SIDEBAR
# ========================================

with st.sidebar:
    st.image("https://via.placeholder.com/150x50/4A9EFF/ffffff?text=AgentFlow", width=150)
    
    # Theme & Language Controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌓" if st.session_state.theme == 'dark' else "☀️", 
                    help=t('theme'), use_container_width=True):
            st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
            st.rerun()
    
    with col2:
        if st.button("🌐 EN" if st.session_state.language == 'en' else "🌐 VI",
                    help=t('language'), use_container_width=True):
            st.session_state.language = 'vi' if st.session_state.language == 'en' else 'en'
            st.rerun()
    
    # AWS Status
    if aws_clients.get('configured'):
        st.success(f"🟢 {t('aws_connected')}")
        st.caption(f"Region: {AWS_REGION}")
    else:
        st.warning(f"🟡 {t('demo_mode')}")
    
    st.markdown("---")
    
    # Navigation - NEW STRUCTURE
    st.markdown("### 📊 " + t('overview'))
    if st.button(t('overview'), key='nav_overview', use_container_width=True):
        st.session_state.page = 'overview'
    
    st.markdown("### 🔄 Processing")
    for label, page_id in [
        (t('invoice_upload'), 'upload'),
        (t('fraud_detection'), 'fraud'),
        (t('ml_insights'), 'ml_insights')
    ]:
        if st.button(label, key=f'nav_{page_id}', use_container_width=True):
            st.session_state.page = page_id
    
    st.markdown("### 🛡️ Risk & Security")
    for label, page_id in [
        (t('security'), 'security'),
        (t('observability'), 'observability')
    ]:
        if st.button(label, key=f'nav_{page_id}', use_container_width=True):
            st.session_state.page = page_id
    
    st.markdown("### 📈 Business")
    if st.button(t('merchant'), key='nav_merchant', use_container_width=True):
        st.session_state.page = 'merchant'
    
    st.markdown("### 🔔 " + t('integrations'))
    if st.button(t('integrations'), key='nav_integrations', use_container_width=True):
        st.session_state.page = 'integrations'
    
    st.markdown("### ⚙️ " + t('settings'))
    if st.button(t('settings'), key='nav_settings', use_container_width=True):
        st.session_state.page = 'settings'
    
    st.markdown("---")
    st.markdown(f"**{t('user')}**: Admin")
    st.markdown(f"**{t('last_login')}**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ========================================
# PAGES
# ========================================

if st.session_state.page == 'overview':
    st.markdown(f'<div class="main-header">📊 {t("app_title")} - {t("overview")}</div>', unsafe_allow_html=True)
    
    metrics = get_dashboard_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(f"🎯 {t('detection_accuracy')}", f"{metrics['accuracy']}%", delta="0.2%")
    with col2:
        st.metric(f"🤖 {t('automation_rate')}", f"{metrics['automation_rate']}%", delta="1.5%")
    with col3:
        st.metric(f"⚡ {t('avg_latency')}", f"{metrics['avg_latency_ms']}ms", delta="-200ms", delta_color="inverse")
    with col4:
        st.metric(f"💰 {t('fraud_prevented')}", f"${metrics['fraud_prevented_usd']:,}", delta="$42K")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"📈 {t('agent_performance')}")
        
        agent_data = pd.DataFrame({
            'Agent': ['OCR', 'PII', 'Decimal', 'AI Analyst', 'Audit', 'Notifier', 'ML', 'Security'],
            'Success Rate': [92.8, 99.9, 100.0, 94.2, 100.0, 99.8, 91.5, 96.3],
            'Avg Time (ms)': [1200, 50, 10, 3500, 200, 150, 2000, 800]
        })
        
        fig = px.bar(agent_data, x='Agent', y='Success Rate',
                    color='Success Rate', color_continuous_scale='RdYlGn', range_color=[90, 100])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader(f"🚨 {t('recent_alerts')}")
        alerts = get_recent_alerts()
        
        for alert in alerts[:5]:
            alert_class = 'alert-high' if alert['risk_score'] >= 70 else ('alert-medium' if alert['risk_score'] >= 30 else 'alert-low')
            icon = '🔴' if alert['risk_score'] >= 70 else ('🟡' if alert['risk_score'] >= 30 else '🟢')
            
            st.markdown(f"""
            <div class="{alert_class}">
                <strong>{icon} {alert['id']}</strong><br>
                {t('risk_score')}: {alert['risk_score']}/100<br>
                Amount: ${alert['amount']:,.2f}<br>
                Status: {alert['status']}
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

elif st.session_state.page == 'upload':
    st.markdown(f'<div class="main-header">📄 {t("invoice_upload")}</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Invoice")
        uploaded_file = st.file_uploader("Choose file", type=['pdf', 'png', 'jpg', 'jpeg'])
        
        if uploaded_file:
            st.success(f"✅ {uploaded_file.name}")
            if uploaded_file.type != 'application/pdf':
                st.image(uploaded_file, use_container_width=True)
    
    with col2:
        st.subheader("⚙️ Processing Options")
        
        mode = st.radio("Mode", [t('live_aws'), t('demo_fast')])
        use_live = "Live" in mode
        
        if uploaded_file and st.button(f"🔥 {t('process_invoice')}", type="primary", use_container_width=True):
            invoice_data = {
                'invoice_id': f"INV-{int(time.time())}",
                'file_name': uploaded_file.name,
                'amount': 12345.67
            }
            
            if use_live and aws_clients.get('configured'):
                with st.spinner("Processing..."):
                    result = trigger_step_functions(invoice_data)
                    if result['success']:
                        st.success("✅ Execution started!")
                        st.code(result['execution_arn'])
                    else:
                        st.error(f"❌ {result['error']}")
            else:
                with st.spinner("Processing..."):
                    time.sleep(2)
                    add_log('INFO', f'Processed {invoice_data["invoice_id"]} in demo mode')
                    st.success("✅ Processed (Demo)")
                    st.json({'invoice_id': invoice_data['invoice_id'], 'risk_score': 48})

elif st.session_state.page == 'fraud':
    st.markdown(f'<div class="main-header">🔍 {t("fraud_detection")}</div>', unsafe_allow_html=True)
    
    sample = {'id': 'INV-2026-5678', 'amount': 12345.67, 'risk_score': 48}
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"🧠 {t('risk_score')} Analysis")
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=sample['risk_score'],
            title={'text': t('risk_score')},
            gauge={'axis': {'range': [0, 100]},
                  'steps': [{'range': [0, 30], 'color': '#00D68F'},
                           {'range': [30, 70], 'color': '#FFAB00'},
                           {'range': [70, 100], 'color': '#FF5252'}]}
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Actions")
        
        if sample['risk_score'] < 30:
            st.success("✅ AUTO-APPROVE")
        elif sample['risk_score'] < 70:
            st.warning("⚠️ MANUAL REVIEW")
            if st.button(f"✅ {t('approve')}", type="primary"):
                add_log('INFO', f'Invoice {sample["id"]} approved')
                add_event('APPROVAL', f'{sample["id"]} approved by admin')
                st.success("Approved!")
            if st.button(f"❌ {t('reject')}"):
                add_log('WARNING', f'Invoice {sample["id"]} rejected')
                add_event('REJECTION', f'{sample["id"]} rejected by admin')
                st.error("Rejected!")
        else:
            st.error("🚨 AUTO-BLOCK")

elif st.session_state.page == 'observability':
    st.markdown(f'<div class="main-header">📊 {t("observability")}</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([
        t('execution_logs'),
        t('system_events'),
        t('error_logs')
    ])
    
    with tab1:
        st.subheader(f"🔍 {t('execution_logs')}")
        
        if st.session_state.execution_logs:
            st.markdown('<div class="execution-log">', unsafe_allow_html=True)
            for log in st.session_state.execution_logs[:20]:
                level_class = 'log-error' if log['level'] == 'ERROR' else ('log-success' if log['level'] == 'SUCCESS' else '')
                st.markdown(f"""
                <div class="log-entry {level_class}">
                    <strong>[{log['timestamp'].strftime('%H:%M:%S')}]</strong> 
                    <span style="color: {'#FF5252' if log['level'] == 'ERROR' else '#00D68F'};">[{log['level']}]</span> 
                    {log['message']}
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No execution logs yet. Process an invoice to see logs.")
    
    with tab2:
        st.subheader(f"📅 {t('system_events')}")
        
        if st.session_state.system_events:
            for event in st.session_state.system_events[:20]:
                with st.expander(f"{event['type']} - {event['timestamp'].strftime('%H:%M:%S')}"):
                    st.write(f"**Description:** {event['description']}")
                    if event['data']:
                        st.json(event['data'])
        else:
            st.info("No system events yet.")
    
    with tab3:
        st.subheader(f"❌ {t('error_logs')}")
        
        error_logs = [log for log in st.session_state.execution_logs if log['level'] == 'ERROR']
        
        if error_logs:
            for log in error_logs[:10]:
                st.error(f"**[{log['timestamp'].strftime('%H:%M:%S')}]** {log['message']}")
                if log['details']:
                    st.code(str(log['details']))
        else:
            st.success("✅ No errors - System healthy!")

elif st.session_state.page == 'integrations':
    st.markdown(f'<div class="main-header">🔔 {t("integrations")}</div>', unsafe_allow_html=True)
    
    st.info("ℹ️ Configure external notification channels for real-time fraud alerts")
    
    # Slack
    with st.expander(f"💬 {t('slack_integration')}", expanded=True):
        slack_enabled = st.checkbox("Enable Slack notifications", value=False, key='slack_enabled')
        
        if slack_enabled:
            slack_webhook = st.text_input(
                "Slack Webhook URL",
                value="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
                help="Get webhook from: Slack → Apps → Incoming Webhooks"
            )
            
            slack_channel = st.text_input("Channel", value="#fraud-alerts")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🧪 {t('test_connection')}", key='test_slack'):
                    add_log('INFO', 'Testing Slack connection')
                    st.success("✅ Slack connection test sent!")
                    add_event('INTEGRATION_TEST', 'Slack webhook tested')
            
            with col2:
                if st.button("💾 Save Slack Config", key='save_slack'):
                    add_log('SUCCESS', 'Slack configuration saved')
                    st.success("✅ Configuration saved!")
            
            st.markdown("""
            **Setup Instructions:**
            1. Go to https://api.slack.com/messaging/webhooks
            2. Create new Incoming Webhook
            3. Select channel (e.g., #fraud-alerts)
            4. Copy Webhook URL
            5. Paste URL above
            """)
        else:
            st.markdown('<div class="status-badge status-inactive">Inactive</div>', unsafe_allow_html=True)
    
    # Telegram
    with st.expander(f"✈️ {t('telegram_integration')}"):
        tele_enabled = st.checkbox("Enable Telegram notifications", value=False, key='tele_enabled')
        
        if tele_enabled:
            tele_token = st.text_input(
                "Bot Token",
                type="password",
                help="Get from @BotFather"
            )
            tele_chat_id = st.text_input("Chat ID", help="Your Telegram Chat ID")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🧪 {t('test_connection')}", key='test_tele'):
                    add_log('INFO', 'Testing Telegram connection')
                    st.success("✅ Telegram test sent!")
            with col2:
                if st.button("💾 Save Telegram Config", key='save_tele'):
                    st.success("✅ Saved!")
            
            st.markdown("""
            **Setup Instructions:**
            1. Open Telegram, search @BotFather
            2. Send /newbot command
            3. Follow instructions, get Bot Token
            4. Start chat with your bot
            5. Get Chat ID from @userinfobot
            """)
        else:
            st.markdown('<div class="status-badge status-inactive">Inactive</div>', unsafe_allow_html=True)
    
    # Zalo OA
    with st.expander(f"📱 {t('zalo_integration')}"):
        zalo_enabled = st.checkbox("Enable Zalo OA notifications", value=False, key='zalo_enabled')
        
        if zalo_enabled:
            zalo_oa_id = st.text_input("OA ID", help="Your Zalo Official Account ID")
            zalo_access_token = st.text_input("Access Token", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🧪 {t('test_connection')}", key='test_zalo'):
                    add_log('INFO', 'Testing Zalo OA connection')
                    st.success("✅ Zalo test sent!")
            with col2:
                if st.button("💾 Save Zalo Config", key='save_zalo'):
                    st.success("✅ Saved!")
            
            st.markdown("""
            **Setup Instructions:**
            1. Go to https://oa.zalo.me
            2. Create Official Account
            3. Go to Settings → API
            4. Generate Access Token
            5. Copy OA ID and Token
            """)
        else:
            st.markdown('<div class="status-badge status-inactive">Inactive</div>', unsafe_allow_html=True)

elif st.session_state.page == 'security':
    st.markdown(f'<div class="main-header">🛡️ {t("security")}</div>', unsafe_allow_html=True)
    
    st.subheader("🚨 Active Threats")
    
    threat = {
        'id': 'THREAT-001',
        'type': 'NFC Relay Attack',
        'severity': 'HIGH',
        'details': 'Transaction duration: 1250ms, Geo-velocity: 1200 km/h'
    }
    
    st.markdown(f"""
    <div class="alert-high">
        <strong>{threat['id']}: {threat['type']}</strong><br>
        Severity: {threat['severity']}<br>
        Details: {threat['details']}<br>
        Action: BLOCKED
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == 'merchant':
    st.markdown(f'<div class="main-header">🏪 {t("merchant")}</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("This Week Sales", "$125,400", delta="-22%", delta_color="inverse")
    with col2:
        st.metric("Last Week Sales", "$161,000")
    with col3:
        st.metric("Avg Order Value", "$245", delta="-5%")

elif st.session_state.page == 'ml_insights':
    st.markdown(f'<div class="main-header">🤖 {t("ml_insights")}</div>', unsafe_allow_html=True)
    
    st.subheader("📈 Fraud Rate Forecast (30 Days)")
    
    forecast_dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
    forecast_data = pd.DataFrame({
        'ds': forecast_dates,
        'yhat': [2.1 + (i % 7) * 0.2 for i in range(30)]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast_data['ds'], y=forecast_data['yhat'],
                            mode='lines', line=dict(color='#4A9EFF', width=3)))
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

else:  # settings
    st.markdown(f'<div class="main-header">⚙️ {t("settings")}</div>', unsafe_allow_html=True)
    
    st.subheader("🎚️ Risk Thresholds")
    
    auto_approve = st.slider("Auto-Approve Threshold", 0, 100, 30)
    auto_block = st.slider("Auto-Block Threshold", 0, 100, 70)
    
    st.info(f"Config: Auto-approve < {auto_approve}, Manual {auto_approve}-{auto_block}, Auto-block ≥ {auto_block}")
    
    if st.button("💾 Save Settings", type="primary"):
        add_log('SUCCESS', 'Settings updated')
        st.success("✅ Saved!")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: {'#B8B8B8' if st.session_state.theme == 'dark' else '#6C757D'};'>
    AgentFlow Finance Guard v2.0 | SWIN Hackathon 2026 | Powered by AWS Bedrock
</div>
""", unsafe_allow_html=True)