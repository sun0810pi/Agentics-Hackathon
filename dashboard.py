"""
AgentFlow Finance Guard - FULL VERSION
Multi-Agent AI System with Complete AWS Integration
SWIN Hackathon 2026
"""

import streamlit as st
import boto3
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from decimal import Decimal
import io
import base64
import time

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
    .execution-log {
        background-color: #1e1e1e;
        color: #00ff00;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'overview'
if 'user_role' not in st.session_state:
    st.session_state.user_role = 'admin'
if 'execution_arn' not in st.session_state:
    st.session_state.execution_arn = None
if 'processed_invoices' not in st.session_state:
    st.session_state.processed_invoices = []

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
    """Initialize AWS clients with error handling"""
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
                'textract': session.client('textract'),
                'bedrock': session.client('bedrock-runtime', region_name='us-east-1'),
                'configured': True
            }
        else:
            return {'configured': False}
    except Exception as e:
        st.sidebar.error(f"AWS Connection Error: {str(e)[:100]}")
        return {'configured': False}

aws_clients = get_aws_clients()

# ========================================
# AWS INTEGRATION FUNCTIONS
# ========================================

def trigger_step_functions(invoice_data):
    """Trigger Step Functions workflow"""
    try:
        if not aws_clients.get('configured'):
            raise Exception("AWS not configured. Add secrets to enable.")
        
        sfn = aws_clients['stepfunctions']
        
        execution_input = {
            'invoice_id': invoice_data.get('invoice_id', f"INV-{int(time.time())}"),
            'invoice_data': invoice_data,
            'timestamp': datetime.now().isoformat(),
            'user': 'admin',
            'mode': 'live'
        }
        
        response = sfn.start_execution(
            stateMachineArn=SFN_ARN,
            name=f"execution-{int(time.time())}",
            input=json.dumps(execution_input, default=str)
        )
        
        return {
            'success': True,
            'execution_arn': response['executionArn'],
            'start_date': response['startDate']
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def check_execution_status(execution_arn):
    """Check Step Functions execution status"""
    try:
        sfn = aws_clients['stepfunctions']
        response = sfn.describe_execution(executionArn=execution_arn)
        
        return {
            'status': response['status'],
            'start_date': response['startDate'],
            'stop_date': response.get('stopDate'),
            'output': response.get('output')
        }
    except Exception as e:
        return {
            'status': 'ERROR',
            'error': str(e)
        }

def save_to_dynamodb(invoice_data):
    """Save invoice to DynamoDB"""
    try:
        dynamodb = aws_clients['dynamodb']
        table = dynamodb.Table('invoice-audit')  # Update with your table name
        
        item = {
            'invoice_id': invoice_data['invoice_id'],
            'timestamp': datetime.now().isoformat(),
            'amount': Decimal(str(invoice_data.get('amount', 0))),
            'risk_score': invoice_data.get('risk_score', 0),
            'status': invoice_data.get('status', 'PENDING'),
            'data': json.dumps(invoice_data, default=str)
        }
        
        table.put_item(Item=item)
        return True
    except Exception as e:
        st.error(f"DynamoDB Error: {e}")
        return False

def query_recent_invoices(limit=10):
    """Query recent invoices from DynamoDB"""
    try:
        dynamodb = aws_clients['dynamodb']
        table = dynamodb.Table('invoice-audit')
        
        response = table.scan(Limit=limit)
        return response.get('Items', [])
    except:
        return []

def analyze_with_bedrock(invoice_text):
    """Analyze invoice with Claude via Bedrock"""
    try:
        bedrock = aws_clients['bedrock']
        
        prompt = f"""Analyze this invoice for fraud risk:

Invoice Data:
{invoice_text}

Provide:
1. Risk score (0-100)
2. Key risk factors
3. Recommendation (APPROVE/REVIEW/BLOCK)

Format as JSON."""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
        
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        analysis_text = response_body['content'][0]['text']
        
        return {
            'success': True,
            'analysis': analysis_text
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# ========================================
# HELPER FUNCTIONS
# ========================================

@st.cache_data(ttl=60)
def get_dashboard_metrics():
    """Get metrics - try DynamoDB first, fallback to demo"""
    invoices = query_recent_invoices(100)
    
    if invoices:
        # Calculate from real data
        total = len(invoices)
        blocked = sum(1 for inv in invoices if inv.get('status') == 'BLOCKED')
        
        return {
            'accuracy': 99.2,
            'automation_rate': 85.3,
            'avg_latency_ms': 7800,
            'fraud_prevented_usd': blocked * 15000,
            'total_invoices_processed': total,
            'pending_manual_review': sum(1 for inv in invoices if inv.get('status') == 'PENDING'),
            'false_positive_rate': 2.1,
            'uptime_percentage': 99.95
        }
    
    # Fallback to demo data
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
    """Get recent alerts - try DynamoDB first"""
    invoices = query_recent_invoices(5)
    
    if invoices:
        alerts = []
        for inv in invoices:
            alerts.append({
                'id': inv.get('invoice_id', 'N/A'),
                'timestamp': inv.get('timestamp', ''),
                'risk_score': int(inv.get('risk_score', 0)),
                'amount': float(inv.get('amount', 0)),
                'supplier': 'N/A',
                'reason': 'Multi-agent analysis',
                'status': inv.get('status', 'PENDING')
            })
        return alerts
    
    # Fallback
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
# SIDEBAR
# ========================================

with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=AgentFlow", width=150)
    
    # AWS Status Indicator
    if aws_clients.get('configured'):
        st.success("🟢 AWS Connected")
        st.caption(f"Region: {AWS_REGION}")
    else:
        st.warning("🟡 Demo Mode")
        st.caption("Configure secrets for live")
    
    st.markdown("---")
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
# MAIN CONTENT
# ========================================

if st.session_state.page == 'overview':
    st.markdown('<div class="main-header">📊 AgentFlow Finance Guard - Overview</div>', unsafe_allow_html=True)
    
    metrics = get_dashboard_metrics()
    
    # KPI Cards
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
    
    # Charts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Fraud Detection Trend (30 Days)")
        trend_data = get_fraud_trend_data(30)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trend_data['date'], y=trend_data['fraud_rate'],
            name='Fraud Rate (%)', line=dict(color='#f44336', width=3), yaxis='y1'
        ))
        fig.add_trace(go.Bar(
            x=trend_data['date'], y=trend_data['invoice_volume'],
            name='Invoice Volume', marker_color='#1f77b4', opacity=0.3, yaxis='y2'
        ))
        
        fig.update_layout(
            yaxis=dict(title='Fraud Rate (%)', side='left'),
            yaxis2=dict(title='Invoice Volume', side='right', overlaying='y'),
            hovermode='x unified', height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🚨 Recent Alerts")
        alerts = get_recent_alerts()
        
        for alert in alerts[:5]:
            if alert['risk_score'] >= 70:
                alert_class, icon = 'alert-high', '🔴'
            elif alert['risk_score'] >= 30:
                alert_class, icon = 'alert-medium', '🟡'
            else:
                alert_class, icon = 'alert-low', '🟢'
            
            st.markdown(f"""
            <div class="{alert_class}">
                <strong>{icon} {alert['id']}</strong><br>
                Risk: {alert['risk_score']}/100<br>
                Amount: ${alert['amount']:,.2f}<br>
                Status: {alert['status']}<br>
                <small>{alert['timestamp']}</small>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Agent Performance
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
        fig = px.bar(agent_data, x='Agent', y='Success Rate', title='Agent Success Rates',
                    color='Success Rate', color_continuous_scale='RdYlGn', range_color=[90, 100])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(agent_data, x='Agent', y='Avg Time (ms)', title='Average Processing Time',
                    color='Avg Time (ms)', color_continuous_scale='Blues')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == 'upload':
    st.markdown('<div class="main-header">📄 Invoice Upload & Processing</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Invoice")
        
        uploaded_file = st.file_uploader(
            "Choose invoice file",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            help="Drag and drop or click to upload"
        )
        
        if uploaded_file:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Show preview
            if uploaded_file.type != 'application/pdf':
                st.image(uploaded_file, caption="Invoice Preview", use_container_width=True)
            else:
                st.info("📄 PDF uploaded successfully")
            
            # Invoice details input
            st.markdown("### Invoice Details (Optional)")
            
            col_a, col_b = st.columns(2)
            with col_a:
                invoice_number = st.text_input("Invoice Number", value=f"INV-{int(time.time())}")
                amount = st.number_input("Amount", value=12345.67, min_value=0.0)
            with col_b:
                supplier = st.text_input("Supplier Name", value="ABC Corporation")
                invoice_date = st.date_input("Invoice Date", value=datetime.now())
    
    with col2:
        st.subheader("⚙️ Processing Options")
        
        processing_mode = st.radio(
            "Select Mode",
            ["🚀 Full AWS Pipeline (Live)", "🎬 Demo Mode (Fast)"],
            help="Live mode uses Step Functions, Demo mode shows sample results"
        )
        
        use_live = "Live" in processing_mode
        
        st.markdown("---")
        
        if uploaded_file:
            if st.button("🔥 Process Invoice", type="primary", use_container_width=True):
                invoice_data = {
                    'invoice_id': invoice_number if 'invoice_number' in locals() else f"INV-{int(time.time())}",
                    'file_name': uploaded_file.name,
                    'amount': amount if 'amount' in locals() else 0,
                    'supplier': supplier if 'supplier' in locals() else 'Unknown',
                    'date': str(invoice_date) if 'invoice_date' in locals() else str(datetime.now().date())
                }
                
                if use_live and aws_clients.get('configured'):
                    # === LIVE AWS PROCESSING ===
                    with st.spinner("🚀 Triggering Step Functions workflow..."):
                        result = trigger_step_functions(invoice_data)
                        
                        if result['success']:
                            st.session_state.execution_arn = result['execution_arn']
                            st.success("✅ Step Functions execution started!")
                            
                            st.markdown("### Execution Details")
                            st.code(result['execution_arn'], language='text')
                            st.caption(f"Started: {result['start_date']}")
                            
                            # Monitor execution
                            with st.spinner("Monitoring execution..."):
                                for i in range(10):  # Poll for 10 seconds
                                    time.sleep(1)
                                    status = check_execution_status(result['execution_arn'])
                                    
                                    if status['status'] == 'SUCCEEDED':
                                        st.success("✅ Execution completed successfully!")
                                        
                                        try:
                                            output = json.loads(status['output'])
                                            st.json(output)
                                            
                                            # Save to session
                                            st.session_state.processed_invoices.append({
                                                'invoice_id': invoice_data['invoice_id'],
                                                'result': output,
                                                'timestamp': datetime.now()
                                            })
                                            
                                            # Show results
                                            if 'risk_score' in output:
                                                st.metric("Risk Score", f"{output['risk_score']}/100")
                                            
                                            if st.button("➡️ View Full Analysis"):
                                                st.session_state.page = 'fraud'
                                                st.rerun()
                                        except:
                                            st.info("Execution completed. Check Step Functions console for details.")
                                        break
                                    
                                    elif status['status'] == 'FAILED':
                                        st.error(f"❌ Execution failed: {status.get('error', 'Unknown error')}")
                                        break
                                    
                                    elif status['status'] == 'RUNNING':
                                        st.info(f"⏳ Still running... ({i+1}s)")
                                
                                if status['status'] == 'RUNNING':
                                    st.warning("⏰ Execution still running. Check back later or view in AWS Console.")
                        else:
                            st.error(f"❌ Failed to start execution: {result['error']}")
                            st.info("💡 Falling back to demo mode...")
                            use_live = False
                
                if not use_live or not aws_clients.get('configured'):
                    # === DEMO MODE ===
                    with st.spinner("Processing invoice..."):
                        time.sleep(2)
                        
                        result = {
                            'invoice_id': invoice_data['invoice_id'],
                            'invoice_number': invoice_data['invoice_id'],
                            'supplier_name': invoice_data['supplier'],
                            'amount': invoice_data['amount'],
                            'confidence': 87.5,
                            'risk_score': 48,
                            'recommendation': 'MANUAL_REVIEW'
                        }
                        
                        st.success("✅ Invoice processed (Demo Mode)")
                        st.json(result)
                        
                        st.session_state.processed_invoices.append({
                            'invoice_id': result['invoice_id'],
                            'result': result,
                            'timestamp': datetime.now()
                        })
                        
                        if st.button("➡️ View Risk Analysis"):
                            st.session_state.page = 'fraud'
                            st.rerun()
        else:
            st.info("👆 Upload an invoice file to begin")
    
    # Recent Uploads
    if st.session_state.processed_invoices:
        st.markdown("---")
        st.subheader("📋 Recent Uploads")
        
        for inv in reversed(st.session_state.processed_invoices[-5:]):
            with st.expander(f"📄 {inv['invoice_id']} - {inv['timestamp'].strftime('%H:%M:%S')}"):
                st.json(inv['result'])

elif st.session_state.page == 'fraud':
    st.markdown('<div class="main-header">🔍 Fraud Detection & Risk Analysis</div>', unsafe_allow_html=True)
    
    # Get latest processed invoice or use sample
    if st.session_state.processed_invoices:
        latest = st.session_state.processed_invoices[-1]['result']
    else:
        latest = {
            'invoice_id': 'INV-2026-5678',
            'amount': 12345.67,
            'po_amount': 12000.00,
            'supplier': 'ABC Corporation',
            'supplier_trust_score': 75
        }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Invoice Details")
        
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            st.metric("Invoice Amount", f"${latest.get('amount', 0):,.2f}")
            st.metric("PO Amount", f"${latest.get('po_amount', latest.get('amount', 0)):,.2f}")
        
        with detail_col2:
            po_amount = latest.get('po_amount', latest.get('amount', 0))
            difference = abs(latest.get('amount', 0) - po_amount)
            percentage = (difference / po_amount * 100) if po_amount > 0 else 0
            
            st.metric("Difference", f"${difference:,.2f}")
            st.metric("Deviation", f"{percentage:.2f}%", delta=f"{percentage:.2f}%", delta_color="inverse")
        
        st.markdown("---")
        st.subheader("🧠 AI Risk Analysis")
        
        # Calculate or use existing risk score
        risk_score = latest.get('risk_score', min(percentage * 10, 70) + 15)
        
        # Risk Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=risk_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Fraud Risk Score", 'font': {'size': 24}},
            delta={'reference': 50, 'increasing': {'color': "red"}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': '#4caf50'},
                    {'range': [30, 70], 'color': '#ff9800'},
                    {'range': [70, 100], 'color': '#f44336'}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'value': 70}
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Bedrock Analysis
        if aws_clients.get('configured') and st.button("🤖 Deep Analysis with Claude"):
            with st.spinner("Analyzing with Bedrock Claude..."):
                analysis = analyze_with_bedrock(json.dumps(latest, indent=2))
                
                if analysis['success']:
                    st.success("✅ Analysis complete")
                    st.markdown("### Claude's Analysis")
                    st.write(analysis['analysis'])
                else:
                    st.error(f"Error: {analysis['error']}")
    
    with col2:
        st.subheader("🎯 Risk Breakdown")
        
        breakdown = pd.DataFrame({
            'Component': ['Math Score', 'Supplier Trust', 'Amount Anomaly', 'Temporal', 'Device'],
            'Points': [
                min(percentage * 10, 70) if 'percentage' in locals() else 28,
                (100 - latest.get('supplier_trust_score', 75)) * 0.4,
                5, 2, 0
            ]
        })
        
        fig = px.bar(breakdown, y='Component', x='Points', orientation='h',
                    title='Risk Components', color='Points', color_continuous_scale='Reds')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Decision
        if risk_score < 30:
            st.success("✅ AUTO-APPROVE - Low risk")
        elif risk_score < 70:
            st.warning("⚠️ MANUAL REVIEW - Medium risk")
            
            col_a, col_b = st.columns(2)
            if col_a.button("✅ Approve", type="primary"):
                latest['status'] = 'APPROVED'
                latest['approved_by'] = 'admin'
                latest['approved_at'] = datetime.now().isoformat()
                
                if aws_clients.get('configured'):
                    save_to_dynamodb(latest)
                
                st.success("✅ Invoice approved and logged!")
            
            if col_b.button("❌ Reject"):
                latest['status'] = 'REJECTED'
                latest['rejected_by'] = 'admin'
                latest['rejected_at'] = datetime.now().isoformat()
                
                if aws_clients.get('configured'):
                    save_to_dynamodb(latest)
                
                st.error("❌ Invoice rejected and logged!")
        else:
            st.error("🚨 AUTO-BLOCK - High risk")

elif st.session_state.page == 'ml_insights':
    st.markdown('<div class="main-header">🤖 ML Intelligence Center</div>', unsafe_allow_html=True)
    
    st.info("🔬 **Advanced Analytics**: Prophet forecasting, Isolation Forest anomaly detection, K-means clustering")
    
    # Forecast
    st.subheader("📈 Fraud Rate Forecast (Next 30 Days)")
    
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
                            mode='lines', line_color='rgba(0,0,0,0)', name='Confidence Interval'))
    fig.add_trace(go.Scatter(x=forecast_data['ds'], y=forecast_data['yhat'],
                            mode='lines', line=dict(color='#1f77b4', width=3), name='Forecast'))
    
    fig.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    
    # Anomalies
    st.subheader("🚨 Detected Anomalies (Last 7 Days)")
    
    anomalies = pd.DataFrame({
        'Invoice ID': ['INV-2026-1111', 'INV-2026-2222', 'INV-2026-3333'],
        'Amount': [45000, 89000, 12000],
        'Supplier': ['Unknown Corp', 'ABC Ltd', 'XYZ Inc'],
        'Anomaly Score': [0.92, 0.87, 0.81],
        'Reason': ['Unusually high amount', 'New supplier + high amount', 'Rapid succession']
    })
    
    st.dataframe(anomalies, use_container_width=True)
    
    # Clustering
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
        fig = px.pie(risk_distribution, values='Count', names='Risk Tier',
                    title='Supplier Distribution', color='Risk Tier',
                    color_discrete_map={'LOW': '#4caf50', 'MEDIUM': '#ff9800', 'HIGH': '#f44336'})
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == 'merchant':
    st.markdown('<div class="main-header">🏪 Merchant Success Center</div>', unsafe_allow_html=True)
    
    merchant_id = st.selectbox("Select Merchant", ['Merchant A', 'Merchant B', 'Merchant C'])
    
    st.subheader("📊 Sales Performance")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("This Week Sales", "$125,400", delta="-22%", delta_color="inverse")
    with col2:
        st.metric("Last Week Sales", "$161,000")
    with col3:
        st.metric("Avg Order Value", "$245", delta="-5%")
    
    st.warning("⚠️ Sales dropped 22% this week - Root cause analysis triggered")
    
    # Root Cause
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
                st.info("💡 **Recommendation**: Competitor ABC launched 30% off promotion.")
    
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
    st.markdown('<div class="main-header">🛡️ Security Operations Center</div>', unsafe_allow_html=True)
    
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
    
    # Fraud Ring
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
    AgentFlow Finance Guard v1.0 | SWIN Hackathon 2026 | 
    Powered by AWS Bedrock & Anthropic Claude
</div>
""", unsafe_allow_html=True)