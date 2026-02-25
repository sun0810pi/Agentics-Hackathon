import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Step 1: theme
try:
    from utils.helpers import apply_theme
    apply_theme()
except Exception as e:
    st.error(f"Theme error: {e}")

# Step 2: login guard
if not st.session_state.get('logged_in', False):
    st.switch_page("app.py")

# Step 3: sidebar
try:
    from components.sidebar import render_sidebar
    render_sidebar()
except Exception as e:
    st.sidebar.error(f"Sidebar: {e}")

# Step 4: FORCE VISIBLE content - no matter what
st.title("📊 Dashboard Overview")
st.success("✅ Page loaded successfully!")
st.write(f"Logged in as: **{st.session_state.get('user_name', '?')}** ({st.session_state.get('user_role', '?')})")

# Step 5: load data safely
try:
    from services.data_provider import get_dashboard_metrics, get_data_provider
    provider = get_data_provider()
    if not provider.backend_available:
        st.warning("⚠️ Backend unavailable — showing demo data.")
    
    metrics = get_dashboard_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Processed", f"{metrics.get('total_processed', 0):,}")
    col2.metric("Accuracy", f"{metrics.get('accuracy', 0):.1f}%")
    col3.metric("Fraud Prevented", f"${metrics.get('fraud_prevented_usd', 0):,.0f}")
    col4.metric("Avg Latency", f"{metrics.get('avg_latency_ms', 0):.0f}ms")

except Exception as e:
    import traceback
    st.error(f"Data error: {e}")
    st.code(traceback.format_exc())

# Step 6: charts
try:
    from components.metrics import metric_card_group
    from components.charts import plot_time_series, plot_risk_distribution
    from services.data_provider import get_data_provider

    provider = get_data_provider()
    time_series = provider.get_time_series(days=30)
    metrics = get_dashboard_metrics()

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📊 Processing Volume (30 Days)")
        if time_series:
            plot_time_series(data=time_series, title="Invoice Processing Trend", height=350)
        else:
            st.info("No time series data")

    with col2:
        st.markdown("### 🎯 Risk Distribution")
        risk_dist = [
            {'risk_level': 'LOW',    'count': metrics.get('total_approved', 0), 'pct': 75},
            {'risk_level': 'MEDIUM', 'count': metrics.get('total_pending', 0),  'pct': 15},
            {'risk_level': 'HIGH',   'count': metrics.get('total_blocked', 0),  'pct': 10},
        ]
        plot_risk_distribution(data=risk_dist, title="Risk Score Distribution", height=350)

except Exception as e:
    import traceback
    st.error(f"Charts error: {e}")
    st.code(traceback.format_exc())

# Navigation
st.divider()
st.markdown("### ⚡ Quick Actions")
c1, c2, c3 = st.columns(3)
c1.markdown('<a href="/Upload" target="_self"><button style="width:100%;padding:0.5rem;background:#4A9EFF;color:white;border:none;border-radius:8px;cursor:pointer;">📄 Upload Invoice</button></a>', unsafe_allow_html=True)
c2.markdown('<a href="/Fraud" target="_self"><button style="width:100%;padding:0.5rem;background:rgba(255,255,255,0.1);color:inherit;border:1px solid rgba(255,255,255,0.2);border-radius:8px;cursor:pointer;">🚨 Fraud Alerts</button></a>', unsafe_allow_html=True)
c3.markdown('<a href="/Observability" target="_self"><button style="width:100%;padding:0.5rem;background:rgba(255,255,255,0.1);color:inherit;border:1px solid rgba(255,255,255,0.2);border-radius:8px;cursor:pointer;">📈 Observability</button></a>', unsafe_allow_html=True)
