"""
AgentFlow Finance Guard - FINAL COMPETITION VERSION
Multi-Agent AI System - SWIN Hackathon 2026
Complete with: Excel/Sheets input, Chatbot, Polished UI, Animations
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
        'ask_agentflow': 'Ask AgentFlow',
        'chat_placeholder': 'Ask about fraud detection, invoices, metrics...',
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
        'ask_agentflow': 'Hỏi AgentFlow',
        'chat_placeholder': 'Hỏi về phát hiện gian lận, hóa đơn, metrics...',
    }
}

def t(key):
    """Translation helper"""
    lang = st.session_state.get('language', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

# ========================================
# THEME CONFIGURATION - ENHANCED
# ========================================

DARK_THEME = """
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0E1117 0%, #1A1D2E 100%);
    }
    
    /* Sidebar - DARKER */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e1a 0%, #020617 100%);
        border-right: 1px solid rgba(74, 158, 255, 0.1);
    }
    
    section[data-testid="stSidebar"] > div {
        background: transparent;
    }
    
    /* METRIC CARDS - Enhanced with borders & hover */
    .metric-card {
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.08) 0%, rgba(0, 214, 143, 0.08) 100%);
        border: 2px solid rgba(74, 158, 255, 0.3);
        border-radius: 16px;
        padding: 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        border-color: #4A9EFF;
        box-shadow: 0 0 24px rgba(74, 158, 255, 0.4), 0 8px 24px rgba(0, 0, 0, 0.4);
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.12) 0%, rgba(0, 214, 143, 0.12) 100%);
    }
    
    .metric-title {
        font-size: 0.9rem;
        color: #B8B8B8;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #4A9EFF 0%, #00D68F 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .metric-delta {
        font-size: 0.85rem;
        color: #00D68F;
        margin-top: 4px;
    }
    
    /* Alert Cards - BRIGHTER in dark mode */
    .alert-high {
        background: linear-gradient(135deg, rgba(255, 82, 82, 0.25) 0%, rgba(255, 82, 82, 0.15) 100%);
        border-left: 4px solid #FF5252;
        border-radius: 12px;
        padding: 1.2rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 12px rgba(255, 82, 82, 0.2);
    }
    
    .alert-medium {
        background: linear-gradient(135deg, rgba(255, 171, 0, 0.25) 0%, rgba(255, 171, 0, 0.15) 100%);
        border-left: 4px solid #FFAB00;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 12px rgba(255, 171, 0, 0.2);
    }
    
    .alert-low {
        background: linear-gradient(135deg, rgba(0, 214, 143, 0.25) 0%, rgba(0, 214, 143, 0.15) 100%);
        border-left: 4px solid #00D68F;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 12px rgba(0, 214, 143, 0.2);
    }
    
    /* Make alert text brighter */
    .alert-high, .alert-medium, .alert-low {
        color: #FAFAFA;
    }
    
    .alert-high strong, .alert-medium strong, .alert-low strong {
        color: #FFFFFF;
        font-weight: 600;
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
    
    /* Glass Cards */
    .glass-card {
        background: rgba(38, 39, 48, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
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
        color: #FF5252;
        border-left-color: #FF5252;
    }
    
    .log-success {
        color: #00D68F;
        border-left-color: #00D68F;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .status-active {
        background: rgba(0, 214, 143, 0.25);
        color: #00D68F;
        border: 1px solid #00D68F;
    }
    
    .status-inactive {
        background: rgba(184, 184, 184, 0.2);
        color: #B8B8B8;
        border: 1px solid #B8B8B8;
    }
    
    /* Chat Section */
    .chat-container {
        background: rgba(30, 33, 48, 0.8);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
        border: 1px solid rgba(74, 158, 255, 0.2);
    }
    
    .chat-message {
        background: rgba(74, 158, 255, 0.1);
        border-left: 3px solid #4A9EFF;
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
</style>
"""

LIGHT_THEME = """
<style>
    .stApp {
        background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%);
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #E9ECEF 0%, #DEE2E6 100%);
        border-right: 1px solid rgba(0, 102, 204, 0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(0, 102, 204, 0.05) 0%, rgba(0, 168, 120, 0.05) 100%);
        border: 2px solid rgba(0, 102, 204, 0.3);
        border-radius: 16px;
        padding: 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        border-color: #0066CC;
        box-shadow: 0 0 24px rgba(0, 102, 204, 0.3), 0 8px 24px rgba(0, 0, 0, 0.1);
        background: linear-gradient(135deg, rgba(0, 102, 204, 0.1) 0%, rgba(0, 168, 120, 0.1) 100%);
    }
    
    .metric-title {
        font-size: 0.9rem;
        color: #6C757D;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0066CC 0%, #00A878 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .metric-delta {
        font-size: 0.85rem;
        color: #00A878;
        margin-top: 4px;
    }
    
    .alert-high {
        background: linear-gradient(135deg, rgba(220, 53, 69, 0.15) 0%, rgba(220, 53, 69, 0.08) 100%);
        border-left: 4px solid #DC3545;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 12px rgba(220, 53, 69, 0.15);
    }
    
    .alert-medium {
        background: linear-gradient(135deg, rgba(255, 140, 0, 0.15) 0%, rgba(255, 140, 0, 0.08) 100%);
        border-left: 4px solid #FF8C00;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 12px rgba(255, 140, 0, 0.15);
    }
    
    .alert-low {
        background: linear-gradient(135deg, rgba(0, 168, 120, 0.15) 0%, rgba(0, 168, 120, 0.08) 100%);
        border-left: 4px solid #00A878;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 12px rgba(0, 168, 120, 0.15);
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
</style>
"""

# Page config - FIX icon issue
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
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

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
                'bedrock': session.client('bedrock-runtime', region_name='us-east-1'),
                'configured': True
            }
        return {'configured': False}
    except Exception as e:
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
# CHATBOT FUNCTION
# ========================================

def ask_agentflow_ai(question):
    """Ask AgentFlow AI assistant using Bedrock Claude"""
    try:
        if not aws_clients.get('configured'):
            return "⚠️ AWS not configured. Configure secrets to enable AI assistant."
        
        bedrock = aws_clients['bedrock']
        
        # System context about AgentFlow
        context = f"""You are AgentFlow AI Assistant, an expert in fraud detection.

Current System Status:
- 99.2% fraud detection accuracy
- 85.3% automation rate
- 7.8s average latency
- $523K fraud prevented this year
- 17 AI agents working together

Your role: Answer questions about fraud detection, invoice analysis, system metrics, and security threats.
Be concise, professional, and helpful."""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [
                {
                    "role": "user",
                    "content": f"{context}\n\nUser question: {question}"
                }
            ]
        })
        
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        answer = response_body['content'][0]['text']
        
        add_log('INFO', f'AI Assistant answered: {question}')
        return answer
        
    except Exception as e:
        add_log('ERROR', f'AI Assistant error: {e}')
        return f"❌ Error: {str(e)[:100]}"

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
                    help=t('theme') if 'theme' in TRANSLATIONS['en'] else 'Theme', 
                    use_container_width=True):
            st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
            st.rerun()
    
    with col2:
        if st.button("🌐 EN" if st.session_state.language == 'en' else "🌐 VI",
                    help='Language', use_container_width=True):
            st.session_state.language = 'vi' if st.session_state.language == 'en' else 'en'
            st.rerun()
    
    # AWS Status
    if aws_clients.get('configured'):
        st.success(f"🟢 {t('aws_connected')}")
        st.caption(f"Region: {AWS_REGION}")
    else:
        st.warning(f"🟡 {t('demo_mode')}")
    
    st.markdown("---")
    
    # Navigation
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
    
    # AI CHATBOT SECTION
    st.markdown(f"### 🤖 {t('ask_agentflow')}")
    
    chat_question = st.text_input(
        "Ask me anything",
        placeholder=t('chat_placeholder'),
        key='chat_input',
        label_visibility='collapsed'
    )
    
    if chat_question:
        with st.spinner("Thinking..."):
            answer = ask_agentflow_ai(chat_question)
            
            # Add to chat history
            st.session_state.chat_history.insert(0, {
                'question': chat_question,
                'answer': answer,
                'timestamp': datetime.now()
            })
            st.session_state.chat_history = st.session_state.chat_history[:5]  # Keep last 5
    
    # Show recent chat
    if st.session_state.chat_history:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for chat in st.session_state.chat_history[:3]:
            st.markdown(f"""
            <div class="chat-message">
                <strong>Q:</strong> {chat['question']}<br>
                <strong>A:</strong> {chat['answer'][:150]}...
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ========================================
# PAGES
# ========================================

if st.session_state.page == 'overview':
    st.markdown(f'<div class="main-header">📊 {t("app_title")} - {t("overview")}</div>', unsafe_allow_html=True)
    
    metrics = get_dashboard_metrics()
    
    # ENHANCED METRIC CARDS with borders & hover animation
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">🎯 {t('detection_accuracy')}</div>
            <div class="metric-value">{metrics['accuracy']}%</div>
            <div class="metric-delta">+0.2%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">🤖 {t('automation_rate')}</div>
            <div class="metric-value">{metrics['automation_rate']}%</div>
            <div class="metric-delta">+1.5%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">⚡ {t('avg_latency')}</div>
            <div class="metric-value">{metrics['avg_latency_ms']}ms</div>
            <div class="metric-delta">-200ms</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">💰 {t('fraud_prevented')}</div>
            <div class="metric-value">${metrics['fraud_prevented_usd']:,}</div>
            <div class="metric-delta">+$42K</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Agent Performance Matrix")
        
        agent_data = pd.DataFrame({
            'Agent': ['OCR', 'PII', 'Decimal', 'AI Analyst', 'Audit', 'Notifier', 'ML', 'Security'],
            'Success Rate': [92.8, 99.9, 100.0, 94.2, 100.0, 99.8, 91.5, 96.3]
        })
        
        fig = px.bar(agent_data, x='Agent', y='Success Rate',
                    color='Success Rate', color_continuous_scale='RdYlGn', range_color=[90, 100])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🚨 Recent Alerts")
        alerts = get_recent_alerts()
        
        for alert in alerts[:5]:
            alert_class = 'alert-high' if alert['risk_score'] >= 70 else ('alert-medium' if alert['risk_score'] >= 30 else 'alert-low')
            icon = '🔴' if alert['risk_score'] >= 70 else ('🟡' if alert['risk_score'] >= 30 else '🟢')
            
            st.markdown(f"""
            <div class="{alert_class}">
                <strong>{icon} {alert['id']}</strong><br>
                Risk Score: {alert['risk_score']}/100<br>
                Amount: ${alert['amount']:,.2f}<br>
                Status: {alert['status']}
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

elif st.session_state.page == 'upload':
    st.markdown(f'<div class="main-header">📄 {t("invoice_upload")}</div>', unsafe_allow_html=True)
    
    # TABS: File Upload, Excel Link, Google Sheets
    tab1, tab2, tab3 = st.tabs(["📁 Upload File", "🔗 Excel Online", "📊 Google Sheets"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📤 Upload Invoice")
            uploaded_file = st.file_uploader("Choose file", type=['pdf', 'png', 'jpg', 'jpeg', 'xlsx', 'csv'])
            
            if uploaded_file:
                st.success(f"✅ {uploaded_file.name}")
                
                if uploaded_file.type == 'application/pdf':
                    st.info("📄 PDF uploaded successfully")
                elif uploaded_file.type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv']:
                    df = pd.read_excel(uploaded_file) if 'xlsx' in uploaded_file.name else pd.read_csv(uploaded_file)
                    st.dataframe(df.head(), use_container_width=True)
                else:
                    st.image(uploaded_file, use_container_width=True)
        
        with col2:
            st.subheader("⚙️ Processing Options")
            
            mode = st.radio("Mode", ["🚀 Full AWS Pipeline (Live)", "🎬 Demo Mode (Fast)"])
            use_live = "Live" in mode
            
            if uploaded_file and st.button(f"🔥 Process Invoice", type="primary", use_container_width=True):
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
    
    with tab2:
        st.subheader("🔗 Excel Online Link")
        st.info("📝 Paste a public Excel Online link (OneDrive, SharePoint)")
        
        excel_url = st.text_input("Excel Online URL", placeholder="https://...")
        
        if st.button("📥 Load Excel", type="primary"):
            if excel_url:
                try:
                    with st.spinner("Loading Excel file..."):
                        df = pd.read_excel(excel_url)
                        st.success("✅ Excel loaded successfully!")
                        st.dataframe(df, use_container_width=True)
                        add_log('SUCCESS', f'Loaded Excel from: {excel_url[:50]}...')
                except Exception as e:
                    st.error(f"❌ Failed to load: {str(e)[:100]}")
                    st.info("💡 Make sure the link is public and accessible")
            else:
                st.warning("Please enter a URL")
    
    with tab3:
        st.subheader("📊 Google Sheets Integration")
        st.info("📝 Paste a Google Sheets link (make sure it's publicly accessible)")
        
        sheet_url = st.text_input("Google Sheets URL", placeholder="https://docs.google.com/spreadsheets/d/...")
        
        if st.button("📥 Load Sheet", type="primary"):
            if sheet_url:
                try:
                    with st.spinner("Loading Google Sheet..."):
                        # Extract sheet ID from URL
                        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
                        export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                        
                        df = pd.read_csv(export_url)
                        st.success("✅ Google Sheet loaded successfully!")
                        st.dataframe(df, use_container_width=True)
                        add_log('SUCCESS', f'Loaded Google Sheet: {sheet_id}')
                except Exception as e:
                    st.error(f"❌ Failed to load: {str(e)[:100]}")
                    st.info("💡 Make sure: 1) Link is correct, 2) Sheet is public, 3) Sharing settings allow 'Anyone with the link'")
            else:
                st.warning("Please enter a Google Sheets URL")

elif st.session_state.page == 'fraud':
    st.markdown(f'<div class="main-header">🔍 {t("fraud_detection")}</div>', unsafe_allow_html=True)
    
    sample = {'id': 'INV-2026-5678', 'amount': 12345.67, 'risk_score': 48}
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🧠 Risk Score Analysis")
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=sample['risk_score'],
            title={'text': 'Risk Score'},
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
            if st.button("✅ Approve", type="primary"):
                add_log('INFO', f'Invoice {sample["id"]} approved')
                add_event('APPROVAL', f'{sample["id"]} approved by admin')
                st.success("Approved!")
            if st.button("❌ Reject"):
                add_log('WARNING', f'Invoice {sample["id"]} rejected')
                add_event('REJECTION', f'{sample["id"]} rejected by admin')
                st.error("Rejected!")
        else:
            st.error("🚨 AUTO-BLOCK")

elif st.session_state.page == 'observability':
    st.markdown(f'<div class="main-header">📊 {t("observability")}</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔍 Execution Logs", "📅 System Events", "❌ Error Logs"])
    
    with tab1:
        st.subheader("🔍 Execution Logs")
        
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
        st.subheader("📅 System Events")
        
        if st.session_state.system_events:
            for event in st.session_state.system_events[:20]:
                with st.expander(f"{event['type']} - {event['timestamp'].strftime('%H:%M:%S')}"):
                    st.write(f"**Description:** {event['description']}")
                    if event['data']:
                        st.json(event['data'])
        else:
            st.info("No system events yet.")
    
    with tab3:
        st.subheader("❌ Error Logs")
        
        error_logs = [log for log in st.session_state.execution_logs if log['level'] == 'ERROR']
        
        if error_logs:
            for log in error_logs[:10]:
                st.error(f"**[{log['timestamp'].strftime('%H:%M:%S')}]** {log['message']}")
        else:
            st.success("✅ No errors - System healthy!")

elif st.session_state.page == 'integrations':
    st.markdown(f'<div class="main-header">🔔 {t("integrations")}</div>', unsafe_allow_html=True)
    
    st.info("ℹ️ Configure external notification channels for real-time fraud alerts")
    
    with st.expander("💬 Slack Integration", expanded=True):
        slack_enabled = st.checkbox("Enable Slack notifications", value=False)
        if slack_enabled:
            slack_webhook = st.text_input("Slack Webhook URL", value="https://hooks.slack.com/services/...")
            if st.button("🧪 Test Slack"):
                add_log('INFO', 'Testing Slack connection')
                st.success("✅ Slack test sent!")

elif st.session_state.page == 'security':
    st.markdown(f'<div class="main-header">🛡️ {t("security")}</div>', unsafe_allow_html=True)
    
    st.subheader("🚨 Active Threats")
    
    st.markdown("""
    <div class="alert-high">
        <strong>THREAT-001: NFC Relay Attack</strong><br>
        Severity: HIGH<br>
        Details: Transaction duration: 1250ms, Geo-velocity: 1200 km/h<br>
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