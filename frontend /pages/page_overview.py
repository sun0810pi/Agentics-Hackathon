from i18n import t
import streamlit as st
from services.data_provider import get_dashboard_metrics, get_agent_metrics, get_data_provider
from utils.helpers import format_currency, format_percentage, format_number
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd


@st.cache_data(ttl=60)
def _load():
    try:
        m  = get_dashboard_metrics()
        a  = get_agent_metrics()
        ts = get_data_provider().get_time_series(days=30)
        return {"ok": True, "m": m, "a": a, "ts": ts}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def render():
    from components.ui_helpers import (
        page_header, section_header, metric_card, divider, spacer, label_tag, is_dark
    )

    D   = is_dark()
    TPL = 'plotly_dark' if D else 'plotly_white'
    T   = '#f5f5f5' if D else '#0a0a0a'
    T2  = '#a3a3a3' if D else '#737373'
    ACC = '#10b981'

    data = _load()
    if not data["ok"]: st.error(f"❌ {data['error']}"); return
    m = data["m"]; ag = data["a"]; ts = data["ts"]

    if not get_data_provider().backend_available:
        st.warning(t("backend_demo"))
        spacer(".25rem")

    # ── Header ───────────────────────────────────────────────────
    page_header("📊", t("overview") if t("overview") != "overview" else "Dashboard Overview",
                f"Real-time fraud detection · {datetime.now().strftime('%b %d %Y, %H:%M')}")

    # ── KPI row ──────────────────────────────────────────────────
    label_tag(t("kpi_section"))
    c1,c2,c3,c4 = st.columns(4)
    metric_card(c1, t("total_processed"), f"{m.get('total_processed',0):,}", "+5.2%", True)
    metric_card(c2, t("accuracy"), f"{m.get('accuracy',0):.1f}%", "+2.1%", True)
    metric_card(c3, t("fraud_prevented"), format_currency(m.get('fraud_prevented_usd',0)), "+12.3%", True)
    metric_card(c4, t("avg_latency"), f"{m.get('avg_latency_ms',0):.0f}ms", "-8.5ms", True)

    spacer("1rem")
    label_tag(t("stats_section"))
    s1,s2,s3,s4 = st.columns(4)
    metric_card(s1, t("approved"),   format_number(m.get('total_approved',0)),   "+3.2%", True)
    metric_card(s2, t("blocked"),    format_number(m.get('total_blocked',0)),    "+15.8%", True)
    metric_card(s3, t("pending"),    format_number(m.get('total_pending',0)),    "-5.1%", False)
    metric_card(s4, t("automation"), format_percentage(m.get('automation_rate',0)), "+2.3%", True)

    spacer("1.25rem")
    divider()

    # ── Charts ───────────────────────────────────────────────────
    section_header("📈", "Transaction Analysis", "30-day processing volume & risk distribution")
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown(f'<div style="font-family:\'DM Sans\',sans-serif;font-size:.78rem;font-weight:600;color:{T2};margin-bottom:.3rem;">Processing Volume</div>', unsafe_allow_html=True)
        if ts:
            from components.charts import plot_time_series
            plot_time_series(data=ts, title="", height=290)
        else:
            st.info("No time series data available")
    with ch2:
        st.markdown(f'<div style="font-family:\'DM Sans\',sans-serif;font-size:.78rem;font-weight:600;color:{T2};margin-bottom:.3rem;">Risk Distribution</div>', unsafe_allow_html=True)
        from components.charts import plot_risk_distribution
        plot_risk_distribution(data=[
            {"risk_level":"LOW",   "count":m.get('total_approved',0), "pct":75.2},
            {"risk_level":"MEDIUM","count":m.get('total_pending',0),  "pct":12.8},
            {"risk_level":"HIGH",  "count":m.get('total_blocked',0),  "pct":12.0},
        ], title="", height=290)

    spacer(".75rem")
    divider()

    # ── Detection Performance ────────────────────────────────────
    section_header("🎯", "Detection Performance", "Accuracy trend & fraud type breakdown")
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(f'<div style="font-family:\'DM Sans\',sans-serif;font-size:.78rem;font-weight:600;color:{T2};margin-bottom:.3rem;">Accuracy Trend (7 Days)</div>', unsafe_allow_html=True)
        days = [(datetime.now()-timedelta(days=i)).strftime("%b %d") for i in range(6,-1,-1)]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=days, y=[95.2,96.1,97.3,96.8,97.6,98.1,98.3],
            mode='lines+markers', line=dict(color=ACC, width=2.5),
            marker=dict(size=6, color=ACC),
            fill='tozeroy', fillcolor='rgba(16,185,129,0.08)'))
        fig.update_layout(template=TPL, height=270, margin=dict(l=0,r=0,t=8,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(range=[94,100], ticksuffix='%'), hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    with p2:
        st.markdown(f'<div style="font-family:\'DM Sans\',sans-serif;font-size:.78rem;font-weight:600;color:{T2};margin-bottom:.3rem;">Fraud Type Breakdown</div>', unsafe_allow_html=True)
        ft = {'Identity Theft':35,'Account Takeover':25,'Synthetic Identity':18,'Card Fraud':12,'Other':10}
        fig2 = go.Figure(data=[go.Pie(
            labels=list(ft.keys()), values=list(ft.values()), hole=0.42,
            marker=dict(colors=[ACC,'#3b82f6','#f59e0b','#ef4444','#8b5cf6'])
        )])
        fig2.update_layout(template=TPL, height=270, margin=dict(l=0,r=0,t=8,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

    spacer(".75rem")
    divider()

    # ── Agent Status ─────────────────────────────────────────────
    section_header("🤖", "Agent Status", "Active ML agents monitoring the system")
    total=ag.get('total',17); active=ag.get('active',15)
    a1,a2,a3,a4 = st.columns(4)
    metric_card(a1, "Active Agents",    f"{active}/{total}",              f"{active/total*100:.1f}%", True)
    metric_card(a2, "Avg Confidence",   f"{ag.get('avg_confidence',0.94)*100:.1f}%", "+1.2%", True)
    metric_card(a3, "Alerts (24h)",     str(ag.get('alerts_24h',23)),     "+5",    True)

    BG2 = "#141414" if D else "#ffffff"
    BOR = "#262626" if D else "#e5e0da"
    with a4:
        st.markdown(f"""<div style="background:{BG2};border:2px solid {BOR};border-radius:12px;
padding:1rem 1.15rem .9rem;box-shadow:3px 3px 0px {'rgba(0,0,0,.35)' if D else 'rgba(0,0,0,.06)'};
position:relative;overflow:hidden;">
<div style="position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,{ACC},#34d399);"></div>
<div style="font-family:'DM Sans',sans-serif;font-size:.65rem;font-weight:700;
  color:{T2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.5rem;">Tier Summary</div>
<div style="font-family:'DM Sans',sans-serif;font-size:.8rem;color:{T};line-height:2;">
  🔵 Core: 8 &nbsp;&nbsp; 🟢 ML: 3<br>🟡 Merchant: 3 &nbsp; 🔴 Security: 3
</div></div>""", unsafe_allow_html=True)

    spacer(".75rem")
    divider()

    # ── Recent Alerts ────────────────────────────────────────────
    section_header("🚨", "Recent High-Priority Alerts")
    st.dataframe(pd.DataFrame([
        {"Time":"2 min ago",  "Type":"🔴 Account Takeover",  "Amount":"$12,450","Risk":"HIGH",  "Status":t("blocked")},
        {"Time":"15 min ago", "Type":"🟡 Suspicious Pattern","Amount":"$3,200", "Risk":"MEDIUM","Status":"Review"},
        {"Time":"32 min ago", "Type":"🔴 Identity Theft",    "Amount":"$8,900", "Risk":"HIGH",  "Status":t("blocked")},
        {"Time":"1 hr ago",   "Type":"🟡 Velocity Check",    "Amount":"$1,500", "Risk":"MEDIUM","Status":t("approved")},
        {"Time":"2 hrs ago",  "Type":"🔴 Card Fraud",        "Amount":"$5,670", "Risk":"HIGH",  "Status":t("blocked")},
    ]), use_container_width=True, hide_index=True)

    spacer(".75rem")
    divider()

    # ── System Health ────────────────────────────────────────────
    section_header("⚡", "System Health", "Latency percentiles & resource utilization")
    h1,h2,h3,h4 = st.columns(4)
    metric_card(h1, "P50 Latency",  "187ms",   "-8ms",    True)
    metric_card(h2, "P95 Latency",  "534ms",   "-15ms",   True)
    metric_card(h3, "P99 Latency",  "1.2s",    "-200ms",  True)
    metric_card(h4, "Throughput",   "450/min", "+25/min", True)

    spacer(".85rem")
    st.markdown(f'<div style="font-family:\'DM Sans\',sans-serif;font-size:.75rem;font-weight:600;color:{T2};margin-bottom:.4rem;">Resource Utilization</div>', unsafe_allow_html=True)
    st.progress(0.67, text="CPU: 67%")
    st.progress(0.52, text="Memory: 52%")
    st.progress(0.34, text="Network: 34%")
    spacer("1.5rem")
    st.caption("💡 Auto-refreshes every 60 seconds")
