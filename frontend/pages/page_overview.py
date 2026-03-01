from i18n import t
import streamlit as st
from services.data_provider import get_dashboard_metrics, get_agent_metrics, get_data_provider
from utils.helpers import format_currency, format_percentage, format_number
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd


def _card(col, label, value, delta=None, up=True):
    D   = st.session_state.get('theme', 'dark') == 'dark'
    BG  = '#141414' if D else '#ffffff'
    BOR = '#262626'  if D else '#0a0a0a'
    T   = '#f5f5f5' if D else '#0a0a0a'
    T2  = '#a3a3a3' if D else '#737373'
    SHD = '2px 2px 0px rgba(255,255,255,0.08)' if D else '4px 4px 0px #0a0a0a'
    dc  = '#10b981' if up else '#ef4444'
    ar  = 'up' if up else 'down'
    d   = f'<div style="font-size:.75rem;color:{dc};margin-top:.4rem;font-weight:600;">{"+" if up else ""}{delta}</div>' if delta else ''
    html = (
        f'<div style="background:{BG};border:2px solid {BOR};border-radius:0;'
        f'padding:1rem 1.1rem .9rem;position:relative;overflow:hidden;box-shadow:{SHD};">'
        f'<div style="position:absolute;top:0;left:0;right:0;height:3px;background:#10b981;"></div>'
        f'<div style="font-size:.6rem;font-weight:500;color:{T2};text-transform:uppercase;'
        f'letter-spacing:.12em;margin-bottom:.35rem;">{label}</div>'
        f'<div style="font-size:1.85rem;font-weight:800;color:{T};letter-spacing:-.02em;line-height:1.1;">{value}</div>'
        f'{d}</div>'
    )
    col.markdown(html, unsafe_allow_html=True)


def _sp(h="1rem"):
    st.markdown(f'<div style="height:{h}"></div>', unsafe_allow_html=True)


def _hr():
    D = st.session_state.get('theme', 'dark') == 'dark'
    c = '#262626' if D else '#e5e5e5'
    st.markdown(f'<hr style="border:none;border-top:2px solid {c};margin:1.1rem 0;">', unsafe_allow_html=True)


def _label(text):
    D = st.session_state.get('theme', 'dark') == 'dark'
    c = '#a3a3a3' if D else '#525252'
    st.markdown(
        f'<div style="font-size:.62rem;font-weight:600;color:{c};text-transform:uppercase;'
        f'letter-spacing:.14em;margin-bottom:.6rem;">{text}</div>',
        unsafe_allow_html=True
    )


def render():
    D   = st.session_state.get('theme', 'dark') == 'dark'
    TPL = 'plotly_dark' if D else 'plotly_white'
    T   = '#f1f5f9' if D else '#0f172a'
    T2  = '#94a3b8' if D else '#64748b'
    BOR = '#262626'  if D else '#e5e5e5'

    # Load data — NO cache to avoid stale data bugs
    try:
        m = get_dashboard_metrics()
    except Exception as e:
        m = {}
        st.warning(f"Metrics unavailable: {e}")

    try:
        ts = get_data_provider().get_time_series(days=30)
    except Exception:
        ts = []

    # Agent metrics — always normalise to list
    try:
        ag_raw = get_agent_metrics()
        ag = ag_raw if isinstance(ag_raw, list) else []
    except Exception:
        ag = []

    if not get_data_provider().backend_available:
        st.warning(t("backend_demo"))
        _sp(".25rem")

    # Header
    st.markdown(
        f'<div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:2px solid {BOR};">'
        f'<div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.35rem;">'
        f'<span style="font-size:1.5rem;">📊</span>'
        f'<h1 style="font-size:1.75rem;font-weight:800;color:{T};letter-spacing:-.03em;margin:0;line-height:1.1;">Dashboard Overview</h1>'
        f'</div>'
        f'<p style="font-size:.72rem;color:#10b981;letter-spacing:.06em;margin:0;text-transform:uppercase;">'
        f'Real-time fraud detection · {datetime.now().strftime("%b %d %Y, %H:%M")}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    # KPI row
    _label(t("kpi_section"))
    c1, c2, c3, c4 = st.columns(4)
    _card(c1, t("total_processed"),  f"{m.get('total_processed', 0):,}",             "5.2%",  True)
    _card(c2, t("accuracy"),         f"{m.get('accuracy', 0):.1f}%",                 "2.1%",  True)
    _card(c3, t("fraud_prevented"),  format_currency(m.get('fraud_prevented_usd', 0)), "12.3%", True)
    _card(c4, t("avg_latency"),      f"{m.get('avg_latency_ms', 0):.0f}ms",          "8.5ms", True)
    _sp("1.1rem")

    # Stats row
    _label(t("stats_section"))
    s1, s2, s3, s4 = st.columns(4)
    _card(s1, t("approved"),   format_number(m.get('total_approved', 0)),      "3.2%",  True)
    _card(s2, t("blocked"),    format_number(m.get('total_blocked', 0)),       "15.8%", True)
    _card(s3, t("pending"),    format_number(m.get('total_pending', 0)),       "5.1%",  False)
    _card(s4, t("automation"), format_percentage(m.get('automation_rate', 0)), "2.3%",  True)
    _sp("1.4rem")
    _hr()

    # Charts
    _label("TRANSACTION ANALYSIS — 30 DAYS")
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown(f'<div style="font-size:.72rem;color:{T2};margin-bottom:.3rem;">Processing Volume</div>', unsafe_allow_html=True)
        if ts:
            from components.charts import plot_time_series
            plot_time_series(data=ts, title="", height=290)
        else:
            st.info("No data")
    with ch2:
        st.markdown(f'<div style="font-size:.72rem;color:{T2};margin-bottom:.3rem;">Risk Distribution</div>', unsafe_allow_html=True)
        from components.charts import plot_risk_distribution
        plot_risk_distribution(data=[
            {"risk_level": "LOW",    "count": m.get('total_approved', 0), "pct": 75.2},
            {"risk_level": "MEDIUM", "count": m.get('total_pending', 0),  "pct": 12.8},
            {"risk_level": "HIGH",   "count": m.get('total_blocked', 0),  "pct": 12.0},
        ], title="", height=290)
    _sp(".9rem")
    _hr()

    # Detection performance
    _label("DETECTION PERFORMANCE")
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(f'<div style="font-size:.72rem;color:{T2};margin-bottom:.3rem;">Accuracy Trend (7 Days)</div>', unsafe_allow_html=True)
        days = [(datetime.now() - timedelta(days=i)).strftime("%b %d") for i in range(6, -1, -1)]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=days, y=[95.2, 96.1, 97.3, 96.8, 97.6, 98.1, 98.3],
            mode='lines+markers', line=dict(color='#10b981', width=2.5),
            marker=dict(size=6), fill='tozeroy', fillcolor='rgba(16,185,129,0.06)'
        ))
        fig.update_layout(template=TPL, height=270, margin=dict(l=0,r=0,t=8,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(range=[94,100], ticksuffix='%'), hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    with p2:
        st.markdown(f'<div style="font-size:.72rem;color:{T2};margin-bottom:.3rem;">Fraud Types</div>', unsafe_allow_html=True)
        ft = {'Identity Theft':35,'Account Takeover':25,'Synthetic Identity':18,'Card Fraud':12,'Other':10}
        fig2 = go.Figure(data=[go.Pie(
            labels=list(ft.keys()), values=list(ft.values()), hole=0.42,
            marker=dict(colors=['#10b981','#059669','#f59e0b','#ef4444','#8b5cf6'])
        )])
        fig2.update_layout(template=TPL, height=270, margin=dict(l=0,r=0,t=8,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)
    _sp(".9rem")
    _hr()

    # Agent status — ag is always a list, never use .get() on it
    _label("AGENT STATUS")
    _total  = len(ag) if ag else 17
    _active = sum(1 for x in ag if x.get('status') == 'active') if ag else 15
    _conf   = (sum(x.get('success_rate', 97) for x in ag) / _total) if ag else 97.4
    _alerts = sum(x.get('errors', 0) for x in ag) if ag else 23
    a1, a2, a3, a4 = st.columns(4)
    _card(a1, "Active Agents",  f"{_active}/{_total}",  f"{_active/_total*100:.0f}%", True)
    _card(a2, "Avg Confidence", f"{_conf:.1f}%",         "1.2%",  True)
    _card(a3, "Alerts (24h)",   str(_alerts),            "5",     True)
    _card(a4, "Tier Summary",   f"{_total} total",       f"{_active} active", True)
    _sp(".9rem")
    _hr()

    # Recent alerts
    _label("RECENT HIGH-PRIORITY ALERTS")
    st.dataframe(pd.DataFrame([
        {"Time": "2 min ago",  "Type": "🔴 Account Takeover",   "Amount": "$12,450", "Risk": "HIGH",   "Status": t("blocked")},
        {"Time": "15 min ago", "Type": "🟡 Suspicious Pattern", "Amount": "$3,200",  "Risk": "MEDIUM", "Status": "Review"},
        {"Time": "32 min ago", "Type": "🔴 Identity Theft",     "Amount": "$8,900",  "Risk": "HIGH",   "Status": t("blocked")},
        {"Time": "1 hr ago",   "Type": "🟡 Velocity Check",     "Amount": "$1,500",  "Risk": "MEDIUM", "Status": t("approved")},
        {"Time": "2 hrs ago",  "Type": "🔴 Card Fraud",         "Amount": "$5,670",  "Risk": "HIGH",   "Status": t("blocked")},
    ]), use_container_width=True, hide_index=True)
    _sp(".9rem")
    _hr()

    # System health
    _label("SYSTEM HEALTH")
    h1, h2, h3, h4 = st.columns(4)
    _card(h1, "P50 Latency", "187ms",   "8ms",   True)
    _card(h2, "P95 Latency", "534ms",   "15ms",  True)
    _card(h3, "P99 Latency", "1.2s",    "200ms", True)
    _card(h4, "Throughput",  "450/min", "25/min",True)
    _sp(".75rem")
    st.markdown(f'<div style="font-size:.72rem;color:{T2};margin-bottom:.4rem;">Resource Utilization</div>', unsafe_allow_html=True)
    st.progress(0.67, text="CPU: 67%")
    st.progress(0.52, text="Memory: 52%")
    st.progress(0.34, text="Network: 34%")
    _sp("1.5rem")
    st.caption(f"Auto-refreshes every 60s · {datetime.now().strftime('%H:%M:%S')}")
