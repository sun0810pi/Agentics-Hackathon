"""
AgentFlow Finance Guard - Main Application
17-Agent AI Fraud Detection System
SWIN Hackathon 2026
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from auth.login import init_session_state, login_page
from components.sidebar import render_sidebar
from themes.dark import DARK_THEME
from themes.light import LIGHT_THEME
from utils.helpers import render_metric_card, log_action
from utils.demo_data import demo_data

# =====================================================
# PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title=f"{config.APP_NAME} v{config.APP_VERSION}",
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/agentflow',
        'Report a bug': 'https://github.com/yourusername/agentflow/issues',
        'About': f'{config.APP_NAME} v{config.APP_VERSION} - {config.HACKATHON}'
    }
)

# =====================================================
# SESSION STATE INITIALIZATION
# =====================================================
init_session_state()

# =====================================================
# THEME LOADING
# =====================================================
theme = DARK_THEME if st.session_state.theme == 'dark' else LIGHT_THEME
st.markdown(theme, unsafe_allow_html=True)

# =====================================================
# AUTHENTICATION CHECK
# =====================================================
if not st.session_state.logged_in:
    login_page()
    st.stop()

# =====================================================
# SIDEBAR
# =====================================================
render_sidebar()

# =====================================================
# MAIN CONTENT
# =====================================================

# Header
st.markdown(f"""
<div class="main-header">
    {config.APP_ICON} Welcome to {config.APP_NAME}
</div>
<div class="sub-header">
    17-Agent AI-Powered Fraud Detection System | {config.HACKATHON}
</div>
""", unsafe_allow_html=True)

# Log page view
log_action("view_home")

# Deployment mode banner
if config.DEPLOYMENT_MODE == "local":
    st.info("🎬 **Demo Mode** - Using local agents with simulated data. No AWS connection required.")
elif config.DEPLOYMENT_MODE == "hybrid":
    from components.api_client import get_api_client
    api_client = get_api_client()
    if api_client.health_check():
        st.success("🚀 **Hybrid Mode** - Connected to FastAPI backend on EC2")
    else:
        st.warning("⚠️ **Fallback Mode** - Backend unavailable, using local processing")
else:
    st.success("🚀 **Production Mode** - Full backend infrastructure active")

st.markdown("---")

# =====================================================
# QUICK ACTIONS
# =====================================================
st.markdown("### 🚀 Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📄 Upload Invoice", use_container_width=True, type="primary"):
        st.switch_page("pages/2_📄_Upload.py")

with col2:
    if st.button("📊 View Dashboard", use_container_width=True):
        st.switch_page("pages/1_📊_Overview.py")

with col3:
    if st.button("🚨 Fraud Alerts", use_container_width=True):
        st.switch_page("pages/3_🚨_Fraud.py")

with col4:
    if st.button("🛡️ Security", use_container_width=True):
        st.switch_page("pages/5_🛡️_Security.py")

st.markdown("---")

# =====================================================
# SYSTEM STATUS OVERVIEW
# =====================================================
st.markdown("### 🤖 Agent System Status")

# Get demo metrics
metrics = demo_data.generate_dashboard_metrics()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Core Detection</div>
        <div class="metric-value">8/8</div>
        <div class="metric-delta">✅ Active</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">ML Intelligence</div>
        <div class="metric-value">3/3</div>
        <div class="metric-delta">✅ Active</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Merchant Success</div>
        <div class="metric-value">3/3</div>
        <div class="metric-delta">✅ Active</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Security Layer</div>
        <div class="metric-value">3/3</div>
        <div class="metric-delta">✅ Active</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# =====================================================
# KEY METRICS
# =====================================================
st.markdown("### 📈 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Detection Accuracy",
        f"{metrics['accuracy']}%",
        "+0.2%",
        help="Percentage of correctly identified fraud cases"
    )

with col2:
    st.metric(
        "Automation Rate",
        f"{metrics['automation_rate']}%",
        "+1.5%",
        help="Percentage of invoices processed without human intervention"
    )

with col3:
    st.metric(
        "False Positive Rate",
        f"{metrics['false_positive_rate']}%",
        "-0.3%",
        delta_color="inverse",
        help="Legitimate invoices incorrectly flagged as fraud"
    )

with col4:
    st.metric(
        "Fraud Prevented",
        f"${metrics['fraud_prevented_usd']:,}",
        "+$52K",
        help="Total fraud amount prevented this month"
    )

st.markdown("---")

# =====================================================
# RECENT ACTIVITY
# =====================================================
st.markdown("### 📊 Recent Activity")

# Get sample invoices
invoices = demo_data.generate_invoices(count=10)

# Create tabs
tab1, tab2, tab3 = st.tabs(["📋 All Invoices", "✅ Approved", "❌ Blocked"])

with tab1:
    for invoice in invoices[:5]:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.markdown(f"**{invoice['invoice_number']}** - {invoice['supplier']}")
            
            with col2:
                st.markdown(f"💰 ${invoice['amount']:,.2f}")
            
            with col3:
                risk_color = "#00d68f" if invoice['risk_score'] < 30 else "#ffab00" if invoice['risk_score'] < 70 else "#ff5252"
                st.markdown(f"<span style='color: {risk_color}'>Risk: {invoice['risk_score']}/100</span>", unsafe_allow_html=True)
            
            with col4:
                status_emoji = "✅" if invoice['status'] == "APPROVED" else "⏳" if invoice['status'] == "PENDING" else "❌"
                st.markdown(f"{status_emoji} {invoice['status']}")
            
            st.markdown("---")

with tab2:
    approved = [inv for inv in invoices if inv['status'] == 'APPROVED']
    if approved:
        for invoice in approved[:5]:
            st.success(f"✅ {invoice['invoice_number']} - ${invoice['amount']:,.2f} - Risk: {invoice['risk_score']}/100")
    else:
        st.info("No approved invoices in this batch")

with tab3:
    blocked = [inv for inv in invoices if inv['status'] == 'BLOCKED']
    if blocked:
        for invoice in blocked[:5]:
            st.error(f"❌ {invoice['invoice_number']} - ${invoice['amount']:,.2f} - Risk: {invoice['risk_score']}/100")
    else:
        st.info("No blocked invoices in this batch")

st.markdown("---")

# =====================================================
# QUICK TIPS
# =====================================================
with st.expander("💡 Quick Tips for Getting Started"):
    st.markdown("""
    ### Getting Started with AgentFlow
    
    **1. Upload Your First Invoice**
    - Navigate to the **Upload** page
    - Drag & drop or select a PDF/image file
    - Click **Process Invoice**
    - View real-time agent execution
    
    **2. Monitor Fraud Activity**
    - Check the **Fraud Detection** page for alerts
    - Review blocked transactions
    - Analyze fraud patterns
    
    **3. Explore Security Features**
    - Visit **Security** page for threat monitoring
    - View fraud ring detection results
    - Check NFC relay attack prevention
    
    **4. View Analytics**
    - **Overview** page shows key metrics
    - **ML Insights** displays predictions
    - **Observability** provides system logs
    
    **5. Manage Settings**
    - Configure thresholds in **Settings**
    - Set up integrations (Slack, Sheets)
    - Customize notifications
    """)

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")

footer_cols = st.columns(5)

with footer_cols[0]:
    st.metric("Version", config.APP_VERSION)

with footer_cols[1]:
    st.metric("Mode", config.DEPLOYMENT_MODE.upper())

with footer_cols[2]:
    st.metric("Status", "🟢 Live")

with footer_cols[3]:
    st.metric("Agents", f"{config.TOTAL_AGENTS}/17 ✅")

with footer_cols[4]:
    st.metric("Uptime", f"{metrics['uptime_pct']}%")

# Copyright
st.markdown(f"""
<div style='text-align: center; color: #718096; font-size: 0.875rem; margin-top: 2rem;'>
    © 2026 {config.APP_NAME} | Built for {config.HACKATHON}
</div>
""", unsafe_allow_html=True)