import streamlit as st
from utils.helpers import apply_theme
apply_theme()
if not st.session_state.get('logged_in', False):
    st.warning('⚠️ Vui lòng đăng nhập để tiếp tục.')
    st.stop()
from components.sidebar import render_sidebar
render_sidebar()
from components.widgets import (
    alert_box,
    success_box,
    card_container,
    status_badge,
    empty_state
)
from components.metrics import metric_card_group
import logging

logger = logging.getLogger(__name__)

# Page header
st.markdown('<h1 class="main-header">🔗 Integrations</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Manage external service connections</p>', unsafe_allow_html=True)

# Integration overview
st.markdown("### 📊 Integration Status")

metric_card_group([
    {'title': 'Active Integrations', 'value': '8', 'delta': '+2 this month'},
    {'title': 'API Calls Today', 'value': '12,547', 'delta': '+8.3%'},
    {'title': 'Success Rate', 'value': '99.2%', 'delta': '+0.5%'},
    {'title': 'Avg Response Time', 'value': '245ms', 'delta': '-12ms'}
])

st.divider()

# Available integrations
st.markdown("### 🔌 Available Integrations")

integrations = [
    {
        'name': 'AWS Cognito',
        'description': 'User authentication and authorization',
        'category': 'Authentication',
        'status': 'Connected',
        'icon': '🔐',
        'last_sync': '2 minutes ago'
    },
    {
        'name': 'AWS S3',
        'description': 'File storage and document management',
        'category': 'Storage',
        'status': 'Connected',
        'icon': '📦',
        'last_sync': '5 minutes ago'
    },
    {
        'name': 'AWS RDS PostgreSQL',
        'description': 'Primary database for invoice data',
        'category': 'Database',
        'status': 'Connected',
        'icon': '🗄️',
        'last_sync': '1 minute ago'
    },
    {
        'name': 'AWS X-Ray',
        'description': 'Distributed tracing and monitoring',
        'category': 'Observability',
        'status': 'Connected',
        'icon': '📈',
        'last_sync': '30 seconds ago'
    },
    {
        'name': 'AWS CloudWatch',
        'description': 'Logging and metrics collection',
        'category': 'Observability',
        'status': 'Connected',
        'icon': '☁️',
        'last_sync': '1 minute ago'
    },
    {
        'name': 'Slack',
        'description': 'Team notifications and alerts',
        'category': 'Communication',
        'status': 'Not Connected',
        'icon': '💬',
        'last_sync': 'Never'
    },
    {
        'name': 'PagerDuty',
        'description': 'Incident management and alerting',
        'category': 'Alerting',
        'status': 'Not Connected',
        'icon': '🚨',
        'last_sync': 'Never'
    },
    {
        'name': 'Datadog',
        'description': 'Advanced monitoring and APM',
        'category': 'Observability',
        'status': 'Not Connected',
        'icon': '🐶',
        'last_sync': 'Never'
    },
    {
        'name': 'Stripe',
        'description': 'Payment processing integration',
        'category': 'Payments',
        'status': 'Not Connected',
        'icon': '💳',
        'last_sync': 'Never'
    },
    {
        'name': 'SendGrid',
        'description': 'Email notifications',
        'category': 'Communication',
        'status': 'Not Connected',
        'icon': '📧',
        'last_sync': 'Never'
    }
]

# Category filter
categories = ['All'] + list(set(i['category'] for i in integrations))
selected_category = st.selectbox("Filter by category", categories, index=0)

# Filter integrations
filtered = integrations if selected_category == 'All' else [
    i for i in integrations if i['category'] == selected_category
]

# Display integrations
for integration in filtered:
    status = integration['status']
    is_connected = status == 'Connected'
    variant = 'success' if is_connected else 'default'
    
    with card_container(
        title=f"{integration['icon']} {integration['name']}",
        variant=variant
    ):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{integration['description']}**")
            st.markdown(f"Category: {integration['category']}")
            st.markdown(f"Last sync: {integration['last_sync']}")
        
        with col2:
            status_badge(
                status,
                'success' if is_connected else 'info'
            )
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if is_connected:
                if st.button("⚙️ Configure", key=f"config_{integration['name']}", use_container_width=True):
                    st.info(f"Configuration for {integration['name']}")
            else:
                if st.button("➕ Connect", key=f"connect_{integration['name']}", use_container_width=True, type="primary"):
                    st.success(f"Connecting to {integration['name']}...")
        
        with col2:
            if is_connected:
                if st.button("🔄 Sync Now", key=f"sync_{integration['name']}", use_container_width=True):
                    st.success(f"Syncing {integration['name']}...")
            else:
                if st.button("📖 Learn More", key=f"learn_{integration['name']}", use_container_width=True):
                    st.info(f"Opening documentation for {integration['name']}...")
        
        with col3:
            if is_connected:
                if st.button("🔌 Disconnect", key=f"disconnect_{integration['name']}", use_container_width=True):
                    st.warning(f"Disconnecting from {integration['name']}...")
            else:
                st.write("")  # Empty space

st.divider()

# Webhooks
st.markdown("### 🪝 Webhooks")

with card_container("Webhook Configuration", "⚡", variant='primary'):
    st.markdown("""
    Configure webhooks to receive real-time notifications about events.
    
    **Available Events:**
    - 🔔 Invoice Processed
    - 🚨 Fraud Detected
    - ✅ Invoice Approved
    - 🚫 Invoice Blocked
    - ⚠️ High Risk Detected
    """)
    
    webhook_url = st.text_input(
        "Webhook URL",
        placeholder="https://your-domain.com/webhook",
        help="POST requests will be sent to this URL"
    )
    
    events = st.multiselect(
        "Subscribe to events",
        options=[
            'invoice.processed',
            'fraud.detected',
            'invoice.approved',
            'invoice.blocked',
            'risk.high'
        ],
        default=['fraud.detected', 'risk.high']
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Webhook", use_container_width=True, type="primary"):
            if webhook_url:
                success_box("✅ Webhook configured successfully!")
            else:
                alert_box("⚠️ Please enter a webhook URL", "warning")
    
    with col2:
        if st.button("🧪 Test Webhook", use_container_width=True):
            if webhook_url:
                st.info("Sending test payload to webhook...")
            else:
                alert_box("⚠️ Please enter a webhook URL", "warning")

st.divider()

# API keys
st.markdown("### 🔑 API Keys")

with card_container("API Key Management", "🔐", variant='warning'):
    st.markdown("""
    Generate API keys for programmatic access to AgentFlow.
    
    **Permissions:**
    - 📖 Read-only access
    - 📝 Write access
    - 🔧 Admin access
    """)
    
    if st.button("➕ Generate New API Key", type="primary"):
        import secrets
        api_key = f"agf_{secrets.token_hex(16)}"
        st.code(api_key, language="text")
        st.warning("⚠️ Save this key securely. It won't be shown again.")
    
    st.markdown("---")
    
    st.markdown("**Active API Keys:**")
    
    api_keys = [
        {'name': 'Production Key', 'created': '2026-01-15', 'last_used': '2 hours ago', 'permissions': 'Read/Write'},
        {'name': 'Development Key', 'created': '2026-02-01', 'last_used': '5 minutes ago', 'permissions': 'Read-only'},
    ]
    
    for key in api_keys:
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
        
        with col1:
            st.text(key['name'])
        
        with col2:
            st.text(f"Created: {key['created']}")
        
        with col3:
            st.text(f"Last used: {key['last_used']}")
        
        with col4:
            st.text(key['permissions'])
        
        with col5:
            if st.button("🗑️", key=f"delete_{key['name']}"):
                st.warning(f"Revoked {key['name']}")