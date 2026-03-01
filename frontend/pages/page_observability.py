import streamlit as st
import random
import pandas as pd
import plotly.graph_objects as go


def _card(col, label, value, delta=None, up=True):
    D   = st.session_state.get('theme', 'dark') == 'dark'
    BG  = '#141414' if D else '#ffffff'
    BOR = '#262626'  if D else '#0a0a0a'
    T   = '#f5f5f5' if D else '#0a0a0a'
    T2  = '#a3a3a3' if D else '#737373'
    SHD = '2px 2px 0px rgba(255,255,255,0.08)' if D else '4px 4px 0px #0a0a0a'
    dc  = '#10b981' if up else '#ef4444'
    d   = f'<div style="font-size:.75rem;color:{dc};margin-top:.35rem;font-weight:600;">{"+" if up else ""}{delta}</div>' if delta else ''
    col.markdown(
        f'<div style="background:{BG};border:2px solid {BOR};border-radius:0;'
        f'padding:1rem 1.1rem .9rem;position:relative;overflow:hidden;box-shadow:{SHD};">'
        f'<div style="position:absolute;top:0;left:0;right:0;height:3px;background:#10b981;"></div>'
        f'<div style="font-size:.6rem;color:{T2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.35rem;">{label}</div>'
        f'<div style="font-size:1.85rem;font-weight:800;color:{T};line-height:1.1;">{value}</div>'
        f'{d}</div>',
        unsafe_allow_html=True
    )


def render():
    from components.widgets import alert_box, progress_bar_animated
    from services.data_provider import get_data_provider
    import logging
    logger = logging.getLogger(__name__)

    D   = st.session_state.get('theme', 'dark') == 'dark'
    TPL = 'plotly_dark' if D else 'plotly_white'
    T   = '#f5f5f5' if D else '#0a0a0a'
    T2  = '#a3a3a3' if D else '#737373'
    BOR = '#262626'  if D else '#e5e5e5'
    BG2 = '#1a1a1a'  if D else '#f5f5f5'

    # Page header
    st.markdown(
        f'<div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:2px solid {BOR};">'
        f'<div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.35rem;">'
        f'<span style="font-size:1.5rem;">📈</span>'
        f'<h1 style="font-size:1.75rem;font-weight:800;color:{T};letter-spacing:-.03em;margin:0;">Observability & Monitoring</h1>'
        f'</div>'
        f'<p style="font-size:.72rem;color:#10b981;letter-spacing:.06em;margin:0;text-transform:uppercase;">'
        f'Distributed tracing · CloudWatch metrics</p></div>',
        unsafe_allow_html=True
    )

    provider = get_data_provider()
    if not provider.backend_available:
        alert_box("⚠️ Backend unavailable. Showing demo observability data.", "warning")

    # Load traces
    try:
        traces = provider.get_xray_traces(limit=10)
    except Exception as e:
        logger.error(f"Error loading traces: {e}")
        traces = []

    # System health KPIs
    st.markdown(f'<div style="font-size:.62rem;font-weight:600;color:{T2};text-transform:uppercase;'
                f'letter-spacing:.14em;margin-bottom:.6rem;">SYSTEM HEALTH</div>', unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    _card(k1, "System Uptime",     "99.95%",  "0.02%", True)
    _card(k2, "Avg Response Time", "245ms",   "12ms",  True)
    _card(k3, "Error Rate",        "0.15%",   "0.05%", True)
    _card(k4, "Active Requests",   "42",      "5",     True)

    st.markdown('<div style="height:.9rem"></div>', unsafe_allow_html=True)
    st.markdown(f'<hr style="border:none;border-top:2px solid {BOR};margin:.5rem 0 1rem;">', unsafe_allow_html=True)

    # Performance metrics
    st.markdown(f'<div style="font-size:.62rem;font-weight:600;color:{T2};text-transform:uppercase;'
                f'letter-spacing:.14em;margin-bottom:.6rem;">PERFORMANCE METRICS</div>', unsafe_allow_html=True)
    p1, p2, p3, p4 = st.columns(4)
    _card(p1, "P50 Latency", "187ms",   "8ms",   True)
    _card(p2, "P95 Latency", "534ms",   "15ms",  True)
    _card(p3, "P99 Latency", "1.2s",    "200ms", True)
    _card(p4, "Throughput",  "450/min", "25/min",True)

    st.markdown('<div style="height:.9rem"></div>', unsafe_allow_html=True)
    st.markdown(f'<hr style="border:none;border-top:2px solid {BOR};margin:.5rem 0 1rem;">', unsafe_allow_html=True)

    # X-Ray traces — NO st.expander (causes "par" rendering bug)
    st.markdown(f'<div style="font-size:.62rem;font-weight:600;color:{T2};text-transform:uppercase;'
                f'letter-spacing:.14em;margin-bottom:.75rem;">RECENT X-RAY TRACES</div>', unsafe_allow_html=True)

    if not traces:
        st.info("No traces available")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("STATUS", ['All', 'SUCCESS', 'ERROR'], index=0)
        with col2:
            min_duration = st.number_input("MIN DURATION (MS)", min_value=0, value=0, step=100)
        with col3:
            max_traces = st.slider("SHOW TRACES", min_value=5, max_value=50, value=10)

        st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)

        for i, trace in enumerate(traces[:max_traces]):
            trace_id  = trace.get('id', f'TRACE-{i}')
            timestamp = trace.get('timestamp', '')
            duration  = trace.get('duration', 0)
            status    = trace.get('status', 'UNKNOWN')
            segments  = trace.get('segments', [])

            if status_filter != 'All' and status != status_filter:
                continue
            if duration < min_duration:
                continue

            ok  = status == 'SUCCESS'
            ts  = timestamp[:19].replace('T', ' ') if len(timestamp) > 10 else timestamp
            sc  = '#10b981' if ok else '#ef4444'
            ico = '✓' if ok else '✗'  # FIXED: Clean symbols
            rb  = '#1a2e1a' if (ok and D) else ('#2e1a1a' if (not ok and D) else ('#e8f5e9' if ok else '#fdecea'))

            # FIXED: X-Ray trace with proper fonts
            st.markdown(
                f'<div style="background:{BG2};border:2px solid {BOR};border-left:4px solid {sc};'
                f'padding:.8rem 1.1rem;margin-bottom:.5rem;display:flex;align-items:center;gap:1rem;'
                f'font-family:system-ui,-apple-system,sans-serif;">'
                f'<span style="font-size:.8rem;font-weight:700;color:{sc};background:{rb};'
                f'padding:.3rem .6rem;border-radius:6px;flex-shrink:0;min-width:1.8rem;text-align:center;">{ico}</span>'
                f'<span style="font-family:\'JetBrains Mono\',\'SF Mono\',\'Courier New\',monospace;'
                f'font-size:.88rem;color:{T};font-weight:600;flex-shrink:0;letter-spacing:-.02em;">{trace_id}</span>'
                f'<span style="font-size:.82rem;color:{T2};font-weight:500;">{duration}ms</span>'
                f'<span style="font-size:.78rem;color:{T2};margin-left:auto;white-space:nowrap;">{ts}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            # Details toggle via session_state button
            tog_key = f"otog_{i}"
            if tog_key not in st.session_state:
                st.session_state[tog_key] = False
            btn_txt = "▼ Hide" if st.session_state[tog_key] else "▶ Details"
            if st.button(btn_txt, key=f"obtn_{i}"):
                st.session_state[tog_key] = not st.session_state[tog_key]
                st.rerun()
            if st.session_state[tog_key]:
                dc1, dc2, dc3 = st.columns(3)
                dc1.metric("Duration", f"{duration}ms")
                dc2.metric("Segments", len(segments))
                dc3.metric("Status", status)
                if segments:
                    st.markdown(f'<div style="font-size:.75rem;color:{T2};margin:.5rem 0 .25rem;">Segments</div>',
                                unsafe_allow_html=True)
                    for seg in segments:
                        sn  = seg.get('name', 'Unknown')
                        sd  = seg.get('duration', 0)
                        ss  = seg.get('status', 'OK')
                        pct = (sd / duration * 100) if duration > 0 else 0
                        sc1, sc2 = st.columns([3, 1])
                        with sc1:
                            st.markdown(f"**{sn}** — {sd}ms")
                            progress_bar_animated(pct, 100, show_percentage=False,
                                color='success' if ss == 'OK' else 'danger')
                        with sc2:
                            st.markdown(f"{pct:.1f}%")
                hm = trace.get('http_method', 'POST')
                hs = trace.get('http_status', 200)
                hu = trace.get('url', '/api/analyze')
                st.code(f"{hm} {hu}  HTTP {hs}")
                st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)

    st.markdown(f'<hr style="border:none;border-top:2px solid {BOR};margin:1rem 0;">', unsafe_allow_html=True)

    # CloudWatch tabs
    st.markdown(f'<div style="font-size:.62rem;font-weight:600;color:{T2};text-transform:uppercase;'
                f'letter-spacing:.14em;margin-bottom:.75rem;">CLOUDWATCH METRICS</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["API Gateway", "Lambda", "Database"])
    times = pd.date_range(end=pd.Timestamp.now(), periods=12, freq='5min')

    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Requests", "4,523", "+12%")
        c2.metric("4xx Errors", "23", "-5%")
        c3.metric("5xx Errors", "7", "-2")
        st.markdown("---")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=[random.randint(350, 450) for _ in range(12)],
            mode='lines+markers', name='Requests/5min', line=dict(color='#10b981', width=2.5)))
        fig.update_layout(template=TPL, height=280, margin=dict(l=0,r=0,t=8,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        c1, c2, c3 = st.columns(3)
        c1.metric("Invocations", "3,892", "+8%")
        c2.metric("Avg Duration", "2.3s", "-200ms")
        c3.metric("Errors", "12", "-3")
        st.markdown("---")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=[random.randint(1800, 2800) for _ in range(12)],
            mode='lines+markers', name='Duration ms', line=dict(color='#f59e0b', width=2.5)))
        fig.update_layout(template=TPL, height=280, margin=dict(l=0,r=0,t=8,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        c1, c2, c3 = st.columns(3)
        c1.metric("CPU Usage", "42%", "-8%")
        c2.metric("Connections", "28", "+3")
        c3.metric("Query Time", "15ms", "-2ms")
        st.markdown("---")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=[random.randint(20, 35) for _ in range(12)],
            mode='lines+markers', name='Connections', line=dict(color='#059669', width=2.5)))
        fig.update_layout(template=TPL, height=280, margin=dict(l=0,r=0,t=8,b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
