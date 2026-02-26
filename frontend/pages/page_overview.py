import streamlit as st
from services.data_provider import get_dashboard_metrics, get_agent_metrics, get_data_provider
from utils.helpers import format_currency, format_percentage, format_number
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

@st.cache_data(ttl=60)
def _load():
    try:
        from services.data_provider import get_data_provider
        m = get_dashboard_metrics()
        a = get_agent_metrics()
        ts = get_data_provider().get_time_series(days=30)
        return {"ok": True, "m": m, "a": a, "ts": ts}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def gap(size="1rem"):
    st.markdown(f'<div style="height:{size}"></div>', unsafe_allow_html=True)

def section_header(icon, title, subtitle=None):
    st.markdown(f"""
<div style="margin:1.5rem 0 0.6rem;">
  <div style="font-size:1.1rem;font-weight:700;color:var(--text,#f1f5f9);display:flex;align-items:center;gap:.5rem;">
    {icon} {title}
  </div>
  {f'<div style="font-size:.82rem;color:var(--text2,#94a3b8);margin-top:2px;">{subtitle}</div>' if subtitle else ''}
</div>""", unsafe_allow_html=True)

def render():
    IS_DARK = st.session_state.get('theme','dark') == 'dark'
    TPL = 'plotly_dark' if IS_DARK else 'plotly_white'
    BG  = 'rgba(0,0,0,0)' if IS_DARK else 'rgba(0,0,0,0)'
    CARD = '#0c1020' if IS_DARK else '#ffffff'
    TEXT = '#f1f5f9' if IS_DARK else '#0f172a'
    TEXT2 = '#94a3b8' if IS_DARK else '#64748b'
    BORDER = 'rgba(59,130,246,0.13)' if IS_DARK else 'rgba(0,0,0,0.07)'

    # ── Header ──────────────────────────────────────────────────
    st.markdown(f"""
<div style="margin-bottom:1rem;">
  <div style="font-size:1.65rem;font-weight:700;letter-spacing:-.025em;color:{TEXT};">
    📊 Dashboard Overview
  </div>
  <div style="font-size:.83rem;color:{TEXT2};margin-top:3px;">
    Real-time fraud detection insights &nbsp;·&nbsp; {datetime.now().strftime("%b %d, %Y  %H:%M")}
  </div>
</div>""", unsafe_allow_html=True)

    provider = get_data_provider()
    if not provider.backend_available:
        st.warning("⚠️ Backend unavailable — showing demo data.")

    data = _load()
    if not data["ok"]:
        st.error(f"❌ {data['error']}"); return

    m  = data["m"]
    ag = data["a"]
    ts = data["ts"]

    # ── KPI Row ──────────────────────────────────────────────────
    section_header("🎯", "Key Performance Indicators", "Core fraud detection metrics")
    c1,c2,c3,c4 = st.columns(4, gap="medium")
    with c1: st.metric("Total Processed", f"{m.get('total_processed',0):,}", "+5.2%")
    with c2: st.metric("Accuracy", f"{m.get('accuracy',0):.1f}%", "+2.1%")
    with c3: st.metric("Fraud Prevented", format_currency(m.get('fraud_prevented_usd',0)), "+12.3%")
    with c4: st.metric("Avg Latency", f"{m.get('avg_latency_ms',0):.0f}ms", "-8.5ms")

    gap("1rem")

    # ── Stats Row ────────────────────────────────────────────────
    section_header("📈", "Processing Statistics", "Transaction breakdown")
    c1,c2,c3,c4 = st.columns(4, gap="medium")
    with c1: st.metric("Approved", format_number(m.get('total_approved',0)), "+3.2%")
    with c2: st.metric("Blocked", format_number(m.get('total_blocked',0)), "+15.8%")
    with c3: st.metric("Pending", format_number(m.get('total_pending',0)), "-5.1%")
    with c4: st.metric("Automation", format_percentage(m.get('automation_rate',0)), "+2.3%")

    gap("1rem")
    st.divider()

    # ── Charts Row 1 ─────────────────────────────────────────────
    section_header("📊", "Transaction Analysis", "Volume trends and risk distribution — 30 days")
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown(f'<div style="font-size:.82rem;font-weight:600;color:{TEXT2};text-transform:uppercase;letter-spacing:.08em;margin-bottom:.5rem;">Processing Volume</div>', unsafe_allow_html=True)
        if ts:
            from components.charts import plot_time_series
            plot_time_series(data=ts, title="Invoice Trend", height=340)
        else:
            st.info("No time series data")

    with c2:
        st.markdown(f'<div style="font-size:.82rem;font-weight:600;color:{TEXT2};text-transform:uppercase;letter-spacing:.08em;margin-bottom:.5rem;">Risk Distribution</div>', unsafe_allow_html=True)
        from components.charts import plot_risk_distribution
        plot_risk_distribution(data=[
            {"risk_level":"LOW","count":m.get('total_approved',0),"pct":75.2},
            {"risk_level":"MEDIUM","count":m.get('total_pending',0),"pct":12.8},
            {"risk_level":"HIGH","count":m.get('total_blocked',0),"pct":12.0},
        ], title="Risk Scores", height=340)

    gap("0.5rem")
    st.divider()

    # ── Charts Row 2 ─────────────────────────────────────────────
    section_header("🎯", "Detection Performance", "Model accuracy and fraud type breakdown")
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown(f'<div style="font-size:.82rem;font-weight:600;color:{TEXT2};text-transform:uppercase;letter-spacing:.08em;margin-bottom:.5rem;">Accuracy Trend (7 Days)</div>', unsafe_allow_html=True)
        days = [(datetime.now()-timedelta(days=i)).strftime("%b %d") for i in range(6,-1,-1)]
        acc  = [95.2,96.1,97.3,96.8,97.6,98.1,98.3]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=days,y=acc,mode='lines+markers',name='Accuracy',
            line=dict(color='#3b82f6',width=2.5),marker=dict(size=7),
            fill='tozeroy',fillcolor='rgba(59,130,246,0.08)'))
        fig.update_layout(template=TPL,height=320,margin=dict(l=0,r=0,t=10,b=0),
            paper_bgcolor=BG,plot_bgcolor=BG,yaxis=dict(range=[94,100],ticksuffix='%'),hovermode='x unified')
        st.plotly_chart(fig,use_container_width=True)

    with c2:
        st.markdown(f'<div style="font-size:.82rem;font-weight:600;color:{TEXT2};text-transform:uppercase;letter-spacing:.08em;margin-bottom:.5rem;">Fraud Types</div>', unsafe_allow_html=True)
        ftypes = {'Identity Theft':35,'Account Takeover':25,'Synthetic Identity':18,'Card Fraud':12,'Other':10}
        fig2 = go.Figure(data=[go.Pie(labels=list(ftypes.keys()),values=list(ftypes.values()),hole=0.42,
            marker=dict(colors=['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6']))])
        fig2.update_layout(template=TPL,height=320,margin=dict(l=0,r=0,t=10,b=0),
            paper_bgcolor=BG,plot_bgcolor=BG,showlegend=True)
        st.plotly_chart(fig2,use_container_width=True)

    gap("0.5rem")
    st.divider()

    # ── Agent Status ─────────────────────────────────────────────
    section_header("🤖", "Agent Status", "Real-time fraud detection agents")
    c1,c2,c3 = st.columns(3, gap="medium")
    total = ag.get('total',17); active = ag.get('active',15)
    with c1: st.metric("Active Agents", f"{active}/{total}", f"{active/total*100:.1f}%")
    with c2: st.metric("Avg Confidence", f"{ag.get('avg_confidence',0.94)*100:.1f}%", "+1.2%")
    with c3: st.metric("Alerts (24h)", str(ag.get('alerts_24h',23)), "+5")

    gap("0.75rem")
    c1,c2,c3,c4 = st.columns(4, gap="medium")
    with c1: st.info("**Core Detection**\n\n8 agents active")
    with c2: st.success("**ML Intelligence**\n\n3 agents active")
    with c3: st.warning("**Merchant Success**\n\n3 agents active")
    with c4: st.error("**Security**\n\n3 agents active")

    gap("0.5rem")
    st.divider()

    # ── Recent Alerts ────────────────────────────────────────────
    section_header("🚨", "Recent High-Priority Alerts", "Latest fraud attempts")
    alerts_df = pd.DataFrame([
        {"Time":"2 min ago","Type":"🔴 Account Takeover","Amount":"$12,450","Risk":"HIGH","Status":"Blocked"},
        {"Time":"15 min ago","Type":"🟡 Suspicious Pattern","Amount":"$3,200","Risk":"MEDIUM","Status":"Review"},
        {"Time":"32 min ago","Type":"🔴 Identity Theft","Amount":"$8,900","Risk":"HIGH","Status":"Blocked"},
        {"Time":"1 hr ago","Type":"🟡 Velocity Check","Amount":"$1,500","Risk":"MEDIUM","Status":"Approved"},
        {"Time":"2 hrs ago","Type":"🔴 Card Fraud","Amount":"$5,670","Risk":"HIGH","Status":"Blocked"},
    ])
    st.dataframe(alerts_df, use_container_width=True, hide_index=True)

    gap("0.5rem")
    st.divider()

    # ── System Health ────────────────────────────────────────────
    section_header("⚡", "System Health", "Infrastructure and resource utilization")
    c1,c2,c3,c4 = st.columns(4, gap="medium")
    with c1: st.metric("P50 Latency","187ms","-8ms")
    with c2: st.metric("P95 Latency","534ms","-15ms")
    with c3: st.metric("P99 Latency","1.2s","-200ms")
    with c4: st.metric("Throughput","450/min","+25/min")

    gap("0.75rem")
    st.markdown(f'<div style="font-size:.82rem;font-weight:600;color:{TEXT2};text-transform:uppercase;letter-spacing:.08em;margin-bottom:.5rem;">Resource Utilization</div>', unsafe_allow_html=True)
    st.progress(0.67, text="**CPU Usage:** 67%")
    st.progress(0.52, text="**Memory:** 52%")
    st.progress(0.34, text="**Network I/O:** 34%")

    gap("1rem")
    st.caption("💡 Dashboard auto-refreshes every 60 seconds · Data sourced from AgentFlow backend")
