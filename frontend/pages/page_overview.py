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

def metric_html(label, value, delta=None, delta_pos=True, theme='dark'):
    """Render a metric card as pure HTML — no Streamlit metric widget."""
    CARD  = '#0c1020' if theme=='dark' else '#ffffff'
    BOR   = 'rgba(59,130,246,0.18)' if theme=='dark' else 'rgba(0,0,0,0.08)'
    TEXT  = '#f1f5f9' if theme=='dark' else '#0f172a'
    TEXT2 = '#94a3b8' if theme=='dark' else '#64748b'
    dc    = '#10b981' if delta_pos else '#ef4444'
    da    = '↑' if delta_pos else '↓'
    delta_html = f'<div style="font-size:.8rem;color:{dc};margin-top:.3rem;font-weight:500;">{da} {delta}</div>' if delta else ''
    return f"""
<div style="background:{CARD};border:1px solid {BOR};border-radius:12px;
  padding:1.1rem 1.25rem 1rem;position:relative;overflow:hidden;
  box-shadow:0 2px 12px rgba(0,0,0,0.15);">
  <div style="position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,#3b82f6,#06b6d4);opacity:.7;"></div>
  <div style="font-size:.68rem;font-weight:600;color:{TEXT2};
    text-transform:uppercase;letter-spacing:.1em;margin-bottom:.5rem;">{label}</div>
  <div style="font-size:1.9rem;font-weight:700;color:{TEXT};
    letter-spacing:-.025em;line-height:1.1;">{value}</div>
  {delta_html}
</div>"""

def spacer(h="1rem"):
    st.markdown(f'<div style="height:{h}"></div>', unsafe_allow_html=True)

def render():
    IS_DARK = st.session_state.get('theme','dark') == 'dark'
    THEME = 'dark' if IS_DARK else 'light'
    TPL   = 'plotly_dark' if IS_DARK else 'plotly_white'
    TEXT  = '#f1f5f9' if IS_DARK else '#0f172a'
    TEXT2 = '#94a3b8' if IS_DARK else '#64748b'
    BOR   = 'rgba(59,130,246,0.13)' if IS_DARK else 'rgba(0,0,0,0.07)'

    provider = get_data_provider()
    data = _load()
    if not data["ok"]: st.error(f"❌ {data['error']}"); return
    m = data["m"]; ag = data["a"]; ts = data["ts"]

    # ── Header ──────────────────────────────────────────────────
    st.markdown(f"""
<div style="margin-bottom:1.25rem;">
  <div style="font-size:1.6rem;font-weight:700;letter-spacing:-.025em;color:{TEXT};">
    📊 Dashboard Overview
  </div>
  <div style="font-size:.82rem;color:{TEXT2};margin-top:3px;">
    Real-time fraud detection · {datetime.now().strftime("%b %d %Y, %H:%M")}
  </div>
</div>""", unsafe_allow_html=True)

    if not provider.backend_available:
        st.warning("⚠️ Backend unavailable — showing demo data.")
        spacer(".25rem")

    # ── KPI Row — HTML cards ──────────────────────────────────
    st.markdown(f'<div style="font-size:.7rem;font-weight:700;color:{TEXT2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.6rem;">🎯 Key Performance Indicators</div>', unsafe_allow_html=True)
    
    # Use 4-col layout with gap via HTML wrapper
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(metric_html("Total Processed", f"{m.get('total_processed',0):,}", "+5.2%", True, THEME), unsafe_allow_html=True)
    with c2: st.markdown(metric_html("Accuracy", f"{m.get('accuracy',0):.1f}%", "+2.1%", True, THEME), unsafe_allow_html=True)
    with c3: st.markdown(metric_html("Fraud Prevented", format_currency(m.get('fraud_prevented_usd',0)), "+12.3%", True, THEME), unsafe_allow_html=True)
    with c4: st.markdown(metric_html("Avg Latency", f"{m.get('avg_latency_ms',0):.0f}ms", "-8.5ms", True, THEME), unsafe_allow_html=True)

    spacer("1.25rem")

    # ── Stats Row — HTML cards ────────────────────────────────
    st.markdown(f'<div style="font-size:.7rem;font-weight:700;color:{TEXT2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.6rem;">📈 Processing Statistics</div>', unsafe_allow_html=True)
    
    s1,s2,s3,s4 = st.columns(4)
    with s1: st.markdown(metric_html("Approved", format_number(m.get('total_approved',0)), "+3.2%", True, THEME), unsafe_allow_html=True)
    with s2: st.markdown(metric_html("Blocked", format_number(m.get('total_blocked',0)), "+15.8%", True, THEME), unsafe_allow_html=True)
    with s3: st.markdown(metric_html("Pending", format_number(m.get('total_pending',0)), "-5.1%", False, THEME), unsafe_allow_html=True)
    with s4: st.markdown(metric_html("Automation Rate", format_percentage(m.get('automation_rate',0)), "+2.3%", True, THEME), unsafe_allow_html=True)

    spacer("1.5rem")
    st.markdown(f'<hr style="border:none;border-top:1px solid {BOR};margin:0 0 1.25rem;">', unsafe_allow_html=True)

    # ── Charts Row 1 ─────────────────────────────────────────
    st.markdown(f'<div style="font-size:.7rem;font-weight:700;color:{TEXT2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.75rem;">📊 Transaction Analysis — 30 Days</div>', unsafe_allow_html=True)
    
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown(f'<div style="font-size:.8rem;font-weight:600;color:{TEXT2};margin-bottom:.4rem;">Processing Volume</div>', unsafe_allow_html=True)
        if ts:
            from components.charts import plot_time_series
            plot_time_series(data=ts, title="Invoice Trend", height=300)
        else:
            st.info("No time series data")
    with ch2:
        st.markdown(f'<div style="font-size:.8rem;font-weight:600;color:{TEXT2};margin-bottom:.4rem;">Risk Distribution</div>', unsafe_allow_html=True)
        from components.charts import plot_risk_distribution
        plot_risk_distribution(data=[
            {"risk_level":"LOW",   "count":m.get('total_approved',0),"pct":75.2},
            {"risk_level":"MEDIUM","count":m.get('total_pending',0), "pct":12.8},
            {"risk_level":"HIGH",  "count":m.get('total_blocked',0), "pct":12.0},
        ], title="Risk Scores", height=300)

    spacer("1rem")
    st.markdown(f'<hr style="border:none;border-top:1px solid {BOR};margin:0 0 1.25rem;">', unsafe_allow_html=True)

    # ── Charts Row 2 ─────────────────────────────────────────
    st.markdown(f'<div style="font-size:.7rem;font-weight:700;color:{TEXT2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.75rem;">🎯 Detection Performance</div>', unsafe_allow_html=True)
    
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(f'<div style="font-size:.8rem;font-weight:600;color:{TEXT2};margin-bottom:.4rem;">Accuracy Trend (7 Days)</div>', unsafe_allow_html=True)
        days = [(datetime.now()-timedelta(days=i)).strftime("%b %d") for i in range(6,-1,-1)]
        fig  = go.Figure()
        fig.add_trace(go.Scatter(x=days, y=[95.2,96.1,97.3,96.8,97.6,98.1,98.3],
            mode='lines+markers', line=dict(color='#3b82f6',width=2.5), marker=dict(size=6),
            fill='tozeroy', fillcolor='rgba(59,130,246,0.08)'))
        fig.update_layout(template=TPL, height=280, margin=dict(l=0,r=0,t=10,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(range=[94,100],ticksuffix='%'), hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    with p2:
        st.markdown(f'<div style="font-size:.8rem;font-weight:600;color:{TEXT2};margin-bottom:.4rem;">Fraud Types</div>', unsafe_allow_html=True)
        ft = {'Identity Theft':35,'Account Takeover':25,'Synthetic Identity':18,'Card Fraud':12,'Other':10}
        fig2 = go.Figure(data=[go.Pie(labels=list(ft.keys()), values=list(ft.values()), hole=0.42,
            marker=dict(colors=['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6']))])
        fig2.update_layout(template=TPL, height=280, margin=dict(l=0,r=0,t=10,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

    spacer("1rem")
    st.markdown(f'<hr style="border:none;border-top:1px solid {BOR};margin:0 0 1.25rem;">', unsafe_allow_html=True)

    # ── Agent Status ─────────────────────────────────────────
    st.markdown(f'<div style="font-size:.7rem;font-weight:700;color:{TEXT2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.6rem;">🤖 Agent Status</div>', unsafe_allow_html=True)
    total=ag.get('total',17); active=ag.get('active',15)
    a1,a2,a3 = st.columns(3)
    with a1: st.markdown(metric_html("Active Agents",f"{active}/{total}",f"{active/total*100:.1f}%",True,THEME), unsafe_allow_html=True)
    with a2: st.markdown(metric_html("Avg Confidence",f"{ag.get('avg_confidence',0.94)*100:.1f}%","+1.2%",True,THEME), unsafe_allow_html=True)
    with a3: st.markdown(metric_html("Alerts (24h)",str(ag.get('alerts_24h',23)),"+5",True,THEME), unsafe_allow_html=True)

    spacer(".75rem")
    t1,t2,t3,t4 = st.columns(4)
    with t1: st.info("**Core Detection**\n8 agents")
    with t2: st.success("**ML Intelligence**\n3 agents")
    with t3: st.warning("**Merchant**\n3 agents")
    with t4: st.error("**Security**\n3 agents")

    spacer("1rem")
    st.markdown(f'<hr style="border:none;border-top:1px solid {BOR};margin:0 0 1.25rem;">', unsafe_allow_html=True)

    # ── Recent Alerts ─────────────────────────────────────────
    st.markdown(f'<div style="font-size:.7rem;font-weight:700;color:{TEXT2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.6rem;">🚨 Recent High-Priority Alerts</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([
        {"Time":"2 min ago","Type":"🔴 Account Takeover","Amount":"$12,450","Risk":"HIGH","Status":"Blocked"},
        {"Time":"15 min ago","Type":"🟡 Suspicious Pattern","Amount":"$3,200","Risk":"MEDIUM","Status":"Review"},
        {"Time":"32 min ago","Type":"🔴 Identity Theft","Amount":"$8,900","Risk":"HIGH","Status":"Blocked"},
        {"Time":"1 hr ago","Type":"🟡 Velocity Check","Amount":"$1,500","Risk":"MEDIUM","Status":"Approved"},
        {"Time":"2 hrs ago","Type":"🔴 Card Fraud","Amount":"$5,670","Risk":"HIGH","Status":"Blocked"},
    ]), use_container_width=True, hide_index=True)

    spacer("1rem")
    st.markdown(f'<hr style="border:none;border-top:1px solid {BOR};margin:0 0 1.25rem;">', unsafe_allow_html=True)

    # ── System Health ─────────────────────────────────────────
    st.markdown(f'<div style="font-size:.7rem;font-weight:700;color:{TEXT2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.6rem;">⚡ System Health</div>', unsafe_allow_html=True)
    h1,h2,h3,h4 = st.columns(4)
    with h1: st.markdown(metric_html("P50 Latency","187ms","-8ms",True,THEME), unsafe_allow_html=True)
    with h2: st.markdown(metric_html("P95 Latency","534ms","-15ms",True,THEME), unsafe_allow_html=True)
    with h3: st.markdown(metric_html("P99 Latency","1.2s","-200ms",True,THEME), unsafe_allow_html=True)
    with h4: st.markdown(metric_html("Throughput","450/min","+25/min",True,THEME), unsafe_allow_html=True)

    spacer(".75rem")
    st.markdown(f'<div style="font-size:.8rem;font-weight:600;color:{TEXT2};margin-bottom:.5rem;">Resource Utilization</div>', unsafe_allow_html=True)
    st.progress(0.67, text="CPU: 67%")
    st.progress(0.52, text="Memory: 52%")
    st.progress(0.34, text="Network: 34%")
    spacer("1rem")
    st.caption("💡 Auto-refreshes every 60 seconds")
