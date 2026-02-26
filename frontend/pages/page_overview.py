import streamlit as st
from components.metrics import metric_card_group, kpi_card
from components.charts import plot_time_series, plot_risk_distribution
from components.widgets import alert_box
from services.data_provider import get_dashboard_metrics, get_agent_metrics, get_data_provider
from utils.helpers import format_currency, format_percentage, format_number

@st.cache_data(ttl=60)
def _load():
    try:
        metrics = get_dashboard_metrics()
        agents = get_agent_metrics()
        ts = get_data_provider().get_time_series(days=30)
        return {"ok": True, "metrics": metrics, "agents": agents, "ts": ts}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def render():
    st.title("📊 Dashboard Overview")
    st.caption("Real-time fraud detection insights")

    provider = get_data_provider()
    if not provider.backend_available:
        st.warning("⚠️ Backend unavailable — showing demo data.")

    data = _load()
    if not data["ok"]:
        st.error(f"Failed to load: {data['error']}"); return

    m = data["metrics"]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Processed", f"{m.get('total_processed',0):,}")
    col2.metric("Accuracy", f"{m.get('accuracy',0):.1f}%", "+2.1%")
    col3.metric("Fraud Prevented", f"${m.get('fraud_prevented_usd',0):,.0f}")
    col4.metric("Avg Latency", f"{m.get('avg_latency_ms',0):.0f}ms")

    st.divider()
    c1, c2 = st.columns(4), st.columns(4)
    metric_card_group([
        {"title":"Approved","value":format_number(m.get('total_approved',0)),"delta":"+3.2%"},
        {"title":"Blocked","value":format_number(m.get('total_blocked',0)),"delta":"+15.8%"},
        {"title":"Pending","value":format_number(m.get('total_pending',0)),"delta":"-5.1%"},
        {"title":"Automation","value":format_percentage(m.get('automation_rate',0)),"delta":"+2.3%"},
    ])

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Processing Volume (30 Days)")
        if data["ts"]:
            plot_time_series(data=data["ts"], title="Invoice Trend", height=350)
        else:
            st.info("No time series data")
    with col2:
        st.subheader("🎯 Risk Distribution")
        plot_risk_distribution(data=[
            {"risk_level":"LOW","count":m.get('total_approved',0),"pct":75},
            {"risk_level":"MEDIUM","count":m.get('total_pending',0),"pct":15},
            {"risk_level":"HIGH","count":m.get('total_blocked',0),"pct":10},
        ], title="Risk Scores", height=350)
