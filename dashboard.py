"""
AgentFlow Finance Guard - Main Streamlit Dashboard
Multi-Agent AI System for Intelligent Fraud Detection
"""

import streamlit as st
import boto3
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from decimal import Decimal

# Page config
st.set_page_config(
    page_title="AgentFlow Finance Guard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-high {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .alert-medium {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .alert-low {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'overview'
if 'user_role' not in st.session_state:
    st.session_state.user_role = 'admin'

# Load AWS credentials from Streamlit secrets (if available)
try:
    AWS_ACCESS_KEY = st.secrets["AWS_ACCESS_KEY"]
    AWS_SECRET_KEY = st.secrets["AWS_SECRET_KEY"]
    SFN_ARN = st.secrets["SFN_ARN"]
    AWS_REGION = st.secrets.get("AWS_REGION", "ap-southeast-1")
except:
    AWS_ACCESS_KEY = None
    AWS_SECRET_KEY = None
    SFN_ARN = None
    AWS_REGION = "ap-southeast-1"

# AWS Clients (with error handling for Streamlit Cloud)
try:
    if AWS_ACCESS_KEY and AWS_SECRET_KEY:
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
        s3_client = boto3.client(
            's3',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
        stepfunctions = boto3.client(
            'stepfunctions',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
    else:
        # Demo mode - no AWS connection
        dynamodb = None
        s3_client = None
        stepfunctions = None
except Exception as e:
    st.info(f"ℹ️ Running in demo mode - Sample data displayed")
    dynamodb = None
    s3_client = None
    stepfunctions = None

# ========================================
# HELPER FUNCTIONS
# ========================================

@st.cache_data(ttl=300)
def get_dashboard_metrics():
    """Get key metrics - using demo data for hackathon"""
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
    """Get recent fraud alerts - demo data"""
    return [
        {
            'id': 'INV-2026-1234',
            'timestamp': '2026-02-15 14:23:15',
            'risk_score': 87,
            'amount': 15423.50,
            'supplier': 'ABC Corp',
            'reason': 'NFC relay attack detected + geo-velocity anomaly',
            'status': 'BLOCKED'
        },
        {
            'id': 'INV-2026-1235',
            'timestamp': '2026-02-15 13:45:30',
            'risk_score': 65,
            'amount': 8234.00,
            'supplier': 'XYZ Ltd',
            'reason': 'Amount mismatch 45% + new supplier',
            'status': 'PENDING_REVIEW'
        },
        {
            'id': 'INV-2026-1236',
            'timestamp': '2026-02-15 12:10:05',
            'risk_score': 42,
            'amount': 3250.75,
            'supplier': 'Tech Solutions',
            'reason': 'Minor amount deviation (3.2%)',
            'status': 'APPROVED'
        }
    ]

def get_fraud_trend_data(days=30):
    """Generate fraud trend data"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    fraud_rates = [2.1 + (i % 7) * 0.3 - 0.5 for i in range(days)]
    invoice_volumes = [3000 + (i % 7) * 500 for i in range(days)]
    
    df = pd.DataFrame({
        'date': dates,
        'fraud_rate': fraud_rates,
        'invoice_volume': invoice_volumes,
        'fraud_count': [int(vol * rate / 100) for vol, rate in zip(invoice_volumes, fraud_rates)]
    })
    return df

# ========================================
# SIDEBAR NAVIGATION
# ========================================

with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=AgentFlow", width=150)
    
    st.markdown("### 🛡️ Navigation")
    
    pages = {
        '📊 Overview': 'overview',
        '📄 Invoice Upload': 'upload',
        '🔍 Fraud Detection': 'fraud',
        '🤖 ML Insights': 'ml_insights',
        '🛡️ Security': 'security',
        '🏪 Merchant Success': 'merchant',
        '⚙️ Settings': 'settings'
    }
    
    for label, page_id in pages.items():
        if st.button(label, key=page_id, use_container_width=True):
            st.session_state.page = page_id
    
    st.markdown("---")
    st.markdown(f"**User**: Admin")
    st.markdown(f"**Role**: {st.session_state.user_role}")
    st.markdown(f"**Last Login**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ========================================
# MAIN CONTENT AREA
# ========================================

if st.session_state.page == 'overview':
    # ====== OVERVIEW DASHBOARD ======
    st.markdown('<div class="main-header">📊 AgentFlow Finance Guard - Overview</div>', unsafe_allow_html=True)
    
    metrics = get_dashboard_metrics()
    
    # Top KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Detection Accuracy", f"{metrics['accuracy']}%", delta="0.2%")
    
    with col2:
        st.metric("🤖 Automation Rate", f"{metrics['automation_rate']}%", delta="1.5%")
    
    with col3:
        st.metric("⚡ Avg Latency", f"{metrics['avg_latency_ms']}ms", delta="-200ms", delta_color="inverse")
    
    with col4:
        st.metric("💰 Fraud Prevented", f"${metrics['fraud_prevented_usd']:,}", delta="$42K")
    
    st.markdown("---")
    
    # Second row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Invoices Processed", f"{metrics['total_invoices_processed']:,}")
    
    with col2:
        st.metric("⏳ Pending Review", metrics['pending_manual_review'])
    
    with col3:
        st.metric("⚠️ False Positive Rate", f"{metrics['false_positive_rate']}%")
    
    with col4:
        st.metric("🔒 System Uptime", f"{metrics['uptime_percentage']}%")
    
    st.markdown("---")
    
    # Fraud Trend Chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Fraud Detection Trend (30 Days)")
        
        trend_data = get_fraud_trend_data(30)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=trend_data['date'],
            y=trend_data['fraud_rate'],
            name='Fraud Rate (%)',
            line=dict(color='#f44336', width=3),
            yaxis='y1'
        ))
        
        fig.add_trace(go.Bar(
            x=trend_data['date'],
            y=trend_data['invoice_volume'],
            name='Invoice Volume',
            marker_color='#1f77b4',
            opacity=0.3,
            yaxis='y2'
        ))
        
        fig.update_layout(
            yaxis=dict(title='Fraud Rate (%)', side='left'),
            yaxis2=dict(title='Invoice Volume', side='right', overlaying='y'),
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🚨 Recent Alerts")
        
        alerts = get_recent_alerts()
        
        for alert in alerts[:5]:
            if alert['risk_score'] >= 70:
                alert_class = 'alert-high'
                icon = '🔴'
            elif alert['risk_score'] >= 30:
                alert_class = 'alert-medium'
                icon = '🟡'
            else:
                alert_class = 'alert-low'
                icon = '🟢'
            
            st.markdown(f"""
            <div class="{alert_class}">
                <strong>{icon} {alert['id']}</strong><br>
                Risk Score: {alert['risk_score']}/100<br>
                Amount: ${alert['amount']:,.2f}<br>
                Status: {alert['status']}<br>
                <small>{alert['timestamp']}</small>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Agent Performance Matrix
    st.subheader("🤖 Agent Performance Matrix")
    
    agent_data = pd.DataFrame({
        'Agent': ['Agent 0: OCR', 'Agent 1: PII', 'Agent 2: Decimal', 'Agent 3: AI Analyst',
                 'Agent 4: Audit', 'Agent 5: Notifier', 'Agent 8: ML Insights', 'Agent 14: Security'],
        'Success Rate': [92.8, 99.9, 100.0, 94.2, 100.0, 99.8, 91.5, 96.3],
        'Avg Time (ms)': [1200, 50, 10, 3500, 200, 150, 2000, 800],
        'Errors (24h)': [8, 0, 0, 12, 0, 1, 5, 3]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            agent_data,
            x='Agent',
            y='Success Rate',
            title='Agent Success Rates',
            color='Success Rate',
            color_continuous_scale='RdYlGn',
            range_color=[90, 100]
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            agent_data,
            x='Agent',
            y='Avg Time (ms)',
            title='Average Processing Time',
            color='Avg Time (ms)',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == 'upload':
    # ====== INVOICE UPLOAD ======
    st.markdown('<div class="main-header">📄 Invoice Upload</div>', unsafe_allow_html=True)
    
    st.info("💡 **Demo Mode**: Upload your invoice for OCR extraction demo")
    
    uploaded_file = st.file_uploader("Upload Invoice", type=['pdf', 'png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📄 Uploaded Document")
            if uploaded_file.type != 'application/pdf':
                st.image(uploaded_file, caption="Invoice Image")
            else:
                st.info("📄 PDF uploaded")
        
        with col2:
            st.subheader("🔍 OCR Processing")
            
            if st.button("🚀 Process Invoice", type="primary"):
                with st.spinner("Processing..."):
                    import time
                    time.sleep(2)
                    
                    result = {
                        'invoice_number': 'INV-2026-5678',
                        'invoice_date': '2026-02-10',
                        'supplier_name': 'ABC Corporation',
                        'amount': 12345.67,
                        'currency': 'USD',
                        'confidence': 87.5
                    }
                    
                    st.success(f"✅ Extracted! (Confidence: {result['confidence']}%)")
                    st.json(result)
                    
                    if st.button("▶️ Continue to Risk Analysis"):
                        st.session_state.page = 'fraud'
                        st.rerun()

elif st.session_state.page == 'fraud':
    # ====== FRAUD DETECTION ======
    st.markdown('<div class="main-header">🔍 Fraud Detection</div>', unsafe_allow_html=True)
    
    sample_invoice = {
        'id': 'INV-2026-5678',
        'amount': 12345.67,
        'po_amount': 12000.00,
        'supplier': 'ABC Corporation'
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Invoice Details")
        
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            st.metric("Invoice Amount", f"${sample_invoice['amount']:,.2f}")
            st.metric("PO Amount", f"${sample_invoice['po_amount']:,.2f}")
        
        with detail_col2:
            difference = abs(sample_invoice['amount'] - sample_invoice['po_amount'])
            percentage = (difference / sample_invoice['po_amount']) * 100
            st.metric("Difference", f"${difference:,.2f}")
            st.metric("Deviation", f"{percentage:.2f}%", delta=f"{percentage:.2f}%", delta_color="inverse")
        
        st.markdown("---")
        st.subheader("🧠 AI Risk Analysis")
        
        risk_score = min(percentage * 10, 70) + 15
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_score,
            title={'text': "Fraud Risk Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'steps': [
                    {'range': [0, 30], 'color': '#4caf50'},
                    {'range': [30, 70], 'color': '#ff9800'},
                    {'range': [70, 100], 'color': '#f44336'}
                ]
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Risk Breakdown")
        
        breakdown = pd.DataFrame({
            'Component': ['Math Score', 'Supplier Trust', 'Amount Anomaly'],
            'Points': [28, 15, 5]
        })
        
        fig = px.bar(breakdown, y='Component', x='Points', orientation='h',
                    color='Points', color_continuous_scale='Reds')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        if risk_score < 30:
            st.success("✅ AUTO-APPROVE - Low risk")
        elif risk_score < 70:
            st.warning("⚠️ MANUAL CHECK - Medium risk")
            col_a, col_b = st.columns(2)
            if col_a.button("✅ Approve", type="primary"):
                st.success("Approved!")
            if col_b.button("❌ Reject"):
                st.error("Rejected!")
        else:
            st.error("🚨 AUTO-BLOCK - High risk")

elif st.session_state.page == 'ml_insights':
    st.markdown('<div class="main-header">🤖 ML Intelligence</div>', unsafe_allow_html=True)
    
    st.subheader("📈 Fraud Rate Forecast (30 Days)")
    
    forecast_dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
    forecast_data = pd.DataFrame({
        'ds': forecast_dates,
        'yhat': [2.1 + (i % 7) * 0.2 for i in range(30)],
        'yhat_lower': [1.8 + (i % 7) * 0.15 for i in range(30)],
        'yhat_upper': [2.5 + (i % 7) * 0.25 for i in range(30)]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast_data['ds'], y=forecast_data['yhat_upper'],
                            fill=None, mode='lines', line_color='rgba(0,0,0,0)', showlegend=False))
    fig.add_trace(go.Scatter(x=forecast_data['ds'], y=forecast_data['yhat_lower'],
                            fill='tonexty', fillcolor='rgba(31,119,180,0.2)', 
                            mode='lines', line_color='rgba(0,0,0,0)', name='Confidence'))
    fig.add_trace(go.Scatter(x=forecast_data['ds'], y=forecast_data['yhat'],
                            mode='lines', line=dict(color='#1f77b4', width=3), name='Forecast'))
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🚨 Detected Anomalies (Last 7 Days)")
    
    anomalies = pd.DataFrame({
        'Invoice ID': ['INV-2026-1111', 'INV-2026-2222', 'INV-2026-3333'],
        'Amount': [45000, 89000, 12000],
        'Supplier': ['Unknown Corp', 'ABC Ltd', 'XYZ Inc'],
        'Anomaly Score': [0.92, 0.87, 0.81],
        'Reason': ['Unusually high', 'New supplier', 'Rapid succession']
    })
    
    st.dataframe(anomalies, use_container_width=True)

elif st.session_state.page == 'merchant':
    st.markdown('<div class="main-header">🏪 Merchant Success</div>', unsafe_allow_html=True)
    
    st.subheader("📊 Sales Performance")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("This Week", "$125,400", delta="-22%", delta_color="inverse")
    with col2:
        st.metric("Last Week", "$161,000")
    with col3:
        st.metric("Avg Order", "$245", delta="-5%")
    
    st.warning("⚠️ Sales dropped 22% - Root cause analysis triggered")

elif st.session_state.page == 'security':
    st.markdown('<div class="main-header">🛡️ Security Operations</div>', unsafe_allow_html=True)
    
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

else:
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    auto_approve = st.slider("Auto-Approve Threshold", 0, 100, 30)
    auto_block = st.slider("Auto-Block Threshold", 0, 100, 70)
    
    st.info(f"Config: Auto-approve < {auto_approve}, Manual {auto_approve}-{auto_block}, Auto-block ≥ {auto_block}")
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("✅ Settings saved!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    AgentFlow Finance Guard v1.0 | SWIN Hackathon 2026 | 
    Powered by AWS Bedrock & Claude
</div>
""", unsafe_allow_html=True)