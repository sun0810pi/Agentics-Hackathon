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
    IS_DARK = st.session_state.get('theme','dark') == 'dark'
    TPL  = 'plotly_dark' if IS_DARK else 'plotly_white'
    CLR  = {'p':'#3b82f6','c':'#06b6d4','g':'#10b981','y':'#f59e0b','r':'#ef4444','v':'#8b5cf6'}

    # CSS: fix the giant gap Streamlit adds between element groups
    st.markdown("""<style>
    /* Kill the massive gap Streamlit adds between vertical elements */
    [data-testid="stVerticalBlock"]>[data-testid="stVerticalBlock"] { gap:0!important; }
    [data-testid="stVerticalBlockBorderWrapper"] { padding:0!important; margin:0!important; }
    div[data-testid="stVerticalBlock"] { gap:0.5rem!important; }
    /* Column gap */
    div[data-testid="stHorizontalBlock"] { gap:0.75rem!important; align-items:stretch!important; }
    div[data-testid="stHorizontalBlock"]>[data-testid="stVerticalBlock"] { gap:0!important; }
    </style>""", unsafe_allow_html=True)

    provider = get_data_provider()
    data = _load()
    if not data["ok"]: st.error(f"❌ {data['error']}"); return
    m = data["m"]; ag = data["a"]; ts = data["ts"]

    if not provider.backend_available:
        st.warning("⚠️ Backend unavailable — showing demo data.")

    # ── HEADER ───────────────────────────────────────────────────
    st.title("📊 Dashboard Overview")
    st.caption(f"Real-time fraud detection insights · {datetime.now().strftime('%b %d %Y, %H:%M')}")

    st.markdown("---")

    # ── KPI ROW ──────────────────────────────────────────────────
    st.markdown("**🎯 Key Performance Indicators**")
    k1,k2,k3,k4 = st.columns(4, gap="medium")
    k1.metric("Total Processed", f"{m.get('total_processed',0):,}", "+5.2%")
    k2.metric("Accuracy",        f"{m.get('accuracy',0):.1f}%",     "+2.1%")
    k3.metric("Fraud Prevented", format_currency(m.get('fraud_prevented_usd',0)), "+12.3%")
    k4.metric("Avg Latency",     f"{m.get('avg_latency_ms',0):.0f}ms", "-8.5ms")

    st.markdown('<div style="height:1.25rem"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="height:0.25rem"></div>', unsafe_allow_html=True)

    # ── STATS ROW ────────────────────────────────────────────────
    st.markdown("**📈 Processing Statistics**")
    s1,s2,s3,s4 = st.columns(4, gap="medium")
    s1.metric("Approved",       format_number(m.get('total_approved',0)),  "+3.2%")
    s2.metric("Blocked",        format_number(m.get('total_blocked',0)),   "+15.8%")
    s3.metric("Pending",        format_number(m.get('total_pending',0)),   "-5.1%")
    s4.metric("Automation Rate",format_percentage(m.get('automation_rate',0)), "+2.3%")

    st.markdown('<div style="height:0.25rem"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="height:0.25rem"></div>', unsafe_allow_html=True)

    # ── CHARTS ───────────────────────────────────────────────────
    st.markdown("**📊 Transaction Analysis — 30 Days**")
    ch1, ch2 = st.columns(2, gap="large")

    with ch1:
        st.markdown("*Processing Volume*")
        if ts:
            from components.charts import plot_time_series
            plot_time_series(data=ts, title="Invoice Trend", height=320)
        else:
            st.info("No time series data available")

    with ch2:
        st.markdown("*Risk Distribution*")
        from components.charts import plot_risk_distribution
        plot_risk_distribution(data=[
            {"risk_level":"LOW",    "count":m.get('total_approved',0), "pct":75.2},
            {"risk_level":"MEDIUM", "count":m.get('total_pending',0),  "pct":12.8},
            {"risk_level":"HIGH",   "count":m.get('total_blocked',0),  "pct":12.0},
        ], title="Risk Scores", height=320)

    st.markdown("---")

    # ── DETECTION PERF ───────────────────────────────────────────
    st.markdown("**🎯 Detection Performance**")
    p1, p2 = st.columns(2, gap="large")

    with p1:
        st.markdown("*Accuracy Trend (7 Days)*")
        days = [(datetime.now()-timedelta(days=i)).strftime("%b %d") for i in range(6,-1,-1)]
        acc  = [95.2,96.1,97.3,96.8,97.6,98.1,98.3]
        fig  = go.Figure()
        fig.add_trace(go.Scatter(x=days, y=acc, mode='lines+markers',
            line=dict(color=CLR['p'], width=2.5), marker=dict(size=6),
            fill='tozeroy', fillcolor='rgba(59,130,246,0.08)'))
        fig.update_layout(template=TPL, height=300,
            margin=dict(l=0,r=0,t=10,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(range=[94,100], ticksuffix='%'), hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)

    with p2:
        st.markdown("*Fraud Types*")
        ftypes = {'Identity Theft':35,'Account Takeover':25,'Synthetic Identity':18,'Card Fraud':12,'Other':10}
        fig2 = go.Figure(data=[go.Pie(
            labels=list(ftypes.keys()), values=list(ftypes.values()), hole=0.42,
            marker=dict(colors=[CLR['p'],CLR['g'],CLR['y'],CLR['r'],CLR['v']]))])
        fig2.update_layout(template=TPL, height=300,
            margin=dict(l=0,r=0,t=10,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── AGENT STATUS ─────────────────────────────────────────────
    st.markdown("**🤖 Agent Status**")
    total = ag.get('total',17); active = ag.get('active',15)
    a1,a2,a3 = st.columns(3, gap="medium")
    a1.metric("Active Agents",   f"{active}/{total}", f"{active/total*100:.1f}%")
    a2.metric("Avg Confidence",  f"{ag.get('avg_confidence',0.94)*100:.1f}%", "+1.2%")
    a3.metric("Alerts (24h)",    str(ag.get('alerts_24h',23)), "+5")

    t1,t2,t3,t4 = st.columns(4, gap="medium")
    with t1: st.info("**Core Detection**\n8 agents")
    with t2: st.success("**ML Intelligence**\n3 agents")
    with t3: st.warning("**Merchant**\n3 agents")
    with t4: st.error("**Security**\n3 agents")

    st.markdown("---")

    # ── RECENT ALERTS ────────────────────────────────────────────
    st.markdown("**🚨 Recent High-Priority Alerts**")
    st.dataframe(pd.DataFrame([
        {"Time":"2 min ago", "Type":"🔴 Account Takeover","Amount":"$12,450","Risk":"HIGH","Status":"Blocked"},
        {"Time":"15 min ago","Type":"🟡 Suspicious Pattern","Amount":"$3,200","Risk":"MEDIUM","Status":"Review"},
        {"Time":"32 min ago","Type":"🔴 Identity Theft","Amount":"$8,900","Risk":"HIGH","Status":"Blocked"},
        {"Time":"1 hr ago",  "Type":"🟡 Velocity Check","Amount":"$1,500","Risk":"MEDIUM","Status":"Approved"},
        {"Time":"2 hrs ago", "Type":"🔴 Card Fraud","Amount":"$5,670","Risk":"HIGH","Status":"Blocked"},
    ]), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── SYSTEM HEALTH ────────────────────────────────────────────
    st.markdown("**⚡ System Health**")
    h1,h2,h3,h4 = st.columns(4, gap="medium")
    h1.metric("P50 Latency","187ms","-8ms")
    h2.metric("P95 Latency","534ms","-15ms")
    h3.metric("P99 Latency","1.2s","-200ms")
    h4.metric("Throughput","450/min","+25/min")

    st.markdown("**Resource Utilization**")
    st.progress(0.67, text="CPU: 67%")
    st.progress(0.52, text="Memory: 52%")
    st.progress(0.34, text="Network: 34%")

    st.caption("💡 Auto-refreshes every 60 seconds")
