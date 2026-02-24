import streamlit as st
from utils.helpers import apply_theme
apply_theme()
from components.metrics import metric_card_group, kpi_card
from components.charts import (
    plot_time_series,
    plot_risk_distribution,
    plot_agent_performance
)
from components.widgets import alert_box, stat_card
from services.data_provider import (
    get_dashboard_metrics,
    get_agent_metrics,
    get_data_provider
)
from utils.helpers import format_currency, format_percentage, format_number
import logging

logger = logging.getLogger(__name__)

# ========================================
# CACHED DATA LOADERS (Performance boost!)
# ========================================

@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_dashboard_data():
    """Load dashboard metrics with caching"""
    try:
        metrics = get_dashboard_metrics()
        agent_metrics = get_agent_metrics()
        provider = get_data_provider()
        time_series = provider.get_time_series(days=30)
        
        return {
            'success': True,
            'metrics': metrics,
            'agents': agent_metrics,
            'time_series': time_series
        }
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return {
            'success': False,
            'error': str(e)
        }


# ========================================
# MAIN PAGE
# ========================================

def show():
    """Render overview dashboard page - OPTIMIZED"""
    
    # Page header
    st.markdown('<h1 style="font-size: 2.5rem; font-weight: 900; margin-bottom: 0.5rem;">📊 Dashboard Overview</h1>', unsafe_allow_html=True)
    st.markdown('<p style="opacity: 0.7; font-size: 1.125rem; margin-bottom: 2rem;">Real-time fraud detection insights and analytics</p>', unsafe_allow_html=True)
    
    # Check backend status
    provider = get_data_provider()
    if not provider.backend_available:
        alert_box(
            "⚠️ Backend unavailable. Showing demo data. Enable backend in Settings for real data.",
            "warning"
        )
    
    # Load data (CACHED!)
    data = load_dashboard_data()
    
    if not data['success']:
        st.error(f"❌ Failed to load dashboard: {data.get('error')}")
        st.stop()
    
    metrics = data['metrics']
    agent_metrics = data['agents']
    time_series = data['time_series']
    
    # Top KPI Cards
    st.markdown("### 📈 Key Performance Indicators")
    
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
            title="Accuracy Rate",
            value=metrics.get('accuracy', 0),
            format_type='percentage',
            delta=2.1,
            target=99.0,
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
    
    # Secondary Metrics Row
    metric_card_group([
        {
            'title': 'Approved',
            'value': format_number(metrics.get('total_approved', 0)),
            'delta': '+3.2%'
        },
        {
            'title': 'Blocked',
            'value': format_number(metrics.get('total_blocked', 0)),
            'delta': '+15.8%'
        },
        {
            'title': 'Pending Review',
            'value': format_number(metrics.get('total_pending', 0)),
            'delta': '-5.1%'
        },
        {
            'title': 'Automation Rate',
            'value': format_percentage(metrics.get('automation_rate', 0)),
            'delta': '+2.3%'
        }
    ])
    
    st.divider()
    
    # Charts Section (Lazy load)
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Processing Volume (30 Days)")
            if time_series:
                plot_time_series(
                    data=time_series,
                    title="Invoice Processing Trend",
                    height=350
                )
            else:
                st.info("No time series data available")
        
        with col2:
            st.markdown("### 🎯 Risk Distribution")
            risk_dist = [
                {'risk_level': 'LOW', 'count': metrics.get('total_approved', 0), 'pct': 75},
                {'risk_level': 'MEDIUM', 'count': metrics.get('total_pending', 0), 'pct': 15},
                {'risk_level': 'HIGH', 'count': metrics.get('total_blocked', 0), 'pct': 10}
            ]
            plot_risk_distribution(
                data=risk_dist,
                title="Risk Score Distribution",
                height=350
            )
    
    st.divider()
    
    # Agent Performance (Collapsed by default for performance)
    with st.expander("🤖 Agent Performance", expanded=False):
        if agent_metrics:
            # Show top 8 agents (Tier 1)
            tier1_agents = [a for a in agent_metrics if a.get('id', 0) <= 7]
            
            if tier1_agents:
                plot_agent_performance(
                    agents=tier1_agents,
                    title="Tier 1 Core Detection Agents",
                    height=400
                )
            
            # Agent status summary
            st.markdown("#### Agent Status Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            total_agents = len(agent_metrics)
            healthy_agents = sum(1 for a in agent_metrics if a.get('status') == 'active')
            avg_success = sum(a.get('success_rate', 0) for a in agent_metrics) / total_agents if total_agents > 0 else 0
            avg_latency = sum(a.get('avg_latency_ms', 0) for a in agent_metrics) / total_agents if total_agents > 0 else 0
            
            with col1:
                stat_card(
                    label="Total Agents",
                    value=total_agents,
                    icon="🤖",
                    trend=None
                )
            
            with col2:
                stat_card(
                    label="Healthy",
                    value=healthy_agents,
                    icon="✅",
                    trend=f"{(healthy_agents/total_agents*100):.0f}%",
                    trend_positive=True
                )
            
            with col3:
                stat_card(
                    label="Avg Success Rate",
                    value=f"{avg_success:.1f}%",
                    icon="🎯",
                    trend="+2.3%",
                    trend_positive=True
                )
            
            with col4:
                stat_card(
                    label="Avg Latency",
                    value=f"{avg_latency:.0f}ms",
                    icon="⚡",
                    trend="-12ms",
                    trend_positive=True
                )
        
        else:
            st.info("No agent metrics available")
    
    st.divider()
    
    # Quick Actions
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
    
    # Footer
    import datetime
    st.caption(f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# Call main function
show()