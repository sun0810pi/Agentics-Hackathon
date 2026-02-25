import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.helpers import apply_theme
apply_theme()
if not st.session_state.get('logged_in', False):
    st.switch_page("app.py")
from components.sidebar import render_sidebar
try:
    render_sidebar()
except Exception as _e:
    st.sidebar.error(f"Sidebar: {_e}")

import logging
from components.metrics import metric_card_group, kpi_card
from components.charts import plot_time_series, plot_risk_distribution, plot_agent_performance
from components.widgets import alert_box, stat_card
from services.data_provider import get_dashboard_metrics, get_agent_metrics, get_data_provider
from utils.helpers import format_currency, format_percentage, format_number

logger = logging.getLogger(__name__)

@st.cache_data(ttl=60)
def load_dashboard_data():
    try:
        metrics = get_dashboard_metrics()
        agent_metrics = get_agent_metrics()
        provider = get_data_provider()
        time_series = provider.get_time_series(days=30)
        return {'success': True, 'metrics': metrics, 'agents': agent_metrics, 'time_series': time_series}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def show():
    st.markdown('<h1 class="main-header">📊 Dashboard Overview</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time fraud detection insights and analytics</p>', unsafe_allow_html=True)

    provider = get_data_provider()
    if not provider.backend_available:
        alert_box("⚠️ Backend unavailable. Showing demo data.", "warning")

    data = load_dashboard_data()
    if not data['success']:
        st.error(f"❌ Failed to load dashboard: {data.get('error')}")
        return

    metrics = data['metrics']
    agent_metrics = data['agents']
    time_series = data['time_series']

    st.markdown("### 📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card(title="Total Processed", value=metrics.get('total_processed', 0), format_type='number', delta=5.2, variant='primary')
    with col2:
        kpi_card(title="Accuracy Rate", value=metrics.get('accuracy', 0), format_type='percentage', delta=2.1, target=99.0, variant='success')
    with col3:
        kpi_card(title="Fraud Prevented", value=metrics.get('fraud_prevented_usd', 0), format_type='currency', delta=12.3, variant='success')
    with col4:
        kpi_card(title="Avg Latency", value=metrics.get('avg_latency_ms', 0), format_type='number', delta=-8.5, variant='primary')

    st.divider()
    metric_card_group([
        {'title': 'Approved', 'value': format_number(metrics.get('total_approved', 0)), 'delta': '+3.2%'},
        {'title': 'Blocked', 'value': format_number(metrics.get('total_blocked', 0)), 'delta': '+15.8%'},
        {'title': 'Pending Review', 'value': format_number(metrics.get('total_pending', 0)), 'delta': '-5.1%'},
        {'title': 'Automation Rate', 'value': format_percentage(metrics.get('automation_rate', 0)), 'delta': '+2.3%'},
    ])

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📊 Processing Volume (30 Days)")
        if time_series:
            plot_time_series(data=time_series, title="Invoice Processing Trend", height=350)
        else:
            st.info("No time series data available")
    with col2:
        st.markdown("### 🎯 Risk Distribution")
        plot_risk_distribution(data=[
            {'risk_level': 'LOW', 'count': metrics.get('total_approved', 0), 'pct': 75},
            {'risk_level': 'MEDIUM', 'count': metrics.get('total_pending', 0), 'pct': 15},
            {'risk_level': 'HIGH', 'count': metrics.get('total_blocked', 0), 'pct': 10},
        ], title="Risk Score Distribution", height=350)

try:
    show()
except Exception as e:
    import traceback
    st.error(f"❌ Page error: {e}")
    st.code(traceback.format_exc())
