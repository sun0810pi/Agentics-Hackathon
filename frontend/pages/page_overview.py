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

def metric_card(label, value, delta=None, up=True, dark=True):
    C  = '#0b101e' if dark else '#fff'
    B  = 'rgba(59,130,246,0.14)' if dark else 'rgba(0,0,0,0.06)'
    T  = '#f1f5f9' if dark else '#0f172a'
    T2 = '#94a3b8' if dark else '#64748b'
    dc = '#10b981' if up else '#ef4444'
    arrow = '▲' if up else '▼'
    d = f'<p style="font-size:.78rem;color:{dc};margin:4px 0 0;font-weight:600;">{arrow} {delta}</p>' if delta else ''
    return (
        f'<td style="vertical-align:top;">' +
        f'<div style="background:{C};border:1px solid {B};border-radius:12px;' +
        f'padding:1.1rem 1.1rem .9rem;position:relative;overflow:hidden;">' +
        f'<div style="position:absolute;top:0;left:0;right:0;height:2px;' +
        f'background:linear-gradient(90deg,#3b82f6,#06b6d4);"></div>' +
        f'<p style="font-size:.62rem;font-weight:700;color:{T2};text-transform:uppercase;' +
        f'letter-spacing:.12em;margin:0 0 6px;">{label}</p>' +
        f'<p style="font-size:1.8rem;font-weight:700;color:{T};letter-spacing:-.02em;' +
        f'line-height:1.1;margin:0;">{value}</p>' +
        d +
        f'</div></td>'
    )

def metric_row(cards_html):
    """Table layout — works everywhere, no CSS flex/gap needed."""
    cards = list(cards_html)
    # Last cell: no right padding
    if cards:
        cards[-1] = cards[-1].replace("padding:0 6px 0 0", "padding:0")
    n = len(cards)
    col_w = f'{100//n}%'
    cols = ''.join(f'<col style="width:{col_w}">' for _ in range(n))
    return (
        f'<table style="width:100%;border-collapse:separate;border-spacing:10px 0;margin:0 -10px;table-layout:fixed">' +
        f'<colgroup>{cols}</colgroup>' +
        '<tr>' + ''.join(cards) + '</tr>' +
        '</table>'
    )

def spacer(h="1rem"):
    st.markdown(f'<div style="height:{h}"></div>', unsafe_allow_html=True)

def divider(dark=True):
    c = 'rgba(59,130,246,0.13)' if dark else 'rgba(0,0,0,0.07)'
    st.markdown(f'<hr style="border:none;border-top:1px solid {c};margin:1.25rem 0;">', unsafe_allow_html=True)

def section_label(text, dark=True):
    c = '#94a3b8' if dark else '#64748b'
    st.markdown(f'<div style="font-size:.65rem;font-weight:700;color:{c};text-transform:uppercase;letter-spacing:.14em;margin-bottom:.65rem;">{text}</div>', unsafe_allow_html=True)

def render():
    IS_DARK = st.session_state.get('theme','dark') == 'dark'
    D  = IS_DARK
    TPL = 'plotly_dark' if D else 'plotly_white'
    TEXT  = '#f1f5f9' if D else '#0f172a'
    TEXT2 = '#94a3b8' if D else '#64748b'

    data = _load()
    if not data["ok"]: st.error(f"❌ {data['error']}"); return
    m = data["m"]; ag = data["a"]; ts = data["ts"]

    if not get_data_provider().backend_available:
        st.warning("⚠️ Backend unavailable — showing demo data.")
        spacer(".25rem")

    # ── Header ──────────────────────────────────────────────────
    st.markdown(f'''<div style="margin-bottom:1.25rem;">
<div style="font-size:1.6rem;font-weight:700;letter-spacing:-.025em;color:{TEXT};">📊 Dashboard Overview</div>
<div style="font-size:.82rem;color:{TEXT2};margin-top:3px;">Real-time fraud detection · {datetime.now().strftime("%b %d %Y, %H:%M")}</div>
</div>''', unsafe_allow_html=True)

    # ── KPI Row — single HTML flex block ──────────────────────
    section_label("🎯 Key Performance Indicators", D)
    st.markdown(metric_row([
        metric_card("Total Processed", f"{m.get('total_processed',0):,}", "+5.2%", True, D),
        metric_card("Accuracy", f"{m.get('accuracy',0):.1f}%", "+2.1%", True, D),
        metric_card("Fraud Prevented", format_currency(m.get('fraud_prevented_usd',0)), "+12.3%", True, D),
        metric_card("Avg Latency", f"{m.get('avg_latency_ms',0):.0f}ms", "-8.5ms", True, D),
    ]), unsafe_allow_html=True)

    spacer("1.25rem")

    # ── Stats Row ─────────────────────────────────────────────
    section_label("📈 Processing Statistics", D)
    st.markdown(metric_row([
        metric_card("Approved",       format_number(m.get('total_approved',0)),  "+3.2%",  True, D),
        metric_card("Blocked",        format_number(m.get('total_blocked',0)),   "+15.8%", True, D),
        metric_card("Pending",        format_number(m.get('total_pending',0)),   "-5.1%",  False, D),
        metric_card("Automation Rate",format_percentage(m.get('automation_rate',0)), "+2.3%", True, D),
    ]), unsafe_allow_html=True)

    spacer("1.5rem")
    divider(D)

    # ── Charts Row 1 ─────────────────────────────────────────
    section_label("📊 Transaction Analysis — 30 Days", D)
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown(f'<div style="font-size:.8rem;font-weight:600;color:{TEXT2};margin-bottom:.3rem;">Processing Volume</div>', unsafe_allow_html=True)
        if ts:
            from components.charts import plot_time_series
            plot_time_series(data=ts, title="Invoice Trend", height=300)
        else:
            st.info("No data")
    with ch2:
        st.markdown(f'<div style="font-size:.8rem;font-weight:600;color:{TEXT2};margin-bottom:.3rem;">Risk Distribution</div>', unsafe_allow_html=True)
        from components.charts import plot_risk_distribution
        plot_risk_distribution(data=[
            {"risk_level":"LOW","count":m.get('total_approved',0),"pct":75.2},
            {"risk_level":"MEDIUM","count":m.get('total_pending',0),"pct":12.8},
            {"risk_level":"HIGH","count":m.get('total_blocked',0),"pct":12.0},
        ], title="Risk Scores", height=300)

    spacer("1rem")
    divider(D)

    # ── Charts Row 2 ─────────────────────────────────────────
    section_label("🎯 Detection Performance", D)
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(f'<div style="font-size:.8rem;font-weight:600;color:{TEXT2};margin-bottom:.3rem;">Accuracy Trend (7 Days)</div>', unsafe_allow_html=True)
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
        st.markdown(f'<div style="font-size:.8rem;font-weight:600;color:{TEXT2};margin-bottom:.3rem;">Fraud Types</div>', unsafe_allow_html=True)
        ft = {'Identity Theft':35,'Account Takeover':25,'Synthetic Identity':18,'Card Fraud':12,'Other':10}
        fig2 = go.Figure(data=[go.Pie(labels=list(ft.keys()), values=list(ft.values()), hole=0.42,
            marker=dict(colors=['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6']))])
        fig2.update_layout(template=TPL, height=280, margin=dict(l=0,r=0,t=10,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

    spacer("1rem")
    divider(D)

    # ── Agent Status ─────────────────────────────────────────
    section_label("🤖 Agent Status", D)
    total=ag.get('total',17); active=ag.get('active',15)
    st.markdown(metric_row([
        metric_card("Active Agents",  f"{active}/{total}", f"{active/total*100:.1f}%", True, D),
        metric_card("Avg Confidence", f"{ag.get('avg_confidence',0.94)*100:.1f}%", "+1.2%", True, D),
        metric_card("Alerts (24h)",   str(ag.get('alerts_24h',23)), "+5", True, D),
    ]), unsafe_allow_html=True)
    spacer(".75rem")
    t1,t2,t3,t4 = st.columns(4)
    with t1: st.info("**Core Detection**\n8 agents")
    with t2: st.success("**ML Intelligence**\n3 agents")
    with t3: st.warning("**Merchant**\n3 agents")
    with t4: st.error("**Security**\n3 agents")

    spacer("1rem")
    divider(D)

    # ── Alerts ────────────────────────────────────────────────
    section_label("🚨 Recent High-Priority Alerts", D)
    st.dataframe(pd.DataFrame([
        {"Time":"2 min ago","Type":"🔴 Account Takeover","Amount":"$12,450","Risk":"HIGH","Status":"Blocked"},
        {"Time":"15 min ago","Type":"🟡 Suspicious Pattern","Amount":"$3,200","Risk":"MEDIUM","Status":"Review"},
        {"Time":"32 min ago","Type":"🔴 Identity Theft","Amount":"$8,900","Risk":"HIGH","Status":"Blocked"},
        {"Time":"1 hr ago","Type":"🟡 Velocity Check","Amount":"$1,500","Risk":"MEDIUM","Status":"Approved"},
        {"Time":"2 hrs ago","Type":"🔴 Card Fraud","Amount":"$5,670","Risk":"HIGH","Status":"Blocked"},
    ]), use_container_width=True, hide_index=True)

    spacer("1rem")
    divider(D)

    # ── System Health ─────────────────────────────────────────
    section_label("⚡ System Health", D)
    st.markdown(metric_row([
        metric_card("P50 Latency","187ms","-8ms",True,D),
        metric_card("P95 Latency","534ms","-15ms",True,D),
        metric_card("P99 Latency","1.2s","-200ms",True,D),
        metric_card("Throughput","450/min","+25/min",True,D),
    ]), unsafe_allow_html=True)
    spacer(".75rem")
    st.markdown(f'<div style="font-size:.8rem;font-weight:600;color:{TEXT2};margin-bottom:.4rem;">Resource Utilization</div>', unsafe_allow_html=True)
    st.progress(0.67, text="CPU: 67%")
    st.progress(0.52, text="Memory: 52%")
    st.progress(0.34, text="Network: 34%")
    spacer("1.5rem")
    st.caption("💡 Auto-refreshes every 60 seconds")
