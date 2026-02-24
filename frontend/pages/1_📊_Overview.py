import streamlit as st
from components.metrics import metric_card_group, kpi_card
from components.charts import plot_time_series, plot_risk_distribution
from components.widgets import alert_box, stat_card
from services.data_provider import get_dashboard_metrics, get_agent_metrics, get_data_provider
from utils.helpers import format_number, format_percentage

# Page content
st.markdown('<h1 class="main-header">📊 Dashboard Overview</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Real-time fraud detection insights</p>', unsafe_allow_html=True)

# Check backend
provider = get_data_provider()
if not provider.backend_available:
    alert_box("⚠️ Backend unavailable. Showing demo data.", "warning")

# Load data
with st.spinner("Loading metrics..."):
    metrics = get_dashboard_metrics()
    agents = get_agent_metrics()

# KPI Cards
st.markdown("### 📈 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    kpi_card(
        title="Total Processed",
        value=metrics.get('total_processed', 0),
        format_type='number',
        delta=5.2,
        variant='primary'
    )

with col2:
    kpi_card(
        title="Accuracy",
        value=metrics.get('accuracy', 0),
        format_type='percentage',
        delta=2.1,
        variant='success'
    )

with col3:
    kpi_card(
        title="Fraud Prevented",
        value=metrics.get('fraud_prevented_usd', 0),
        format_type='currency',
        delta=12.3,
        variant='success'
    )

with col4:
    kpi_card(
        title="Avg Latency",
        value=metrics.get('avg_latency_ms', 0),
        format_type='number',
        delta=-8.5,
        variant='primary'
    )

st.divider()

# Secondary metrics
metric_card_group([
    {'title': 'Approved', 'value': format_number(metrics.get('total_approved', 0)), 'delta': '+3.2%'},
    {'title': 'Blocked', 'value': format_number(metrics.get('total_blocked', 0)), 'delta': '+15.8%'},
    {'title': 'Pending', 'value': format_number(metrics.get('total_pending', 0)), 'delta': '-5.1%'},
    {'title': 'Automation', 'value': format_percentage(metrics.get('automation_rate', 0)), 'delta': '+2.3%'}
])

st.divider()

# Charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Processing Volume")
    time_series = provider.get_time_series(30)
    if time_series:
        plot_time_series(time_series, "30-Day Trend", 350)

with col2:
    st.markdown("### 🎯 Risk Distribution")
    risk_dist = [
        {'risk_level': 'LOW', 'count': metrics.get('total_approved', 0), 'pct': 75},
        {'risk_level': 'MEDIUM', 'count': metrics.get('total_pending', 0), 'pct': 15},
        {'risk_level': 'HIGH', 'count': metrics.get('total_blocked', 0), 'pct': 10}
    ]
    plot_risk_distribution(risk_dist, "Risk Levels", 350)

st.divider()

# Quick actions
st.markdown("### ⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📄 Upload Invoice", use_container_width=True, type="primary"):
        st.switch_page("pages/2_📄_Upload.py")

with col2:
    if st.button("🚨 View Fraud Alerts", use_container_width=True):
        st.switch_page("pages/3_🚨_Fraud.py")

with col3:
    if st.button("📈 Observability", use_container_width=True):
        st.switch_page("pages/6_📈_Observability.py")