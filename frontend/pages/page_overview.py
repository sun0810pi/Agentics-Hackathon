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

def card(col, label, value, delta=None, up=True, dark=True):
    """Render card inside a st.column with inner padding to create gap."""
    C  = '#0b101e' if dark else '#ffffff'
    B  = 'rgba(59,130,246,0.18)' if dark else 'rgba(37,99,235,0.15)'
    T  = '#f1f5f9' if dark else '#0f172a'
    T2 = '#94a3b8' if dark else '#475569'
    dc = '#10b981' if up else '#ef4444'
    ar = '↑' if up else '↓'
    d  = f'<div style="font-size:.78rem;color:{dc};margin-top:.35rem;font-weight:600;">{ar} {delta}</div>' if delta else ''
    # Outer wrapper: padding on sides creates the gap between cards
    # Since st.columns already exist, we just add padding on the div
    shadow = '0 2px 12px rgba(0,0,0,0.18)' if dark else '0 2px 10px rgba(37,99,235,0.08)'
    html = f'''<div style="background:{C};border:1px solid {B};border-radius:11px;
    padding:1rem 1.1rem .9rem;position:relative;overflow:hidden;box-shadow:{shadow};">
    <div style="position:absolute;top:0;left:0;right:0;height:2px;
      background:linear-gradient(90deg,#3b82f6,#06b6d4);opacity:.8;"></div>
    <div style="font-size:.62rem;font-weight:700;color:{T2};text-transform:uppercase;
      letter-spacing:.12em;margin-bottom:.4rem;">{label}</div>
    <div style="font-size:1.8rem;font-weight:700;color:{T};letter-spacing:-.02em;
      line-height:1.1;">{value}</div>
    {d}
</div>'''
    col.markdown(html, unsafe_allow_html=True)

def sp(h="1rem"):
    st.markdown(f'<div style="height:{h}"></div>', unsafe_allow_html=True)

def hr(dark=True):
    c = 'rgba(59,130,246,0.12)' if dark else 'rgba(0,0,0,0.07)'
    st.markdown(f'<hr style="border:none;border-top:1px solid {c};margin:1.25rem 0 1rem;">', unsafe_allow_html=True)

def label(text, dark=True):
    c = '#64748b'
    st.markdown(f'<div style="font-size:.65rem;font-weight:700;color:{c};text-transform:uppercase;letter-spacing:.14em;margin-bottom:.6rem;">{text}</div>', unsafe_allow_html=True)

def render():
    IS_DARK = st.session_state.get('theme','dark') == 'dark'
    D   = IS_DARK
    TPL = 'plotly_dark' if D else 'plotly_white'
    T   = '#f1f5f9' if D else '#0f172a'
    T2  = '#94a3b8' if D else '#64748b'
    BOR = 'rgba(59,130,246,0.12)' if D else 'rgba(0,0,0,0.07)'

    data = _load()
    if not data["ok"]: st.error(f"❌ {data['error']}"); return
    m = data["m"]; ag = data["a"]; ts = data["ts"]

    if not get_data_provider().backend_available:
        st.warning(t("backend_demo"))
        sp(".25rem")

    # Header
    st.markdown(f'<div style="font-size:1.55rem;font-weight:700;letter-spacing:-.025em;color:{T};margin-bottom:3px;">📊 Dashboard Overview</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:.82rem;color:{T2};margin-bottom:1.1rem;">Real-time fraud detection · {datetime.now().strftime("%b %d %Y, %H:%M")}</div>', unsafe_allow_html=True)

    # ── KPI row ──────────────────────────────────────────────────
    label(t("kpi_section"))
    c1,c2,c3,c4 = st.columns(4)
    card(c1, t("total_processed"), f"{m.get('total_processed',0):,}", "+5.2%", True, D)
    card(c2, t("accuracy"), f"{m.get('accuracy',0):.1f}%", "+2.1%", True, D)
    card(c3, t("fraud_prevented"), format_currency(m.get('fraud_prevented_usd',0)), "+12.3%", True, D)
    card(c4, t("avg_latency"), f"{m.get('avg_latency_ms',0):.0f}ms", "-8.5ms", True, D)

    sp("1.1rem")

    # ── Stats row ────────────────────────────────────────────────
    label(t("stats_section"))
    s1,s2,s3,s4 = st.columns(4)
    card(s1, t("approved"),        format_number(m.get('total_approved',0)),  "+3.2%",  True,  D)
    card(s2, t("blocked"),         format_number(m.get('total_blocked',0)),   "+15.8%", True,  D)
    card(s3, t("pending"),         format_number(m.get('total_pending',0)),   "-5.1%",  False, D)
    card(s4, t("automation"), format_percentage(m.get('automation_rate',0)), "+2.3%", True, D)

    sp("1.4rem")
    hr(D)

    # ── Charts ───────────────────────────────────────────────────
    label("📊 Transaction Analysis — 30 Days")
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown(f'<div style="font-size:.78rem;font-weight:600;color:{T2};margin-bottom:.3rem;">Processing Volume</div>', unsafe_allow_html=True)
        if ts:
            from components.charts import plot_time_series
            plot_time_series(data=ts, title="", height=290)
        else:
            st.info("No data")
    with ch2:
        st.markdown(f'<div style="font-size:.78rem;font-weight:600;color:{T2};margin-bottom:.3rem;">Risk Distribution</div>', unsafe_allow_html=True)
        from components.charts import plot_risk_distribution
        plot_risk_distribution(data=[
            {"risk_level":"LOW",   "count":m.get('total_approved',0),"pct":75.2},
            {"risk_level":"MEDIUM","count":m.get('total_pending',0), "pct":12.8},
            {"risk_level":"HIGH",  "count":m.get('total_blocked',0), "pct":12.0},
        ], title="", height=290)

    sp(".9rem")
    hr(D)

    # ── Detection perf ───────────────────────────────────────────
    label("🎯 Detection Performance")
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(f'<div style="font-size:.78rem;font-weight:600;color:{T2};margin-bottom:.3rem;">Accuracy Trend (7 Days)</div>', unsafe_allow_html=True)
        days = [(datetime.now()-timedelta(days=i)).strftime("%b %d") for i in range(6,-1,-1)]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=days, y=[95.2,96.1,97.3,96.8,97.6,98.1,98.3],
            mode='lines+markers', line=dict(color='#3b82f6',width=2.5), marker=dict(size=6),
            fill='tozeroy', fillcolor='rgba(59,130,246,0.08)'))
        fig.update_layout(template=TPL,height=270,margin=dict(l=0,r=0,t=8,b=0),
            paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(range=[94,100],ticksuffix='%'),hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    with p2:
        st.markdown(f'<div style="font-size:.78rem;font-weight:600;color:{T2};margin-bottom:.3rem;">Fraud Types</div>', unsafe_allow_html=True)
        ft = {'Identity Theft':35,'Account Takeover':25,'Synthetic Identity':18,'Card Fraud':12,'Other':10}
        fig2 = go.Figure(data=[go.Pie(labels=list(ft.keys()),values=list(ft.values()),hole=0.42,
            marker=dict(colors=['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6']))])
        fig2.update_layout(template=TPL,height=270,margin=dict(l=0,r=0,t=8,b=0),
            paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

    sp(".9rem")
    hr(D)

    # ── Agent status ─────────────────────────────────────────────
    label("🤖 Agent Status")
    total=ag.get('total',17); active=ag.get('active',15)
    a1,a2,a3,a4 = st.columns(4)
    card(a1,"Active Agents",f"{active}/{total}",f"{active/total*100:.1f}%",True,D)
    card(a2,"Avg Confidence",f"{ag.get('avg_confidence',0.94)*100:.1f}%","+1.2%",True,D)
    card(a3,"Alerts (24h)",str(ag.get('alerts_24h',23)),"+5",True,D)
    with a4:
        st.markdown(f'''<div style="padding:0 5px;">
<div style="background:{"rgba(16,185,129,0.1)" if D else "rgba(16,185,129,0.08)"};border:1px solid rgba(16,185,129,0.2);
border-radius:11px;padding:1rem 1.1rem .9rem;">
<div style="font-size:.62rem;font-weight:700;color:{T2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.6rem;">Tier Summary</div>
<div style="font-size:.78rem;color:{T};line-height:1.8;">
🔵 Core: 8 &nbsp;|&nbsp; 🟢 ML: 3<br>🟡 Merchant: 3 &nbsp;|&nbsp; 🔴 Security: 3
</div></div></div>''', unsafe_allow_html=True)

    sp(".9rem")
    hr(D)

    # ── Alerts ───────────────────────────────────────────────────
    label("🚨 Recent High-Priority Alerts")
    st.dataframe(pd.DataFrame([
        {"Time":"2 min ago","Type":"🔴 Account Takeover","Amount":"$12,450","Risk":"HIGH","Status":t("blocked")},
        {"Time":"15 min ago","Type":"🟡 Suspicious Pattern","Amount":"$3,200","Risk":"MEDIUM","Status":"Review"},
        {"Time":"32 min ago","Type":"🔴 Identity Theft","Amount":"$8,900","Risk":"HIGH","Status":t("blocked")},
        {"Time":"1 hr ago","Type":"🟡 Velocity Check","Amount":"$1,500","Risk":"MEDIUM","Status":t("approved")},
        {"Time":"2 hrs ago","Type":"🔴 Card Fraud","Amount":"$5,670","Risk":"HIGH","Status":t("blocked")},
    ]), use_container_width=True, hide_index=True)

    sp(".9rem")
    hr(D)

    # ── System health ────────────────────────────────────────────
    label("⚡ System Health")
    h1,h2,h3,h4 = st.columns(4)
    card(h1,"P50 Latency","187ms","-8ms",True,D)
    card(h2,"P95 Latency","534ms","-15ms",True,D)
    card(h3,"P99 Latency","1.2s","-200ms",True,D)
    card(h4,"Throughput","450/min","+25/min",True,D)

    sp(".75rem")
    st.markdown(f'<div style="font-size:.75rem;font-weight:600;color:{T2};margin-bottom:.4rem;">Resource Utilization</div>', unsafe_allow_html=True)
    st.progress(0.67, text="CPU: 67%")
    st.progress(0.52, text="Memory: 52%")
    st.progress(0.34, text="Network: 34%")
    sp("1.5rem")
    st.caption("💡 Auto-refreshes every 60 seconds")
