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
import redis
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
    st.session_state.user_role = 'admin'  # TODO: Implement proper auth

# AWS Clients (with error handling for local dev)
try:
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
    s3_client = boto3.client('s3', region_name='ap-southeast-1')
    stepfunctions = boto3.client('stepfunctions', region_name='ap-southeast-1')
    textract = boto3.client('textract', region_name='ap-southeast-1')
    bedrock = boto3.client('bedrock-runtime', region_name='ap-southeast-1')
    
    # Redis for caching
    redis_client = redis.Redis(
        host='localhost',  # TODO: Use ElastiCache in production
        port=6379,
        decode_responses=True
    )
except Exception as e:
    st.warning(f"⚠️ Running in local mode. AWS services unavailable: {e}")
    dynamodb = None
    redis_client = None

# ========================================
# HELPER FUNCTIONS
# ========================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_dashboard_metrics():
    """Fetch key metrics from Redis cache"""
    try:
        if redis_client:
            cached = redis_client.get('dashboard:metrics')
            if cached:
                return json.loads(cached)
    except:
        pass
    
    # Fallback to sample data for demo
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
    """Fetch recent fraud alerts from DynamoDB"""
    # Sample data for demo
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
    
    # Sample trend data
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
    
    # User info
    st.markdown(f"**User**: Admin")
    st.markdown(f"**Role**: {st.session_state.user_role}")
    st.markdown(f"**Last Login**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ========================================
# MAIN CONTENT AREA
# ========================================

# Page routing
if st.session_state.page == 'overview':
    # ====== OVERVIEW DASHBOARD ======
    st.markdown('<div class="main-header">📊 AgentFlow Finance Guard - Overview</div>', unsafe_allow_html=True)
    
    # Fetch metrics
    metrics = get_dashboard_metrics()
    
    # Top KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 Detection Accuracy",
            f"{metrics['accuracy']}%",
            delta="0.2%",
            help="Fraud detection accuracy rate"
        )
    
    with col2:
        st.metric(
            "🤖 Automation Rate",
            f"{metrics['automation_rate']}%",
            delta="1.5%",
            help="Percentage of auto-approved/blocked invoices"
        )
    
    with col3:
        st.metric(
            "⚡ Avg Latency",
            f"{metrics['avg_latency_ms']}ms",
            delta="-200ms",
            delta_color="inverse",
            help="Average processing time per invoice"
        )
    
    with col4:
        st.metric(
            "💰 Fraud Prevented",
            f"${metrics['fraud_prevented_usd']:,}",
            delta="$42K",
            help="Total fraud amount prevented (YTD)"
        )
    
    st.markdown("---")
    
    # Second row of metrics
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
        
        # Fraud rate line
        fig.add_trace(go.Scatter(
            x=trend_data['date'],
            y=trend_data['fraud_rate'],
            name='Fraud Rate (%)',
            line=dict(color='#f44336', width=3),
            yaxis='y1'
        ))
        
        # Invoice volume bars
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
    st.markdown('<div class="main-header">📄 Invoice Upload - OCR Extraction</div>', unsafe_allow_html=True)
    
    st.info("💡 **Tip**: Hệ thống hỗ trợ PDF, PNG, JPG. Confidence score > 70% sẽ được xử lý tự động.")
    
    uploaded_file = st.file_uploader(
        "Upload Invoice",
        type=['pdf', 'png', 'jpg', 'jpeg'],
        help="Drag and drop hoặc click để upload"
    )
    
    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📄 Uploaded Document")
            
            if uploaded_file.type == 'application/pdf':
                st.info("PDF preview (first page)")
                # TODO: Render PDF preview
            else:
                st.image(uploaded_file, caption="Invoice Image")
        
        with col2:
            st.subheader("🔍 OCR Processing")
            
            if st.button("🚀 Process Invoice", type="primary"):
                with st.spinner("Processing with Amazon Textract..."):
                    # TODO: Implement actual Textract call
                    import time
                    time.sleep(2)
                    
                    # Sample extraction result
                    extraction_result = {
                        'invoice_number': 'INV-2026-5678',
                        'invoice_date': '2026-02-10',
                        'supplier_name': 'ABC Corporation',
                        'supplier_email': 'billing@abccorp.com',
                        'amount': 12345.67,
                        'currency': 'USD',
                        'po_number': 'PO-2026-1234',
                        'confidence': 87.5
                    }
                    
                    confidence = extraction_result['confidence']
                    
                    if confidence >= 70:
                        st.success(f"✅ Extracted successfully! (Confidence: {confidence}%)")
                    else:
                        st.error(f"⚠️ Low confidence ({confidence}%) - Manual review required")
                    
                    st.json(extraction_result)
                    
                    # Show next steps
                    if confidence >= 70:
                        st.markdown("### Next Steps")
                        st.markdown("1. ✅ PII Preprocessing")
                        st.markdown("2. 🔢 Decimal Matching")
                        st.markdown("3. 🧠 AI Risk Analysis")
                        
                        if st.button("▶️ Continue to Risk Analysis"):
                            st.session_state.page = 'fraud'
                            st.rerun()

elif st.session_state.page == 'fraud':
    # ====== FRAUD DETECTION ======
    st.markdown('<div class="main-header">🔍 Fraud Detection & Risk Analysis</div>', unsafe_allow_html=True)
    
    # Sample invoice for demo
    sample_invoice = {
        'id': 'INV-2026-5678',
        'amount': 12345.67,
        'po_amount': 12000.00,
        'supplier': 'ABC Corporation',
        'supplier_trust_score': 75,
        'invoice_date': '2026-02-10'
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
            st.metric("Deviation", f"{percentage:.2f}%", 
                     delta=f"{percentage:.2f}%",
                     delta_color="inverse")
        
        st.markdown("---")
        
        # Risk Score Gauge
        st.subheader("🧠 AI Risk Analysis")
        
        # Calculate risk score (simplified)
        math_score = min(percentage * 10, 70)
        trust_score = (100 - sample_invoice['supplier_trust_score']) * 0.4
        risk_score = math_score + trust_score
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = risk_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Fraud Risk Score", 'font': {'size': 24}},
            delta = {'reference': 50, 'increasing': {'color': "red"}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 30], 'color': '#4caf50'},
                    {'range': [30, 70], 'color': '#ff9800'},
                    {'range': [70, 100], 'color': '#f44336'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Risk Breakdown")
        
        breakdown = pd.DataFrame({
            'Component': ['Math Score', 'Supplier Trust', 'Amount Anomaly', 'Temporal', 'Device'],
            'Points': [math_score, trust_score, 5, 2, 0],
            'Max': [70, 40, 10, 10, 10]
        })
        
        fig = px.bar(
            breakdown,
            y='Component',
            x='Points',
            orientation='h',
            title='Risk Components',
            color='Points',
            color_continuous_scale='Reds'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Decision
        if risk_score < 30:
            decision = "AUTO-APPROVE"
            st.success(f"✅ Decision: {decision}")
            st.markdown("Low risk - Automatically approved")
        elif risk_score < 70:
            decision = "MANUAL CHECK"
            st.warning(f"⚠️ Decision: {decision}")
            st.markdown("Medium risk - Requires human review")
            
            st.markdown("### Take Action")
            col_a, col_b = st.columns(2)
            if col_a.button("✅ Approve", type="primary"):
                st.success("Invoice approved!")
            if col_b.button("❌ Reject", type="secondary"):
                st.error("Invoice rejected!")
        else:
            decision = "AUTO-BLOCK"
            st.error(f"🚨 Decision: {decision}")
            st.markdown("High risk - Automatically blocked")

elif st.session_state.page == 'ml_insights':
    # ====== ML INSIGHTS ======
    st.markdown('<div class="main-header">🤖 ML Intelligence Center</div>', unsafe_allow_html=True)
    
    st.info("🔬 **Advanced Analytics**: Prophet forecasting, Isolation Forest anomaly detection, K-means clustering")
    
    # Fraud Forecast
    st.subheader("📈 Fraud Rate Forecast (Next 30 Days)")
    
    forecast_dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
    forecast_data = pd.DataFrame({
        'ds': forecast_dates,
        'yhat': [2.1 + (i % 7) * 0.2 for i in range(30)],
        'yhat_lower': [1.8 + (i % 7) * 0.15 for i in range(30)],
        'yhat_upper': [2.5 + (i % 7) * 0.25 for i in range(30)]
    })
    
    fig = go.Figure()
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=forecast_data['ds'], y=forecast_data['yhat_upper'],
        fill=None, mode='lines', line_color='rgba(0,0,0,0)',
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=forecast_data['ds'], y=forecast_data['yhat_lower'],
        fill='tonexty', mode='lines', line_color='rgba(0,0,0,0)',
        fillcolor='rgba(31, 119, 180, 0.2)',
        name='Confidence Interval'
    ))
    
    # Forecast line
    fig.add_trace(go.Scatter(
        x=forecast_data['ds'], y=forecast_data['yhat'],
        mode='lines', line=dict(color='#1f77b4', width=3),
        name='Forecast'
    ))
    
    fig.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    
    # Anomaly Detection
    st.subheader("🚨 Detected Anomalies (Last 7 Days)")
    
    anomalies = pd.DataFrame({
        'Invoice ID': ['INV-2026-1111', 'INV-2026-2222', 'INV-2026-3333'],
        'Amount': [45000, 89000, 12000],
        'Supplier': ['Unknown Corp', 'ABC Ltd', 'XYZ Inc'],
        'Anomaly Score': [0.92, 0.87, 0.81],
        'Reason': ['Unusually high amount', 'New supplier + high amount', 'Rapid succession']
    })
    
    st.dataframe(anomalies, use_container_width=True)
    
    # Supplier Risk Clustering
    st.subheader("🎯 Supplier Risk Segmentation")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        risk_distribution = pd.DataFrame({
            'Risk Tier': ['LOW', 'MEDIUM', 'HIGH'],
            'Count': [234, 87, 23]
        })
        
        st.dataframe(risk_distribution)
        
        st.markdown("### Summary")
        st.markdown("- **Low Risk**: 68% of suppliers")
        st.markdown("- **Medium Risk**: 25%")
        st.markdown("- **High Risk**: 7% (flagged)")
    
    with col2:
        fig = px.pie(
            risk_distribution,
            values='Count',
            names='Risk Tier',
            title='Supplier Distribution',
            color='Risk Tier',
            color_discrete_map={'LOW': '#4caf50', 'MEDIUM': '#ff9800', 'HIGH': '#f44336'}
        )
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == 'merchant':
    # ====== MERCHANT SUCCESS ======
    st.markdown('<div class="main-header">🏪 Merchant Success Center</div>', unsafe_allow_html=True)
    
    merchant_id = st.selectbox("Select Merchant", ['Merchant A', 'Merchant B', 'Merchant C'])
    
    # Sales Performance
    st.subheader("📊 Sales Performance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("This Week Sales", "$125,400", delta="-22%", delta_color="inverse")
    
    with col2:
        st.metric("Last Week Sales", "$161,000")
    
    with col3:
        st.metric("Avg Order Value", "$245", delta="-5%")
    
    st.warning("⚠️ Sales dropped 22% this week - Root cause analysis triggered")
    
    # Root Cause Analysis
    st.subheader("🔍 Root Cause Analysis")
    
    causes = [
        {'factor': '💰 Pricing', 'issue': 'Prices 35% above market average', 'impact': 'HIGH'},
        {'factor': '📦 Inventory', 'issue': '3 best-sellers out of stock', 'impact': 'MEDIUM'},
        {'factor': '⭐ Reviews', 'issue': '8 negative reviews in past 7 days', 'impact': 'LOW'}
    ]
    
    for cause in causes:
        with st.expander(f"{cause['factor']} - {cause['impact']} Impact"):
            st.write(f"**Issue**: {cause['issue']}")
            
            if 'Pricing' in cause['factor']:
                st.info("💡 **Recommendation**: Competitor ABC launched 30% off promotion. Consider matching or emphasizing free shipping.")
    
    # Image Quality
    st.subheader("📸 Product Image Quality")
    
    quality_data = pd.DataFrame({
        'Product': ['Product A', 'Product B', 'Product C', 'Product D'],
        'Quality Score': [85, 62, 91, 45],
        'Issues': ['None', 'Blurry', 'None', 'Poor lighting + blurry']
    })
    
    for _, row in quality_data.iterrows():
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.write(f"**{row['Product']}**")
        
        with col2:
            score = row['Quality Score']
            if score >= 80:
                st.success(f"✅ {score}/100")
            elif score >= 60:
                st.warning(f"⚠️ {score}/100")
            else:
                st.error(f"❌ {score}/100")
        
        with col3:
            if row['Issues'] != 'None':
                st.write(f"Issues: {row['Issues']}")

elif st.session_state.page == 'security':
    # ====== SECURITY ======
    st.markdown('<div class="main-header">🛡️ Security Operations Center</div>', unsafe_allow_html=True)
    
    # Real-time threat feed
    st.subheader("🚨 Active Threats")
    
    threats = [
        {
            'id': 'THREAT-001',
            'type': 'NFC Relay Attack',
            'severity': 'HIGH',
            'timestamp': '2026-02-15 14:30:25',
            'details': 'Transaction duration: 1250ms, Geo-velocity: 1200 km/h',
            'action': 'BLOCKED'
        },
        {
            'id': 'THREAT-002',
            'type': 'Account Takeover',
            'severity': 'MEDIUM',
            'timestamp': '2026-02-15 13:15:10',
            'details': 'Typing speed changed from 45 WPM to 85 WPM',
            'action': 'FORCE_REAUTH'
        }
    ]
    
    for threat in threats:
        severity_color = 'alert-high' if threat['severity'] == 'HIGH' else 'alert-medium'
        
        st.markdown(f"""
        <div class="{severity_color}">
            <strong>{threat['id']}: {threat['type']}</strong><br>
            Severity: {threat['severity']}<br>
            Time: {threat['timestamp']}<br>
            Details: {threat['details']}<br>
            Action: {threat['action']}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Fraud Ring Detection
    st.subheader("🕸️ Fraud Ring Detection")
    
    st.info("🔬 **Graph Analysis**: Louvain community detection on 15,234 accounts")
    
    st.markdown("""
    **Detected Fraud Ring #1**:
    - 12 accounts
    - Shared 3 device fingerprints
    - 147 fraudulent invoices ($2.3M)
    - All accounts created within 72 hours
    """)
    
    if st.button("🔍 View Full Network Graph"):
        st.info("Network visualization would render here (using Plotly Network Graph)")

else:
    # ====== SETTINGS ======
    st.markdown('<div class="main-header">⚙️ System Settings</div>', unsafe_allow_html=True)
    
    st.subheader("🎚️ Risk Thresholds")
    
    auto_approve_threshold = st.slider("Auto-Approve Threshold", 0, 100, 30)
    auto_block_threshold = st.slider("Auto-Block Threshold", 0, 100, 70)
    
    st.info(f"Current Configuration: Auto-approve < {auto_approve_threshold}, Manual review {auto_approve_threshold}-{auto_block_threshold}, Auto-block ≥ {auto_block_threshold}")
    
    st.subheader("🔔 Notifications")
    
    slack_webhook = st.text_input("Slack Webhook URL", value="https://hooks.slack.com/services/...")
    email_alerts = st.checkbox("Enable Email Alerts", value=True)
    
    st.subheader("🔐 Security")
    
    mfa_enabled = st.checkbox("Require MFA", value=True)
    session_timeout = st.number_input("Session Timeout (minutes)", value=30, min_value=5, max_value=120)
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("✅ Settings saved successfully!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    AgentFlow Finance Guard v1.0 | Powered by AWS Bedrock & Anthropic Claude | 
    <a href='#'>Documentation</a> | <a href='#'>Support</a>
</div>
""", unsafe_allow_html=True)